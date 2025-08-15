"""Integration tests for the database schema generator system."""

from typing import Dict, List

import pytest

from source.cli.generators.generator_db_schema import GeneratorDBSchema
from source.cli.graphql.configuracion_y_constantes import (
    DatabaseType,
    FuenteRelacion,
    InfoDirectiva,
    InfoEnum,
    InfoField,
    InfoRelacion,
    InfoTabla,
    ObjetivoRelacion,
    TipoLink,
    TipoRelacion,
)


class TestGeneratorDBSchemaIntegration:
    """Integration tests for the GeneratorDBSchema with actual implementations.

    Tests the integration between different components of the system.
    """

    @pytest.fixture
    def sample_data(
        self,
    ) -> tuple[Dict[str, InfoTabla], Dict[str, InfoEnum], List[InfoRelacion]]:
        """Create sample test data for schema generation."""
        # Create a simple enum
        enums = {
            "UserRole": InfoEnum(nombre="UserRole", valores=["ADMIN", "USER"]),
        }

        # Create simple tables
        tablas = {
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
                    "name": InfoField(
                        nombre="name",
                        tipo_campo="String",
                        es_lista=False,
                        es_requerido=True,
                        directivas={},
                    ),
                    "role": InfoField(
                        nombre="role",
                        tipo_campo="UserRole",
                        es_lista=False,
                        es_requerido=True,
                        directivas={},
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
                        directivas={"id": InfoDirectiva("id", {})},
                    ),
                    "title": InfoField(
                        nombre="title",
                        tipo_campo="String",
                        es_lista=False,
                        es_requerido=True,
                        directivas={},
                    ),
                },
            ),
        }

        # Create a simple relationship
        relaciones = [
            InfoRelacion(
                fuente=FuenteRelacion(
                    tabla_fuente="User",
                    campo_fuente="posts",
                    fuente_es_lista=True,
                    nombre_constraint_fuente="fk_user_posts",
                    on_delete="CASCADE",
                ),
                objetivo=ObjetivoRelacion(
                    tabla_objetivo="Post",
                    campo_inverso="author",
                    nombre_constraint_objetivo="fk_post_author",
                    on_delete_inverso="SET_NULL",
                ),
                tipo_relation=TipoRelacion.ONE_TO_MANY.value,
                nombre_relacion="UserPosts",
                tipo_link=TipoLink.INLINE.value,
            )
        ]

        return tablas, enums, relaciones

    def test_mysql_generator_creates_valid_schema(self, sample_data):
        """Test that the MySQL generator creates a valid schema."""
        tables, enums, relationships = sample_data

        # Create a MySQL generator with output disabled for test
        generator = GeneratorDBSchema(DatabaseType.MYSQL)

        # Generate schema
        schema_sql = generator.generate_schema(
            tables, enums, relationships, print_output=False, print_sql=False
        )

        # Verify schema contains expected elements
        assert "CREATE TABLE User" in schema_sql
        assert "CREATE TABLE Post" in schema_sql
        assert "ENUM('ADMIN', 'USER')" in schema_sql
        assert "VARCHAR(25)" in schema_sql
        assert "ENGINE=InnoDB DEFAULT CHARSET=utf8mb4" in schema_sql
        assert "FOREIGN KEY" in schema_sql

    # def test_postgresql_generator_creates_valid_schema(self, sample_data):
    #     """Test that the PostgreSQL generator creates a valid schema."""
    #     tables, enums, relationships = sample_data

    #     # Create a PostgreSQL generator with output disabled for test
    #     generator = GeneratorDBSchema(DatabaseType.POSTGRESQL)

    #     # Generate schema
    #     schema_sql = generator.generate_schema(
    #         tables, enums, relationships, print_output=False, print_sql=False
    #     )

    #     # Verify schema contains expected elements
    #     assert "CREATE TABLE User" in schema_sql
    #     assert "CREATE TABLE Post" in schema_sql

    #     # PostgreSQL handles enums differently
    #     assert "CREATE TYPE userrole_type AS ENUM" in schema_sql.lower()
    #     assert "VARCHAR(25)" in schema_sql

    #     # PostgreSQL doesn't have the ENGINE setting
    #     assert "ENGINE=InnoDB" not in schema_sql
    #     assert "FOREIGN KEY" in schema_sql

    # def test_generators_produce_different_schemas(self, sample_data):
    #     """Test that MySQL and PostgreSQL generators produce \
    #         different schemas."""
    #     tables, enums, relationships = sample_data

    #     # Create generators
    #     mysql_generator = GeneratorDBSchema(DatabaseType.MYSQL)
    #     pg_generator = GeneratorDBSchema(DatabaseType.POSTGRESQL)

    #     # Generate schemas
    #     mysql_schema = mysql_generator.generate_schema(
    #         tables, enums, relationships, print_output=False, print_sql=False
    #     )

    #     pg_schema = pg_generator.generate_schema(
    #         tables, enums, relationships, print_output=False, print_sql=False
    #     )

    #     # Verify schemas are different
    #     assert mysql_schema != pg_schema

    #     # MySQL specific content
    #     assert "ENGINE=InnoDB" in mysql_schema
    #     assert "ENGINE=InnoDB" not in pg_schema

    #     # PostgreSQL specific content
    #     assert "CREATE TYPE userrole_type" in pg_schema.lower()

    #     # Verify type mapping differences
    #     # MySQL uses BOOLEAN type
    #     if "BOOLEAN" in mysql_schema and "BOOLEAN" in pg_schema:
    #         # Both might use BOOLEAN so this isn't a reliable test
    #         pass
    #     # PostgreSQL uses different INT type
    #     elif "INTEGER" in pg_schema and "INT" in mysql_schema:
    #         assert "INTEGER" in pg_schema
    #         assert "INTEGER" not in mysql_schema
