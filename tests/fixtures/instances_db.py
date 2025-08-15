"""Fixture for instances db"""

import pytest

from source.cli.generators import (
    GeneratorSchemaMySQL,
    GeneratorSchemaPostgreSQL,
)


@pytest.fixture(name="generador_mysql")
def fixture_generador_mysql():
    """Fixture que proporciona una instancia del generador."""
    return GeneratorSchemaMySQL()


@pytest.fixture(name="generator_postgres")
def fixture_generator_postgres():
    """Fixture that provides an instance of the PostgreSQL generator."""
    return GeneratorSchemaPostgreSQL()
