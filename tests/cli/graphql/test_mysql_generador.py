"""Pruebas para el modulo GeneradorEsquemaMySQL."""

from unittest.mock import patch
import pytest
from source.cli.graphql import (
    GeneradorEsquemaMySQL,
)
from source.cli.graphql.configuracion_y_constantes import (
    FuenteRelacion,
    InfoDirectiva,
    InfoEnum,
    InfoField,
    InfoRelacion,
    InfoTabla,
    ObjetivoRelacion,
    TipoLink,
    TipoRelacion,
    OnDelete,
)


@pytest.fixture(name="generador_mysql")
def fixture_generador_mysql():
    """Fixture que proporciona una instancia del generador."""
    return GeneradorEsquemaMySQL()


@pytest.fixture(name="campo_id")
def fixture_campo_id():
    """Fixture que proporciona un campo ID."""
    return InfoField(
        nombre="id",
        tipo_campo="ID",
        es_lista=False,
        es_requerido=True,
        directivas={
            "id": InfoDirectiva(nombre="id", argumentos={}),
        },
    )


@pytest.fixture(name="tablas_simples")
def fixture_tablas_simples(campo_id):
    # pylint: disable=duplicate-code
    """Fixture con tablas simples sin relaciones."""
    return {
        "User": InfoTabla(
            nombre="User",
            campos={
                "id": campo_id,
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


@pytest.fixture(name="enums_basicos")
def fixture_enums_basicos():
    """Fixture con enums basicos."""
    return {
        "UserStatus": InfoEnum(
            nombre="UserStatus",
            valores=["ACTIVE", "INACTIVE", "PENDING"],
        ),
    }


@pytest.fixture(name="relacion_one_to_many")
def fixture_relacion_one_to_many():
    """Fixture con una relacion one-to-many."""
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
            tipo_relation=TipoRelacion.ONE_TO_MANY.value,
            nombre_relacion="UserPosts",
            tipo_link=TipoLink.INLINE.value,
        )
    ]


@pytest.fixture(name="relacion_many_to_many")
def fixture_relacion_many_to_many():
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


@pytest.fixture(name="relacion_one_to_one")
def fixture_relacion_one_to_one():
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


@pytest.fixture(name="relacion_one_to_one_con_fuente_cascade")
def fixture_relacion_one_to_one_con_fuente_cascade():
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


@pytest.fixture(name="relacion_one_to_one_sin_campo_inverso")
def fixture_relacion_one_to_one_sin_campo_inverso():
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


@pytest.fixture(name="tabla_con_relaciones_otm")
def fixture_tabla_con_relaciones_otm(campo_id):
    """Fixture con tablas que tienen relaciones 1:N."""
    # pylint: disable=duplicate-code
    return {
        "User": InfoTabla(
            nombre="User",
            campos={
                "id": campo_id,
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
                "id": campo_id,
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
    # pylint: enable=duplicate-code


@pytest.fixture(name="tabla_con_relaciones_mtm")
def fixture_tabla_con_relaciones_mtm(campo_id):
    """Fixture con tablas que tienen relaciones N:M."""
    # pylint: disable=duplicate-code
    return {
        "User": InfoTabla(
            nombre="User",
            campos={
                "id": campo_id,
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
                "id": campo_id,
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


@pytest.fixture(name="tabla_con_relaciones_oto")
def fixture_tabla_con_relaciones_oto(campo_id):
    """Fixture con tablas que tienen relaciones 1:1."""
    # pylint: disable=duplicate-code
    return {
        "User": InfoTabla(
            nombre="User",
            campos={
                "id": campo_id,
                "name": InfoField(
                    nombre="name",
                    tipo_campo="String",
                    es_lista=False,
                    es_requerido=True,
                    directivas={},
                ),
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
                "id": campo_id,
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


@pytest.fixture(name="tabla_con_relaciones_oto_con_fuente_cascade")
def fixture_tabla_con_relaciones_oto_con_fuente_cascade(campo_id):
    """Fixture con tablas que tienen relaciones 1:1 con fuente CASCADE."""
    # pylint: disable=duplicate-code
    return {
        "User": InfoTabla(
            nombre="User",
            campos={
                "id": campo_id,
                "name": InfoField(
                    nombre="name",
                    tipo_campo="String",
                    es_lista=False,
                    es_requerido=True,
                    directivas={},
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
                "id": campo_id,
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


@pytest.fixture(name="tabla_con_relaciones_oto_sin_campo_inverso")
def fixture_tabla_con_relaciones_oto_sin_campo_inverso(campo_id):
    """Fixture con tablas que tienen relaciones 1:1 sin campo inverso."""
    # pylint: disable=duplicate-code
    return {
        "User": InfoTabla(
            nombre="User",
            campos={
                "id": campo_id,
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
                "id": InfoField(
                    nombre="id",
                    tipo_campo="ID",
                    es_lista=False,
                    es_requerido=True,
                    directivas={},
                ),
            },
        ),
    }
    # pylint: enable=duplicate-code


def test_inicializacion_exitosa(generador_mysql):
    """Prueba la inicializacion exitosa de GeneradorEsquemaMySQL."""
    assert isinstance(generador_mysql, GeneradorEsquemaMySQL)
    assert generador_mysql.consola is not None
    assert generador_mysql.esquema_mysql == []
    assert generador_mysql.visualizar_salida is None
    assert generador_mysql.visualizar_sql is None


def test_get_esquema_mysql_vacio(generador_mysql):
    """Prueba que el esquema MySQL es vacio cuando no hay \
        relaciones ni tablas."""

    sql = generador_mysql.generar_esquema(
        relaciones=[],
        tablas={},
        enums={},
    )

    assert isinstance(sql, str)
    assert sql == "\n\n"


def test_get_esquema_sql(generador_mysql):
    """Prueba que el esquema SQL se obtiene correctamente."""
    generador_mysql.esquema_mysql = [
        "CREATE TABLE User (id INT PRIMARY KEY, name VARCHAR(100));",
        "CREATE TABLE Post (id INT PRIMARY KEY, title VARCHAR(100));",
    ]

    sql = generador_mysql.get_esquema_sql()

    assert isinstance(sql, str)
    assert "CREATE TABLE User" in sql
    assert "CREATE TABLE Post" in sql
    # Comprobamos que el esquema SQL tiene 3 líneas
    # (2 tablas + 1 línea vacía al final)
    assert len(sql.split("\n")) == 3


def test_generar_esquema_otm(
    generador_mysql,
    tabla_con_relaciones_otm,
    relacion_one_to_many,
):
    """Prueba la generacion completa del esquema con rel 1:N."""
    with patch.object(generador_mysql.consola, "print"):
        sql = generador_mysql.generar_esquema(
            tablas=tabla_con_relaciones_otm,
            enums={},
            relaciones=relacion_one_to_many,
            visualizar_salida=False,
            visualizar_sql=False,
        )

    assert isinstance(sql, str)
    assert "CREATE TABLE User" in sql
    assert "`name` VARCHAR(255) NOT NULL," in sql
    assert "CREATE TABLE Post" in sql
    assert (
        "ALTER TABLE `Post`\n"
        "ADD COLUMN `user_id` VARCHAR(25) NOT NULL,\n"
        "ADD CONSTRAINT `fk_User_posts_Post` FOREIGN KEY (`user_id`) "
        "REFERENCES `User` (id) ON DELETE CASCADE;"
    ) in sql
    assert "`hashtags` JSON NOT NULL" in sql
    assert "`createdAt` DATETIME DEFAULT CURRENT_TIMESTAMP" in sql
    assert "`updatedAt` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE" in sql


def test_generar_esquema_mtm(
    generador_mysql,
    tabla_con_relaciones_mtm,
    relacion_many_to_many,
):
    """Prueba la generacion completa del esquema con rel N:M."""
    with patch.object(generador_mysql.consola, "print"):
        sql = generador_mysql.generar_esquema(
            tablas=tabla_con_relaciones_mtm,
            enums={},
            relaciones=relacion_many_to_many,
            visualizar_salida=False,
            visualizar_sql=False,
        )

    assert isinstance(sql, str)
    assert "CREATE TABLE User" in sql
    assert "CREATE TABLE Role" in sql
    assert "CREATE TABLE UserRoles" in sql
    assert "PRIMARY KEY (`user_id`, `role_id`),\n" in sql
    assert (
        "CONSTRAINT `fk_User_roles_Role` FOREIGN KEY "
        "(`user_id`) REFERENCES `User`(id) ON DELETE SET NULL,\n"
    ) in sql
    assert (
        "CONSTRAINT `fk_Role_users_User` FOREIGN KEY "
        "(`role_id`) REFERENCES `Role`(id) ON DELETE SET NULL\n"
    ) in sql


def test_generar_esquema_oto(
    generador_mysql,
    tabla_con_relaciones_oto,
    enums_basicos,
    relacion_one_to_one,
):
    """Prueba la generacion completa del esquema con rel 1:1."""
    with patch.object(generador_mysql.consola, "print"):
        sql = generador_mysql.generar_esquema(
            tablas=tabla_con_relaciones_oto,
            enums=enums_basicos,
            relaciones=relacion_one_to_one,
            visualizar_salida=False,
            visualizar_sql=False,
        )

    assert isinstance(sql, str)
    assert "CREATE TABLE User" in sql
    assert "CREATE TABLE Profile" in sql
    assert "ALTER TABLE `Profile`\n" in sql
    assert "`status` ENUM('ACTIVE', 'INACTIVE', 'PENDING')\n" in sql
    assert (
        "ADD CONSTRAINT `fk_User_profile_Profile` FOREIGN KEY (`user_id`) "
        "REFERENCES `User` (id) ON DELETE CASCADE;"
    ) in sql


def test_generar_esquema_oto_con_fuente_cascade(
    generador_mysql,
    tabla_con_relaciones_oto_con_fuente_cascade,
    relacion_one_to_one_con_fuente_cascade,
):
    """Prueba la generacion del esquema con rel 1:1 y fuente CASCADE."""
    with patch.object(generador_mysql.consola, "print"):
        sql = generador_mysql.generar_esquema(
            tablas=tabla_con_relaciones_oto_con_fuente_cascade,
            enums={},
            relaciones=relacion_one_to_one_con_fuente_cascade,
            visualizar_salida=False,
            visualizar_sql=False,
        )

    assert "CREATE TABLE User" in sql
    assert "CREATE TABLE Profile" in sql
    assert "ALTER TABLE `User`\n" in sql
    assert (
        "ADD CONSTRAINT `fk_User_profile_Profile` FOREIGN KEY (`user_id`) "
        "REFERENCES `Profile` (id) ON DELETE CASCADE;"
    ) in sql


def test_generar_esquema_oto_sin_campo_inverso(
    generador_mysql,
    tabla_con_relaciones_oto_sin_campo_inverso,
    relacion_one_to_one_sin_campo_inverso,
):
    """Prueba la generacion del esquema con rel 1:1 sin campo inverso."""
    with patch.object(generador_mysql.consola, "print"):
        sql = generador_mysql.generar_esquema(
            tablas=tabla_con_relaciones_oto_sin_campo_inverso,
            enums={},
            relaciones=relacion_one_to_one_sin_campo_inverso,
            visualizar_salida=False,
            visualizar_sql=False,
        )

    assert "CREATE TABLE User" in sql
    assert "CREATE TABLE Profile" in sql
    assert "ALTER TABLE `User`\n" in sql
    assert (
        "ADD CONSTRAINT `fk_User_profile_Profile` FOREIGN KEY (`profile_id`) "
        "REFERENCES `Profile` (id) ON DELETE CASCADE;"
    ) in sql
    assert (
        "ADD CONSTRAINT `fk_User_public_profile_Profile_1` FOREIGN KEY "
        "(`public_profile_id`) REFERENCES `Profile` (id) ON DELETE CASCADE;"
    ) in sql


def test_generar_esquema_con_directivas_avanzadas(
    generador_mysql,
    tablas_simples,
):
    """Prueba la generacion del esquema con directivas avanzadas."""
    with patch.object(generador_mysql.consola, "print") as mock_print:
        sql = generador_mysql.generar_esquema(
            tablas=tablas_simples,
            enums={},
            relaciones=[],
            visualizar_salida=True,
            visualizar_sql=True,
        )

    assert "CREATE TABLE User" in sql
    assert "`name` VARCHAR(255) NOT NULL DEFAULT 'Anonymous'" in sql
    assert "`hashtags` JSON NOT NULL" in sql
    assert "`age` INT DEFAULT 18" in sql
    assert "UNIQUE KEY `uk_email` (`email`)" in sql

    assert mock_print.called


def test_visualizar_salida_tablas(
    generador_mysql,
    tablas_simples,
):
    """Prueba la visualizacion de salida de tablas."""
    with patch.object(generador_mysql.consola, "print") as mock_print:
        # pylint: disable=protected-access
        generador_mysql._visualizar_salida_tablas(
            tabla_sql="CREATE TABLE User (...)",
            info_tabla=tablas_simples["User"],
            nom_tabla="User",
            visualizar_sql=True,
        )
        # pylint: enable=protected-access

    # verifica que se haya llamado a print
    assert mock_print.called
    # verifica que se llamo multiples veces (tree, panel y mensaje final)
    assert mock_print.call_count >= 3


def test_visualizar_salida_relaciones_mtm(
    generador_mysql,
    relacion_many_to_many,
):
    """Prueba la visualizacion de salida de relaciones."""
    with patch.object(generador_mysql.consola, "print") as mock_print:
        # pylint: disable=protected-access
        generador_mysql._visualizar_salida_relaciones(
            relacion=relacion_many_to_many[0],
            data_sql="CREATE TABLE UserRoles (...)",
            visualizar_salida=True,
            visualizar_sql=True,
            nombre_sql="UserRoles",
        )
        # pylint: enable=protected-access

    # verifica que se haya llamado a print
    assert mock_print.called
    # verifica que se llamo multiples veces (tree, panel y mensaje final)
    assert mock_print.call_count >= 3


def test_visualizar_salida_relaciones_otm(
    generador_mysql,
    relacion_one_to_many,
):
    """Prueba la visualizacion de salida de relaciones 1:N."""
    with patch.object(generador_mysql.consola, "print") as mock_print:
        # pylint: disable=protected-access
        generador_mysql._visualizar_salida_relaciones(
            relacion=relacion_one_to_many[0],
            data_sql="ALTER TABLE Post ADD COLUMN posts_id VARCHAR(25);",
            visualizar_salida=True,
            visualizar_sql=True,
            nombre_sql="Post",
        )
        # pylint: enable=protected-access

    # verifica que se haya llamado a print
    assert mock_print.called
    # verifica que se llamo multiples veces (tree, panel y mensaje final)
    assert mock_print.call_count >= 3


@pytest.fixture(name="relacion_itself")
def fixture_relacion_itself():
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


@pytest.fixture(name="tabla_con_relaciones_itself")
def fixture_tabla_con_relaciones_itself(campo_id):
    """Fixture con tablas que tienen relaciones de tipo itself."""
    return {
        "User": InfoTabla(
            nombre="friends",
            campos={
                "id": campo_id,
                "name": InfoField(
                    nombre="name",
                    tipo_campo="String",
                    es_lista=False,
                    es_requerido=True,
                    directivas={},
                ),
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


def test_generar_esquema_mysql_con_relacion_itself(
    generador_mysql, relacion_itself, tabla_con_relaciones_itself
):
    """Prueba la generacion del esquema MySQL con relaciones de tipo itself."""
    with patch.object(generador_mysql.consola, "print"):
        sql = generador_mysql.generar_esquema(
            relaciones=relacion_itself,
            tablas=tabla_con_relaciones_itself,
            enums={},
        )

    assert isinstance(sql, str)
    assert "CREATE TABLE User" in sql
    assert "CREATE TABLE UserToFriends" in sql
    assert "PRIMARY KEY (`user_A`, `user_B`)" in sql
    assert "CONSTRAINT `fk_User_friends_User_friends`" in sql
    assert "Y (`user_A`) REFERENCES `User`(id) ON DELETE CASCADE" in sql
    assert "CONSTRAINT `fk_User_friends_User`" in sql
    assert "Y (`user_B`) REFERENCES `User`(id) ON DELETE CASCADE" in sql


def test_transformar_esquema_mysql(generador_mysql):
    """Prueba la transformacion del esquema MySQL."""
    esquema = """
    type User {
        id: ID!
        name: String!
        password: String! @protected
        posts: [Post!] @relation(name: "UserPosts", onDelete: CASCADE)
    }
    """
    try:
        resultado = generador_mysql.transformar_esquema_graphql(esquema)
        assert isinstance(resultado, str)
        assert "type User" in resultado
        assert "posts: [Post!]" in resultado
        assert "@relation" not in resultado
        assert "password" not in resultado
    except ValueError as e:
        pytest.fail(f"Transformacion fallida: {str(e)}")


def test_transformar_esquema_graphql_error(generador_mysql):
    """Prueba la transformacion del esquema Graphql con error."""
    esquema = """ type User { id: ID! name: String!! } """
    with pytest.raises(ValueError, match="Error al transformar esquema"):
        generador_mysql.transformar_esquema_graphql(esquema)
