"""Pruebas para la migracion"""

from unittest.mock import patch
import pytest
from source.cli.graphql.configuracion_y_constantes import (
    InfoDiffCampos,
    InfoDiffEsquema,
    InfoDirectiva,
    InfoField,
    InfoMigracion,
    InfoTabla,
    OnDelete,
    TipoLink,
    TipoRelacion,
)
from source.cli.graphql.exceptions import (
    GraphQLStoreError,
    MigrationError,
    MigrationGenerationError,
)
from source.cli.graphql.mysql_migracion import GeneradorMigracionMySQL


@pytest.fixture(name="generador_migracion")
def fixture_generador_migracion():
    """Fixture que proporciona una instancia del generador de migración."""
    return GeneradorMigracionMySQL()


@pytest.fixture(name="esquema_anterior")
def fixture_esquema_anterior():
    """Fixture con esquema GraphQL anterior."""
    return """
    type User {
        id: ID! @id
        name: String!
        email: String
    }

    enum UserStatus {
        ACTIVE
        INACTIVE
    }
    """


@pytest.fixture(name="esquema_nuevo")
def fixture_esquema_nuevo():
    """Fixture con esquema GraphQL nuevo."""
    return """
    type User {
        id: ID! @id
        name: String!
        email: String
        age: Int
        status: UserStatus
    }

    type Post {
        id: ID! @id
        title: String!
        content: String
        author: User @relation(name: "UserPosts", onDelete: CASCADE)
    }

    enum UserStatus {
        ACTIVE
        INACTIVE
        PENDING
    }
    """


@pytest.fixture(name="esquema_identico")
def fixture_esquema_identico():
    """Fixture con esquema idéntico al anterior."""
    return """
    type User {
        id: ID! @id
        name: String!
        email: String
    }

    enum UserStatus {
        ACTIVE
        INACTIVE
    }
    """


@pytest.fixture(name="tabla_post")
def fixture_tabla_post():
    """Fixture con tabla Post."""
    return InfoTabla(
        nombre="Post",
        campos={
            "id": InfoField(
                nombre="id",
                tipo_campo="ID",
                es_lista=False,
                es_requerido=True,
                directivas={"id": InfoDirectiva(nombre="id", argumentos={})},
            ),
        },
    )


@pytest.fixture(name="campo_age")
def fixture_campo_age():
    """Fixture con campo age."""
    return InfoField(
        nombre="age",
        tipo_campo="Int",
        es_lista=False,
        es_requerido=False,
        directivas={},
    )


@pytest.fixture(name="campo_status")
def fixture_campo_status():
    """Fixture con campo status enum."""
    return InfoField(
        nombre="status",
        tipo_campo="UserStatus",
        es_lista=False,
        es_requerido=False,
        directivas={},
    )


@pytest.fixture(name="diferencias_simples")
def fixture_diferencias_simples(campo_age, tabla_post):
    """Fixture con diferencias simples."""
    diferencias = InfoDiffEsquema()

    diferencias.tablas.agregadas = ["Post"]

    diferencias.tablas.campos["User"] = InfoDiffCampos(agregados=[campo_age])
    diferencias.tablas.campos["Post"] = InfoDiffCampos(
        agregados=list(tabla_post.campos.values())
    )

    return diferencias


@pytest.fixture(name="diferencias_vacias")
def fixture_diferencias_vacias():
    """Fixture con diferencias vacías."""
    return InfoDiffEsquema()


def test_inicializacion_generador_migracion(generador_migracion):
    """Prueba la inicialización correcta del generador."""
    assert isinstance(generador_migracion, GeneradorMigracionMySQL)
    assert generador_migracion.consola is not None
    assert generador_migracion.migraciones_sql == []
    assert generador_migracion.parser is not None
    assert generador_migracion.visualizar_salida is True
    assert generador_migracion.visualizar_sql is True


