"""Pruebas para GeneradorMigracionMySQL"""

from unittest.mock import MagicMock, patch
import pytest

from source.cli.migracion.comando_migracion import ComandoMigracion


@pytest.fixture(name="comando_migracion")
def fixture_comando_migracion():
    """Fixture para proporcionar una instancia de ComandoMigracion."""
    return ComandoMigracion()


def test_crear_comando_agregar_argumentos(comando_migracion):
    """Prueba que crear_comando agrega correctamente \
        los argumentos al subparser."""
    # pylint: disable=duplicate-code
    # mock subparsers
    mock_subparsers = MagicMock()
    # mock parser
    mock_parser = MagicMock()
    mock_subparsers.add_parser.return_value = mock_parser

    comando_migracion.crear_comando(mock_subparsers)

    mock_subparsers.add_parser.assert_called_once_with(
        "migracion",
        help="Migrar una base de datos a partir de un esquema GraphQL",
    )

    def requerido(title):
        return {"required": False, "help": title}

    argumentos_esperados = [
        (
            ("--esquema", "-e"),
            requerido("Ruta al archivo de esquema GraphQL"),
        ),
        (
            ("--antiguo-esquema",),
            requerido("Ruta del archivo de esquema GraphQL antiguo"),
        ),
        (
            ("--salida", "-s"),
            {
                "required": False,
                "default": "migraciones",
                "help": "Directorio de salida para las migraciones generadas",
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

    # verificar cada llamada específica
    llamadas = mock_parser.add_argument.call_args_list
    for i, (args, kwargs) in enumerate(argumentos_esperados):
        arg_actual, kwargs_actual = llamadas[i]
        assert arg_actual == args
        assert kwargs_actual == kwargs
    # pylint: enable=duplicate-code


@patch("source.cli.migracion.comando_migracion.migracion")
def test_contenido_comando_ejecutar_migracion(
    mock_migracion,
    comando_migracion,
):
    """Prueba que contenido_comando ejecuta la función migracion."""

    # Simular argumentos de prueba
    args = MagicMock()
    args.comando = "migracion"
    args.esquema = "nuevo_esquema.graphql"
    args.antiguo_esquema = "antiguo_esquema.graphql"
    args.salida = "migraciones"
    args.no_visualizar_salida = False
    args.no_visualizar_sql = False

    comando_migracion.contenido_comando(args)

    mock_migracion.assert_called_once_with(args)
