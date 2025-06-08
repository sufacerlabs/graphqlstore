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


@pytest.fixture(name="mock_args")
def fixture_mock_args():
    """Fixture para proporcionar argumnetos simulados."""
    args = MagicMock()
    args.comando = "conexion"
    return args


@pytest.fixture(name="mock_params")
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


def test_ejecutar_comando_conexion(inst_cli, mock_args):
    """Test execution of the conexion comando"""

    # Mockear el método agregar_comando del constructor
    with patch.object(inst_cli.constructor, "parsear", return_value=mock_args):
        with patch.object(
            inst_cli.comando_conexion, "contenido_comando"
        ) as mock_contenido:
            inst_cli.ejecutar()

    # verificar que la funcion conexion fue llamada (indirectamente
    # a traves del metodo contenido_comando). Ya que este metodo
    # se llama desde contenido_comando

    mock_contenido.assert_called_once_with(mock_args)

    # verificar que el comando conexion fue asignado correctamente
    assert inst_cli.args.comando == "conexion"


def test_ejecutar_con_args(inst_cli, mock_params):
    """Prueba de ejecución con argumentos específicos"""

    # mockear el metodo agregar_comando del constructor
    with patch.object(
        inst_cli.constructor,
        "parsear",
        return_value=mock_params,
    ):
        # mockear el metodo contenido_coamdo de ComandoConexion
        with patch.object(
            inst_cli.comando_conexion,
            "contenido_comando",
        ) as mock_contenido:

            inst_cli.ejecutar()

            # verificar  que se ejecuto el comando correspondiente
            mock_contenido.assert_called_once_with(mock_params)

    # verificar que los argumentos fueron asignados correctamente
    assert inst_cli.args.comando == "conexion"
    assert inst_cli.args.archivo == "./home/user/file.json"
    assert inst_cli.args.host == "localhost"
    assert inst_cli.args.puerto == "3306"
    assert inst_cli.args.usuario == "admin"
    assert inst_cli.args.password == "password"
    assert inst_cli.args.db_nombre == "graphqlstore_db"
