"""Pruebas para el módulo CLI de GraphQLStore"""

import sys
from unittest.mock import patch, MagicMock
from source.cli.conexion.comando_conexion import ComandoConexion
from source.cli.main import CLI


class TestCLI:
    """Clase de pruebas para la interfaz de línea de comandos de \
        GraphQLStore"""

    def setup_method(self):
        """Inicialización antes de cada prueba"""
        # Limpiar cualquier import previo del módulo que se va a probar
        if "source.cli.main.conexion" in sys.modules:
            del sys.modules["source.cli.main.conexion"]

        if "source.cli.conexion.main" in sys.modules:
            del sys.modules["source.cli.conexion.main"]

        if "argparse.ArgumentParser.parse_args" in sys.modules:
            del sys.modules["argparse.ArgumentParser.parse_args"]

    def teardown_method(self):
        """Limpieza después de cada prueba"""
        # Limpiar cualquier import previo del módulo que se va a probar
        if "source.cli.main.conexion" in sys.modules:
            del sys.modules["source.cli.main.conexion"]

    def test_inicializar(self):
        """Prueba de la inicialización correcta del objeto CLI"""
        cli = CLI()
        assert cli.titulo == "GraphQLStore CLI"
        assert isinstance(cli.comando_conexion, ComandoConexion)
        assert cli.args is None
        assert cli.constructor is not None

    def test_titulo_personalizado(self):
        """Prueba de inicialización con título personalizado"""
        titulo_personalizado = "GraphQLStore Server CLI"
        cli = CLI(titulo=titulo_personalizado)
        assert cli.titulo == titulo_personalizado
        assert cli.constructor.parser.description == titulo_personalizado

    @patch("argparse.ArgumentParser.parse_args")
    def test_ejecutar_sin_comando(self, mock_parse_args):
        """Prueba del comportamiento cuando no se proporciona un comando"""
        cli = CLI()

        # configurar el mock para devolver args sin comando
        args = MagicMock()
        args.comando = None
        mock_parse_args.return_value = args

        # mockeamos el método print_help para verificar que se llama
        with patch.object(cli.constructor.parser, "print_help") as mock_help:
            cli.ejecutar()
            mock_help.assert_called_once()

    @patch("source.cli.core.ConstructorCLI.parsear")
    def test_ejecutar_comando_conexion(self, mock_parse_args):
        """Test execution of the conexion comando"""
        cli = CLI()

        # Configurar mock para devolver args con comando 'conexion'
        args = MagicMock()
        args.comando = "conexion"
        mock_parse_args.return_value = args

        # Mockear el método agregar_comando del constructor
        with patch.object(cli.constructor, "agregar_comando") as mock_agregar:
            # Mockear el método contenido_comando de ComandoConexion
            with patch.object(ComandoConexion, "contenido_comando") as m_conte:
                cli.ejecutar()

                # Verificar que se parseó el comando
                mock_agregar.assert_called_once_with(cli.comando_conexion)

                # Verificar que se llamó al método parsear del constructor
                mock_parse_args.assert_called_once()

                # Verificar que se ejecutó el comando correspondiente
                m_conte.assert_called_once_with(args)

        # verificar que la funcion conexion fue llamada (indirectamente
        # a traves del metodo contenido_comando). Ya que este metodo
        # se llama desde contenido_comando
        assert cli.args.comando == "conexion"

    @patch("source.cli.core.ConstructorCLI.parsear")
    def test_ejecutar_con_args(self, mock_parse_args):
        """Prueba de ejecución con argumentos específicos"""
        cli = CLI()

        # mockear args para retornar el comando 'conexion' con valores
        # específicos para los argumentos
        args = MagicMock()
        args.comando = "conexion"
        args.archivo = "./home/user/file.json"
        args.host = "localhost"
        args.puerto = "3306"
        args.usuario = "admin"
        args.password = "password"
        args.db_nombre = "graphqlstore_db"
        mock_parse_args.return_value = args

        # mockear el metodo agregar_comando del constructor
        with patch.object(cli.constructor, "agregar_comando") as mock_agregar:
            # mockear el metodo contenido_coamdo de ComandoConexion
            with patch.object(ComandoConexion, "contenido_comando") as m_conte:

                cli.ejecutar()

                # verificar que se parseo el comando
                mock_agregar.assert_called_once_with(cli.comando_conexion)

                # verificar que se llamo al metodo  parsear del constructor
                mock_parse_args.assert_called_once()

                # verificar  que se ejecuto el comando correspondiente
                m_conte.assert_called_once_with(args)

        # verificar que los argumentos fueron asignados correctamente
        assert cli.args.comando == "conexion"
        assert cli.args.archivo == "./home/user/file.json"
        assert cli.args.host == "localhost"
        assert cli.args.puerto == "3306"
        assert cli.args.usuario == "admin"
        assert cli.args.password == "password"
        assert cli.args.db_nombre == "graphqlstore_db"
