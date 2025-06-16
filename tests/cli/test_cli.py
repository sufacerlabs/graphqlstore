"""Pruebas para el módulo CLI de GraphQLStore"""

from unittest.mock import patch, MagicMock
import pytest
from source.cli.conexion.comando_conexion import ComandoConexion
from source.cli.main import CLI


@pytest.fixture(name="inst_cli")
def fixture_instancia_cli():
    """Fixture para proporcionar una instancia de CLI."""
    return CLI()


@pytest.fixture(name="inst_cli_titulo")
def fixture_instancia_cli_titulo():
    """Fixture para proporcionar una instancia de CLI \
        con título personalizado."""
    titulo_personalizado = "GraphQLStore Server CLI"
    return CLI(titulo=titulo_personalizado)


@pytest.fixture(name="mock_args_conexion")
def fixture_mock_args():
    """Fixture para proporcionar argumnetos simulados.
    para el comando conexion."""
    args = MagicMock()
    args.comando = "conexion"
    return args


@pytest.fixture(name="mock_args_probar_conexion")
def fixture_mock_args_probar_conexion():
    """Fixture para proporcionar argumentos simulados \
    para el comando probar_conexion."""
    args = MagicMock()
    args.comando = "probar_conexion"
    return args


@pytest.fixture(name="mock_params_conexion")
def fixture_mock_args_params():
    """Fixture para proporcionar argumentos simulados \
    con parámetros específicos."""
    args = MagicMock()
    args.comando = "conexion"
    args.archivo = "./home/user/file.json"
    args.host = "localhost"
    args.puerto = "3306"
    args.usuario = "admin"
    args.password = "password"
    args.db_nombre = "graphqlstore_db"
    return args


@pytest.fixture(name="mock_params_probar_conexion")
def fixture_mock_args_params_probar_conexion():
    """Fixture para proporcionar argumentos simulados \
    con parámetros específicos para probar_conexion."""
    args = MagicMock()
    args.comando = "probar_conexion"
    args.verbose = True
    return args


@pytest.fixture(name="mock_params_inicializar")
def fixture_mock_args_params_inicializar():
    """Fixture para proporcionar argumentos simulados \
    con parámetros específicos para inicializar."""
    args = MagicMock()
    args.comando = "inicializar"
    args.esquema = "./home/user/schema.graphql"
    args.salida = "generated"
    args.no_visualizar_salida = False
    args.no_visualizar_sql = False
    return args


def test_inicializar(inst_cli):
    """Prueba de la inicialización correcta del objeto CLI"""
    assert inst_cli.titulo == "GraphQLStore CLI"
    assert isinstance(inst_cli.comando_conexion, ComandoConexion)
    assert inst_cli.args is None
    assert inst_cli.constructor is not None


def test_titulo_personalizado(inst_cli_titulo):
    """Prueba de inicialización con título personalizado"""
    assert inst_cli_titulo.titulo == "GraphQLStore Server CLI"
    msg = "GraphQLStore Server CLI"
    assert inst_cli_titulo.constructor.parser.description == msg


def test_ejecutar_sin_comando(inst_cli):
    """Prueba del comportamiento cuando no se proporciona un comando"""

    # configurar el mock para devolver args sin comando
    args = MagicMock()
    args.comando = None

    # mockear
    with patch.object(inst_cli.constructor, "parsear", return_value=args):
        with patch.object(inst_cli.constructor.parser, "print_help") as mhelp:
            inst_cli.ejecutar()
            mhelp.assert_called_once()


def test_ejecutar_comando_conexion(inst_cli, mock_args_conexion):
    """Test execution of the conexion comando"""

    # Mockear el método agregar_comando del constructor
    with patch.object(
        inst_cli.constructor,
        "parsear",
        return_value=mock_args_conexion,
    ):
        with patch.object(
            inst_cli.comando_conexion, "contenido_comando"
        ) as mock_contenido:
            inst_cli.ejecutar()

    # verificar que la funcion conexion fue llamada (indirectamente
    # a traves del metodo contenido_comando). Ya que este metodo
    # se llama desde contenido_comando

    mock_contenido.assert_called_once_with(mock_args_conexion)

    # verificar que el comando conexion fue asignado correctamente
    assert inst_cli.args.comando == "conexion"


def test_ejecutar_conexion_con_args(inst_cli, mock_params_conexion):
    """Prueba de ejecución con argumentos específicos"""

    # mockear el metodo agregar_comando del constructor
    with patch.object(
        inst_cli.constructor,
        "parsear",
        return_value=mock_params_conexion,
    ):
        # mockear el metodo contenido_coamdo de ComandoConexion
        with patch.object(
            inst_cli.comando_conexion,
            "contenido_comando",
        ) as mock_contenido:

            inst_cli.ejecutar()

            # verificar  que se ejecuto el comando correspondiente
            mock_contenido.assert_called_once_with(mock_params_conexion)

    # verificar que los argumentos fueron asignados correctamente
    assert inst_cli.args.comando == "conexion"
    assert inst_cli.args.archivo == "./home/user/file.json"
    assert inst_cli.args.host == "localhost"
    assert inst_cli.args.puerto == "3306"
    assert inst_cli.args.usuario == "admin"
    assert inst_cli.args.password == "password"
    assert inst_cli.args.db_nombre == "graphqlstore_db"


def test_ejecutar_comando_probar_conexion(inst_cli, mock_args_probar_conexion):
    """Prueba de ejecución del comando probar_conexion"""

    # Mockear el método agregar_comando del constructor
    with patch.object(
        inst_cli.constructor,
        "parsear",
        return_value=mock_args_probar_conexion,
    ):
        with patch.object(
            inst_cli.comando_probar_conexion, "contenido_comando"
        ) as mock_contenido:
            inst_cli.ejecutar()

    mock_contenido.assert_called_once_with(mock_args_probar_conexion)

    assert inst_cli.args.comando == "probar_conexion"


def test_ejecutar_comando_probar_conexion_con_args(
    inst_cli, mock_params_probar_conexion
):
    """Prueba de ejecución del comando probar_conexion \
        con argumentos"""

    # Mockear el método agregar_comando del constructor
    with patch.object(
        inst_cli.constructor,
        "parsear",
        return_value=mock_params_probar_conexion,
    ):
        with patch.object(
            inst_cli.comando_probar_conexion,
            "contenido_comando",
        ) as mock_contenido:

            inst_cli.ejecutar()

            mock_contenido.assert_called_once_with(
                mock_params_probar_conexion,
            )

    assert inst_cli.args.comando == "probar_conexion"
    assert inst_cli.args.verbose is True


def test_ejecutar_inicializar_con_args(inst_cli, mock_params_inicializar):
    """Prueba de ejecución del comando inicializar con argumentos"""

    # Mockear el método agregar_comando del constructor
    with patch.object(
        inst_cli.constructor,
        "parsear",
        return_value=mock_params_inicializar,
    ):
        with patch.object(
            inst_cli.comando_inicializar,
            "contenido_comando",
        ) as mock_contenido:

            inst_cli.ejecutar()

            mock_contenido.assert_called_once_with(
                mock_params_inicializar,
            )

    assert inst_cli.args.comando == "inicializar"
    assert inst_cli.args.esquema == "./home/user/schema.graphql"