def test_generar_migracion_sin_cambios(
    generador_migracion,
    esquema_anterior,
    esquema_identico,
):
    """Prueba generación cuando no hay cambios."""
    with patch.object(generador_migracion, "diff_esquemas") as mock_diff:
        mock_diff.return_value = InfoDiffEsquema()

        # now mock console print
        with patch.object(generador_migracion.consola, "print") as mock_print:
            resultado = generador_migracion.generar_migracion(
                esquema_anterior=esquema_anterior,
                esquema_nuevo=esquema_identico,
                visualizar_salida=True,
            )

    assert isinstance(resultado, InfoMigracion)
    assert resultado.sql_generado == ""
    assert not resultado.diferencias.tiene_cambios()

    assert mock_print.called
    assert "No se detectaron cambios" in mock_print.call_args[0][0]


@patch.object(GeneradorMigracionMySQL, "diff_esquemas")
@patch.object(GeneradorMigracionMySQL, "generar_sql_migracion")
def test_generar_migracion_exitosa(
    mock_generar_sql,
    mock_diff_esquemas,
    generador_migracion,
    esquema_anterior,
    esquema_nuevo,
    diferencias_simples,
):
    """Prueba generación exitosa de migración."""
    # pylint: disable=too-many-arguments,too-many-positional-arguments

    # mockear
    mock_diff_esquemas.return_value = diferencias_simples
    mock_generar_sql.return_value = "CREATE TABLE Post (id VARCHAR(25));"

    with patch.object(generador_migracion.consola, "print") as mock_print:

        resultado = generador_migracion.generar_migracion(
            esquema_anterior=esquema_anterior,
            esquema_nuevo=esquema_nuevo,
            visualizar_salida=True,
            visualizar_sql=False,
        )

    # verifiar
    assert isinstance(resultado, InfoMigracion)
    assert resultado.esquema_anterior == esquema_anterior
    assert resultado.esquema_nuevo == esquema_nuevo
    assert resultado.diferencias == diferencias_simples
    assert "CREATE TABLE" in resultado.sql_generado
    assert resultado.id_migracion.startswith("migration_")

    mock_diff_esquemas.assert_called_once_with(esquema_anterior, esquema_nuevo)
    mock_generar_sql.assert_called_once_with(diferencias_simples)

    # verificar que se llamaron ambos prints
    assert mock_print.call_count == 3

    args = mock_print.call_args_list

    assert "Generando migracion" in args[0][0][0]
    assert "Migracion generada exitosamente" in args[1][0][0]
    assert "Total de sentencias SQL: 2" in args[2][0][0]
    # pylint: enable=too-many-arguments,too-many-positional-arguments


def test_generar_migracion_con_id_personalizado(
    generador_migracion,
    esquema_anterior,
    esquema_nuevo,
):
    """Prueba generación con ID personalizado."""
    id_personalizado = "migration_custom_test_123"

    with patch.object(generador_migracion, "diff_esquemas") as mock_diff:
        mock_diff.return_value = InfoDiffEsquema()

        resultado = generador_migracion.generar_migracion(
            esquema_anterior=esquema_anterior,
            esquema_nuevo=esquema_nuevo,
            id_migracion=id_personalizado,
            visualizar_salida=False,
        )

        assert resultado.id_migracion == id_personalizado


def test_generar_migracion_error_comparacion(
    generador_migracion,
    esquema_anterior,
):
    """Prueba manejo de errores en comparación."""
    esquema_invalido = "invalid graphql syntax {"

    with pytest.raises(MigrationError):
        generador_migracion.generar_migracion(
            esquema_anterior=esquema_anterior,
            esquema_nuevo=esquema_invalido,
            visualizar_salida=False,
        )


