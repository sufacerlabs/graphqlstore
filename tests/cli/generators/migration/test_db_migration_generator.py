"""Tests for the GeneratorDBMigration class."""

from unittest.mock import MagicMock, patch

from source.cli.generators.migration.db_migration_generator import (
    GeneratorDBMigration,
)
from source.cli.generators.migration.migration_factory import (
    MigrationGeneratorFactory,
)
from source.cli.graphql.configuracion_y_constantes import (
    DatabaseType,
)


class TestGeneratorDBMigration:
    """Test suite for the GeneratorDBMigration class."""

    @patch(
        "source.cli.generators.migration.db_migration_generator."
        "MigrationGeneratorFactory"
    )
    def test_init_default(self, mock_factory):
        """Test initialization with default database type (MySQL)."""
        mock_generator = MagicMock()
        mock_factory.create_generator.return_value = mock_generator

        generator = GeneratorDBMigration()

        mock_factory.create_generator.assert_called_once_with(
            DatabaseType.MYSQL,
        )

        # pylint: disable=protected-access
        assert generator._generator == mock_generator
        # pylint: enable=protected-access
        assert generator.db_type == DatabaseType.MYSQL

    @patch(
        "source.cli.generators.migration.db_migration_generator."
        "MigrationGeneratorFactory"
    )
    def test_init_postgresql(self, mock_factory):
        """Test initialization with PostgreSQL database type."""
        mock_generator = MagicMock()
        mock_factory.create_generator.return_value = mock_generator

        generator = GeneratorDBMigration(DatabaseType.POSTGRESQL)

        mock_factory.create_generator.assert_called_once_with(
            DatabaseType.POSTGRESQL,
        )

        # pylint: disable=protected-access
        assert generator._generator == mock_generator
        # pylint: enable=protected-access
        assert generator.db_type == DatabaseType.POSTGRESQL

    def test_property_console(self):
        """Test console property forwarding."""
        with patch.object(
            MigrationGeneratorFactory, "create_generator"
        ) as mock_create_generator:
            mock_generator = MagicMock()
            mock_generator.console = "mock_console"
            mock_create_generator.return_value = mock_generator

            generator = GeneratorDBMigration()

            assert generator.console == "mock_console"

    def test_property_migration_sql(self):
        """Test migration_sql property forwarding."""
        with patch.object(
            MigrationGeneratorFactory, "create_generator"
        ) as mock_create_generator:
            mock_generator = MagicMock()
            mock_generator.migration_sql = ["SQL1", "SQL2"]
            mock_create_generator.return_value = mock_generator

            generator = GeneratorDBMigration()

            assert generator.migration_sql == ["SQL1", "SQL2"]

    def test_property_print_output(self):
        """Test print_output property getter/setter."""
        with patch.object(
            MigrationGeneratorFactory, "create_generator"
        ) as mock_create_generator:
            mock_generator = MagicMock()
            mock_generator.print_output = True
            mock_create_generator.return_value = mock_generator

            generator = GeneratorDBMigration()

            # Test getter
            assert generator.print_output is True

            # Test setter
            generator.print_output = False
            assert generator.print_output is False

    def test_property_print_sql(self):
        """Test print_sql property getter/setter."""
        with patch.object(
            MigrationGeneratorFactory, "create_generator"
        ) as mock_create_generator:
            mock_generator = MagicMock()
            mock_generator.print_sql = True
            mock_create_generator.return_value = mock_generator

            generator = GeneratorDBMigration()

            # Test getter
            assert generator.print_sql is True

            # Test setter
            generator.print_sql = False
            assert generator.print_sql is False

    def test_generate_migration(self):
        """Test generate_migration method forwarding."""
        with patch.object(
            MigrationGeneratorFactory,
            "create_generator",
        ) as mock_create_generator:
            mock_generator = MagicMock()
            mock_generator.generate_migration.return_value = {
                "id_migracion": "mock_id",
                "timestamp": "2023-10-01T00:00:00Z",
                "esquema_anterior": "mock_schema_old",
                "esquema_nuevo": "mock_schema_new",
                "diferencias": MagicMock(),
                "sql_generado": "mock_sql",
            }
            mock_create_generator.return_value = mock_generator

            generator = GeneratorDBMigration()

            # create mock data
            mock_esquema_anterior = "schema_old"
            mock_esquema_nuevo = "schema_new"

            result = generator.generar_migracion(
                previous_schema=mock_esquema_anterior,
                new_schema=mock_esquema_nuevo,
                print_output=True,
                print_sql=True,
            )

            assert result["id_migracion"] == "mock_id"

    def test_diff_schemas(self):
        """Test diff_schemas method forwarding."""
        with patch.object(
            MigrationGeneratorFactory, "create_generator"
        ) as mock_create_generator:
            mock_generator = MagicMock()
            mock_generator.diff_schemas.return_value = {
                "tablas": {
                    "agregadas": ["mock_table"],
                },
            }

            mock_create_generator.return_value = mock_generator

            generator = GeneratorDBMigration()
            mock_schema_actual = {"tables": ["table1"]}
            mock_schema_nuevo = {"tables": ["table1", "table2"]}
            result = generator.diff_schemas(
                schema_actual=mock_schema_actual,
                schema_nuevo=mock_schema_nuevo,
            )

            assert result["tablas"]["agregadas"] == ["mock_table"]

    def test_generate_sql_migration(self):
        """Test generate_sql_migration method forwarding."""
        with patch.object(
            MigrationGeneratorFactory, "create_generator"
        ) as mock_create_generator:
            mock_generator = MagicMock()
            mock_generator.generate_sql_migration.return_value = "mock_sql"
            mock_create_generator.return_value = mock_generator

            generator = GeneratorDBMigration()
            mock_diff_schema = {"tablas": {"agregadas": ["mock_table"]}}
            result = generator.generar_sql_migracion(mock_diff_schema)

            assert result == "mock_sql"

    def test_get_migration_sql(self):
        """Test get_migration_sql method forwarding."""
        with patch.object(
            MigrationGeneratorFactory, "create_generator"
        ) as mock_create_generator:
            mock_generator = MagicMock()
            mock_generator.migrations_sql = ["mock_sql"]
            mock_create_generator.return_value = mock_generator

            generator = GeneratorDBMigration()
            result = generator.get_migration_sql()
            assert result == ["mock_sql"]

    def test_get_db_type(self):
        """Test get_db_type method."""
        with patch.object(
            MigrationGeneratorFactory, "create_generator"
        ) as mock_create_generator:
            mock_generator = MagicMock()

            mock_generator.get_db_type.return_value = DatabaseType.MYSQL
            mock_create_generator.return_value = mock_generator

            generator = GeneratorDBMigration()
            result = generator.get_db_type()

            assert result == DatabaseType.MYSQL

            mock_generator.get_db_type.return_value = DatabaseType.POSTGRESQL
            mock_create_generator.return_value = mock_generator

            generator = GeneratorDBMigration(DatabaseType.POSTGRESQL)
            result = generator.get_db_type()

            assert result == DatabaseType.POSTGRESQL

    def test_create_for_mysql(self):
        """Test create_for_mysql method."""
        with patch.object(GeneratorDBMigration, "__init__") as mock_init:
            mock_init.return_value = None
            GeneratorDBMigration.create_for_mysql()

            # Verify constructor was called with MySQL
            mock_init.assert_called_once_with(DatabaseType.MYSQL)

    def test_create_for_postgresql(self):
        """Test create_for_postgresql method."""
        with patch.object(GeneratorDBMigration, "__init__") as mock_init:
            mock_init.return_value = None
            GeneratorDBMigration.create_for_postgresql()

            # Verify constructor was called with PostgreSQL
            mock_init.assert_called_once_with(DatabaseType.POSTGRESQL)
