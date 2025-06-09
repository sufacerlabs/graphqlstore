"""Pruebas para la funcion proconexion"""

from pathlib import Path
from unittest.mock import Mock, patch
import pytest
from source.cli.database.adaptadores.mysql import AdaptadorMySQL
from source.cli.loaders.conf_json_loader import ConfiguracionJsonLoader
from source.cli.probar_conexion.main import proconexion


@pytest.fixture(name="mock_args")
def fixture_mock_args():
    """Fixture que proporciona argumentos simulados."""
    args = Mock()
    args.verbose = False
    return args


@pytest.fixture(name="mock_args_verbose")
def fixture_mock_args_verbose():
    """Fixture que proporciona argumentos simulados con verbose activado."""
    args = Mock()
    args.verbose = True
    return args


@pytest.fixture(name="config_valida")
def fixture_config_valida():
    """Fixture que proporciona una configuración válida."""
    return {
        "DB_HOST": "localhost",
        "DB_PUERTO": "3306",
        "DB_USUARIO": "user",
        "DB_PASSWORD": "password",
        "DB_NOMBRE": "database",
    }


@pytest.fixture(name="mock_loader")
def fixture_config_json_loader(config_valida):
    """Fixture que proporciona un ConfiguracionJsonLoader simulado."""
    loader = Mock(spec=ConfiguracionJsonLoader)
    loader.cargar_configuracion.return_value = config_valida
    loader.verificar_configuracion.return_value = None

    return loader


@pytest.fixture(name="adapt_mysql")
def fixture_adapt_mysql():
    """Fixture que proporciona un adaptador MySQL simulado."""
    adaptador = Mock(spec=AdaptadorMySQL)
    adaptador.conectar.return_value = None
    adaptador.probar_conexion.return_value = None

    return adaptador


@pytest.fixture(name="ruta")
def fxiture_cwd_ruta():
    """Fixture que proporciona una ruta."""
    return Path("/ruta/al/proyecto")


def test_proconexion_exitoso_verbose_falso(
    mock_args, config_valida, mock_loader, adapt_mysql, ruta
):
    """Prueba que verifica la conexion exitosa con verbose desactivado."""

    with (
        patch("source.cli.probar_conexion.main.Path.cwd", return_value=ruta),
        patch(
            "source.cli.probar_conexion.main.ConfiguracionJsonLoader",
            return_value=mock_loader,
        ),
        patch(
            "source.cli.probar_conexion.main.AdaptadorMySQL",
            return_value=adapt_mysql,
        ),
    ):

        proconexion(mock_args)

    # Verificar que se llamaron los métodos correctos
    mock_loader.cargar_configuracion.assert_called_once()
    mock_loader.verificar_configuracion.assert_called_once()
    adapt_mysql.conectar.assert_called_once_with(config_valida)
    adapt_mysql.probar_conexion.assert_called_once_with(mock_args.verbose)


def test_proconexion_exitoso_verbose_verdadero(
    mock_args_verbose, config_valida, mock_loader, adapt_mysql, ruta
):
    """Prueba que verifica la conexion exitosa con verbose activado."""

    with (
        patch("source.cli.probar_conexion.main.Path.cwd", return_value=ruta),
        patch(
            "source.cli.probar_conexion.main.ConfiguracionJsonLoader",
            return_value=mock_loader,
        ),
        patch(
            "source.cli.probar_conexion.main.AdaptadorMySQL",
            return_value=adapt_mysql,
        ),
    ):

        proconexion(mock_args_verbose)

    # Verificar que se llamaron los métodos correctos
    mock_loader.cargar_configuracion.assert_called_once()
    mock_loader.verificar_configuracion.assert_called_once()
    adapt_mysql.conectar.assert_called_once_with(config_valida)
    adapt_mysql.probar_conexion.assert_called_once_with(
        mock_args_verbose.verbose,
    )


def test_proconexion_configuracion_invalida(
    mock_args,
    mock_loader,
    adapt_mysql,
    ruta,
):
    """Prueba que verifica el comportamiento \
        cuando la configuracion es invalida."""

    # Simular que la configuracion es vacia
    mock_loader.cargar_configuracion.return_value = {}

    with (
        patch("source.cli.probar_conexion.main.Path.cwd", return_value=ruta),
        patch(
            "source.cli.probar_conexion.main.ConfiguracionJsonLoader",
            return_value=mock_loader,
        ),
        patch(
            "source.cli.probar_conexion.main.AdaptadorMySQL",
            return_value=adapt_mysql,
        ),
    ):

        proconexion(mock_args)

    # Verificar que no se llamaron los metodos de conexion
    adapt_mysql.conectar.assert_not_called()
    adapt_mysql.probar_conexion.assert_not_called()