def test_generar_migracion_procesar_relaciones(
    generador_migracion,
):
    """Prueba generación de migración con procesamiento
    de relaciones completo."""

    esquema_anterior = """
    type User {
        id: ID! @id
        posts: [Post] @relation(name: "UserPosts", onDelete: CASCADE)
    }

    type Post {
        id: ID! @id
        author: User @relation(name: "UserPosts")
    }
    """

    esquema_nuevo = """
    type User {
        id: ID! @id
        name: String!
        posts: [Post] @relation(name: "UserPosts")
        roles: [Role] @relation(name: "UserRoles", link: TABLE)
    }

    type Post {
        id: ID! @id
        title: String!
        author: User @relation(name: "UserPosts")
        tags: [Tag] @relation(name: "PostTags", link: TABLE)
    }

    type Role {
        id: ID! @id
        name: String!
        users: [User] @relation(name: "UserRoles", link: TABLE)
    }

    type Tag {
        id: ID! @id
        name: String!
        posts: [Post] @relation(name: "PostTags", link: TABLE)
    }
    """
    # pylint: disable=protected-access
    generador_migracion._enums_disponibles = {}
    # pylint: enable=protected-access

    with patch.object(generador_migracion.consola, "print"):
        resultado = generador_migracion.generar_migracion(
            esquema_anterior=esquema_anterior,
            esquema_nuevo=esquema_nuevo,
            visualizar_salida=False,
            visualizar_sql=False,
        )

    diferencias = resultado.diferencias

    assert "Role" in diferencias.tablas.agregadas
    assert "Tag" in diferencias.tablas.agregadas
    assert len(diferencias.tablas.agregadas) == 2

    assert len(diferencias.relaciones.agregadas) == 2

    relaciones_nombres = [
        rel.nombre_relacion for rel in diferencias.relaciones.agregadas
    ]
    assert "UserRoles" in relaciones_nombres
    assert "PostTags" in relaciones_nombres

    # verificar que las relaciones many-to-many tienen el tipo correcto
    for relacion in diferencias.relaciones.agregadas:
        assert relacion.tipo_relation == TipoRelacion.MANY_TO_MANY.value
        assert relacion.tipo_link == TipoLink.TABLE.value

    sql_generado = resultado.sql_generado
    assert "UserRoles" in sql_generado
    assert "PostTags" in sql_generado
    assert "CREATE TABLE" in sql_generado

    assert "user_id" in sql_generado or "user_A" in sql_generado
    assert "role_id" in sql_generado or "role_B" in sql_generado
    assert "post_id" in sql_generado or "post_A" in sql_generado
    assert "tag_id" in sql_generado or "tag_B" in sql_generado


def test_generar_migracion_relaciones_eliminadas(
    generador_migracion,
):
    """Prueba generación de migración cuando se eliminan relaciones."""

    esquema_anterior = """
    type User {
        id: ID! @id
        name: String!
        posts: [Post] @relation(name: "UserPosts", onDelete: CASCADE)
        roles: [Role] @relation(name: "UserRoles", link: TABLE)
    }

    type Post {
        id: ID! @id
        title: String!
        author: User @relation(name: "UserPosts")
    }

    type Role {
        id: ID! @id
        name: String!
        users: [User] @relation(name: "UserRoles", link: TABLE)
    }
    """

    esquema_nuevo = """
    type User { id: ID! @id }

    type Post { id: ID! @id }

    type Role { id: ID! @id }
    """

    with patch.object(generador_migracion.consola, "print"):
        resultado = generador_migracion.generar_migracion(
            esquema_anterior=esquema_anterior,
            esquema_nuevo=esquema_nuevo,
            visualizar_salida=False,
            visualizar_sql=False,
        )

    diferencias = resultado.diferencias

    # Verificar relaciones eliminadas
    assert len(diferencias.relaciones.eliminadas) == 2

    relaciones_eliminadas = [
        rel.nombre_relacion for rel in diferencias.relaciones.eliminadas
    ]
    assert "UserPosts" in relaciones_eliminadas
    assert "UserRoles" in relaciones_eliminadas

    sql_generado = resultado.sql_generado
    assert "DROP FOREIGN KEY" in sql_generado or "DROP TABLE" in sql_generado


