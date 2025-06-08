"""Pruebas para ConfiguracionJsonLoader"""

import json
from pathlib import Path
from unittest.mock import Mock, mock_open, patch
import pytest

from source.cli.loaders.conf_json_loader import ConfiguracionJsonLoader


@pytest.fixture(name="mock_ruta_archivo")
def fixture_mock_ruta_archivo():
    """Fixture para proporcionar una ruta de archivo simulada."""
    return Mock(spec=Path)


@pytest.fixture(name="conf_json_loader")
def fixture_configuracion_json_loader(mock_ruta_archivo):
    """Fixture para proporcionar una instancia de ConfiguracionJsonLoader."""
    return ConfiguracionJsonLoader(mock_ruta_archivo)


@pytest.fixture(name="conf_data")
def fixture_config_data_valido():
    """Fixture para proporcionar datos de configuración JSON válidos."""
    return {
        "DB_HOST": "localhost",
        "DB_PUERTO": "3306",
        "DB_USUARIO": "user",
        "DB_PASSWORD": "password",
        "DB_NOMBRE": "database",
    }


@pytest.fixture(name="conf_data_incom")
def fixture_config_data_incompleto():
    """Fixture para proporcionar datos de configuración JSON incompletos."""
    return {"DB_HOST": "localhost", "DB_PUERTO": "3306"}


def test_inicializacion(conf_json_loader, mock_ruta_archivo):
    """Prueba para inicializar ConfiguracionJsonLoader correctamente."""
    assert conf_json_loader.ruta_archivo == mock_ruta_archivo
    assert conf_json_loader.co_si == "bold green"
    assert conf_json_loader.co_no == "bold red"
    assert conf_json_loader.conf is None
    assert hasattr(conf_json_loader, "consola")


def test_cargar_config_archivo_no_existe(conf_json_loader, mock_ruta_archivo):
    """Prueba cargar_configuracion cuando el archivo de configuracion \
        no existe."""

    mock_ruta_archivo.exists.return_value = False

    with patch.object(conf_json_loader.consola, "print") as mock_print:
        resultado = conf_json_loader.cargar_configuracion()

    assert resultado == {}

    mock_print.assert_called_once_with(
        "❌ Archivo de configuracion no encontrado. "
        "Asegurate de haber ejecutado primeramente "
        "el comando 'conexion'",
        style="bold red",
    )


def test_cargar_config_exitosa(conf_json_loader, mock_ruta_archivo, conf_data):
    """Prueba cargar_configuracion con un archivo JSON valido."""

    mock_ruta_archivo.exists.return_value = True

    with (
        patch("builtins.open", mock_open()),
        patch("json.load", return_value=conf_data),
    ):
        with patch.object(conf_json_loader.consola, "print"):
            resultado = conf_json_loader.cargar_configuracion()

    assert resultado == conf_data
    assert conf_json_loader.conf["DB_HOST"] == "localhost"
    assert conf_json_loader.conf["DB_PUERTO"] == "3306"
    assert conf_json_loader.conf["DB_USUARIO"] == "user"
    assert conf_json_loader.conf["DB_PASSWORD"] == "password"
    assert conf_json_loader.conf["DB_NOMBRE"] == "database"


def test_cargar_config_error_json(conf_json_loader, mock_ruta_archivo):
    """Prueba cargar_configuracion con un error de decodificacion JSON."""

    mock_ruta_archivo.exists.return_value = True

    json_error = json.JSONDecodeError("ErrorFormat", "", 0)

    with (
        patch("builtins.open", mock_open()),
        patch("json.load", side_effect=json_error),
    ):
        with patch.object(conf_json_loader.consola, "print") as mock_print:
            resultado = conf_json_loader.cargar_configuracion()

    assert resultado == {}

    mock_print.assert_called_once_with(
        "Error al leer el archivo de configuracion: "
        "ErrorFormat: line 1 column 1 (char 0)",
        style="bold red",
    )


def test_verificar_configuracion_completa(conf_json_loader, conf_data):
    """Prueba verificar_configuracion con todos los campos necesarios."""

    conf_json_loader.conf = conf_data

    with patch.object(conf_json_loader.consola, "print") as mock_print:
        resultado = conf_json_loader.verificar_configuracion()

    assert resultado is None
    mock_print.assert_not_called()


def test_verificar_configuracion_faltantes(conf_json_loader, conf_data_incom):
    """Prueba verificar_configuracion con campos faltantes."""

    conf_json_loader.conf = conf_data_incom

    with patch.object(conf_json_loader.consola, "print") as mock_print:
        resultado = conf_json_loader.verificar_configuracion()

    assert resultado is None
    mock_print.assert_called_once_with(
        "❌ Faltan los siguientes parametros en la configuracion: "
        "DB_USUARIO, DB_PASSWORD, DB_NOMBRE",
        style="bold red",
    )
