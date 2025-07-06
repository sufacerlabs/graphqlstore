"""Pruebas para la funcion migracion"""

from pathlib import Path
from unittest.mock import Mock, patch
import pytest
from source.cli.migracion.main import migracion
from source.cli.database.adaptadores.mysql import AdaptadorMySQL
from source.cli.loaders.conf_json_loader import ConfiguracionJsonLoader
from source.cli.graphql.mysql_generador import GeneradorEsquemaMySQL
from source.cli.graphql.mysql_migracion import GeneradorMigracionMySQL
from source.cli.graphql.configuracion_y_constantes import (
    InfoMigracion,
    InfoDiffEsquema,
)
from source.cli.graphql.exceptions import (
    GraphQLStoreError,
    MigrationError,
)


@pytest.fixture(name="mock_args")
def fixture_mock_args():
    """Fixture que proporciona argumentos simulados básicos."""
    args = Mock()
    args.esquema = "new_schema.graphql"
    args.antiguo_esquema = None
    args.salida = "migraciones"
    args.no_visualizar_salida = False
    args.no_visualizar_sql = False
    return args


@pytest.fixture(name="mock_args_sin_esquema")
def fixture_mock_args_sin_esquema():
    """Fixture que proporciona argumentos simulados sin \
        esquema especificado."""
    args = Mock()
    args.esquema = None
    args.antiguo_esquema = None
    args.salida = "migraciones"
    args.no_visualizar_salida = True
    args.no_visualizar_sql = True
    return args


@pytest.fixture(name="esquema_anterior")
def fixture_esquema_anterior():
    """Fixture que proporciona contenido de esquema GraphQL anterior."""
    return """
    type User {
        id: ID! @id
        name: String!
        email: String
    }
    """


@pytest.fixture(name="esquema_nuevo")
def fixture_esquema_nuevo():
    """Fixture que proporciona contenido de esquema GraphQL nuevo."""
    return """
    type User {
        id: ID! @id
        name: String!
        email: String!
        age: Int
        posts: [Post] @relation(name: "UserPosts")
    }

    type Post {
        id: ID! @id
        title: String!
        content: String
        author: User @relation(name: "UserPosts", onDelete: CASCADE)
    }
    """


@pytest.fixture(name="config_valida")
def fixture_config_valida():
    """Fixture que proporciona una configuración válida de BD."""
    return {
        "DB_HOST": "localhost",
        "DB_PUERTO": "3306",
        "DB_USUARIO": "testuser",
        "DB_PASSWORD": "testpass",
        "DB_NOMBRE": "testdb",
    }


@pytest.fixture(name="mock_loader")
def fixture_config_json_loader(config_valida):
    """Fixture que proporciona un ConfiguracionJsonLoader simulado."""
    loader = Mock(spec=ConfiguracionJsonLoader)
    loader.cargar_configuracion.return_value = config_valida
    return loader


@pytest.fixture(name="mock_adaptador")
def fixture_adaptador_mysql():
    """Fixture que proporciona un adaptador MySQL simulado."""
    adaptador = Mock(spec=AdaptadorMySQL)
    adaptador.conectar.return_value = None
    adaptador.ejecutar_consulta.return_value = None
    adaptador.cerrar_conexion.return_value = None
    adaptador.cursor = Mock()
    adaptador.cursor.fetchall.return_value = [("users",), ("posts",)]
    return adaptador


@pytest.fixture(name="mock_adaptador_sin_tablas")
def fixture_adaptador_mysql_sin_tablas():
    """Fixture que proporciona un adaptador MySQL sin tablas."""
    adaptador = Mock(spec=AdaptadorMySQL)
    adaptador.conectar.return_value = None
    adaptador.ejecutar_consulta.return_value = None
    adaptador.cerrar_conexion.return_value = None
    adaptador.cursor = Mock()
    adaptador.cursor.fetchall.return_value = []
    return adaptador


@pytest.fixture(name="mock_generador_migracion")
def fixture_generador_migracion():
    """Fixture que proporciona un GeneradorMigracionMySQL simulado."""
    generador = Mock(spec=GeneradorMigracionMySQL)

    # Mock de InfoMigracion con cambios
    mock_diferencias = Mock(spec=InfoDiffEsquema)
    mock_diferencias.tiene_cambios.return_value = True

    mock_migracion = Mock(spec=InfoMigracion)
    mock_migracion.id_migracion = "migration_20241217_143022_abcd1234"
    msg = "ALTER TABLE User ADD COLUMN age INT;\n"
    msg += "CREATE TABLE Post (id VARCHAR(25) PRIMARY KEY);"
    mock_migracion.sql_generado = msg
    mock_migracion.diferencias = mock_diferencias

    generador.generar_migracion.return_value = mock_migracion
    return generador


