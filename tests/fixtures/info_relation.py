"""Fixtures for testing GraphQL relations"""

import pytest

from source.cli.graphql.configuracion_y_constantes import (
    FuenteRelacion,
    InfoRelacion,
    ObjetivoRelacion,
    OnDelete,
    TipoRelacion,
    TipoLink,
)


@pytest.fixture(name="many_to_one_relation")
def fixture_many_to_one_relation():
    """Fixture with a relation many to one."""
    return [
        InfoRelacion(
            fuente=FuenteRelacion(
                tabla_fuente="User",
                campo_fuente="posts",
                fuente_es_lista=True,
                nombre_constraint_fuente="fk_User_posts_Post",
                on_delete=OnDelete.SET_NULL.value,
            ),
            objetivo=ObjetivoRelacion(
                tabla_objetivo="Post",
                campo_inverso="author",
                nombre_constraint_objetivo=None,
                on_delete_inverso=OnDelete.CASCADE.value,
            ),
            tipo_relation=TipoRelacion.MANY_TO_ONE.value,
            nombre_relacion="UserPosts",
            tipo_link=TipoLink.INLINE.value,
        )
    ]


@pytest.fixture(name="one_to_many_relation")
def fixture_one_to_many_relation():
    """Fixture with a relation one to many."""
    return [
        InfoRelacion(
            fuente=FuenteRelacion(
                tabla_fuente="Product",
                campo_fuente="productType",
                fuente_es_lista=False,
                nombre_constraint_fuente="fk_Product_productType_ProductType",
                on_delete=OnDelete.CASCADE.value,
            ),
            objetivo=ObjetivoRelacion(
                tabla_objetivo="ProductType",
                campo_inverso="products",
                nombre_constraint_objetivo=None,
                on_delete_inverso=OnDelete.SET_NULL.value,
            ),
            tipo_relation=TipoRelacion.ONE_TO_MANY.value,
            nombre_relacion="ProductTypeProduct",
            tipo_link=TipoLink.INLINE.value,
        )
    ]


@pytest.fixture(name="many_to_many_relation")
def fixture_many_to_many_relation():
    """Fixture con una relacion many-to-many."""
    return [
        InfoRelacion(
            fuente=FuenteRelacion(
                tabla_fuente="User",
                campo_fuente="roles",
                fuente_es_lista=True,
                nombre_constraint_fuente="fk_User_roles_Role",
                on_delete=OnDelete.SET_NULL.value,
            ),
            objetivo=ObjetivoRelacion(
                tabla_objetivo="Role",
                campo_inverso="users",
                nombre_constraint_objetivo="fk_Role_users_User",
                on_delete_inverso=OnDelete.SET_NULL.value,
            ),
            tipo_relation=TipoRelacion.MANY_TO_MANY.value,
            nombre_relacion="UserRoles",
            tipo_link=TipoLink.TABLE.value,
        )
    ]


@pytest.fixture(name="one_to_one_relation")
def fixture_one_to_one_relation():
    """Fixture con una relacion one-to-one."""
    return [
        InfoRelacion(
            fuente=FuenteRelacion(
                tabla_fuente="User",
                campo_fuente="profile",
                fuente_es_lista=False,
                nombre_constraint_fuente="fk_User_profile_Profile",
                on_delete=OnDelete.SET_NULL.value,
            ),
            objetivo=ObjetivoRelacion(
                tabla_objetivo="Profile",
                campo_inverso="user",
                nombre_constraint_objetivo="fk_Profile_user_User",
                on_delete_inverso=OnDelete.CASCADE.value,
            ),
            tipo_relation=TipoRelacion.ONE_TO_ONE.value,
            nombre_relacion="UserProfile",
            tipo_link=TipoLink.INLINE.value,
        )
    ]


@pytest.fixture(name="one_to_one_relation_with_cascade_source")
def fixture_one_to_one_relation_with_cascade_source():
    """Fixture con una relacion one-to-one con fuente CASCADE."""
    return [
        InfoRelacion(
            fuente=FuenteRelacion(
                tabla_fuente="User",
                campo_fuente="profile",
                fuente_es_lista=False,
                nombre_constraint_fuente="fk_User_profile_Profile",
                on_delete=OnDelete.CASCADE.value,
            ),
            objetivo=ObjetivoRelacion(
                tabla_objetivo="Profile",
                campo_inverso="user",
                nombre_constraint_objetivo=None,
                on_delete_inverso="SET_NULL",
            ),
            tipo_relation=TipoRelacion.ONE_TO_ONE.value,
            nombre_relacion="UserProfile",
            tipo_link=TipoLink.INLINE.value,
        )
    ]


@pytest.fixture(name="one_to_one_relation_without_inverse_field")
def fixture_one_to_one_relation_without_inverse_field():
    """Fixture con una relacion one-to-one sin campo inverso."""
    return [
        InfoRelacion(
            fuente=FuenteRelacion(
                tabla_fuente="User",
                campo_fuente="profile",
                fuente_es_lista=False,
                nombre_constraint_fuente="fk_User_profile_Profile",
                on_delete=OnDelete.CASCADE.value,
            ),
            objetivo=ObjetivoRelacion(
                tabla_objetivo="Profile",
                campo_inverso=None,  # Sin campo inverso
                nombre_constraint_objetivo=None,
                on_delete_inverso=OnDelete.SET_NULL.value,
            ),
            tipo_relation=TipoRelacion.ONE_TO_ONE.value,
            nombre_relacion="UserProfile",
            tipo_link=TipoLink.INLINE.value,
        ),
        InfoRelacion(
            fuente=FuenteRelacion(
                tabla_fuente="User",
                campo_fuente="public_profile",
                fuente_es_lista=False,
                nombre_constraint_fuente="fk_User_public_profile_Profile_1",
                on_delete=OnDelete.CASCADE.value,
            ),
            objetivo=ObjetivoRelacion(
                tabla_objetivo="Profile",
                campo_inverso=None,  # Sin campo inverso
                nombre_constraint_objetivo=None,
                on_delete_inverso=OnDelete.SET_NULL.value,
            ),
            tipo_relation=TipoRelacion.ONE_TO_ONE.value,
            nombre_relacion="UserProfilePublic",
            tipo_link=TipoLink.INLINE.value,
        ),
    ]


@pytest.fixture(name="self_relation")
def fixture_self_relation():
    """Fixture con una relacion de tipo itself."""
    return [
        InfoRelacion(
            fuente=FuenteRelacion(
                tabla_fuente="User",
                campo_fuente="friends",
                fuente_es_lista=True,
                nombre_constraint_fuente="fk_User_friends_User_friends",
                on_delete=OnDelete.CASCADE.value,
            ),
            objetivo=ObjetivoRelacion(
                tabla_objetivo="User",
                campo_inverso="friends",
                nombre_constraint_objetivo="fk_User_friends_User",
                on_delete_inverso=OnDelete.CASCADE.value,
            ),
            tipo_relation=TipoRelacion.MANY_TO_MANY.value,
            nombre_relacion="UserToFriends",
            tipo_link=TipoLink.TABLE.value,
        )
    ]
