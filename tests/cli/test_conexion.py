"""Pruebas para la funcion conexion"""

import json
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch
import pytest

from source.cli.conexion import conexion


@pytest.fixture(name="mock_args")
def mock_argumentos():
    """Fixture para simular los argumentos de la línea de comandos."""
    # mockear los argumentos de la línea de comandos
    args = MagicMock()
    args.archivo = None
    args.host = None
    args.puerto = None
    args.usuario = None
    args.password = None
    args.db_nombre = None
    return args


@patch("source.cli.conexion.Console")
@patch("source.cli.conexion.Path.cwd")
@patch("builtins.open", new_callable=mock_open)
def test_conexion_sin_params(_mock_file, mock_cwd, mock_consola, mock_args):
    """Test de conexion sin parámetros, que debe solicitar \
        entrada interactiva."""

    # configurar mocks
    mock_cwd.return_value = Path("/ruta/simulada")
    mock_consola_instancia = mock_consola.return_value

    # Configurar mock Path.exists para que retorne False
    with patch.object(Path, "exists", return_value=False):
        # simular entrada interactiva
        with patch("builtins.input", return_value="testhost"):
            conexion(mock_args)
    # Verificar que se imprimio el mensaje correcto
    mock_consola_instancia.print.assert_any_call(
        "Ingrese los datos de la base de datos:"
    )


@patch("source.cli.conexion.Console")
@patch("source.cli.conexion.Path.cwd")
@patch("builtins.open", new_callable=mock_open)
def test_conexion_con_archivo(_mock_file, mock_cwd, mock_consola, mock_args):
    """Test de conexion cargando configuración desde un archivo."""

    mock_consola_instancia = mock_consola.return_value
    mock_cwd.return_value = Path("/ruta/simulada")

    # Configurar mock Path.exists para que retorne False
    with patch.object(Path, "exists", return_value=False):
        # mockear el archivo de configuración
        mock_args.archivo = "./mi/ruta/config.json"

        archivo_contenido = '{"DB_HOST": "archivo_host", "DB_PUERTO": "3306"}'

        # mockear archivo origen
        mock_archivo_origen = mock_open(read_data=archivo_contenido)

        # configurar mock de Path.write_text para
        # simular escritura del archivo
        with (
            patch("builtins.open", mock_archivo_origen),
            patch.object(Path, "write_text") as mock_write_texto,
        ):
            conexion(mock_args)

            # verificar que se llamo a write_text para copiar el contenido
            mock_write_texto.assert_called_once_with(
                archivo_contenido, encoding="utf-8"
            )

    # verificar que se imprimio el mensaje correcto
    mock_consola_instancia.print.assert_any_call(
        "Configuracion cargada con el archivo pasado.", style="bold green"
    )


@patch("source.cli.conexion.Console")
@patch("source.cli.conexion.Path.cwd")
@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='{"DB_HOST": "existing_host", "DB_PUERTO": "5432"}',
)
def test_conexion_con_configuracion_existente(
    mock_file, mock_cwd, mock_consola, mock_args
):
    """Prueba de conexion con configuracion existente."""

    # configurar mocks
    mock_cwd.return_value = Path("/ruta/simulada")
    mock_consola_instancia = mock_consola.return_value

    # configurar mock Path.exists para que retorne True
    with patch.object(Path, "exists", return_value=True):
        conexion(mock_args)

    # verificar que se intento leer el archivo
    mock_file.assert_called()

    # verificar que se imprimio el mensaje correcto
    mock_consola_instancia.print.assert_any_call(
        "Configure las base de datos que necesite.", style="bold green"
    )

    # verificar que se imprimio el mensaje correcto
    mock_consola_instancia.print.assert_any_call(
        "Configuracion cargada desde el archivo existente.", style="bold green"
    )


@patch("source.cli.conexion.Console")
@patch("source.cli.conexion.Path.cwd")
@patch("builtins.open", new_callable=mock_open)
def test_conexion_con_params(_mock_file, mock_cwd, mock_consola, mock_args):
    """Prueba de conexion con parametros especificos."""

    # configurar mocks
    mock_cwd.return_value = Path("/ruta/simulada")
    mock_consola_instancia = mock_consola.return_value

    # mockear los argumentos
    mock_args.host = "localhost"
    mock_args.puerto = "5432"
    mock_args.usuario = "usuario"
    mock_args.password = "password"
    mock_args.db_nombre = "mi_base_datos"

    with patch.object(Path, "exists", return_value=False):
        conexion(mock_args)

    # verificar que se imprimio el mensaje correcto
    mock_consola_instancia.print.assert_any_call(
        "✅ Configuracion de conexion guardado exitosamente", style="bold green"
    )


@patch("source.cli.conexion.Console")
@patch("source.cli.conexion.Path.cwd")
@patch("builtins.open", side_effect=json.JSONDecodeError("ErrorFormat", "", 0))
def test_conexion_error_archivo_configuracion(
    _mock_file, mock_cwd, mock_consola, mock_args
):
    """Prueba de conexion con error al leer el archivo\
        de configuracion."""

    # configurar mocks
    mock_cwd.return_value = Path("/ruta/simulada")
    mock_consola_instancia = mock_consola.return_value

    # simular que el archivo existe pero tiene un error
    # JSON invalido.

    with patch.object(Path, "exists", return_value=True):
        conexion(mock_args)

    # verificar que se muestra el error
    mock_consola_instancia.print.assert_any_call(
        "Error al leer el archivo de configuracion: "
        "ErrorFormat: line 1 column 1 (char 0)",
        style="bold red",
    )


@patch("source.cli.conexion.Console")
@patch("source.cli.conexion.Path.cwd")
@patch("builtins.open", side_effect=FileNotFoundError("Archivo no encontrado"))
def test_conexion_error_archivo_no_encontrado(
    _mock_file, mock_cwd, mock_consola, mock_args
):
    """Prueba de conexion con error al abrir el archivo de configuracion."""

    # configurar mocks
    mock_cwd.return_value = Path("/ruta/simulada")
    mock_consola_instancia = mock_consola.return_value

    # mockear el archivo de configuracion
    mock_args.archivo = "./mi/ruta/config.json"

    # simular que el archivo no existe
    with patch.object(Path, "exists", return_value=False):
        conexion(mock_args)

    # verificar que se muestra el mensaje de error
    mock_consola_instancia.print.assert_any_call(
        "Error al leer el archivo de configuracion: Archivo no encontrado",
        style="bold red",
    )


@patch("source.cli.conexion.Console")
@patch("source.cli.conexion.Path.cwd")
@patch("builtins.open", new_callable=mock_open)
def test_conexion_parametros_error_guardar(
    _mock_file, mock_cwd, mock_consola, mock_args
):
    """Prueba de conexion con error al guardar los parametros."""

    # configurar mocks
    mock_cwd.return_value = Path("/ruta/simulada")
    mock_consola_instancia = mock_consola.return_value

    # mockear los argumentos
    mock_args.host = "localhost"
    mock_args.puerto = "5432"
    mock_args.usuario = "usuario"
    mock_args.password = "password"
    mock_args.db_nombre = "mi_base_datos"

    # simular un error al guardar el archivo
    with (
        patch.object(Path, "exists", return_value=False),
        patch("builtins.open", side_effect=OSError("Error al guardar")),
    ):
        conexion(mock_args)

    # verificar que se muestra el mensaje de error
    mock_consola_instancia.print.assert_any_call(
        "Error al guardar la configuracion: Error al guardar", style="bold red"
    )
