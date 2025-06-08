"""Pruebas para el adaptador MySQL."""

from unittest.mock import MagicMock, patch
import mysql.connector
import pytest

from source.cli.database.adaptadores.mysql import AdaptadorMySQL


@pytest.fixture(name="adapt_mysql")
def fixture_adaptador_mysql():
    """Fixture que proporciona una instancia del adaptador MySQL."""
    return AdaptadorMySQL()


@pytest.fixture(name="conf_valida")
def fixture_configuracion_valida():
    """Fixture con configuración válida para la conexión."""
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "3306",
        "DB_USER": "test_user",
        "DB_PASSWORD": "test_password",
        "DB_NAME": "test_db",
    }


@pytest.fixture(name="configuracion_invalida")
def fixture_configuracion_invalida():
    """Fixture con configuración incompleta"""
    return {
        "DB_HOST": "localhost",
    }


def test_inicializacion(adapt_mysql):
    """Prueba de inicialización del adaptador MySQL."""
    assert adapt_mysql.conexion is None
    assert adapt_mysql.cursor is None
    assert adapt_mysql.consola is not None


@patch("mysql.connector.connect")
def test_connect_exitoso(mock_connect, adapt_mysql, conf_valida):
    """Prueba  de conexión exitosa al adaptador MySQL."""

    # crear mocks
    mock_conexion = MagicMock()
    mock_cursor = MagicMock()
    mock_conexion.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conexion

    # conectar
    adapt_mysql.conectar(conf_valida)

    #  verificar que se llamo al metodo connect
    mock_connect.assert_called_once_with(
        host="localhost",
        port="3306",
        user="test_user",
        password="test_password",
        database="test_db",
    )

    assert adapt_mysql.conexion == mock_conexion
    assert adapt_mysql.cursor == mock_cursor


@patch("mysql.connector.connect")
def test_connect_con_configuracion_por_defecto(mock_connect, adapt_mysql):
    """Prueba de conexión con configuración por defecto."""
    mock_conexion = MagicMock()
    mock_cursor = MagicMock()
    mock_conexion.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conexion

    # Ejecutar conectar sin parámetros
    adapt_mysql.conectar({})

    # Verificar que se usaron los valores por defecto
    mock_connect.assert_called_once_with(
        host="localhost", port="3306", user="", password="", database=""
    )


@patch("mysql.connector.connect")
def test_connect_falla_conexion(mock_connect, adapt_mysql, conf_valida):
    """Prueba de fallo en la conexion al adaptador MySQL."""

    # mockear la excepcion de mysql.connector
    error_mysql = mysql.connector.Error("Error de conexión")
    mock_connect.side_effect = error_mysql

    # verificar que se lanza ValueError
    with pytest.raises(ValueError) as exc_info:
        adapt_mysql.conectar(conf_valida)

    # verificar el mensaje de error
    assert "Fallo de conexion de la base de datos" in str(exc_info.value)
    assert "Error de conexión" in str(exc_info.value)


@patch("mysql.connector.connect")
def test_probar_conexion_exitoso_verbose_falso(
    mock_connect,
    adapt_mysql,
    conf_valida,
):
    """Prueba de conexion exitosa con verbose=False."""

    # crear mocks
    mock_conexion = MagicMock()
    mock_cursor = MagicMock()
    mock_conexion.cursor.return_value = mock_cursor
    mock_conexion.is_connected.return_value = True
    mock_conexion.server_info = "8.0.25"
    mock_cursor.fetchone.return_value = ["test_db"]
    mock_connect.return_value = mock_conexion

    # conectar
    adapt_mysql.conectar(conf_valida)

    # mockear console.print
    with patch.object(adapt_mysql.consola, "print") as mock_print:
        adapt_mysql.probar_conexion(verbose=False)

    # verificar que se imprimieron los mensajes correctos
    print_calls = [call[0][0] for call in mock_print.call_args_list]
    assert "Intentando conectarse a la base de datos...\n" in print_calls
    assert "✅ Conectado exitosamente a la base de datos!\n" in print_calls


@patch("mysql.connector.connect")
def test_probar_conexion_exitoso_verbose_verdadero(
    mock_connect, adapt_mysql, conf_valida
):
    """Prueba de conexion exitosa con verbose=True."""

    # crear mocks
    mock_conexion = MagicMock()
    mock_cursor = MagicMock()
    mock_conexion.cursor.return_value = mock_cursor
    mock_conexion.is_connected.return_value = True
    mock_conexion.server_info = "8.0.25"
    mock_cursor.fetchone.return_value = ["test_db"]
    mock_cursor.fetchall.return_value = [("table1",), ("table2",)]
    mock_connect.return_value = mock_conexion

    # conectar
    adapt_mysql.conectar(conf_valida)

    # mockear console.print
    with patch.object(adapt_mysql.consola, "print") as mock_print:
        adapt_mysql.probar_conexion(verbose=True)

    # verificar que se imprimieron los mensajes correctos
    print_calls = [call[0][0] for call in mock_print.call_args_list]

    assert any("Version del servidor: 8.0.25" in call for call in print_calls)
    msg = "Conectado a la base de datos: test_db"
    assert any(msg in call for call in print_calls)
    assert any("Numbero de tablas: [2]" in call for call in print_calls)


