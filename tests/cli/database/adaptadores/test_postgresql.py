"""Tests for the PostgreSQL adapter."""

from unittest.mock import MagicMock, patch
import psycopg2
import pytest

from source.cli.database.adaptadores.postgresql import AdaptadorPostgreSQL


@pytest.fixture(name="postgresql_adapter")
def fixture_postgresql_adapter():
    """Fixture that provides an instance of the PostgreSQL adapter."""
    return AdaptadorPostgreSQL()


@pytest.fixture(name="conf_valida")
def fixture_configuracion_valida():
    """Fixture con configuración válida para la conexión."""
    return {
        "DB_HOST": "localhost",
        "DB_PUERTO": "5432",
        "DB_USUARIO": "test_user",
        "DB_PASSWORD": "test_password",
        "DB_NOMBRE": "test_db",
    }


@pytest.fixture(name="configuracion_invalida")
def fixture_configuracion_invalida():
    """Fixture con configuración incompleta"""
    return {
        "DB_HOST": "localhost",
    }


def test_inicialization(postgresql_adapter):
    """Test initialization of the PostgreSQL adapter."""
    assert postgresql_adapter.conexion is None
    assert postgresql_adapter.cursor is None
    assert postgresql_adapter.consola is not None


@patch("psycopg2.connect")
def test_successful_connection(mock_connect, postgresql_adapter, conf_valida):
    """Test successful connection to the PostgreSQL adapter."""

    # crear mocks
    mock_conexion = MagicMock()
    mock_cursor = MagicMock()
    mock_conexion.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conexion

    # conectar
    postgresql_adapter.conectar(conf_valida)

    #  verificar que se llamo al metodo connect
    mock_connect.assert_called_once_with(
        host="localhost",
        port="5432",
        user="test_user",
        password="test_password",
        database="test_db",
    )

    assert postgresql_adapter.conexion == mock_conexion
    assert postgresql_adapter.cursor == mock_cursor


@patch("psycopg2.connect")
def test_connect_with_default_configuration(mock_connect, postgresql_adapter):
    """Test connection with default configuration."""
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_connection

    # connect with parameters
    postgresql_adapter.conectar({})

    # verify that it was called with default parameters
    mock_connect.assert_called_once_with(
        host="localhost",
        port="5432",
        user="postgres",
        password="",
        database="postgres",
    )


@patch("psycopg2.connect")
def test_failed_connection(mock_connect, postgresql_adapter, conf_valida):
    """Test failed connection to the PostgreSQL"""

    error_pg = psycopg2.Error("Connection failed")
    mock_connect.side_effect = error_pg

    with patch.object(postgresql_adapter.consola, "print") as mock_print:
        postgresql_adapter.conectar(conf_valida)

    calls = [call[0][0] for call in mock_print.call_args_list]

    message = "❌ Error al conectar a la base de datos"
    assert any(message in msg for msg in calls)
    message = "Detalles del error: Connection failed"
    assert any(message in msg for msg in calls)


@patch("psycopg2.connect")
def test_successful_connection_verbose_false(
    mock_connect,
    postgresql_adapter,
    conf_valida,
):
    """Test successful connection with verbose=False."""

    mock_connection = MagicMock()
    mock_cursor = MagicMock()

    mock_connection.cursor.return_value = mock_cursor
    mock_connection.closed.return_value = False
    mock_connection.server_info = "13.3"

    mock_cursor.fetchone.return_value = ["test_db"]

    mock_connect.return_value = mock_connection

    # connect to the database
    postgresql_adapter.conectar(conf_valida)

    with patch.object(postgresql_adapter.consola, "print") as mock_print:
        postgresql_adapter.probar_conexion(verbose=False)

    # verify that these messages were successfully printed
    print_calls = [call[0][0] for call in mock_print.call_args_list]
    assert "Intentando conectarse a la base de datos...\n" in print_calls
    assert "✅ Conectado exitosamente a la base de datos!\n" in print_calls


