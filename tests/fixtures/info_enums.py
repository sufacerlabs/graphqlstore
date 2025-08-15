"""Fixtures for testing basic enums"""

import pytest

from source.cli.graphql.configuracion_y_constantes import InfoEnum


@pytest.fixture(name="basic_enums")
def fixture_basic_enums():
    """Fixture with basic enums."""
    return {
        "UserStatus": InfoEnum(
            nombre="UserStatus",
            valores=["ACTIVE", "INACTIVE"],
        ),
    }
