"""Pruebas para ParserGraphQLEsquema"""

import pytest

# from graphql import GraphQLError
from source.cli.graphql import ParserGraphQLEsquema

from source.cli.graphql.configuracion_y_constantes import (
    InfoDirectiva,
    InfoParseEsquema,
    InfoTabla,
    TipoField,
)
from source.cli.graphql.exceptions import SchemaError


@pytest.fixture(name="parser")
def fix_parser():
    """Fixture que proporciona una instancia del parser."""
    return ParserGraphQLEsquema()


@pytest.fixture(name="esquema_simple")
def fix_esquema_simple():
    """Fixture con un esquema GraphQL simple."""
    return """
    type User {
        id: ID!
        name: String!
        email: String
        age: Int
        active: Boolean
    }
    """


@pytest.fixture(name="esquema_con_enum")
def fix_esquema_con_enum():
    """Fixture con un esquema GraphQL que incluye un enum."""
    return """
    type User {
        id: ID!
        name: String!
        role: UserRole!
    }

    enum UserRole {
        ADMIN
        USER
        GUEST
    }
    """


@pytest.fixture(name="esquema_con_directivas")
def fix_esquema_con_directivas():
    """Fixture con un esquema que incluye directivas."""
    return """
    type User {
        id: ID! @id
        name: String!
        email: String!
        createdAt: DateTime @createdAt
        updatedAt: DateTime @updatedAt
        isActive: Boolean @default(value: "true")
    }
    """


@pytest.fixture(name="esquema_con_relaciones")
def fix_esquema_con_relaciones():
    """Fixture con un esquema que incluye relaciones."""
    return """
    type User {
        id: ID!
        name: String!
        posts: [Post!]! @relation(name: "UserPosts")
    }

    type Post {
        id: ID!
        title: String!
        content: String
        author: User! @relation(name: "UserPosts", onDelete: CASCADE)
    }
    """


@pytest.fixture(name="esquema_complejo")
def fix_esquema_complejo():
    """Fixture con un esquema GraphQL más complejo."""
    return """
    type User {
        id: ID!
        name: String!
        email: String
        age: Int
        active: Boolean
        role: UserRole!
        posts: [Post!]! @relation(name: "UserPosts")
        users: [User!]! @relation(name: "UserFriends")
        houses: [House!]! @relation(name: "UserHouses", link: TABLE)
        createdAt: DateTime @createdAt
        updatedAt: DateTime @updatedAt
    }

    type Post {
        id: ID!
        title: String!
        content: String
        author: User! @relation(name: "UserPosts", onDelete: CASCADE)
        createdAt: DateTime @createdAt
        updatedAt: DateTime @updatedAt
    }

    type House {
        id: ID!
        address: String!
        owners: [User!]! @relation(name: "UserHouses", link: TABLE)
        createdAt: DateTime @createdAt
        updatedAt: DateTime @updatedAt
    }

    enum UserRole {
        ADMIN
        USER
        GUEST
    }
    """


@pytest.fixture(name="esquema_con_excluidos")
def fix_esquema_con_excluidos():
    """Fixture con un esquema GraphQL que incluye tipos excluidos."""
    return """
    type Query {
        users: [User!]!
        user(id: ID!): User
    }

    type Mutation {
        createUser(name: String!, email: String!): User!
        updateUser(id: ID!, name: String, email: String): User
        deleteUser(id: ID!): Boolean
    }

    type Subscription {
        userCreated: User!
        userUpdated: User!
        userDeleted: ID!
    }

    type User {
        id: ID!
        name: String!
        emai: String
        createdAt: DateTime @createdAt
        updatedAt: DateTime @updatedAt
    }
    """


def test_get_typo_mapping(parser):
    """Prueba que el mapeo de tipos se obtiene correctamente."""
    mapping = parser.get_type_mapping()

    assert isinstance(mapping, dict)
    assert mapping[TipoField.ID.value] == "VARCHAR(25)"
    assert mapping[TipoField.STRING.value] == "VARCHAR(255)"
    assert mapping[TipoField.INT.value] == "INT"
    assert mapping[TipoField.BOOLEAN.value] == "BOOLEAN"
    assert mapping[TipoField.DATETIME.value] == "DATETIME"
    assert mapping[TipoField.FLOAT.value] == "DECIMAL(10, 2)"
    assert mapping[TipoField.JSON.value] == "JSON"


def test_parse_esquema_simple(parser, esquema_simple):
    """Prueba que el parser procesa un esquema simple correctamente."""
    resultado = parser.parse_esquema(esquema_simple)

    assert isinstance(resultado, InfoParseEsquema)
    assert len(resultado.tablas) == 1
    assert len(resultado.enums) == 0

    # verificar la tabla User
    tabla_user = resultado.tablas["User"]
    assert isinstance(tabla_user, InfoTabla)
    assert tabla_user.nombre == "User"
    assert len(tabla_user.campos) == 5

    # verificar los campos de la tabla User
    assert "id" in tabla_user.campos
    assert "name" in tabla_user.campos
    assert "email" in tabla_user.campos
    assert "age" in tabla_user.campos
    assert "active" in tabla_user.campos


