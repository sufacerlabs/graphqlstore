"""Fixtures for testing tables"""

import pytest

from source.cli.graphql.configuracion_y_constantes import (
    InfoTabla,
    InfoField,
    InfoDirectiva,
)


@pytest.fixture(name="simple_tables")
def fixture_simple_tables(field_id):
    # pylint: disable=duplicate-code
    """Fixture with simple tables without relationships."""
    return {
        "User": InfoTabla(
            nombre="User",
            campos={
                "id": field_id,
                "name": InfoField(
                    nombre="name",
                    tipo_campo="String",
                    es_lista=False,
                    es_requerido=True,
                    directivas={
                        "default": InfoDirectiva(
                            nombre="default",
                            argumentos={"value": "Anonymous"},
                        ),
                    },
                ),
                "hash_tags": InfoField(
                    nombre="has_tags",
                    tipo_campo="Json",
                    es_lista=True,
                    es_requerido=True,
                    directivas={
                        "db": InfoDirectiva(
                            nombre="db",
                            argumentos={"rename": "hashtags"},
                        ),
                    },
                ),
                "email": InfoField(
                    nombre="email",
                    tipo_campo="String",
                    es_lista=False,
                    es_requerido=True,
                    directivas={
                        "unique": InfoDirectiva(
                            nombre="unique",
                            argumentos={},
                        ),
                    },
                ),
                "age": InfoField(
                    nombre="age",
                    tipo_campo="Int",
                    es_lista=False,
                    es_requerido=False,
                    directivas={
                        "default": InfoDirectiva(
                            nombre="default",
                            argumentos={"value": 18},
                        ),
                    },
                ),
            },
        )
    }
    # pylint: enable=duplicate-code


@pytest.fixture(name="table_with_self_relations")
def fixture_table_with_self_relations(field_id, field_name):
    """Fixture con tablas que tienen relaciones de tipo itself."""
    return {
        "User": InfoTabla(
            nombre="friends",
            campos={
                "id": field_id,
                "name": field_name,
                "friends": InfoField(
                    nombre="friends",
                    tipo_campo="User",
                    es_lista=True,
                    es_requerido=False,
                    directivas={
                        "relation": InfoDirectiva(
                            nombre="relation",
                            argumentos={
                                "name": "UserToFriends",
                                "link": "TABLE",
                                "onDelete": "CASCADE",
                            },
                        )
                    },
                ),
            },
        )
    }


@pytest.fixture(name="table_with_many_to_one_relation")
def fixture_table_with_many_to_one_relation(field_id, field_name):
    """Fixture with tables with relationship 1:N."""
    # pylint: disable=duplicate-code
    return {
        "User": InfoTabla(
            nombre="User",
            campos={
                "id": field_id,
                "name": field_name,
                "posts": InfoField(
                    nombre="posts",
                    tipo_campo="Post",
                    es_lista=True,
                    es_requerido=False,
                    directivas={
                        "relation": InfoDirectiva(
                            nombre="relation",
                            argumentos={
                                "name": "UserPosts",
                                "onDelete": "CASCADE",
                            },
                        ),
                    },
                ),
                "hashtags": InfoField(
                    nombre="hashtags",
                    tipo_campo="String",
                    es_lista=True,
                    es_requerido=True,
                    directivas={},
                ),
                "createdAt": InfoField(
                    nombre="createdAt",
                    tipo_campo="DateTime",
                    es_lista=False,
                    es_requerido=False,
                    directivas={
                        "createdAt": InfoDirectiva(
                            nombre="createdAt",
                            argumentos={},
                        ),
                    },
                ),
                "updatedAt": InfoField(
                    nombre="updatedAt",
                    tipo_campo="DateTime",
                    es_lista=False,
                    es_requerido=False,
                    directivas={
                        "updatedAt": InfoDirectiva(
                            nombre="updatedAt",
                            argumentos={},
                        ),
                    },
                ),
            },
        ),
        "Post": InfoTabla(
            nombre="Post",
            campos={
                "id": field_id,
                "author": InfoField(
                    nombre="author",
                    tipo_campo="User",
                    es_lista=False,
                    es_requerido=True,
                    directivas={
                        "relation": InfoDirectiva(
                            nombre="relation",
                            argumentos={
                                "name": "UserPosts",
                                "onDelete": "CASCADE",
                            },
                        ),
                    },
                ),
            },
        ),
    }
    # pylint: enable=duplicate-code


@pytest.fixture(name="table_with_one_to_many_relation")
def fixture_table_with_one_to_many_relation(field_id):
    """Fixture with tables with relationship 1:N."""
    return {
        "Product": InfoTabla(
            nombre="Product",
            campos={
                "id": field_id,
                "productType": InfoField(
                    nombre="productType",
                    tipo_campo="ProductType",
                    es_lista=False,
                    es_requerido=False,
                    directivas={
                        "relation": InfoDirectiva(
                            nombre="relation",
                            argumentos={
                                "name": "ProductTypeProduct",
                                "onDelete": "CASCADE",
                            },
                        ),
                    },
                ),
            },
        ),
        "ProductType": InfoTabla(
            nombre="ProductType",
            campos={
                "id": field_id,
                "products": InfoField(
                    nombre="products",
                    tipo_campo="Product",
                    es_lista=True,
                    es_requerido=False,
                    directivas={
                        "relation": InfoDirectiva(
                            nombre="relation",
                            argumentos={
                                "name": "ProductTypeProduct",
                            },
                        ),
                    },
                ),
            },
        ),
    }