def test_generar_migracion_relaciones_one_to_one_cascade(
    generador_migracion,
):
    """Prueba generación de migración con relaciones one-to-one."""

    esquema_anterior = """
    type User { id: ID! @id name: String! }

    type Profile { id: ID! @id bio: String }
    """

    esquema_nuevo = """
    type User {
        id: ID! @id
        name: String!
        profile: Profile @relation(name: "UserProfile")
    }

    type Profile {
        id: ID! @id
        bio: String
        user: User @relation(name: "UserProfile", onDelete: CASCADE)
    }
    """

    with patch.object(generador_migracion.consola, "print"):
        resultado = generador_migracion.generar_migracion(
            esquema_anterior=esquema_anterior,
            esquema_nuevo=esquema_nuevo,
            visualizar_salida=False,
            visualizar_sql=False,
        )

    diferencias = resultado.diferencias

    relacion = diferencias.relaciones.agregadas[0]
    assert relacion.tipo_relation == TipoRelacion.ONE_TO_ONE.value
    assert relacion.nombre_relacion == "UserProfile"

    sql_generado = resultado.sql_generado
    assert "UNIQUE" in sql_generado


def test_generar_migracion_relaciones_one_cascade_to_one(
    generador_migracion,
):
    """Prueba generación de migración con relaciones one-to-one con CASCADE."""

    esquema_anterior = """
    type User { id: ID! @id name: String! }
    type Profile { id: ID! @id bio: String }
    """

    esquema_nuevo = """
    type User {
        id: ID! @id
        name: String!
        profile: Profile @relation(name: "UserProfile", onDelete: CASCADE)
    }

    type Profile {
        id: ID! @id
        bio: String
        user: User @relation(name: "UserProfile")
    }
    """

    with patch.object(generador_migracion.consola, "print"):
        resultado = generador_migracion.generar_migracion(
            esquema_anterior=esquema_anterior,
            esquema_nuevo=esquema_nuevo,
            visualizar_salida=False,
            visualizar_sql=False,
        )

    sql_generado = resultado.sql_generado
    assert "ON DELETE CASCADE" in sql_generado


def test_generar_migracion_relaciones_one_to_one_set_null(
    generador_migracion,
):
    """Prueba generación de migración con relaciones
    one-to-one con SET NULL."""

    esquema_anterior = """
    type User { id: ID! @id }
    type Profile { id: ID! @id }
    """

    esquema_nuevo = """
    type User {
        id: ID! @id
        name: String!
        profile: Profile @relation(name: "UserProfile", onDelete: SET_NULL)
    }

    type Profile {
        id: ID! @id
        bio: String
        user: User @relation(name: "UserProfile")
    }
    """

    with patch.object(generador_migracion.consola, "print"):
        resultado = generador_migracion.generar_migracion(
            esquema_anterior=esquema_anterior,
            esquema_nuevo=esquema_nuevo,
            visualizar_salida=False,
            visualizar_sql=False,
        )

    sql_generado = resultado.sql_generado
    assert "ON DELETE SET NULL" in sql_generado


def test_generar_migracion_relaciones_one_to_many(
    generador_migracion,
):
    """Prueba generación de migración con relaciones one-to-many."""

    esquema_anterior = """
    type User { id: ID! @id name: String! }

    type Post { id: ID! @id title: String! }
    """

    esquema_nuevo = """
    type User {
        id: ID! @id
        name: String!
        posts: [Post] @relation(name: "UserPosts")
    }

    type Post {
        id: ID! @id
        title: String!
        author: User @relation(name: "UserPosts", onDelete: CASCADE)
    }
    """
    with patch.object(generador_migracion.consola, "print"):
        resultado = generador_migracion.generar_migracion(
            esquema_anterior=esquema_anterior,
            esquema_nuevo=esquema_nuevo,
            visualizar_salida=False,
            visualizar_sql=False,
        )

    sql_generado = resultado.sql_generado
    assert "REFERENCES `User`(id)" in sql_generado