@patch("mysql.connector.connect")
def test_probar_conexion_falla_verbose_falso(
    mock_connect,
    adapt_mysql,
    conf_valida,
):
    """Prueba de fallo en la conexion con verbose=False."""

    # crear mocks
    mock_conexion = MagicMock()
    mock_cursor = MagicMock()
    mock_conexion.cursor.return_value = mock_cursor
    mysql_err = mysql.connector.Error("Error de conexion")
    mock_conexion.is_connected.side_effect = mysql_err
    mock_connect.return_value = mock_conexion

    # conectar
    adapt_mysql.conectar(conf_valida)

    # mockear console.print
    with patch.object(adapt_mysql.consola, "print") as mock_print:
        adapt_mysql.probar_conexion(verbose=False)

    # verificar que se imprime el mensaje de error
    print_calls = [call[0][0] for call in mock_print.call_args_list]

    message = "❌ Fallo la conexion a la base datos"
    assert any(message in msg for msg in print_calls)


@patch("mysql.connector.connect")
def test_probar_conexion_falla_verbose_verdadero(
    mock_connect, adapt_mysql, conf_valida
):
    """Prueba de fallo en la conexion con verbose=True."""

    # crear mocks
    mock_conexion = MagicMock()
    mock_cursor = MagicMock()
    mock_conexion.cursor.return_value = mock_cursor
    mysql_err = mysql.connector.Error("Error de conexion")
    mock_conexion.is_connected.side_effect = mysql_err
    mock_connect.return_value = mock_conexion

    # ejecutar conexion
    adapt_mysql.conectar(conf_valida)

    # mockear console.print
    with (
        patch.object(adapt_mysql.consola, "print") as mock_print,
        patch("traceback.format_exc", return_value="Detalles del traceback"),
    ):
        adapt_mysql.probar_conexion(verbose=True)

    # verificar que se imprime el mensaje de error
    print_calls = [call[0][0] for call in mock_print.call_args_list]

    mensaje = "❌ Fallo la conexion a la base datos"
    assert any(mensaje in msg for msg in print_calls)
    mensaje = "Traceback..." and "Detalles del traceback"
    assert any(mensaje in msg for msg in print_calls)


def test_ejecutar_consulta_sin_conexion(adapt_mysql):
    """Prueba de ejecucion de una consulta SQL."""

    # verificar que se lanza ValueError si no hay cursor
    with pytest.raises(ValueError) as exc_info:
        adapt_mysql.ejecutar_consulta("SELECT 1")

    assert "Base de datos no conectada." in str(exc_info.value)


@patch("mysql.connector.connect")
def test_ejecutar_consulta_con_conexion(
    mock_connect,
    adapt_mysql,
    conf_valida,
):
    """Prueba de ejecucion de una consulta SQL con conexion establecida."""

    # crear mocks
    mock_conexion = MagicMock()
    mock_cursor = MagicMock()
    mock_conexion.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conexion

    # ejecutar conexion
    adapt_mysql.conectar(conf_valida)

    sql_query = "SELECT * FROM users"

    # ejecutar consulta
    adapt_mysql.ejecutar_consulta(sql_query)

    # verificar que se llamo al cursor.execute
    mock_cursor.execute.assert_called_once_with(sql_query)


def test_cerrar_conexion_sin_conexion(adapt_mysql):
    """Prueba de cerrar conexion sin conexion establecida."""
    # no deberia lanzar excepcion
    adapt_mysql.cerrar_conexion()

    # verificar que no se lanza error al cerrar sin conexion
    assert adapt_mysql.conexion is None
    assert adapt_mysql.cursor is None


@patch("mysql.connector.connect")
def test_cerrar_conexion_con_conexion(mock_connect, adapt_mysql, conf_valida):
    """Prueba de cerrar conexion con conexion establecida."""

    # crear mocks
    mock_conexion = MagicMock()
    mock_cursor = MagicMock()
    mock_conexion.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conexion

    # conectar
    adapt_mysql.conectar(conf_valida)

    # cerrar conexion
    adapt_mysql.cerrar_conexion()

    # verificar que se cerro la conexion y cursor
    mock_cursor.close.assert_called_once()
    mock_conexion.close.assert_called_once()