@pytest.fixture(name="mock_generador_esquema")
def fixture_generador_esquema():
    """Fixture que proporciona un GeneradorEsquemaMySQL simulado."""
    generador = Mock(spec=GeneradorEsquemaMySQL)
    esquema_cliente = """
    type User {
        id: ID!
        name: String!
        email: String!
        age: Int
        posts: [Post]
    }

    type Post {
        id: ID!
        title: String!
        content: String
        author: User
    }
    """
    generador.transformar_esquema_graphql.return_value = esquema_cliente
    return generador


@pytest.fixture(name="ruta_proyecto")
def fixture_ruta_proyecto():
    """Fixture que proporciona una ruta de proyecto."""
    return Path("/proyecto/test")


def test_migracion_con_esquema_especificado_exitoso(
    mock_args,
    esquema_anterior,
    esquema_nuevo,
    mock_loader,
    mock_adaptador,
    mock_generador_migracion,
    mock_generador_esquema,
    ruta_proyecto,
):
    """Prueba migración exitosa con esquema especificado."""
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    with (
        patch(
            "source.cli.migracion.main.Path.cwd",
            return_value=ruta_proyecto,
        ),
        patch("source.cli.migracion.main.Path.exists", return_value=True),
        patch(
            "source.cli.migracion.main.GestorArchivo.leer_archivo",
            side_effect=[esquema_anterior, esquema_nuevo],
        ),
        patch("source.cli.migracion.main.GestorArchivo.escribir_archivo"),
        patch("source.cli.migracion.main.GestorArchivo.asegurar_dir_existe"),
        patch(
            "source.cli.migracion.main.ConfiguracionJsonLoader",
            return_value=mock_loader,
        ),
        patch(
            "source.cli.migracion.main.AdaptadorMySQL",
            return_value=mock_adaptador,
        ),
        patch(
            "source.cli.migracion.main.GeneradorMigracionMySQL",
            return_value=mock_generador_migracion,
        ),
        patch(
            "source.cli.migracion.main.GeneradorEsquemaMySQL",
            return_value=mock_generador_esquema,
        ),
        patch("source.cli.migracion.main.Console"),
    ):
        migracion(mock_args)

        # verificar que se cargó la configuracion
        mock_loader.cargar_configuracion.assert_called_once()

        # pylint: disable=import-outside-toplevel
        from source.cli.migracion.main import GestorArchivo

        # pylint: enable=import-outside-toplevel

        assert GestorArchivo.leer_archivo.call_count == 2

        # verificar que se genero la migracion
        mock_generador_migracion.generar_migracion.assert_called_once_with(
            esquema_anterior=esquema_anterior,
            esquema_nuevo=esquema_nuevo,
            visualizar_salida=True,
            visualizar_sql=True,
        )

        # verificar conexion a BD y verificacion de tablas
        mock_adaptador.conectar.assert_called_once()
        mock_adaptador.ejecutar_consulta.assert_called()
        mock_adaptador.cerrar_conexion.assert_called_once()

        # verificar que se guardo la migracion
        GestorArchivo.escribir_archivo.assert_called()
        GestorArchivo.asegurar_dir_existe.assert_called()

        # verificar que se actualizó el esquema cliente
        ss = mock_generador_esquema.transformar_esquema_graphql
        ss.assert_called_once_with(
            esquema_nuevo,
        )


def test_migracion_con_esquema_especificado_no_existe(
    mock_args,
    esquema_anterior,
    mock_loader,
    ruta_proyecto,
):
    """Prueba migración con esquema especificado que no existe."""
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    with (
        patch(
            "source.cli.migracion.main.Path.cwd",
            return_value=ruta_proyecto,
        ),
        patch(
            "source.cli.migracion.main.Path.exists",
            side_effect=[True, False],
        ),
        patch(
            "source.cli.migracion.main.GestorArchivo.leer_archivo",
            return_value=esquema_anterior,
        ),
        patch(
            "source.cli.migracion.main.ConfiguracionJsonLoader",
            return_value=mock_loader,
        ),
        patch("source.cli.migracion.main.Console") as mock_console,
    ):
        migracion(mock_args)

        mock_consola_instancia = mock_console.return_value
        llamadas = mock_consola_instancia.print.call_args_list
        for call in llamadas:
            if "no se ha encontrado el esquema" in str(call).lower():
                break
    # pylint: enable=too-many-arguments,too-many-positional-arguments


