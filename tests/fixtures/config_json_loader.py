"""Fixtures for testing configuration JSON loader."""

from unittest.mock import Mock
import pytest

from source.cli.loaders.conf_json_loader import ConfiguracionJsonLoader


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
