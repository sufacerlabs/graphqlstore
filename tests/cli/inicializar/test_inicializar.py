"""Pruebas para la funcion inicializar"""

from pathlib import Path
from unittest.mock import Mock, patch
import pytest
from source.cli.inicializar.main import inicializar
from source.cli.database.adaptadores.mysql import AdaptadorMySQL
from source.cli.loaders.conf_json_loader import ConfiguracionJsonLoader
from source.cli.graphql import (
    ParserGraphQLEsquema,
    ProcesarRelaciones,
    GeneradorEsquemaMySQL,
)


@pytest.fixture(name="mock_args")
def fixture_mock_args():
    """Fixture que proporciona argumentos simulados básicos."""
    args = Mock()
    args.esquema = "test_schema.graphql"
    args.salida = "output"
    args.no_visualizar_salida = False
    args.no_visualizar_sql = False
    return args


@pytest.fixture(name="mock_args_sin_esquema")
def fixture_mock_args_sin_esquema():
    """Fixture que proporciona argumentos simulados \
        sin esquema especificado."""
    args = Mock()
    args.esquema = None
    args.salida = "output"
    args.no_visualizar_salida = True
    args.no_visualizar_sql = True
    return args


@pytest.fixture(name="esquema_contenido")
def fixture_esquema_contenido():
    """Fixture que proporciona contenido de esquema GraphQL."""
    return """
    type User {
        id: ID!
        name: String!
        email: String!
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
    adaptador.cursor.fetchall.return_value = []  # Sin tablas por defecto
    return adaptador


@pytest.fixture(name="mock_parser")
def fixture_parser_graphql():
    """Fixture que proporciona un parser GraphQL simulado."""
    parser = Mock(spec=ParserGraphQLEsquema)
    mock_info_parseada = Mock()
    mock_info_parseada.tablas = {}
    mock_info_parseada.enums = {}
    parser.parse_esquema.return_value = mock_info_parseada
    return parser


@pytest.fixture(name="mock_procesar_relaciones")
def fixture_procesar_relaciones():
    """Fixture que proporciona un procesador de relaciones simulado."""
    procesador = Mock(spec=ProcesarRelaciones)
    procesador.procesar_relaciones.return_value = []
    return procesador


@pytest.fixture(name="mock_generador")
def fixture_generador_mysql():
    """Fixture que proporciona un generador de esquema MySQL simulado."""
    generador = Mock(spec=GeneradorEsquemaMySQL)
    generador.generar_esquema.return_value = "CREATE TABLE test (id INT);"
    fake = "Type User {\n  id: ID!\n}\n"
    generador.transformar_esquema_graphql.return_value = fake
    return generador


@pytest.fixture(name="ruta_proyecto")
def fixture_ruta_proyecto():
    """Fixture que proporciona una ruta de proyecto."""
    return Path("/proyecto/test")


# pylint: disable=too-many-arguments, too-many-positional-arguments
def test_inicializar_con_esquema_especificado_exitoso(
    mock_args,
    esquema_contenido,
    config_valida,
    mock_loader,
    mock_adaptador,
    mock_parser,
    mock_procesar_relaciones,
    mock_generador,
    ruta_proyecto,
):
    """Prueba inicializacion exitosa con esquema especificado."""

    with (
        patch(
            "source.cli.inicializar.main.Path.cwd",
            return_value=ruta_proyecto,
        ),
        patch(
            "source.cli.inicializar.main.GestorArchivo.asegurar_dir_existe",
        ),
        patch("source.cli.inicializar.main.Path.exists", return_value=True),
        patch(
            "source.cli.inicializar.main.GestorArchivo.leer_archivo",
            return_value=esquema_contenido,
        ),
        patch(
            "source.cli.inicializar.main.GestorArchivo.escribir_archivo",
        ),
        patch(
            "source.cli.inicializar.main.ConfiguracionJsonLoader",
            return_value=mock_loader,
        ),
        patch(
            "source.cli.inicializar.main.AdaptadorMySQL",
            return_value=mock_adaptador,
        ),
        patch(
            "source.cli.inicializar.main.ParserGraphQLEsquema",
            return_value=mock_parser,
        ),
        patch(
            "source.cli.inicializar.main.ProcesarRelaciones",
            return_value=mock_procesar_relaciones,
        ),
        patch(
            "source.cli.inicializar.main.GeneradorEsquemaMySQL",
            return_value=mock_generador,
        ),
        patch(
            "source.cli.inicializar.main.Console",
        ),
    ):
        inicializar(mock_args)

        # verificar que se creo el directorio de salida
        # pylint: disable=import-outside-toplevel
        from source.cli.inicializar.main import GestorArchivo

        # pylint: enable=import-outside-toplevel
        GestorArchivo.asegurar_dir_existe.assert_called_once()

        # verificar que se leyo el esquema del archivo
        GestorArchivo.leer_archivo.assert_called()

        # verificar que se parceo el esquema
        mock_parser.parse_esquema.assert_called_once_with(esquema_contenido)

        # verificar que se procesaron las relaciones
        mock_procesar_relaciones.procesar_relaciones.assert_called_once()

        # verificar que se genero el esquema MySQL
        mock_generador.generar_esquema.assert_called_once()

        # verificar conexion a la base de datos
        mock_loader.cargar_configuracion.assert_called_once()
        mock_adaptador.conectar.assert_called_once_with(config_valida)
        mock_adaptador.ejecutar_consulta.assert_called()
        mock_adaptador.cerrar_conexion.assert_called_once()


# pylint: enable=too-many-arguments, too-many-positional-arguments


# pylint: disable=too-many-arguments, too-many-positional-arguments
def test_inicializar_sin_esquema_encuentra_archivo_graphql(
    mock_args_sin_esquema,
    esquema_contenido,
    mock_loader,
    mock_adaptador,
    mock_parser,
    mock_procesar_relaciones,
    mock_generador,
    ruta_proyecto,
):
    """Prueba inicializacion exitosa sin esquema, \
        pero encuentra archivo .graphql."""

    mock_esquema_archivo = ruta_proyecto / "schema.graphql"

    with (
        patch(
            "source.cli.inicializar.main.Path.cwd",
            return_value=ruta_proyecto,
        ),
        patch(
            "source.cli.inicializar.main.GestorArchivo.asegurar_dir_existe",
        ),
        patch(
            "source.cli.inicializar.main.GestorArchivo.leer_archivo",
            return_value=esquema_contenido,
        ),
        patch(
            "source.cli.inicializar.main.GestorArchivo.escribir_archivo",
        ),
        patch.object(Path, "glob", return_value=iter([mock_esquema_archivo])),
        patch(
            "source.cli.inicializar.main.ConfiguracionJsonLoader",
            return_value=mock_loader,
        ),
        patch(
            "source.cli.inicializar.main.AdaptadorMySQL",
            return_value=mock_adaptador,
        ),
        patch(
            "source.cli.inicializar.main.ParserGraphQLEsquema",
            return_value=mock_parser,
        ),
        patch(
            "source.cli.inicializar.main.ProcesarRelaciones",
            return_value=mock_procesar_relaciones,
        ),
        patch(
            "source.cli.inicializar.main.GeneradorEsquemaMySQL",
            return_value=mock_generador,
        ),
        patch(
            "source.cli.inicializar.main.Console",
        ),
    ):
        inicializar(mock_args_sin_esquema)

        # verificar que se encontro y leyo el archivo .graphql
        # pylint: disable=import-outside-toplevel
        from source.cli.inicializar.main import GestorArchivo

        # pylint: enable=import-outside-toplevel
        GestorArchivo.leer_archivo.assert_called()

        # verificar que se parceo el esquema
        mock_parser.parse_esquema.assert_called_once_with(esquema_contenido)


# pylint: enable=too-many-arguments, too-many-positional-arguments


def test_inicializar_falla_sin_esquema_y_sin_archivo_graphql(
    mock_args_sin_esquema,
    mock_loader,
    ruta_proyecto,
):
    """Prueba que verifica el fallo al no encontrar \
        esquema ni archivo .graphql."""

    with (
        patch(
            "source.cli.inicializar.main.Path.cwd",
            return_value=ruta_proyecto,
        ),
        patch(
            "source.cli.inicializar.main.GestorArchivo.asegurar_dir_existe",
        ),
        patch.object(Path, "glob", return_value=iter([])),
        patch(
            "source.cli.inicializar.main.ConfiguracionJsonLoader",
            return_value=mock_loader,
        ),
        patch("source.cli.inicializar.main.Console") as mock_console,
    ):

        inicializar(mock_args_sin_esquema)

        # verificar que muestra un mensaje de error
        mock_console.return_value.print.assert_called_once_with(
            "No se ha proporcionado un esquema y tampoco se "
            "ha encontrado un archivo .graphql en el directorio actual.",
            style="bold red",
        )


def test_inicializar_falla_esquema_no_existe(
    mock_args,
    mock_loader,
    ruta_proyecto,
):
    """Prueba que verifica el fallo al no encontrar el esquema especificado."""

    with (
        patch(
            "source.cli.inicializar.main.Path.cwd",
            return_value=ruta_proyecto,
        ),
        patch(
            "source.cli.inicializar.main.GestorArchivo.asegurar_dir_existe",
        ),
        patch("source.cli.inicializar.main.Path.exists", return_value=False),
        patch(
            "source.cli.inicializar.main.ConfiguracionJsonLoader",
            return_value=mock_loader,
        ),
        patch("source.cli.inicializar.main.Console") as mock_console,
    ):

        inicializar(mock_args)

        # verificar que muestra un mensaje de error
        mock_console.return_value.print.assert_called_once_with(
            f"El archivo de esquema '{mock_args.esquema}' no existe.",
            style="bold red",
        )


# pylint: disable=too-many-arguments, too-many-positional-arguments
def test_inicializar_sin_configuracion_db(
    mock_args,
    esquema_contenido,
    mock_parser,
    mock_procesar_relaciones,
    mock_generador,
    ruta_proyecto,
):
    """Prueba especifica para interracion con la base \
        de datos"""

    mock_loader = Mock()
    mock_loader.cargar_configuracion.return_value = None

    with (
        patch(
            "source.cli.inicializar.main.Path.cwd",
            return_value=ruta_proyecto,
        ),
        patch(
            "source.cli.inicializar.main.GestorArchivo.asegurar_dir_existe",
        ),
        patch("source.cli.inicializar.main.Path.exists", return_value=True),
        patch(
            "source.cli.inicializar.main.GestorArchivo.leer_archivo",
            return_value=esquema_contenido,
        ),
        patch(
            "source.cli.inicializar.main.GestorArchivo.escribir_archivo",
        ),
        patch(
            "source.cli.inicializar.main.ConfiguracionJsonLoader",
            return_value=mock_loader,
        ),
        patch(
            "source.cli.inicializar.main.ParserGraphQLEsquema",
            return_value=mock_parser,
        ),
        patch(
            "source.cli.inicializar.main.ProcesarRelaciones",
            return_value=mock_procesar_relaciones,
        ),
        patch(
            "source.cli.inicializar.main.GeneradorEsquemaMySQL",
            return_value=mock_generador,
        ),
        patch("source.cli.inicializar.main.Console") as mock_console,
    ):
        inicializar(mock_args)

        mock_loader.cargar_configuracion.assert_called_once()

        # verificar que se print se llamo 4 veces
        # mostrando solo los mensajes iniciales
        assert mock_console.return_value.print.call_count == 4


# pylint: enable=too-many-arguments, too-many-positional-arguments


# pylint: disable=too-many-arguments, too-many-positional-arguments
def test_inicializar_db_con_tablas_existentes(
    mock_args,
    esquema_contenido,
    mock_loader,
    mock_parser,
    mock_procesar_relaciones,
    mock_generador,
    ruta_proyecto,
):
    """Prueba comportamiento cuando la base de datos \
        ya tiene tablas existentes."""

    mock_adaptador = Mock(spec=AdaptadorMySQL)
    mock_adaptador.conectar.return_value = None
    mock_adaptador.ejecutar_consulta.return_value = None
    mock_adaptador.cursor = Mock()
    mock_adaptador.cursor.fetchall.return_value = [("t1",), ("t2",)]

    with (
        patch(
            "source.cli.inicializar.main.Path.cwd",
            return_value=ruta_proyecto,
        ),
        patch(
            "source.cli.inicializar.main.GestorArchivo.asegurar_dir_existe",
        ),
        patch("source.cli.inicializar.main.Path.exists", return_value=True),
        patch(
            "source.cli.inicializar.main.GestorArchivo.leer_archivo",
            return_value=esquema_contenido,
        ),
        patch(
            "source.cli.inicializar.main.ConfiguracionJsonLoader",
            return_value=mock_loader,
        ),
        patch(
            "source.cli.inicializar.main.AdaptadorMySQL",
            return_value=mock_adaptador,
        ),
        patch(
            "source.cli.inicializar.main.ParserGraphQLEsquema",
            return_value=mock_parser,
        ),
        patch(
            "source.cli.inicializar.main.ProcesarRelaciones",
            return_value=mock_procesar_relaciones,
        ),
        patch(
            "source.cli.inicializar.main.GeneradorEsquemaMySQL",
            return_value=mock_generador,
        ),
        patch("source.cli.inicializar.main.Console") as mock_console,
    ):
        inicializar(mock_args)

        # verificar que se muestra el mensaje sobre
        # el comando migracion

        mock_consola_instancia = mock_console.return_value
        llamadas = mock_consola_instancia.print.call_args_list
        assert any("migracion" in str(call) for call in llamadas)


# pylint: enable=too-many-arguments, too-many-positional-arguments


def test_ini_multi_archivos_gql_sin_esquema_especificado(
    mock_args_sin_esquema,
    ruta_proyecto,
):
    """Prueba que verifica el comportamiento al encontrar
    varios archivos .graphql."""

    mock_esquema_archivos = [
        ruta_proyecto / "schema1.graphql",
        ruta_proyecto / "schema2.graphql",
    ]

    with (
        patch(
            "source.cli.inicializar.main.Path.cwd",
            return_value=ruta_proyecto,
        ),
        patch(
            "source.cli.inicializar.main.GestorArchivo.asegurar_dir_existe",
        ),
        patch.object(Path, "glob", return_value=iter(mock_esquema_archivos)),
        patch("source.cli.inicializar.main.Console") as mock_console,
    ):
        inicializar(mock_args_sin_esquema)

        # verificar que se leyeron los archivos .graphql
        assert len(mock_esquema_archivos) == 2

        # verificar que se muestra un mensaje de error
        mock_console.return_value.print.assert_called_once_with(
            "Se encontraron múltiples archivos .graphql en el "
            "directorio actual. Por favor, especifique un "
            "esquema específico usando el parámetro --esquema.",
            style="bold red",
        )
