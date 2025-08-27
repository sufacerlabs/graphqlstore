"""Fixtures for testing GraphQL schema differences."""

import pytest

from source.cli.graphql.configuracion_y_constantes import (
    InfoDiffCampos,
    InfoDiffEsquema,
)


@pytest.fixture(name="simple_differences")
def fixture_simple_differences(field_age, field_id):
    """Fixture with simple differences."""
    diferencias = InfoDiffEsquema()

    diferencias.tablas.agregadas = ["Post"]

    diferencias.tablas.campos["User"] = InfoDiffCampos(agregados=[field_age])
    diferencias.tablas.campos["Post"] = InfoDiffCampos(agregados=[field_id])

    return diferencias
