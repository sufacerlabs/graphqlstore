"""Fixtures for instances of migration generators."""

import pytest

from source.cli.generators.migration import (
    MySQLMigrationGenerator,
    PostgreSQLMigrationGenerator,
)


@pytest.fixture(name="mysql_generator_migra")
def fixture_mysql_generador_migracion():
    """Fixture que proporciona una instancia del generador de migración."""
    return MySQLMigrationGenerator()


@pytest.fixture(name="pg_generator_migra")
def fixture_pg_generador_migracion():
    """Fixture que proporciona una instancia del generador PostgreSQL."""
    return PostgreSQLMigrationGenerator()