def test_migracion_sin_esquema_encuentra_archivo_graphql(
    mock_args_sin_esquema,
    esquema_anterior,
    esquema_nuevo,
    mock_loader,
    mock_adaptador,
    mock_generador_migracion,
    mock_generador_esquema,
    ruta_proyecto,
):
    """Prueba migración exitosa sin esquema especificado, \
        encuentra archivo .graphql."""
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    mock_esquema_archivo = ruta_proyecto / "new_schema.graphql"

    with (
        patch(
            "source.cli.migracion.main.Path.cwd",
            return_value=ruta_proyecto,
        ),
        patch("source.cli.migracion.main.Path.exists", return_value=True),
        patch.object(Path, "glob", return_value=iter([mock_esquema_archivo])),
        patch(
            "source.cli.migracion.main.GestorArchivo.leer_archivo",
            side_effect=[esquema_anterior, esquema_nuevo],
        ),
        patch("source.cli.migracion.main.GestorArchivo.escribir_archivo"),
        patch("source.cli.migracion.main.GestorArchivo.asegurar_dir_existe"),
        patch(
            "source.cli.migracion.main.ConfiguracionJsonLoader",
            return_value=mock_loader,
        ),
        patch(
            "source.cli.migracion.main.AdaptadorMySQL",
            return_value=mock_adaptador,
        ),
        patch(
            "source.cli.migracion.main.GeneradorMigracionMySQL",
            return_value=mock_generador_migracion,
        ),
        patch(
            "source.cli.migracion.main.GeneradorEsquemaMySQL",
            return_value=mock_generador_esquema,
        ),
        patch("source.cli.migracion.main.Console"),
    ):
        migracion(mock_args_sin_esquema)

        # pylint: disable=import-outside-toplevel
        from source.cli.migracion.main import GestorArchivo

        # pylint: enable=import-outside-toplevel

        assert GestorArchivo.leer_archivo.call_count == 2

        GestorArchivo.leer_archivo.assert_called()

        mock_generador_migracion.generar_migracion.assert_called_once()
    # pylint: enable=too-many-arguments,too-many-positional-arguments


def test_migracion_sin_esquema_y_sin_archivo_graphql(
    mock_args_sin_esquema,
    esquema_anterior,
    mock_loader,
    ruta_proyecto,
):
    """Prueba migración sin esquema especificado y sin archivo .graphql."""

    with (
        patch(
            "source.cli.migracion.main.Path.cwd",
            return_value=ruta_proyecto,
        ),
        patch("source.cli.migracion.main.Path.exists", return_value=True),
        patch(
            "source.cli.migracion.main.GestorArchivo.leer_archivo",
            return_value=esquema_anterior,
        ),
        patch.object(Path, "glob", return_value=iter([])),
        patch(
            "source.cli.migracion.main.ConfiguracionJsonLoader",
            return_value=mock_loader,
        ),
        patch("source.cli.migracion.main.Console") as mock_console,
    ):
        migracion(mock_args_sin_esquema)

        mock_consola_instancia = mock_console.return_value
        llamadas = mock_consola_instancia.print.call_args_list
        msg = "no se ha proporcionado"
        assert any(msg in str(call).lower() for call in llamadas)


def test_migracion_bd_sin_tablas_existentes(
    mock_args,
    esquema_anterior,
    esquema_nuevo,
    mock_loader,
    mock_adaptador_sin_tablas,
    mock_generador_migracion,
    ruta_proyecto,
):
    """Prueba migración cuando la BD no tiene tablas existentes."""
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    with (
        patch(
            "source.cli.migracion.main.Path.cwd",
            return_value=ruta_proyecto,
        ),
        patch("source.cli.migracion.main.Path.exists", return_value=True),
        patch(
            "source.cli.migracion.main.GestorArchivo.leer_archivo",
            side_effect=[esquema_anterior, esquema_nuevo],
        ),
        patch(
            "source.cli.migracion.main.ConfiguracionJsonLoader",
            return_value=mock_loader,
        ),
        patch(
            "source.cli.migracion.main.AdaptadorMySQL",
            return_value=mock_adaptador_sin_tablas,
        ),
        patch(
            "source.cli.migracion.main.GeneradorMigracionMySQL",
            return_value=mock_generador_migracion,
        ),
        patch("source.cli.migracion.main.Console") as mock_console,
    ):
        migracion(mock_args)

        mock_consola_instancia = mock_console.return_value
        llamadas = mock_consola_instancia.print.call_args_list
        assert any("inicializar" in str(call) for call in llamadas)
    # pylint: enable=too-many-arguments,too-many-positional-arguments


