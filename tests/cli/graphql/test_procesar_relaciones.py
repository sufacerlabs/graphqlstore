"""Pruebas para ProcesarRelaciones"""

import pytest
from source.cli.graphql import (
    ProcesarRelaciones,
    RelationshipError,
)
from source.cli.graphql.configuracion_y_constantes import (
    InfoEnum,
    InfoField,
    InfoRelacion,
    InfoTabla,
    TipoField,
    TipoLink,
    TipoRelacion,
    InfoDirectiva,
)


@pytest.fixture(name="tipos_escalares")
def fixture_tipos_escalares():
    """Fixture para tipos escalares."""
    return {
        TipoField.ID.value: "VARCHAR(25)",
        TipoField.STRING.value: "VARCHAR(255)",
        TipoField.INT.value: "INT",
        TipoField.FLOAT.value: "DECIMAL(10, 2)",
        TipoField.BOOLEAN.value: "BOOLEAN",
        TipoField.DATETIME.value: "DATETIME",
        TipoField.JSON.value: "JSON",
    }


@pytest.fixture(name="tipos_enumerados")
def fixture_tipos_enumerados():
    """Fixture para tipos enumerados."""
    return {
        "UserRole": InfoEnum(
            nombre="UserRole",
            valores=["ADMIN", "USER", "GUEST"],
        ),
        "Status": InfoEnum(
            nombre="Status",
            valores=["ACTIVE", "INACTIVE", "PENDING"],
        ),
    }


@pytest.fixture(name="tablas_simples")
def fixture_tablas_simples():
    """Fixture para tablas simples."""
    return {
        "User": InfoTabla(
            nombre="User",
            campos={
                "id": InfoField(
                    nombre="id",
                    tipo_campo="ID",
                    es_lista=False,
                    es_requerido=False,
                    directivas={
                        "id": InfoDirectiva(
                            nombre="id",
                            argumentos={},
                        ),
                    },
                ),
                "name": InfoField(
                    nombre="name",
                    tipo_campo="String",
                    es_lista=False,
                    es_requerido=True,
                    directivas={},
                ),
                "email": InfoField(
                    nombre="email",
                    tipo_campo="String",
                    es_lista=False,
                    es_requerido=True,
                    directivas={},
                ),
            },
        )
    }


