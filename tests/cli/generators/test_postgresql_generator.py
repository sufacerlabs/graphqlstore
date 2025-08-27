"""Tests for the PostgreSQL schema generator."""

from unittest.mock import patch

from source.cli.generators.postgresql_generator import (
    GeneratorSchemaPostgreSQL,
)
from source.cli.graphql.configuracion_y_constantes import (
    DatabaseType,
    InfoDirectiva,
    InfoField,
    InfoTabla,
    TipoField,
)


def test_init_success(generator_postgres):
    """Test successful initialization of GeneratorSchemaPostgreSQL."""
    assert isinstance(generator_postgres, GeneratorSchemaPostgreSQL)
    assert generator_postgres.console is not None
    assert generator_postgres.schema_sql == []
    assert generator_postgres.print_output is None
    assert generator_postgres.print_sql is None


def test_database_type(generator_postgres):
    """Test that the database type is correctly identified as PostgreSQL."""
    assert generator_postgres.get_database_type() == DatabaseType.POSTGRESQL


def test_type_mapping(generator_postgres):
    """Test the type mapping for PostgreSQL."""
    mapping = generator_postgres.get_type_mapping()
    assert mapping[TipoField.ID.value] == "VARCHAR(25)"
    assert mapping[TipoField.STRING.value] == "VARCHAR(255)"
    assert mapping[TipoField.INT.value] == "INTEGER"
    assert mapping[TipoField.FLOAT.value] == "DECIMAL(10, 2)"
    assert mapping[TipoField.BOOLEAN.value] == "BOOLEAN"
    assert mapping[TipoField.DATETIME.value] == "TIMESTAMP"
    assert mapping[TipoField.JSON.value] == "JSONB"


def test_engine_specific_settings(generator_postgres):
    """Test engine specific settings - PostgreSQL doesn't \
        need ENGINE definition."""
    assert generator_postgres.get_engine_specific_settings() == ""


def test_primary_key_column(generator_postgres):
    """Test that the primary key column is generated correctly."""
    primary_key = generator_postgres.get_primary_key_column()
    assert primary_key == "id VARCHAR(25) NOT NULL PRIMARY KEY"


def test_get_schema_sql(generator_postgres):
    """Test that the schema SQL is returned correctly."""
    generator_postgres.schema_sql = [
        "CREATE TABLE User (id VARCHAR(25) PRIMARY KEY, name VARCHAR(255));",
        "CREATE TABLE Post (id VARCHAR(25) PRIMARY KEY);",
    ]

    sql = generator_postgres.get_schema_sql()
    assert isinstance(sql, str)
    assert "CREATE TABLE User" in sql
    assert "CREATE TABLE Post" in sql
    assert len(sql.split("\n")) == 3  # 2 tables + 1 empty line


def test_enum_type_generation(generator_postgres, basic_enums):
    """Test enum type generation which is different in PostgreSQL."""
    with patch.object(generator_postgres.console, "print"):
        sql = generator_postgres.generate_schema(
            tables={},
            enums=basic_enums,
            relationships=[],
            print_output=False,
            print_sql=False,
        )

    assert "CREATE TYPE UserStatus_enum AS ENUM('ACTIVE'," in sql


def test_generate_schema_with_advanced_directives(
    generator_postgres,
    simple_tables,
    basic_enums,
):
    """Test schema generation with advanced directives."""
    with patch.object(generator_postgres.console, "print") as mock_print:
        sql = generator_postgres.generate_schema(
            tables=simple_tables,
            enums=basic_enums,
            relationships=[],
            print_output=True,
            print_sql=True,
        )

    assert "CREATE TYPE UserStatus_enum AS ENUM" in sql
    assert 'CREATE TABLE "User"' in sql
    assert "name VARCHAR(255) NOT NULL DEFAULT 'Anonymous'" in sql
    assert "hashtags JSONB NOT NULL" in sql
    assert "age INTEGER DEFAULT 18" in sql
    assert "CONSTRAINT uk_email UNIQUE (email)" in sql
    assert mock_print.called


def test_generate_schema_many_to_many(
    generator_postgres,
    table_with_many_to_many_relation,
    many_to_many_relation,
):
    """Test schema generation with many-to-many relationship."""
    with patch.object(generator_postgres.console, "print"):
        sql = generator_postgres.generate_schema(
            tables=table_with_many_to_many_relation,
            enums={},
            relationships=many_to_many_relation,
            print_output=False,
            print_sql=False,
        )

    assert 'CREATE TABLE "UserRoles"' in sql
    assert "PRIMARY KEY (user_id, role_id)" in sql
    assert "CONSTRAINT fk_User_roles_Role FOREIGN KEY" in sql
    assert "ON DELETE SET NULL" in sql
    assert "CONSTRAINT fk_Role_users_User FOREIGN KEY" in sql