@pytest.fixture(name="table_with_many_to_many_relation")
def fixture_table_with_many_to_many_relation(field_id, field_name):
    """Fixture con tablas que tienen relaciones N:M."""
    # pylint: disable=duplicate-code
    return {
        "User": InfoTabla(
            nombre="User",
            campos={
                "id": field_id,
                "roles": InfoField(
                    nombre="roles",
                    tipo_campo="Role",
                    es_lista=True,
                    es_requerido=False,
                    directivas={
                        "relation": InfoDirectiva(
                            nombre="relation",
                            argumentos={
                                "name": "UserRoles",
                                "link": "TABLE",
                            },
                        ),
                    },
                ),
            },
        ),
        "Role": InfoTabla(
            nombre="Role",
            campos={
                "id": field_id,
                "name": field_name,
                "users": InfoField(
                    nombre="users",
                    tipo_campo="User",
                    es_lista=True,
                    es_requerido=False,
                    directivas={
                        "relation": InfoDirectiva(
                            nombre="relation",
                            argumentos={
                                "name": "UserRoles",
                                "link": "TABLE",
                            },
                        ),
                    },
                ),
            },
        ),
    }
    # pylint: enable=duplicate-code


@pytest.fixture(name="table_with_one_to_one_relation")
def fixture_table_with_one_to_one_relation(field_id, field_name):
    """Fixture con tablas que tienen relaciones 1:1."""
    # pylint: disable=duplicate-code
    return {
        "User": InfoTabla(
            nombre="User",
            campos={
                "id": field_id,
                "name": field_name,
                "profile": InfoField(
                    nombre="profile",
                    tipo_campo="Profile",
                    es_lista=False,
                    es_requerido=False,
                    directivas={
                        "relation": InfoDirectiva(
                            nombre="relation",
                            argumentos={
                                "name": "UserProfile",
                            },
                        ),
                    },
                ),
                "status": InfoField(
                    nombre="status",
                    tipo_campo="UserStatus",
                    es_lista=False,
                    es_requerido=False,
                    directivas={},
                ),
            },
        ),
        "Profile": InfoTabla(
            nombre="Profile",
            campos={
                "id": field_id,
                "user": InfoField(
                    nombre="user",
                    tipo_campo="User",
                    es_lista=False,
                    es_requerido=False,
                    directivas={
                        "relation": InfoDirectiva(
                            nombre="relation",
                            argumentos={
                                "name": "UserProfile",
                                "onDelete": "CASCADE",
                            },
                        ),
                    },
                ),
            },
        ),
    }
    # pylint: enable=duplicate-code


@pytest.fixture(name="table_with_one_to_one_relation_with_cascade_source")
def fixture_table_with_one_to_one_relation_with_cascade_source(
    field_id,
    field_name,
):
    """Fixture con tablas que tienen relaciones 1:1 con fuente CASCADE."""
    # pylint: disable=duplicate-code
    return {
        "User": InfoTabla(
            nombre="User",
            campos={
                "id": field_id,
                "name": field_name,
                "profile": InfoField(
                    nombre="profile",
                    tipo_campo="Profile",
                    es_lista=False,
                    es_requerido=True,
                    directivas={
                        "relation": InfoDirectiva(
                            nombre="relation",
                            argumentos={
                                "name": "UserProfile",
                                "onDelete": "CASCADE",  # Fuente CASCADE
                            },
                        ),
                    },
                ),
            },
        ),
        "Profile": InfoTabla(
            nombre="Profile",
            campos={
                "id": field_id,
                "user": InfoField(
                    nombre="user",
                    tipo_campo="User",
                    es_lista=False,
                    es_requerido=False,
                    directivas={
                        "relation": InfoDirectiva(
                            nombre="relation",
                            argumentos={
                                "name": "UserProfile",
                                "onDelete": "SET_NULL",  # Fuente CASCADE
                            },
                        ),
                    },
                ),
            },
        ),
    }
    # pylint: enable=duplicate-code


@pytest.fixture(name="table_with_one_to_one_relation_without_inverse_field")
def fixture_table_with_one_to_one_relation_without_inverse_field(field_id):
    """Fixture con tablas que tienen relaciones 1:1 sin campo inverso."""
    # pylint: disable=duplicate-code
    return {
        "User": InfoTabla(
            nombre="User",
            campos={
                "id": field_id,
                "profile": InfoField(
                    nombre="profile",
                    tipo_campo="Profile",
                    es_lista=False,
                    es_requerido=False,
                    directivas={
                        "relation": InfoDirectiva(
                            nombre="relation",
                            argumentos={
                                "name": "UserProfile",
                                "onDelete": "CASCADE",
                            },
                        ),
                    },
                ),
                "public_profile": InfoField(
                    nombre="public_profile",
                    tipo_campo="Profile",
                    es_lista=False,
                    es_requerido=False,
                    directivas={
                        "relation": InfoDirectiva(
                            nombre="relation",
                            argumentos={
                                "name": "UserProfilePublic",
                                "onDelete": "CASCADE",
                            },
                        ),
                    },
                ),
            },
        ),
        "Profile": InfoTabla(
            nombre="Profile",
            campos={
                "id": field_id,
            },
        ),
    }
    # pylint: enable=duplicate-code
