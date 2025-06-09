"""Pruebas para ComandoProbarConexion"""

from unittest.mock import MagicMock, patch
import pytest

from source.cli.probar_conexion import ComandoProbarConexion


@pytest.fixture(name="comando_procon")
def fixture_comando_probar_conexion():
    """Fixture para proporcionar una instancia de ComandoProbarConexion."""
    return ComandoProbarConexion()


def test_crear_comando_agregar_argumentos(comando_procon):
    """Prueba para que crear_comando agrega correctamente \
        los argumentos al subparser."""

    # mock subparsers
    mock_subparsers = MagicMock()
    # mock parser
    mock_parser = MagicMock()

    mock_subparsers.add_parser.return_value = mock_parser

    comando_procon.crear_comando(mock_subparsers)

    com_nom = "probar-conexion"
    mock_subparsers.add_parser.assert_called_once_with(
        com_nom, help="Probar la conexion a la base de datos configurada"
    )

    # verificar que se agregaron los argumentos esperados

    def requerido(title):
        return {"action": "store_true", "help": title}

    argumentos_esperados = [
        # --verbose, -v
        (
            ("--verbose", "-v"),
            requerido("Mostrar mas detalles de la informacion de la conexion"),
        )
    ]

    assert mock_parser.add_argument.call_count == len(argumentos_esperados)

    # verificar cada llamada especifica
    llamadas = mock_parser.add_argument.call_args_list
    for i, (args, kwargs) in enumerate(argumentos_esperados):
        arg_actual, kwargs_actual = llamadas[i]
        assert arg_actual == args
        assert kwargs_actual == kwargs


@patch("source.cli.probar_conexion.comando_probar_conexion.proconexion")
def test_contenido_comando(mock_proconexion, comando_procon):
    """Prueba que el metodo contenido_comando llama a la funcion proconexion"""

    # mock args
    mock_args = MagicMock()
    mock_args.comando = "probar-conexion"

    comando_procon.contenido_comando(mock_args)

    # verificar que se llamo a la funcion proconexion
    mock_proconexion.assert_called_once_with(mock_args)
