"""Prueba para la función main del módulo source.main."""

from contextlib import redirect_stdout
import io
import runpy
import sys
from unittest.mock import MagicMock, patch


class TestMain:
    """Pruebas para la función main"""

    def setup_method(self):
        """Configuración antes de cada prueba."""
        # limpiar cualquier import previo del modulo que se va a probar
        if "source.main" in sys.modules:
            del sys.modules["source.main"]

        if "source.cli.main.CLI" in sys.modules:
            del sys.modules["source.cli.main.CLI"]

    def teardown_method(self):
        """Limpieza después de cada prueba."""
        # limpiar cualquier import previo del modulo que se va a probar
        if "source.main" in sys.modules:
            del sys.modules["source.main"]

    def test_main_ejecutar_cli(self):
        """Prueba que la función main ejecuta CLI correctamente."""

        with patch("sys.argv", ["main.py"]):
            with patch("source.cli.main.CLI") as mock_cli_clase:
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

        capturar_salida = io.StringIO()

        with patch("sys.argv", ["main.py", "conexion"]):
            with redirect_stdout(capturar_salida):
                with patch("source.cli.main.CLI") as mock_cli_clase:
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
        salida = capturar_salida.getvalue()

        # verificar una salida especifica
        assert "GraphQL CLI - conexion" in salida

        # verificar que se creo una instancia de CLI
        mock_cli_clase.assert_called_once()
        # verificar que se llamo al metodo ejecutar
        mock_cli_instancia.ejecutar.assert_called_once()

    def test_main_ejecutar_cli_con_arg_inicializar(self):
        """Prueba que la funcion main ejecuta CLI con \
            argumento de inicializar."""

        capturar_salida = io.StringIO()

        with patch("sys.argv", ["main.py", "inicializar"]):
            with redirect_stdout(capturar_salida):
                with patch("source.cli.main.CLI") as mock_cli_clase:
                    # mockear instancia de cli
                    mock_cli_instancia = MagicMock()

                    def mock_resultado():
                        print("GraphQL CLI - inicializar")
                        print("Inicializando base de datos...")

                    mock_cli_instancia.ejecutar.side_effect = mock_resultado
                    mock_cli_clase.return_value = mock_cli_instancia

                    # Importar y ejecutar main después de configurar los mocks
                    # pylint: disable=import-outside-toplevel

                    from source.main import main

                    # pylint: disable=import-outside-toplevel

                    main()

        # verificar la salida capturada
        salida = capturar_salida.getvalue()

        # verificar una salida especifica
        assert "GraphQL CLI - inicializar" in salida

        # verificar que se creo una instancia de CLI
        mock_cli_clase.assert_called_once()
        # verificar que se llamo al metodo ejecutar
        mock_cli_instancia.ejecutar.assert_called_once()

    def test_main_ejecutar_cli_con_arg_migracion(self):
        """Prueba que la funcion main ejecuta CLI con \
            argumento de migracion."""

        capturar_salida = io.StringIO()

        with patch("sys.argv", ["main.py", "migracion"]):
            with redirect_stdout(capturar_salida):
                with patch("source.cli.main.CLI") as mock_cli_clase:
                    # mockear instancia de cli
                    mock_cli_instancia = MagicMock()

                    def mock_resultado():
                        print("GraphQL CLI - migracion")
                        print("Migrando base de datos...")

                    mock_cli_instancia.ejecutar.side_effect = mock_resultado
                    mock_cli_clase.return_value = mock_cli_instancia

                    # Importar y ejecutar main después de configurar los mocks
                    # pylint: disable=import-outside-toplevel

                    from source.main import main

                    # pylint: disable=import-outside-toplevel

                    main()

        # verificar la salida capturada
        salida = capturar_salida.getvalue()

        # verificar una salida especifica
        assert "GraphQL CLI - migracion" in salida

        # verificar que se creo una instancia de CLI
        mock_cli_clase.assert_called_once()
        # verificar que se llamo al metodo ejecutar
        mock_cli_instancia.ejecutar.assert_called_once()

    def test_main_como_script(self):
        """Prueba que la funcion main se ejecuta como script."""
        with patch("source.cli.main.CLI") as mock_cli_clase:
            # mockear instancia  de cli
            mock_cli_instancia = MagicMock()
            mock_cli_clase.return_value = mock_cli_instancia

            try:
                # ejecutar el modulo como si fuera un script
                runpy.run_module("source.main", run_name="__main__")
            except SystemExit:
                pass

            # verificar que se ejecuto correctamente
            mock_cli_clase.assert_called_once()
            mock_cli_instancia.ejecutar.assert_called_once()

    def test_main_import_fallback_cli(self):
        """Prueba que el import fallback funciona cuando
        source.cli.main.CLI no esta disponible."""

        mock_cli_instancia = MagicMock()
        mock_cli_class = MagicMock(return_value=mock_cli_instancia)

        # mockear modulo cli
        mock_cli_main = MagicMock()
        mock_cli_main.CLI = mock_cli_class

        with patch.dict(
            "sys.modules", {"source.cli.main": None, "cli.main": mock_cli_main}
        ):

            # pylint: disable=import-outside-toplevel
            from source.main import main

            # pylint: disable=import-outside-toplevel
            main()

            mock_cli_class.assert_called_once()
            mock_cli_instancia.ejecutar.assert_called_once()
