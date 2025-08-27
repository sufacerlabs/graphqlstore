"""Tests for the GeneratorDBSchema class."""

from unittest.mock import MagicMock, patch


from source.cli.generators.factory import GeneratorSchemaFactory
from source.cli.generators.generator_db_schema import GeneratorDBSchema
from source.cli.graphql.configuracion_y_constantes import (
    DatabaseType,
    InfoEnum,
    InfoRelacion,
    InfoTabla,
)


class TestGeneratorDBSchema:
    """Test suite for the GeneratorDBSchema class."""

    @patch("source.cli.generators.generator_db_schema.GeneratorSchemaFactory")
    def test_init_default(self, mock_factory):
        """Test initialization with default database type (MySQL)."""
        mock_generator = MagicMock()
        mock_factory.create_generator.return_value = mock_generator

        generator = GeneratorDBSchema()

        mock_factory.create_generator.assert_called_once_with(
            DatabaseType.MYSQL,
        )

        #  pylint: disable=protected-access
        assert generator._generator == mock_generator
        # pylint: enable=protected-access
        assert generator.db_type == DatabaseType.MYSQL

    @patch("source.cli.generators.generator_db_schema.GeneratorSchemaFactory")
    def test_init_postgresql(self, mock_factory):
        """Test initialization with PostgreSQL database type."""
        mock_generator = MagicMock()
        mock_factory.create_generator.return_value = mock_generator

        generator = GeneratorDBSchema(DatabaseType.POSTGRESQL)

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
            GeneratorSchemaFactory, "create_generator"
        ) as mock_create_generator:
            mock_generator = MagicMock()
            mock_generator.console = "mock_console"
            mock_create_generator.return_value = mock_generator

            generator = GeneratorDBSchema()

            assert generator.console == "mock_console"

    def test_property_schema_sql(self):
        """Test schema_sql property forwarding."""
        with patch.object(
            GeneratorSchemaFactory, "create_generator"
        ) as mock_create_generator:
            mock_generator = MagicMock()
            mock_generator.schema_sql = ["SQL1", "SQL2"]
            mock_create_generator.return_value = mock_generator

            generator = GeneratorDBSchema()

            assert generator.schema_sql == ["SQL1", "SQL2"]

    def test_property_print_output(self):
        """Test print_output property getter/setter."""
        with patch.object(
            GeneratorSchemaFactory, "create_generator"
        ) as mock_create_generator:
            mock_generator = MagicMock()
            mock_generator.print_output = True
            mock_create_generator.return_value = mock_generator

            generator = GeneratorDBSchema()

            # Test getter
            assert generator.print_output is True

            # Test setter
            generator.print_output = False
            assert mock_generator.print_output is False

    def test_property_print_sql(self):
        """Test print_sql property getter/setter."""
        with patch.object(
            GeneratorSchemaFactory, "create_generator"
        ) as mock_create_generator:
            mock_generator = MagicMock()
            mock_generator.print_sql = True
            mock_create_generator.return_value = mock_generator

            generator = GeneratorDBSchema()

            # Test getter
            assert generator.print_sql is True

            # Test setter
            generator.print_sql = False
            assert mock_generator.print_sql is False

    def test_generate_schema(self):
        """Test generate_schema method forwarding."""
        with patch.object(
            GeneratorSchemaFactory, "create_generator"
        ) as mock_create_generator:
            mock_generator = MagicMock()
            mock_generator.generate_schema.return_value = "MOCK_SCHEMA_SQL"
            mock_create_generator.return_value = mock_generator

            generator = GeneratorDBSchema()

            # Create mock data
            mock_tables = {"Table1": MagicMock(spec=InfoTabla)}
            mock_enums = {"Enum1": MagicMock(spec=InfoEnum)}
            mock_relationships = [MagicMock(spec=InfoRelacion)]

            result = generator.generate_schema(
                mock_tables,
                mock_enums,
                mock_relationships,
                print_output=True,
                print_sql=False,
            )

            # Verify method was called with the correct parameters
            mock_generator.generate_schema.assert_called_once_with(
                tables=mock_tables,
                enums=mock_enums,
                relationships=mock_relationships,
                print_output=True,
                print_sql=False,
            )

            # Verify result is correctly returned
            assert result == "MOCK_SCHEMA_SQL"

    def test_get_schema_sql(self):
        """Test get_schema_sql method forwarding."""
        with patch.object(
            GeneratorSchemaFactory, "create_generator"
        ) as mock_create_generator:
            mock_generator = MagicMock()
            mock_generator.get_schema_sql.return_value = "FULL_SCHEMA_SQL"
            mock_create_generator.return_value = mock_generator

            generator = GeneratorDBSchema()

            result = generator.get_schema_sql()

            # Verify method was called
            mock_generator.get_schema_sql.assert_called_once()

            # Verify result is correctly returned
            assert result == "FULL_SCHEMA_SQL"

    def test_create_for_mysql(self):
        """Test crear_para_mysql class method."""
        with patch(
            "source.cli.generators.GeneratorDBSchema.__init__",
        ) as mock_init:
            mock_init.return_value = None
            GeneratorDBSchema.create_for_mysql()

            # Verify constructor was called with MySQL
            mock_init.assert_called_once_with(DatabaseType.MYSQL)

    def test_create_for_postgresql(self):
        """Test create_for_postgresql class method."""
        with patch(
            "source.cli.generators.GeneratorDBSchema.__init__",
        ) as mock_init:
            mock_init.return_value = None
            GeneratorDBSchema.create_for_postgresql()

            # Verify constructor was called with PostgreSQL
            mock_init.assert_called_once_with(DatabaseType.POSTGRESQL)

    def test_get_db_type(self):
        """Test get_db_type method."""
        with patch.object(GeneratorSchemaFactory, "create_generator"):
            # Test with MySQL
            generator_mysql = GeneratorDBSchema(DatabaseType.MYSQL)
            assert generator_mysql.get_db_type() == DatabaseType.MYSQL

            # Test with PostgreSQL
            generator_pg = GeneratorDBSchema(DatabaseType.POSTGRESQL)
            assert generator_pg.get_db_type() == DatabaseType.POSTGRESQL
