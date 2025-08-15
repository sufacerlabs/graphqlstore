"""Test for transform GraphQL schema to secure GraphQL schema"""

import pytest

from source.cli.graphql.transform_schema_graphql import (
    transform_schema_graphql,
)


def test_transformar_esquema_mysql():
    """Prueba la transformacion del esquema MySQL."""
    esquema = """
    type User {
        id: ID!
        password: String! @protected
        posts: [Post!] @relation(name: "UserPosts", onDelete: CASCADE)
    }
    """
    try:
        resultado = transform_schema_graphql(esquema)
        assert isinstance(resultado, str)
        assert "type User" in resultado
        assert "posts: [Post!]" in resultado
        assert "@relation" not in resultado
        assert "password:" not in resultado
    except ValueError as e:
        pytest.fail(f"Error transforming schema: {str(e)}")


def test_transformar_esquema_graphql_error():
    """Prueba la transformacion del esquema Graphql con error."""
    esquema = """ type User { id: ID! name: String!! } """
    with pytest.raises(ValueError, match="Error transforming schema"):
        transform_schema_graphql(esquema)