def test_diff_esquemas_procesar_relaciones_auto_relacion(
    generador_migracion,
):
    """Prueba procesamiento de auto-relaciones (self-referencing)."""

    esquema_anterior = """
    type Category { id: ID! @id name: String! }
    """

    esquema_nuevo = """
    type Category {
        id: ID! @id
        name: String!
        subcategories: [Category] @relation(
            name: "CategoryHierarchy", link: TABLE, onDelete: CASCADE
        )
    }
    """

    diferencias = generador_migracion.diff_esquemas(
        esquema_anterior=esquema_anterior, esquema_nuevo=esquema_nuevo
    )

    assert len(diferencias.relaciones.agregadas) == 1

    relacion = diferencias.relaciones.agregadas[0]
    assert relacion.fuente.tabla_fuente == "Category"
    assert relacion.objetivo.tabla_objetivo == "Category"
    assert relacion.tipo_relation == TipoRelacion.MANY_TO_MANY.value


def test_diff_esquemas_relaciones_con_diferentes_on_delete(
    generador_migracion,
):
    """Prueba procesamiento de relaciones con diferentes políticas onDelete."""

    esquema_anterior = """
    type User { id: ID! @id name: String! }

    type Post { id: ID! @id title: String! }
    """

    esquema_nuevo = """
    type User {
        id: ID! @id
        name: String!
        posts: [Post] @relation(name: "UserPosts", onDelete: SET_NULL)
    }

    type Post {
        id: ID! @id
        title: String!
        author: User @relation(name: "UserPosts", onDelete: CASCADE)
    }
    """

    diferencias = generador_migracion.diff_esquemas(
        esquema_anterior=esquema_anterior, esquema_nuevo=esquema_nuevo
    )

    assert len(diferencias.relaciones.agregadas) == 1

    relacion = diferencias.relaciones.agregadas[0]
    assert relacion.fuente.on_delete == OnDelete.SET_NULL.value
    assert relacion.objetivo.on_delete_inverso == OnDelete.CASCADE.value


def test_generar_migracion_eliminar_campos(
    generador_migracion,
    esquema_anterior,
    esquema_nuevo,
):
    """Prueba generación de migración con eliminación de campos."""

    esquema_anterior = """
    type User { id: ID! @id name: String! email: String }
    """

    esquema_nuevo = """
    type User { id: ID! @id name: String! }
    """

    with patch.object(generador_migracion.consola, "print"):
        resultado = generador_migracion.generar_migracion(
            esquema_anterior=esquema_anterior,
            esquema_nuevo=esquema_nuevo,
            visualizar_salida=False,
            visualizar_sql=False,
        )

    diferencias = resultado.diferencias

    campos_eliminados = [
        campo.nombre for campo in diferencias.tablas.campos["User"].eliminados
    ]
    assert "email" in campos_eliminados

    sql_generado = resultado.sql_generado
    assert "DROP COLUMN `email`" in sql_generado


def test_generar_migracion_agregar_campos(
    generador_migracion,
    esquema_anterior,
    esquema_nuevo,
):
    """Prueba generación de migración con agregado de campos."""

    esquema_anterior = """
    type User { id: ID! @id name: String! }
    """

    esquema_nuevo = """
    type User { id: ID! @id name: String! age: Int }
    """

    with patch.object(generador_migracion.consola, "print"):
        resultado = generador_migracion.generar_migracion(
            esquema_anterior=esquema_anterior,
            esquema_nuevo=esquema_nuevo,
            visualizar_salida=False,
            visualizar_sql=False,
        )

    diferencias = resultado.diferencias

    campos_agregados = [
        campo.nombre for campo in diferencias.tablas.campos["User"].agregados
    ]
    assert "age" in campos_agregados

    sql_generado = resultado.sql_generado
    assert "ADD COLUMN `age` INT" in sql_generado


