"""Prueba para la función main del módulo source.main."""

from contextlib import redirect_stdout
import io
from pathlib import Path
import subprocess
import sys
from unittest.mock import MagicMock, patch


class TestMain:
    """Pruebas para la función main"""

    def setup_method(self):
        """Configuración antes de cada prueba."""
        # limpiar cualquier import previo del modulo que se va a probar
        if "source.main" in sys.modules:
            del sys.modules["source.main"]

        if "cli.main.CLI" in sys.modules:
            del sys.modules["cli.main.CLI"]

    def teardown_method(self):
        """Limpieza después de cada prueba."""
        # limpiar cualquier import previo del modulo que se va a probar
        if "source.main" in sys.modules:
            del sys.modules["source.main"]

    def test_main_ejecutar_cli(self):
        """Prueba que la función main ejecuta CLI correctamente."""

        with patch("sys.argv", ["main.py"]):
            with patch("cli.main.CLI") as mock_cli_clase:
                # mocker instancia de cli
                mock_cli_instancia = MagicMock()
                mock_cli_clase.return_value = mock_cli_instancia

                # Importar y ejecutar main después de configurar los mocks
                # pylint: disable=import-outside-toplevel

                from source.main import main

                # pylint: disable=import-outside-toplevel

                main()

                # Verificar que se creo una instancia de CLI
                mock_cli_clase.assert_called_once()

                # Verificar que se llamo al metodo ejecutar
                mock_cli_instancia.ejecutar.assert_called_once()

    def test_main_ejecutar_cli_con_arg_conexion(self):
        """Prueba que la funcion main ejecuta CLI con argumento de conexion."""

        captured_output = io.StringIO()

        with patch("sys.argv", ["main.py", "conexion"]):
            with redirect_stdout(captured_output):
                with patch("cli.main.CLI") as mock_cli_clase:
                    # mockear instancia de cli
                    mock_cli_instancia = MagicMock()

                    def mock_resultado():
                        print("GraphQL CLI - conexion")
                        print("Configure las base de datos que necesite.")

                    mock_cli_instancia.ejecutar.side_effect = mock_resultado
                    mock_cli_clase.return_value = mock_cli_instancia

                    # Importar y ejecutar main después de configurar los mocks
                    # pylint: disable=import-outside-toplevel

                    from source.main import main

                    # pylint: disable=import-outside-toplevel

                    main()

        # verificar la salida capturada
        output = captured_output.getvalue()

        # verificar una salida especifica
        assert "GraphQL CLI - conexion" in output

        # verificar que se creo una instancia de CLI
        mock_cli_clase.assert_called_once()
        # verificar que se llamo al metodo ejecutar
        mock_cli_instancia.ejecutar.assert_called_once()

    def test_main_como_script(self):
        """Prueba que la funcion main se ejecuta como script."""
        ruta_main = Path(__file__).parent.parent / "source" / "main.py"

        resultado = subprocess.run(
            [sys.executable, str(ruta_main)],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        # verificar que el script se ejecuto sin errores
        assert resultado.returncode == 0

        # verificar que la salida no contiene errores
        assert not resultado.stderr or "error" not in resultado.stderr.lower()