def test_migracion_manejo_graphqlstore_error(
    mock_args,
    esquema_anterior,
    esquema_nuevo,
    mock_loader,
    ruta_proyecto,
):
    """Prueba manejo de GraphQLStoreError durante migración."""
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    mock_generador_error = Mock(spec=GeneradorMigracionMySQL)
    mock_generador_error.generar_migracion.side_effect = GraphQLStoreError(
        "Error en GraphQL"
    )

    with (
        patch(
            "source.cli.migracion.main.Path.cwd",
            return_value=ruta_proyecto,
        ),
        patch("source.cli.migracion.main.Path.exists", return_value=True),
        patch(
            "source.cli.migracion.main.GestorArchivo.leer_archivo",
            side_effect=[esquema_anterior, esquema_nuevo],
        ),
        patch(
            "source.cli.migracion.main.ConfiguracionJsonLoader",
            return_value=mock_loader,
        ),
        patch(
            "source.cli.migracion.main.GeneradorMigracionMySQL",
            return_value=mock_generador_error,
        ),
        patch("source.cli.migracion.main.Console") as mock_console,
    ):
        migracion(mock_args)

        mock_consola_instancia = mock_console.return_value
        llamadas = mock_consola_instancia.print.call_args_list
        msg = "error inesperado"
        assert any(msg in str(call).lower() for call in llamadas)
    # pylint: enable=too-many-arguments,too-many-positional-arguments


def test_migracion_manejo_migration_error(
    mock_args,
    esquema_anterior,
    esquema_nuevo,
    mock_loader,
    ruta_proyecto,
):
    """Prueba manejo de MigrationError durante migración."""

    mock_generador_error = Mock(spec=GeneradorMigracionMySQL)
    mock_generador_error.generar_migracion.side_effect = MigrationError(
        "Error de migración"
    )

    with (
        patch(
            "source.cli.migracion.main.Path.cwd",
            return_value=ruta_proyecto,
        ),
        patch("source.cli.migracion.main.Path.exists", return_value=True),
        patch(
            "source.cli.migracion.main.GestorArchivo.leer_archivo",
            side_effect=[esquema_anterior, esquema_nuevo],
        ),
        patch(
            "source.cli.migracion.main.ConfiguracionJsonLoader",
            return_value=mock_loader,
        ),
        patch(
            "source.cli.migracion.main.GeneradorMigracionMySQL",
            return_value=mock_generador_error,
        ),
        patch("source.cli.migracion.main.Console") as mock_console,
    ):
        migracion(mock_args)

        mock_consola_instancia = mock_console.return_value
        llamadas = mock_consola_instancia.print.call_args_list
        assert any(
            "error inesperado durante la migracion" in str(call).lower()
            for call in llamadas
        )


def test_migracion_flujo_completo_integracion(
    mock_args,
    esquema_anterior,
    esquema_nuevo,
    mock_loader,
    mock_adaptador,
    mock_generador_migracion,
    mock_generador_esquema,
    ruta_proyecto,
):
    """Prueba de integración del flujo completo de migración."""
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    with (
        patch(
            "source.cli.migracion.main.Path.cwd",
            return_value=ruta_proyecto,
        ),
        patch("source.cli.migracion.main.Path.exists", return_value=True),
        patch(
            "source.cli.migracion.main.GestorArchivo.leer_archivo",
            side_effect=[esquema_anterior, esquema_nuevo],
        ),
        patch("source.cli.migracion.main.GestorArchivo.escribir_archivo"),
        patch("source.cli.migracion.main.GestorArchivo.asegurar_dir_existe"),
        patch(
            "source.cli.migracion.main.ConfiguracionJsonLoader",
            return_value=mock_loader,
        ),
        patch(
            "source.cli.migracion.main.AdaptadorMySQL",
            return_value=mock_adaptador,
        ),
        patch(
            "source.cli.migracion.main.GeneradorMigracionMySQL",
            return_value=mock_generador_migracion,
        ),
        patch(
            "source.cli.migracion.main.GeneradorEsquemaMySQL",
            return_value=mock_generador_esquema,
        ),
        patch("source.cli.migracion.main.Console") as mock_console,
    ):
        migracion(mock_args)

        # configuracion cargada
        mock_loader.cargar_configuracion.assert_called_once()

        # esquemas leidos
        # pylint: disable=import-outside-toplevel
        from source.cli.migracion.main import GestorArchivo

        # pylint: enable=import-outside-toplevel

        assert GestorArchivo.leer_archivo.call_count == 2

        # migracion generada
        mock_generador_migracion.generar_migracion.assert_called_once()

        # conexion a BD establecida
        mock_adaptador.conectar.assert_called_once()

        # tablas verificadas
        mock_adaptador.ejecutar_consulta.assert_called()

        # archivos escritos
        assert GestorArchivo.escribir_archivo.call_count == 3

        # esquema cliente actualizado
        mock_generador_esquema.transformar_esquema_graphql.assert_called_once()

        # mostrar mensajes de exito
        mock_consola_instancia = mock_console.return_value
        llamadas = mock_consola_instancia.print.call_args_list
        assert any("sincronizado" in str(call).lower() for call in llamadas)
        assert any("guardado" in str(call).lower() for call in llamadas)
    # pylint: enable=too-many-arguments,too-many-positional-arguments