@pytest.fixture(name="relacion_many_to_one")
def fixture_relacion_many_to_one():
    """Fixture para una relación one-to-many."""
    return {
        "User": InfoTabla(
            nombre="User",
            campos={
                "id": InfoField(
                    nombre="id",
                    tipo_campo="ID",
                    es_lista=False,
                    es_requerido=True,
                    directivas={
                        "id": InfoDirectiva(
                            nombre="id",
                            argumentos={},
                        ),
                    },
                ),
                "name": InfoField(
                    nombre="name",
                    tipo_campo="String",
                    es_lista=False,
                    es_requerido=True,
                    directivas={},
                ),
                "posts": InfoField(
                    nombre="posts",
                    tipo_campo="Post",
                    es_lista=True,
                    es_requerido=True,
                    directivas={
                        "relation": InfoDirectiva(
                            nombre="relation", argumentos={"name": "UserPosts"}
                        )
                    },
                ),
            },
        ),
        "Post": InfoTabla(
            nombre="Post",
            campos={
                "id": InfoField(
                    nombre="id",
                    tipo_campo="ID",
                    es_lista=False,
                    es_requerido=True,
                    directivas={
                        "id": InfoDirectiva(
                            nombre="id",
                            argumentos={},
                        ),
                    },
                ),
                "title": InfoField(
                    nombre="title",
                    tipo_campo="String",
                    es_lista=False,
                    es_requerido=True,
                    directivas={},
                ),
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


@pytest.fixture(name="relacion_many_to_many")
def fixture_relacion_many_to_many():
    """Fixture para una relación many-to-many."""
    return {
        "User": InfoTabla(
            nombre="User",
            campos={
                "id": InfoField(
                    nombre="id",
                    tipo_campo="ID",
                    es_lista=False,
                    es_requerido=True,
                    directivas={
                        "id": InfoDirectiva(
                            nombre="id",
                            argumentos={},
                        ),
                    },
                ),
                "name": InfoField(
                    nombre="name",
                    tipo_campo="String",
                    es_lista=False,
                    es_requerido=True,
                    directivas={},
                ),
                "groups": InfoField(
                    nombre="groups",
                    tipo_campo="Group",
                    es_lista=True,
                    es_requerido=True,
                    directivas={
                        "relation": InfoDirectiva(
                            nombre="relation",
                            argumentos={
                                "name": "UserGroups",
                                "link": "TABLE",
                            },
                        )
                    },
                ),
            },
        ),
        "Group": InfoTabla(
            nombre="Group",
            campos={
                "id": InfoField(
                    nombre="id",
                    tipo_campo="ID",
                    es_lista=False,
                    es_requerido=True,
                    directivas={
                        "id": InfoDirectiva(
                            nombre="id",
                            argumentos={},
                        ),
                    },
                ),
                "name": InfoField(
                    nombre="name",
                    tipo_campo="String",
                    es_lista=False,
                    es_requerido=True,
                    directivas={},
                ),
                "users": InfoField(
                    nombre="users",
                    tipo_campo="User",
                    es_lista=True,
                    es_requerido=True,
                    directivas={
                        "relation": InfoDirectiva(
                            nombre="relation",
                            argumentos={
                                "name": "UserGroups",
                                "link": "TABLE",
                            },
                        )
                    },
                ),
            },
        ),
    }


@pytest.fixture(name="relacion_one_to_one")
def fixture_relacion_one_to_one():
    """Fixture para una relación one-to-one."""
    # pylint: disable=duplicate-code
    return {
        "User": InfoTabla(
            nombre="User",
            campos={
                "id": InfoField(
                    nombre="id",
                    tipo_campo="ID",
                    es_lista=False,
                    es_requerido=True,
                    directivas={
                        "id": InfoDirectiva(nombre="id", argumentos={}),
                    },
                ),
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
                            },
                        ),
                    },
                ),
            },
        ),
        "Profile": InfoTabla(
            nombre="Profile",
            campos={
                "id": InfoField(
                    nombre="id",
                    tipo_campo="ID",
                    es_lista=False,
                    es_requerido=True,
                    directivas={
                        "id": InfoDirectiva(
                            nombre="id",
                            argumentos={},
                        ),
                    },
                ),
                "bio": InfoField(
                    nombre="bio",
                    tipo_campo="String",
                    es_lista=False,
                    es_requerido=False,
                    directivas={},
                ),
                "user": InfoField(
                    nombre="user",
                    tipo_campo="User",
                    es_lista=False,
                    es_requerido=True,
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


@pytest.fixture(name="relacion_sin_nombre")
def fixture_relacion_sin_nombre():
    """Fixture para una relación sin nombre."""
    return {
        "User": InfoTabla(
            nombre="User",
            campos={
                "id": InfoField(
                    nombre="id",
                    tipo_campo="ID",
                    es_lista=False,
                    es_requerido=True,
                    directivas={
                        "id": InfoDirectiva(
                            nombre="id",
                            argumentos={},
                        ),
                    },
                ),
                "profile": InfoField(
                    nombre="profile",
                    tipo_campo="Profile",
                    es_lista=False,
                    es_requerido=True,
                    directivas={
                        "relation": InfoDirectiva(
                            nombre="relation",
                            argumentos={},
                        ),
                    },
                ),
            },
        ),
        "Profile": InfoTabla(
            nombre="Profile",
            campos={
                "id": InfoField(
                    nombre="id",
                    tipo_campo="ID",
                    es_lista=False,
                    es_requerido=True,
                    directivas={
                        "id": InfoDirectiva(
                            nombre="id",
                            argumentos={},
                        ),
                    },
                ),
                "bio": InfoField(
                    nombre="bio",
                    tipo_campo="String",
                    es_lista=False,
                    es_requerido=False,
                    directivas={},
                ),
                "user": InfoField(
                    nombre="user",
                    tipo_campo="User",
                    es_lista=False,
                    es_requerido=True,
                    directivas={
                        "relation": InfoDirectiva(
                            nombre="relation",
                            argumentos={},
                        ),
                    },
                ),
            },
        ),
    }


@pytest.fixture(name="relacion_con_link_erroneo_many_to_many")
def fixture_relacion_con_link_erroneo_many_to_many():
    """Fixture para una relación many-to-many con link erroneo."""
    # pylint: disable=duplicate-code
    return {
        "User": InfoTabla(
            nombre="User",
            campos={
                "id": InfoField(
                    nombre="id",
                    tipo_campo="ID",
                    es_lista=False,
                    es_requerido=True,
                    directivas={
                        "id": InfoDirectiva(nombre="id", argumentos={}),
                    },
                ),
                "groups": InfoField(
                    nombre="groups",
                    tipo_campo="Group",
                    es_lista=True,
                    es_requerido=True,
                    directivas={
                        "relation": InfoDirectiva(
                            nombre="relation",
                            argumentos={
                                "name": "UserGroups",
                                "link": "INLINE",  # link erroneo
                            },
                        )
                    },
                ),
            },
        ),
        "Group": InfoTabla(
            nombre="Group",
            campos={
                "id": InfoField(
                    nombre="id",
                    tipo_campo="ID",
                    es_lista=False,
                    es_requerido=True,
                    directivas={
                        "id": InfoDirectiva(nombre="id", argumentos={}),
                    },
                ),
                "users": InfoField(
                    nombre="users",
                    tipo_campo="User",
                    es_lista=True,
                    es_requerido=True,
                    directivas={
                        "relation": InfoDirectiva(
                            nombre="relation",
                            argumentos={
                                "name": "UserGroups",
                                "link": "INLINE",  # link erroneo
                            },
                        )
                    },
                ),
            },
        ),
    }
    # pylint: enable=duplicate-code


@pytest.fixture(name="proceso_simple")
def fixture_proceso_simple(tipos_escalares, tipos_enumerados):
    """Fixture que proporciona un procesador simple"""
    return ProcesarRelaciones({}, tipos_escalares, tipos_enumerados)


@pytest.fixture(name="proceso_con_tablas_simples")
def fixture_proceso_con_tablas_simples(
    tablas_simples,
    tipos_escalares,
    tipos_enumerados,
):
    """Fixture que proporciona un procesador con tablas simples"""
    return ProcesarRelaciones(
        tablas=tablas_simples,
        scalar_types=tipos_escalares,
        enum_types=tipos_enumerados,
    )


@pytest.fixture(name="proceso_con_relacion_many_to_one")
def fixture_proceso_con_relacion_many_to_one(
    relacion_many_to_one,
    tipos_escalares,
    tipos_enumerados,
):
    """Fixture que proporciona un procesador con una relación one-to-many"""
    return ProcesarRelaciones(
        tablas=relacion_many_to_one,
        scalar_types=tipos_escalares,
        enum_types=tipos_enumerados,
    )


@pytest.fixture(name="proceso_con_relacion_con_dos_one_to_many")
def fixture_proceso(
    con_relacion_con_dos_one_to_many,
    tipos_escalares,
    tipos_enumerados,
):
    """Fixture que proporciona un procesador con una \
        relación con dos one-to-many"""
    return ProcesarRelaciones(
        tablas=con_relacion_con_dos_one_to_many,
        scalar_types=tipos_escalares,
        enum_types=tipos_enumerados,
    )


@pytest.fixture(name="proceso_con_relacion_many_to_many")
def fixture_proceso_con_relacion_many_to_many(
    relacion_many_to_many,
    tipos_escalares,
    tipos_enumerados,
):
    """Fixture que proporciona un procesador con una relación many-to-many"""
    return ProcesarRelaciones(
        tablas=relacion_many_to_many,
        scalar_types=tipos_escalares,
        enum_types=tipos_enumerados,
    )


@pytest.fixture(name="proceso_con_relacion_one_to_one")
def fixture_proceso_con_relacion_one_to_one(
    relacion_one_to_one,
    tipos_escalares,
    tipos_enumerados,
):
    """Fixture que proporciona un procesador con una relación one-to-one"""
    return ProcesarRelaciones(
        tablas=relacion_one_to_one,
        scalar_types=tipos_escalares,
        enum_types=tipos_enumerados,
    )


@pytest.fixture(name="proceso_con_relacion_dos_one_to_many")
def fixture_proceso_con_relacion_dos_one_to_many(
    con_relacion_con_dos_one_to_many,
    tipos_escalares,
    tipos_enumerados,
):
    """Fixture que proporciona un procesador con una \
        relación con dos one-to-many"""
    return ProcesarRelaciones(
        tablas=con_relacion_con_dos_one_to_many,
        scalar_types=tipos_escalares,
        enum_types=tipos_enumerados,
    )


@pytest.fixture(name="proceso_con_relacion_sin_nombre")
def fixture_proceso_con_relacion_sin_nombre(
    relacion_sin_nombre,
    tipos_escalares,
    tipos_enumerados,
):
    """Fixture que proporciona un procesador con una relación sin nombre"""
    return ProcesarRelaciones(
        tablas=relacion_sin_nombre,
        scalar_types=tipos_escalares,
        enum_types=tipos_enumerados,
    )


@pytest.fixture(name="proceso_con_relacion_con_link_erroneo_many_to_many")
def fixture_proceso_con_relacion_con_link_erroneo_many_to_many(
    relacion_con_link_erroneo_many_to_many,
    tipos_escalares,
    tipos_enumerados,
):
    """Fixture que proporciona un procesador con una relación many-to-many \
        con link erroneo"""
    return ProcesarRelaciones(
        tablas=relacion_con_link_erroneo_many_to_many,
        scalar_types=tipos_escalares,
        enum_types=tipos_enumerados,
    )


def test_inicializacion_exitosa(
    tablas_simples,
    tipos_escalares,
    tipos_enumerados,
):
    """Prueba la inicializacion exitosa del procesador"""
    procesar_relaciones = ProcesarRelaciones(
        tablas=tablas_simples,
        scalar_types=tipos_escalares,
        enum_types=tipos_enumerados,
    )

    assert procesar_relaciones.tablas == tablas_simples
    assert procesar_relaciones.scalar_types == tipos_escalares
    assert procesar_relaciones.enum_types == tipos_enumerados
    assert not procesar_relaciones.relaciones
    assert procesar_relaciones.relaciones_procesadas == set()
    assert procesar_relaciones.nombres_constraint_usados == set()


def test_inicializacion_args_vacios():
    """Prueba la inicializacion con argumentos vacios"""
    procesar_relaciones = ProcesarRelaciones({}, {}, {})
    assert procesar_relaciones.tablas == {}
    assert procesar_relaciones.scalar_types == {}
    assert procesar_relaciones.enum_types == {}


def test_procesar_relaciones_sin_relaciones(
    proceso_con_tablas_simples,
):
    """Prueba procesar relaciones sin relaciones definidas"""
    relaciones = proceso_con_tablas_simples.procesar_relaciones()

    assert len(relaciones) == 0
    assert proceso_con_tablas_simples.get_relaciones() == []


def test_get_relaciones_inicialmente_vacio(proceso_simple):
    """Prueba que get_relaciones devuelve una lista vacia al inicio"""
    relaciones = proceso_simple.get_relaciones()
    assert relaciones == []


def test_validar_relaciones_sin_nombre(
    proceso_con_relacion_sin_nombre,
):
    """Prueba que se lanza un error si una relación no tiene nombre"""
    with pytest.raises(RelationshipError) as exc_info:
        proceso_con_relacion_sin_nombre.procesar_relaciones()

    assert "Falta un nombre para la relacion" in str(exc_info.value)
    assert "entre User.profile y Profile" in str(exc_info.value)


def test_validar_relacion_many_to_many_con_link_erroneo(
    proceso_con_relacion_con_link_erroneo_many_to_many,
):
    """Prueba que se lanza un error si una relación many-to-many \
        tiene link erroneo"""
    ps = proceso_con_relacion_con_link_erroneo_many_to_many
    with pytest.raises(RelationshipError) as ex_inf:
        ps.procesar_relaciones()

    assert "Para relaciones N:M entre User.groups y Group" in str(ex_inf.value)
    assert "debe usarse tipo de link TABLE." in str(ex_inf.value)


def test_procesar_relacion_many_to_one(
    proceso_con_relacion_many_to_one,
):
    """Prueba procesar una relación one-to-many"""
    relaciones = proceso_con_relacion_many_to_one.procesar_relaciones()

    assert len(relaciones) == 1
    rela = relaciones[0]

    # verificar informacion de la relación
    assert isinstance(rela, InfoRelacion)
    assert rela.nombre_relacion == "UserPosts"
    assert rela.tipo_relation == TipoRelacion.MANY_TO_ONE.value
    assert rela.tipo_link == TipoLink.INLINE.value  # valor por defecto

    # verificar fuente
    assert rela.fuente.tabla_fuente == "User"
    assert rela.fuente.campo_fuente == "posts"
    assert rela.fuente.fuente_es_lista is True
    assert rela.fuente.on_delete == "SET_NULL"  # valor por defecto
    assert rela.fuente.nombre_constraint_fuente == "fk_User_posts_Post_author"

    # verificar objetivo
    assert rela.objetivo.tabla_objetivo == "Post"
    assert rela.objetivo.campo_inverso == "author"
    assert rela.objetivo.on_delete_inverso == "CASCADE"
    assert rela.objetivo.nombre_constraint_objetivo is None


def test_procesar_relacion_many_to_many(
    proceso_con_relacion_many_to_many,
):
    """Prueba procesar una relación many-to-many"""
    relaciones = proceso_con_relacion_many_to_many.procesar_relaciones()

    assert len(relaciones) == 1
    rela = relaciones[0]

    # verificar informacion de la relación
    assert isinstance(rela, InfoRelacion)
    assert rela.nombre_relacion == "UserGroups"
    assert rela.tipo_relation == TipoRelacion.MANY_TO_MANY.value
    assert rela.tipo_link == TipoLink.TABLE.value

    # verificar fuente
    assert rela.fuente.tabla_fuente == "User"
    assert rela.fuente.campo_fuente == "groups"
    assert rela.fuente.fuente_es_lista is True
    assert rela.fuente.on_delete == "SET_NULL"
    assert rela.fuente.nombre_constraint_fuente == "fk_User_groups_Group_users"

    # verificar objetivo
    assert rela.objetivo.tabla_objetivo == "Group"
    assert rela.objetivo.campo_inverso == "users"
    assert rela.objetivo.on_delete_inverso == "SET_NULL"
    assert rela.objetivo.nombre_constraint_objetivo == "fk_Group_users_User"


def test_procesar_relacion_one_to_one(
    proceso_con_relacion_one_to_one,
):
    """Prueba procesar una relación one-to-one"""
    relaciones = proceso_con_relacion_one_to_one.procesar_relaciones()

    assert len(relaciones) == 1
    rela = relaciones[0]

    # verificar informacion de la relación
    assert isinstance(rela, InfoRelacion)
    assert rela.nombre_relacion == "UserProfile"
    assert rela.tipo_relation == TipoRelacion.ONE_TO_ONE.value
    assert rela.tipo_link == TipoLink.INLINE.value  # valor por defecto

    # verificar fuente
    assert rela.fuente.tabla_fuente == "User"
    assert rela.fuente.campo_fuente == "profile"
    assert rela.fuente.fuente_es_lista is False

    # verificar objetivo
    assert rela.objetivo.tabla_objetivo == "Profile"
    assert rela.objetivo.campo_inverso == "user"
