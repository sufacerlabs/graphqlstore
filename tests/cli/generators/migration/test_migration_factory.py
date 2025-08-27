"""Tests for the MigrationGeneratorFactory class."""

from typing import Type
from unittest.mock import MagicMock

import pytest

from source.cli.generators.migration.migration_base import (
    BaseMigrationGenerator,
)
from source.cli.generators.migration.migration_factory import (
    MigrationGeneratorFactory,
)
from source.cli.generators.migration.migration_mysql import (
    MySQLMigrationGenerator,
)
from source.cli.generators.migration.migration_postgresql import (
    PostgreSQLMigrationGenerator,
)
from source.cli.graphql.configuracion_y_constantes import DatabaseType


class TestMigrationGeneratorFactory:
    """Test suite for the MigrationGeneratorFactory."""

    def test_create_generator_mysql(self):
        """Test creating a MySQL migration generator."""
        generator = MigrationGeneratorFactory.create_generator(
            DatabaseType.MYSQL,
        )
        assert isinstance(generator, MySQLMigrationGenerator)
        assert generator.get_database_type() == DatabaseType.MYSQL

    def test_create_generator_postgresql(self):
        """Test creating a PostgreSQL migration generator."""
        generator = MigrationGeneratorFactory.create_generator(
            DatabaseType.POSTGRESQL,
        )
        assert isinstance(generator, PostgreSQLMigrationGenerator)
        assert generator.get_database_type() == DatabaseType.POSTGRESQL

    def test_create_generator_unsupported_type(self):
        """Test error when creating a generator for an unsupported type."""
        # Create a mock database type that's not supported
        mock_db_type = MagicMock(spec=DatabaseType)
        mock_db_type.value = "UNSUPPORTED_DB"
        mock_db_type.name = "UNSUPPORTED_DB"

        with pytest.raises(ValueError) as excinfo:
            MigrationGeneratorFactory.create_generator(mock_db_type)

        assert "Database type not supported" in str(excinfo.value)
        assert "UNSUPPORTED_DB" in str(excinfo.value)

    def test_get_supported_types(self):
        """Test getting the list of supported database types."""
        supported_types = MigrationGeneratorFactory.get_supported_types()
        assert DatabaseType.MYSQL in supported_types
        assert DatabaseType.POSTGRESQL in supported_types
        # Should have only MySQL and PostgreSQL for now
        assert len(supported_types) == 2

    def test_register_generator(self):
        """Test registering a new generator."""
        # Create a mock generator class
        mock_generator_class = MagicMock(spec=Type[BaseMigrationGenerator])
        mock_generator_instance = MagicMock(spec=BaseMigrationGenerator)
        mock_generator_class.return_value = mock_generator_instance

        # Create a mock database type
        mock_db_type = MagicMock(spec=DatabaseType)
        mock_db_type.value = "NEW_DB_TYPE"

        # Register the new generator
        MigrationGeneratorFactory.register_generator(
            mock_db_type,
            mock_generator_class,
        )

        # Verify the generator is now supported
        assert mock_db_type in MigrationGeneratorFactory.get_supported_types()

        # Verify we can create a generator of this type
        generator = MigrationGeneratorFactory.create_generator(mock_db_type)
        assert generator == mock_generator_instance

        MigrationGeneratorFactory.create_generator(mock_db_type)
        mock_generator_class.assert_called()

        # Clean up by removing the mock generator from the factory
        # pylint: disable=protected-access
        MigrationGeneratorFactory._generators.pop(mock_db_type)
        # pylint: enable=protected-access