def test_generar_migracion_modificar_campos(
    generador_migracion,
    esquema_anterior,
    esquema_nuevo,
):
    """Prueba generación de migración con modificación de campos."""

    esquema_anterior = """
    type User { id: ID! @id name: String! email: String }
    """

    esquema_nuevo = """
    type User { id: ID! @id name: String! email: String! }
    """

    with patch.object(generador_migracion.consola, "print"):
        resultado = generador_migracion.generar_migracion(
            esquema_anterior=esquema_anterior,
            esquema_nuevo=esquema_nuevo,
            visualizar_salida=False,
            visualizar_sql=False,
        )

    diferencias = resultado.diferencias

    cambios_email = diferencias.tablas.campos["User"].modificados[0]
    assert cambios_email.nombre == "email"
    assert cambios_email.info_antigua.es_requerido is False
    assert cambios_email.info_nueva.es_requerido is True

    sql_generado = resultado.sql_generado
    assert "MODIFY COLUMN `email` VARCHAR(255) NOT NULL" in sql_generado


def test_generar_migracion_modificar_enum(
    generador_migracion,
    esquema_anterior,
    esquema_nuevo,
):
    """Prueba generación de migración con modificación de enums
    en una tabla existente."""

    esquema_anterior = """
    enum UserStatus {
        ACTIVE
        INACTIVE
    }

    type User {
        id: ID! @id
        name: String!
        status: UserStatus
    }
    """

    esquema_nuevo = """
    enum UserStatus {
        ACTIVE
        INACTIVE
        PENDING
    }

    type User {
        id: ID! @id
        name: String!
        status: UserStatus
    }
    """

    with patch.object(generador_migracion.consola, "print"):
        resultado = generador_migracion.generar_migracion(
            esquema_anterior=esquema_anterior,
            esquema_nuevo=esquema_nuevo,
            visualizar_salida=True,
            visualizar_sql=True,
        )

    diferencias = resultado.diferencias

    assert len(diferencias.enums.modificados) == 1

    cambio_enum = diferencias.enums.modificados[0]
    assert cambio_enum.nombre == "UserStatus"
    assert cambio_enum.valores_antiguos == ["ACTIVE", "INACTIVE"]
    assert cambio_enum.valores_nuevos == ["ACTIVE", "INACTIVE", "PENDING"]

    sql_generado = resultado.sql_generado
    assert "ENUM('ACTIVE', 'INACTIVE', 'PENDING')" in sql_generado


def test_generar_migracion_nuevo_enum(
    generador_migracion,
    esquema_anterior,
    esquema_nuevo,
):
    """Prueba generación de migración con un nuevo enum agregado."""

    esquema_anterior = """
    type User {
        id: ID! @id
        name: String!
    }
    """

    esquema_nuevo = """
    type User {
        id: ID! @id
        name: String!
        status: UserStatus
    }

    enum UserStatus {
        ACTIVE
        INACTIVE
    }
    """

    with patch.object(generador_migracion.consola, "print"):
        resultado = generador_migracion.generar_migracion(
            esquema_anterior=esquema_anterior,
            esquema_nuevo=esquema_nuevo,
            visualizar_salida=False,
            visualizar_sql=False,
        )

    diferencias = resultado.diferencias

    assert len(diferencias.enums.agregados) == 1

    nuevo_enum = diferencias.enums.agregados[0]
    assert nuevo_enum.nombre == "UserStatus"
    assert set(nuevo_enum.valores) == {"ACTIVE", "INACTIVE"}

    sql_generado = resultado.sql_generado
    assert "ADD COLUMN `status` ENUM('ACTIVE', 'INACTIVE')" in sql_generado


