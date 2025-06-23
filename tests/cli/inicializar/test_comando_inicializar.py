"""Pruebas para ComandoInicializar"""

from unittest.mock import MagicMock, patch
import pytest

from source.cli.inicializar.comando_inicializar import ComandoInicializar


@pytest.fixture(name="comando_init")
def comando_conexion():
    """Fixture para proporcionar una  instancia de ComandoInicializar."""
    return ComandoInicializar()


def test_crear_comando_agregar_argumentos(comando_init):
    """Prueba que crear_comando agrega correctamente \
        los argumentos al subparser."""
    # pylint: disable=duplicate-code
    # mock subparsers
    mock_subparsers = MagicMock()
    # mock parser
    mock_parser = MagicMock()
    mock_subparsers.add_parser.return_value = mock_parser

    comando_init.crear_comando(mock_subparsers)

    mock_subparsers.add_parser.assert_called_once_with(
        "inicializar",
        help="Inicializar una nueva base de datos desde un esquema GraphQL",
    )

    # verificar que se agregaron los argumentos esperados

    def requerido(title):
        return {"required": False, "help": title}

    argumentos_esperados = [
        (
            ("--esquema", "-e"),
            requerido("Ruta al archivo de esquema GraphQL"),
        ),
        (
            ("--salida", "-s"),
            {
                "required": False,
                "default": "generated",
                "help": "Directorio de salida para los archivos generados",
            },
        ),
        (
            ("--no-visualizar-salida", "-nv"),
            {
                "default": False,
                "action": "store_true",
                "help": "No visualizar salida",
            },
        ),
        (
            ("--no-visualizar-sql", "-nvs"),
            {
                "default": False,
                "action": "store_true",
                "help": "No visualizar salida SQL",
            },
        ),
    ]

    assert mock_parser.add_argument.call_count == len(argumentos_esperados)

    # verificar cada llamada especifica
    llamadas = mock_parser.add_argument.call_args_list
    for i, (args, kwargs) in enumerate(argumentos_esperados):
        arg_actual, kwargs_actual = llamadas[i]
        assert arg_actual == args
        assert kwargs_actual == kwargs
    # pylint: enable=duplicate-code


@patch("source.cli.inicializar.comando_inicializar.inicializar")
def test_contenido_comando_ejecuta_inicializar(mock_inicializar, comando_init):
    """Prueba que contenido_comando ejecuta la funcion inicializar \
        con los args correctos."""
    mock_args = MagicMock()
    mock_args.comando = "inicializar"
    mock_args.esquema = "ruta/al/esquema.graphql"
    mock_args.salida = "directorio/salida"
    mock_args.no_visualizar_salida = False
    mock_args.no_visualizar_sql = False

    comando_init.contenido_comando(mock_args)

    mock_inicializar.assert_called_once_with(mock_args)
