"""Pruebas para ComandoServidor"""

from unittest.mock import MagicMock, patch
import pytest

from source.cli.servidor.comando_servidor import ComandoServidor


@pytest.fixture(name="comando_servidor")
def fixture_comando_servidor():
    """Fixture para proporcionar una instancia de ComandoServidor."""
    return ComandoServidor()


def test_crear_comando_agregar_argumentos(comando_servidor):
    """Prueba que crear_comando agrega correctamente \
        los argumentos al subparser."""

    # mock subparsers
    mock_subparsers = MagicMock()
    # mock parser
    mock_parser = MagicMock()
    mock_subparsers.add_parser.return_value = mock_parser

    comando_servidor.crear_comando(mock_subparsers)

    mock_subparsers.add_parser.assert_called_once_with(
        "servidor",
        help="(opcional) Crear un servidor GraphQL de pruebas en node",
    )


@patch("source.cli.servidor.comando_servidor.servidor")
def test_contenido_comando_ejecuta_servidor(
    mock_inicializar,
    comando_servidor,
):
    """Prueba que contenido_comando ejecuta la funcion iniciar_servidor."""
    # mock args
    mock_args = MagicMock()
    mock_args.comando = "servidor"

    comando_servidor.contenido_comando(mock_args)

    mock_inicializar.assert_called_once()
