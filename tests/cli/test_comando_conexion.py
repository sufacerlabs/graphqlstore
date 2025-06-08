"""Pruebas para ComandoConexion"""

from unittest.mock import MagicMock, patch
import pytest

from source.cli.conexion.comando_conexion import ComandoConexion


@pytest.fixture(name="comando_conn")
def comando_conexion():
    """Fixture para proporcionar una  instancia de ComandoConexion."""
    return ComandoConexion()


def test_crear_comando_agregar_argumentos(comando_conn):
    """Prueba  que  crear_comando agrega correctamente \
        los argumentos al subparser."""

    # mock subparsers
    mock_subparsers = MagicMock()
    # mock parser
    mock_parser = MagicMock()
    mock_subparsers.add_parser.return_value = mock_parser

    comando_conn.crear_comando(mock_subparsers)

    mock_subparsers.add_parser.assert_called_once_with(
        "conexion", help="Configurar la conexion a la base de datos"
    )

    # verificar que se agregaron los argumentos esperados

    # define a function and pass title for help
    def requerido(title):
        return {"required": False, "help": title}

    argumentos_esperados = [
        # --archivo, -a
        (
            ("--archivo", "-a"),
            requerido("Ruta al archivo de configuracion (formato JSON)"),
        ),
        # --host
        (("--host",), requerido("Host de la base de datos")),
        # --puerto
        (("--puerto",), requerido("Puerto de la base de datos")),
        # --usuario
        (("--usuario",), requerido("Usuario de la base de datos")),
        # --password
        (
            ("--password",),
            requerido("Contraseña de la base de datos"),
        ),
        # --db-nombre
        (("--db-nombre",), requerido("Nombre de la base de datos")),
    ]

    assert mock_parser.add_argument.call_count == len(argumentos_esperados)

    # verificar cada llamada especifica
    llamadas = mock_parser.add_argument.call_args_list
    for i, (args, kwargs) in enumerate(argumentos_esperados):
        arg_actual, kwargs_actual = llamadas[i]
        assert arg_actual == args
        assert kwargs_actual == kwargs


@patch("source.cli.conexion.comando_conexion.conexion")
def test_contenido_comando_ejecuta_conexion(
    mock_conexion, comando_conn: ComandoConexion
):
    """Prueba que el método contenido_comando llama a la función conexion."""

    # mockear argumentos
    args = MagicMock()
    args.comando = "conexion"

    comando_conn.contenido_comando(args)

    # verificar que se llama a la función conexion
    mock_conexion.assert_called_once_with(args)