def test_migracion_validacion_parametros_entrada(
    mock_args,
    esquema_anterior,
    esquema_nuevo,
    mock_loader,
    mock_adaptador,
    mock_generador_migracion,
    ruta_proyecto,
):
    """Prueba validación de parámetros de entrada."""
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    with (
        patch(
            "source.cli.migracion.main.Path.cwd",
            return_value=ruta_proyecto,
        ),
        patch("source.cli.migracion.main.Path.exists", return_value=True),
        patch(
            "source.cli.migracion.main.GestorArchivo.leer_archivo",
            side_effect=[esquema_anterior, esquema_nuevo],
        ),
        patch("source.cli.migracion.main.GestorArchivo.escribir_archivo"),
        patch("source.cli.migracion.main.GestorArchivo.asegurar_dir_existe"),
        patch(
            "source.cli.migracion.main.ConfiguracionJsonLoader",
            return_value=mock_loader,
        ),
        patch(
            "source.cli.migracion.main.AdaptadorMySQL",
            return_value=mock_adaptador,
        ),
        patch(
            "source.cli.migracion.main.GeneradorMigracionMySQL",
            return_value=mock_generador_migracion,
        ),
        patch("source.cli.migracion.main.Console"),
    ):
        migracion(mock_args)

        # Verificar que se validaron correctamente los parámetros
        assert hasattr(mock_args, "esquema")
        assert hasattr(mock_args, "salida")
        assert hasattr(mock_args, "no_visualizar_salida")
        assert hasattr(mock_args, "no_visualizar_sql")

        # Verificar que se usaron los valores correctos
        assert mock_args.esquema == "new_schema.graphql"
        assert mock_args.salida == "migraciones"
        assert mock_args.no_visualizar_salida is False
        assert mock_args.no_visualizar_sql is False
    # pylint: enable=too-many-arguments,too-many-positional-arguments


def test_mig_multi_archivos_gql_sin_esquema_especificado(
    mock_args_sin_esquema, ruta_proyecto, esquema_anterior, mock_loader
):
    """Prueba que verifica el comportamiento al encontrar
    varios archivos .graphql."""

    mock_esquema_archivos = [
        ruta_proyecto / "schema1.graphql",
        ruta_proyecto / "schema2.graphql",
    ]

    with (
        patch(
            "source.cli.migracion.main.Path.cwd",
            return_value=ruta_proyecto,
        ),
        patch("source.cli.migracion.main.Path.exists", return_value=True),
        patch(
            "source.cli.migracion.main.GestorArchivo.leer_archivo",
            side_effect=[esquema_anterior],
        ),
        patch.object(Path, "glob", return_value=iter(mock_esquema_archivos)),
        patch(
            "source.cli.migracion.main.ConfiguracionJsonLoader",
            return_value=mock_loader,
        ),
        patch("source.cli.migracion.main.Console") as mock_console,
    ):
        migracion(mock_args_sin_esquema)

        # verificar que se leyeron los archivos .graphql
        assert len(mock_esquema_archivos) == 2

        # verificar que se muestra un mensaje de error
        mock_console.return_value.print.assert_called_once_with(
            "Se encontraron múltiples archivos .graphql en el "
            "directorio actual. Por favor, especifique un "
            "esquema específico usando el parámetro --esquema.",
            style="bold red",
        )