def test_parse_esquema_con_enum(parser, esquema_con_enum):
    """Prueba que el parser procesa un esquema con enum correctamente."""
    resultado = parser.parse_esquema(esquema_con_enum)

    assert len(resultado.enums) == 1

    # verificar el enum UserRole
    enum_user_role = resultado.enums["UserRole"]
    assert enum_user_role.nombre == "UserRole"
    assert enum_user_role.valores == ["ADMIN", "USER", "GUEST"]


def test_parse_esquema_con_directivas(parser, esquema_con_directivas):
    """Prueba que el parser procesa un esquema con directivas correctamente."""
    resultado = parser.parse_esquema(esquema_con_directivas)

    tabla_user = resultado.tablas["User"]

    # verificar las directivas en los campos
    campo_id = tabla_user.campos["id"]
    assert "id" in campo_id.directivas
    assert isinstance(campo_id.directivas["id"], InfoDirectiva)

    campo_created_at = tabla_user.campos["createdAt"]
    assert "createdAt" in campo_created_at.directivas

    campo_updated_at = tabla_user.campos["updatedAt"]
    assert "updatedAt" in campo_updated_at.directivas

    campo_is_active = tabla_user.campos["isActive"]
    assert "default" in campo_is_active.directivas
    directiva_default = campo_is_active.directivas["default"]
    assert directiva_default.argumentos["value"] == "true"


def test_parse_esquema_con_relaciones(parser, esquema_con_relaciones):
    """Prueba que el  parser procesa un esquema con relaciones \
        correctamente."""

    resultado = parser.parse_esquema(esquema_con_relaciones)

    tabla_user = resultado.tablas["User"]

    # verificar la tabla User y sus relaciones
    tabla_user = resultado.tablas["User"]
    campo_posts = tabla_user.campos["posts"]
    assert campo_posts.tipo_campo == "Post"
    assert campo_posts.es_lista is True
    assert campo_posts.es_requerido

    # verificar la tabla Post y su relación con User
    tabla_post = resultado.tablas["Post"]
    campo_author = tabla_post.campos["author"]
    assert campo_author.tipo_campo == "User"
    assert campo_author.es_lista is False
    assert campo_author.es_requerido is True


def test_parse_esquema_complejo(parser, esquema_complejo):
    """Prueba que el parser procesa un esquema complejo correctamente."""
    resultado = parser.parse_esquema(esquema_complejo)

    assert len(resultado.tablas) == 3
    assert len(resultado.enums) == 1

    # verificar tablas
    assert "User" in resultado.tablas
    assert "Post" in resultado.tablas
    assert "House" in resultado.tablas

    # verficar enums
    assert "UserRole" in resultado.enums

    # verificar directivas de las relaciones
    tabla_user = resultado.tablas["User"]

    # verificar la relación User -> Post
    campo_posts = tabla_user.campos["posts"]
    assert campo_posts.tipo_campo == "Post"
    assert campo_posts.es_lista is True
    assert campo_posts.es_requerido is True
    directiva_relacion = campo_posts.directivas["relation"]
    assert directiva_relacion.argumentos["name"] == "UserPosts"

    # verificar la relación User -> House
    campo_houses = tabla_user.campos["houses"]
    assert campo_houses.tipo_campo == "House"
    assert campo_houses.es_lista is True
    assert campo_houses.es_requerido is True
    directiva_relacion = campo_houses.directivas["relation"]
    assert directiva_relacion.argumentos["name"] == "UserHouses"
    assert directiva_relacion.argumentos["link"] == "TABLE"

    # verificar la relación inversa en Post
    tabla_post = resultado.tablas["Post"]

    # verificar la relación Post -> User
    campo_author = tabla_post.campos["author"]
    assert campo_author.tipo_campo == "User"
    assert campo_author.es_lista is False
    assert campo_author.es_requerido is True
    directiva_relacion = campo_author.directivas["relation"]
    assert directiva_relacion.argumentos["name"] == "UserPosts"
    assert directiva_relacion.argumentos["onDelete"] == "CASCADE"

    # verificar la relación House -> User
    tabla_house = resultado.tablas["House"]
    campo_owners = tabla_house.campos["owners"]
    assert campo_owners.tipo_campo == "User"
    assert campo_owners.es_lista is True
    assert campo_owners.es_requerido is True
    directiva_relacion = campo_owners.directivas["relation"]
    assert directiva_relacion.argumentos["name"] == "UserHouses"
    assert directiva_relacion.argumentos["link"] == "TABLE"


def test_parse_esquema_con_excluidos(parser, esquema_con_excluidos):
    """Prueba que el parser maneja tipos excluidos correctamente."""
    resultado = parser.parse_esquema(esquema_con_excluidos)

    # verificar que la tabla Query y Mutation no están en el resultado
    assert "Query" not in resultado.tablas
    assert "Mutation" not in resultado.tablas

    # verificar que la tabla Subscription no está en el resultado
    assert "Subscription" not in resultado.tablas

    # verificar que la tabla User se parsea correctamente
    assert "User" in resultado.tablas
    tabla_user = resultado.tablas["User"]
    assert len(tabla_user.campos) == 5


@pytest.mark.parametrize(
    "esquema_invalido",
    [
        "type User {id: ID!",
    ],
)
def test_parse_esquema_invalido(parser, esquema_invalido):
    """Prueba que el parser maneja errores de sintaxis \
        en el esquema."""

    with pytest.raises(SchemaError) as exc_info:
        parser.parse_esquema(esquema_invalido)

    assert "Error al parsear el esquema GraphQL" in str(exc_info.value)