def test_generate_schema_many_to_one(
    generator_postgres,
    table_with_many_to_one_relation,
    many_to_one_relation,
):
    """Test schema generation with many-to-one relationship."""
    with patch.object(generator_postgres.console, "print"):
        sql = generator_postgres.generate_schema(
            tables=table_with_many_to_one_relation,
            enums={},
            relationships=many_to_one_relation,
            print_output=False,
            print_sql=False,
        )

    assert 'ALTER TABLE "Post"' in sql
    assert "ADD COLUMN user_id VARCHAR(25)" in sql
    assert (
        "ADD CONSTRAINT fk_User_posts_Post FOREIGN KEY (user_id) "
        'REFERENCES "User"(id) ON DELETE CASCADE'
    ) in sql


def test_one_to_one_with_source_cascade(
    generator_postgres,
    one_to_one_relation_with_cascade_source,
):
    """Test schema generation with one-to-one relationship \
        with source CASCADE."""
    # Set up test tables
    tables = {
        "User": InfoTabla(
            nombre="User",
            campos={
                "id": InfoField(
                    nombre="id",
                    tipo_campo="ID",
                    es_lista=False,
                    es_requerido=True,
                    directivas={"id": InfoDirectiva("id", {})},
                ),
                "profile": InfoField(
                    nombre="profile",
                    tipo_campo="Profile",
                    es_lista=False,
                    es_requerido=True,
                    directivas={
                        "relation": InfoDirectiva(
                            "relation",
                            {
                                "name": "UserProfile",
                                "onDelete": "CASCADE",
                            },
                        )
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
                    directivas={"id": InfoDirectiva("id", {})},
                ),
                "user": InfoField(
                    nombre="user",
                    tipo_campo="User",
                    es_lista=False,
                    es_requerido=False,
                    directivas={
                        "relation": InfoDirectiva(
                            "relation",
                            {
                                "name": "UserProfile",
                                "onDelete": "SET_NULL",
                            },
                        )
                    },
                ),
            },
        ),
    }

    with patch.object(generator_postgres.console, "print"):
        sql = generator_postgres.generate_schema(
            tables=tables,
            enums={},
            relationships=one_to_one_relation_with_cascade_source,
            print_output=False,
            print_sql=False,
        )

    # In PostgreSQL with CASCADE on source, the source table gets the FK
    assert 'ALTER TABLE "User"' in sql
    assert (
        "ADD CONSTRAINT fk_User_profile_Profile FOREIGN KEY (user_id) "
        'REFERENCES "Profile"(id) ON DELETE CASCADE;'
    ) in sql


def test_get_empty_postgres_schema(generator_postgres):
    """Test generating an empty PostgreSQL schema."""
    sql = generator_postgres.generate_schema({}, {}, [])
    assert isinstance(sql, str)
    assert sql == "\n\n"


def test_generate_schema_with_self_relation(
    generator_postgres, self_relation, table_with_self_relations
):
    """Test schema generation with self relationship"""
    with patch.object(generator_postgres.console, "print"):
        sql = generator_postgres.generate_schema(
            relationships=self_relation,
            tables=table_with_self_relations,
            enums={},
        )
    assert 'CREATE TABLE "UserToFriends"' in sql
    assert "PRIMARY KEY (user_A, user_B)" in sql
    assert "CONSTRAINT fk_User_friends_User_friends" in sql
    assert 'Y (user_A) REFERENCES "User"(id) ON DELETE CASCADE' in sql
    assert "CONSTRAINT fk_User_friends_User" in sql
    assert 'Y (user_B) REFERENCES "User"(id) ON DELETE CASCADE' in sql


def test_generar_esquema_otm(
    generator_postgres,
    table_with_one_to_many_relation,
    one_to_many_relation,
):
    """Test the complete generation of the schema with 1:N relationship."""
    with patch.object(generator_postgres.console, "print"):
        sql = generator_postgres.generate_schema(
            tables=table_with_one_to_many_relation,
            enums={},
            relationships=one_to_many_relation,
            print_output=False,
            print_sql=False,
        )

    assert 'CREATE TABLE "Product"' in sql
    assert 'CREATE TABLE "ProductType"' in sql
    assert 'ALTER TABLE "Product"' in sql
    assert "ADD COLUMN productType_id VARCHAR(25)" in sql
    assert (
        "ADD CONSTRAINT fk_Product_productType_ProductType FOREIGN KEY "
        '(productType_id) REFERENCES "ProductType"(id) ON DELETE CASCADE;'
    ) in sql


def test_generar_esquema_oto(
    generator_postgres,
    table_with_one_to_one_relation,
    basic_enums,
    one_to_one_relation,
):
    """Prueba la generacion completa del esquema con rel 1:1."""
    with patch.object(generator_postgres.console, "print"):
        sql = generator_postgres.generate_schema(
            tables=table_with_one_to_one_relation,
            enums=basic_enums,
            relationships=one_to_one_relation,
            print_output=False,
            print_sql=False,
        )
    assert 'ALTER TABLE "Profile"' in sql
    assert "status UserStatus_enum" in sql
    assert (
        "ADD CONSTRAINT fk_User_profile_Profile FOREIGN KEY (user_id) "
        'REFERENCES "User"(id) ON DELETE CASCADE;'
    ) in sql
