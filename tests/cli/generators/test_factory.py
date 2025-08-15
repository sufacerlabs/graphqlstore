"""Tests for the GeneratorSchemaFactory class."""

from typing import Type
from unittest.mock import MagicMock

import pytest

from source.cli.generators.base import BaseSchemaGenerator
from source.cli.generators.factory import GeneratorSchemaFactory
from source.cli.generators.mysql_generator import GeneratorSchemaMySQL
from source.cli.generators.postgresql_generator import (
    GeneratorSchemaPostgreSQL,
)
from source.cli.graphql.configuracion_y_constantes import DatabaseType


class TestGeneratorSchemaFactory:
    """Test suite for the GeneratorSchemaFactory."""

    def test_create_generator_mysql(self):
        """Test creating a MySQL generator."""
        generator = GeneratorSchemaFactory.create_generator(DatabaseType.MYSQL)
        assert isinstance(generator, GeneratorSchemaMySQL)
        assert generator.get_database_type() == DatabaseType.MYSQL

    def test_create_generator_postgresql(self):
        """Test creating a PostgreSQL generator."""
        generator = GeneratorSchemaFactory.create_generator(
            DatabaseType.POSTGRESQL,
        )
        assert isinstance(generator, GeneratorSchemaPostgreSQL)
        assert generator.get_database_type() == DatabaseType.POSTGRESQL

    def test_create_generator_unsupported_type(self):
        """Test error when creating a generator for an unsupported type."""
        # Create a mock database type that's not supported
        mock_db_type = MagicMock(spec=DatabaseType)
        mock_db_type.value = "UNSUPPORTED_DB"
        mock_db_type.name = "UNSUPPORTED_DB"

        with pytest.raises(ValueError) as excinfo:
            GeneratorSchemaFactory.create_generator(mock_db_type)

        assert "Database type not supported" in str(excinfo.value)
        assert "UNSUPPORTED_DB" in str(excinfo.value)

    def test_get_supported_types(self):
        """Test getting the list of supported database types."""
        supported_types = GeneratorSchemaFactory.get_supported_types()
        assert DatabaseType.MYSQL in supported_types
        assert DatabaseType.POSTGRESQL in supported_types
        # Should have only MySQL and PostgreSQL for now
        assert len(supported_types) == 2

    def test_register_generator(self):
        """Test registering a new generator."""
        # Create a mock generator class
        mock_generator_class = MagicMock(spec=Type[BaseSchemaGenerator])
        mock_generator_instance = MagicMock(spec=BaseSchemaGenerator)
        mock_generator_class.return_value = mock_generator_instance

        # Create a mock database type
        mock_db_type = MagicMock(spec=DatabaseType)
        mock_db_type.value = "NEW_DB_TYPE"

        # Register the new generator
        GeneratorSchemaFactory.register_generator(
            mock_db_type,
            mock_generator_class,
        )

        # Verify the generator is now supported
        assert mock_db_type in GeneratorSchemaFactory.get_supported_types()

        # Verify we can create a generator of this type
        generator = GeneratorSchemaFactory.create_generator(mock_db_type)
        assert generator == mock_generator_instance

        # Clean up by removing the mock generator from the factory
        # pylint: disable=protected-access
        GeneratorSchemaFactory._generators.pop(mock_db_type)
        # pylint: enable=protected-access