@patch("psycopg2.connect")
def test_successful_connection_verbose_true(
    mock_connect,
    postgresql_adapter,
    conf_valida,
):
    """Test successful connection with verbose=True."""

    mock_connection = MagicMock()
    mock_cursor = MagicMock()

    mock_connection.cursor.return_value = mock_cursor
    mock_connection.closed.return_value = False
    mock_connection.info.server_version = "13.3"

    mock_cursor.fetchone.return_value = ["test_db"]
    mock_cursor.fetchall.return_value = [("table1",), ("table2",)]

    mock_connect.return_value = mock_connection

    # connect to the database
    postgresql_adapter.conectar(conf_valida)

    with patch.object(postgresql_adapter.consola, "print") as mock_print:
        postgresql_adapter.probar_conexion(verbose=True)

    # verify that these messages were successfully printed
    print_calls = [call[0][0] for call in mock_print.call_args_list]

    assert any("Version del servidor: 13.3" in msg for msg in print_calls)
    msg = "Conectado a la base de datos: test_db"
    assert any(msg in call for call in print_calls)
    assert any("Numbero de tablas: [2]" in msg for msg in print_calls)


@patch("psycopg2.connect")
def test_failed_connection_verbose_true(
    mock_connect,
    postgresql_adapter,
    conf_valida,
):
    """Test failed connection with verbose=True."""

    # mock the connection
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # set up the mock cursor to raise an exception when used
    pg_error = psycopg2.Error("Connection failed")
    mock_cursor.execute.side_effect = pg_error

    # Connect first (this will be successful)
    postgresql_adapter.conectar(conf_valida)

    # now test probar_conexion which should fail
    # when it tries to execute a query
    with (
        patch.object(postgresql_adapter.consola, "print") as mock_print,
        patch("traceback.format_exc", return_value="Traceback info"),
    ):
        postgresql_adapter.probar_conexion(verbose=True)

    # check the printed error messages
    print_calls = [call[0][0] for call in mock_print.call_args_list]

    assert any("Fallo la conexion a la base" in msg for msg in print_calls)
    assert any("Traceback info" in msg for msg in print_calls)


def test_execute_query_without_connection(postgresql_adapter):
    """Test executing a query without an active connection."""
    with pytest.raises(ValueError) as exc_info:
        postgresql_adapter.ejecutar_consulta("SELECT 1")

    assert "Base de datos no conectada" in str(exc_info.value)


@patch("psycopg2.connect")
def test_execute_query_with_connection(
    mock_connect,
    postgresql_adapter,
    conf_valida,
):
    """Test executing a SQL query with a established connection."""

    # mock the connection
    mock_connection = MagicMock()
    mock_cursor = MagicMock()

    mock_connection.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_connection

    # connect to the database
    postgresql_adapter.conectar(conf_valida)

    # execute a query
    sql_query = "SELECT * FROM test_table"

    # execute the query
    postgresql_adapter.ejecutar_consulta(sql_query)

    # verify that the cursor's execute method was called
    # with the correct SQL query
    mock_cursor.execute.assert_called_once_with(sql_query)


def test_close_connection_without_connection(postgresql_adapter):
    """Test closing the connection when there is no an established \
        connection."""
    # it should not raise an error
    postgresql_adapter.cerrar_conexion()

    # verify that it does not raise an error without connection
    assert postgresql_adapter.conexion is None
    assert postgresql_adapter.cursor is None


@patch("psycopg2.connect")
def test_close_connection_with_connection(
    mock_connect,
    postgresql_adapter,
    conf_valida,
):
    """Test closing the connection when there is an established connection."""

    # mock the connection
    mock_connection = MagicMock()
    mock_cursor = MagicMock()

    mock_connection.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_connection

    # connect to the database
    postgresql_adapter.conectar(conf_valida)

    # close the connection
    postgresql_adapter.cerrar_conexion()

    # verify that the cursor and connection were closed
    mock_cursor.close.assert_called_once()
    mock_connection.close.assert_called_once()


def test_test_connection_without_connection_neither_cursor(postgresql_adapter):
    """Test test connection without an established connection \
        neither cursor."""

    assert postgresql_adapter.conexion is None
    assert postgresql_adapter.cursor is None

    # it should not raise an error only return None
    postgresql_adapter.probar_conexion(verbose=False)


def test_database_is_empty(postgresql_adapter):
    """Test if the database is empty"""

    postgresql_adapter.cursor = MagicMock()
    postgresql_adapter.conexion = MagicMock()
    postgresql_adapter.cursor.fetchall.return_value = []

    result = postgresql_adapter.empty_database()

    postgresql_adapter.cursor.execute.assert_called_once_with(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'public';",
    )
    assert result is True


def test_can_not_check_if_database_is_empty_without_connection(
    postgresql_adapter,
):
    """Test if it raises an error when trying to check if the database is \
        empty without an established connection."""

    with pytest.raises(ValueError) as exc_info:
        postgresql_adapter.empty_database()

    assert "Base de datos no conectada" in str(exc_info.value)