def test_generar_migracion_eliminar_enum(
    generador_migracion,
    esquema_anterior,
    esquema_nuevo,
):
    """Prueba generación de migración con eliminación de enums."""

    esquema_anterior = """
    enum UserStatus {
        ACTIVE
        INACTIVE
    }

    type User {
        id: ID! @id
        name: String!
        status: UserStatus
    }
    """

    esquema_nuevo = """
    type User {
        id: ID! @id
        name: String!
    }
    """

    with patch.object(generador_migracion.consola, "print"):
        resultado = generador_migracion.generar_migracion(
            esquema_anterior=esquema_anterior,
            esquema_nuevo=esquema_nuevo,
            visualizar_salida=False,
            visualizar_sql=False,
        )

    diferencias = resultado.diferencias

    assert len(diferencias.enums.eliminados) == 1
    assert "UserStatus" in diferencias.enums.eliminados

    sql_generado = resultado.sql_generado
    assert "DROP COLUMN `status`" in sql_generado


def test_generar_migracion_eliminar_tablas(
    generador_migracion,
    esquema_anterior,
    esquema_nuevo,
):
    """Prueba generación de migración con eliminación de tablas."""

    esquema_anterior = """
    type User {
        id: ID! @id
        name: String!
    }

    type Post {
        id: ID! @id
        title: String!
    }
    """

    esquema_nuevo = """
    type User {
        id: ID! @id
        name: String!
    }
    """

    with patch.object(generador_migracion.consola, "print"):
        resultado = generador_migracion.generar_migracion(
            esquema_anterior=esquema_anterior,
            esquema_nuevo=esquema_nuevo,
            visualizar_salida=False,
            visualizar_sql=False,
        )

    diferencias = resultado.diferencias

    assert "Post" in diferencias.tablas.eliminadas

    sql_generado = resultado.sql_generado
    assert "DROP TABLE IF EXISTS `Post`" in sql_generado


def test_generar_sql_migracion_error_metodo_privado(generador_migracion):
    """Prueba manejo de errores cuando un método privado falla."""

    diferencias = InfoDiffEsquema()
    diferencias.tablas.agregadas = ["NewTable"]
    diferencias.tablas.campos["NewTable"] = InfoDiffCampos(
        agregados=[
            InfoField(
                nombre="id",
                tipo_campo="ID",
                es_lista=False,
                es_requerido=True,
                directivas={"id": InfoDirectiva(nombre="id", argumentos={})},
            )
        ]
    )

    with patch.object(
        generador_migracion,
        "_generar_sql_crear_tabla",
        side_effect=GraphQLStoreError("Error crear tabla"),
    ):
        with pytest.raises(MigrationGenerationError) as exc_info:
            generador_migracion.generar_sql_migracion(diferencias)

        assert "Error generando SQL: Error crear tabla" in str(exc_info.value)


def test_generar_migracion_con_directivas_avanzadas(
    generador_migracion,
    esquema_anterior,
    esquema_nuevo,
):
    """Prueba generación de migración cuando no se define columna ID."""

    esquema_anterior = """
    type User {
        id: ID! @id
        name: String!
        email: String
    }
    """

    esquema_nuevo = """
    type Employee {
        name: String! @default(value: "emp_123")
        age: Int @default(value: 18)
        email: String @unique
        status: EmployeeStatus @default(value: ACTIVE)
        createdAt: DateTime @createdAt
        updatedAt: DateTime @updatedAt
    }

    enum EmployeeStatus { ACTIVE INACTIVE }
    """

    with patch.object(generador_migracion.consola, "print"):
        resultado = generador_migracion.generar_migracion(
            esquema_anterior=esquema_anterior,
            esquema_nuevo=esquema_nuevo,
            visualizar_salida=True,
            visualizar_sql=True,
        )

    diferencias = resultado.diferencias

    assert "id" not in diferencias.tablas.campos["Employee"].agregados

    sql_generado = resultado.sql_generado
    assert "`id` VARCHAR(25) NOT NULL PRIMARY KEY" in sql_generado
    assert "`email` VARCHAR(255) UNIQUE" in sql_generado
    assert "`name` VARCHAR(255) NOT NULL DEFAULT 'emp_123'" in sql_generado
    assert "`age` INT DEFAULT 18" in sql_generado
    assert "ENUM('ACTIVE', 'INACTIVE') DEFAULT 'ACTIVE'" in sql_generado
