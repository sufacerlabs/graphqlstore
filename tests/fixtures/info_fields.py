"""Fixtures for testing GraphQL field information."""

import pytest

from source.cli.graphql.configuracion_y_constantes import (
    InfoDirectiva,
    InfoField,
)


@pytest.fixture(name="field_id")
def fixture_field_id():
    """Fixture that provides an ID field."""
    return InfoField(
        nombre="id",
        tipo_campo="ID",
        es_lista=False,
        es_requerido=True,
        directivas={
            "id": InfoDirectiva(nombre="id", argumentos={}),
        },
    )


@pytest.fixture(name="field_name")
def fixture_field_name():
    """Fixture that provides a name field."""
    return InfoField(
        nombre="name",
        tipo_campo="String",
        es_lista=False,
        es_requerido=True,
        directivas={},
    )


@pytest.fixture(name="field_age")
def fixture_field_age():
    """Fixture that provides an age field."""
    return InfoField(
        nombre="age",
        tipo_campo="Int",
        es_lista=False,
        es_requerido=False,
        directivas={},
    )
