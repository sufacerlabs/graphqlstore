"""Pruebas para la migración PostgreSQL"""

from unittest.mock import patch
import pytest
from source.cli.graphql.configuracion_y_constantes import (
    InfoDiffCampos,
    InfoDiffEsquema,
    InfoDirectiva,
    InfoField,
    InfoMigracion,
    OnDelete,
    TipoLink,
    TipoRelacion,
)
from source.cli.graphql.exceptions import (
    GraphQLStoreError,
    MigrationError,
    MigrationGenerationError,
)
from source.cli.generators.migration import PostgreSQLMigrationGenerator


def test_inicializacion_pg_generator_migra(pg_generator_migra):
    """Prueba la inicialización correcta del generador PostgreSQL."""
    assert isinstance(pg_generator_migra, PostgreSQLMigrationGenerator)
    assert pg_generator_migra.console is not None
    assert pg_generator_migra.migrations_sql == []
    assert pg_generator_migra.parser is not None
    assert pg_generator_migra.print_output is True
    assert pg_generator_migra.print_sql is True


def test_generar_migracion_sin_cambios(
    pg_generator_migra,
    prev_schema_01,
):
    """Prueba generación cuando no hay cambios."""
    with patch.object(pg_generator_migra, "diff_schemas") as mock_diff:
        mock_diff.return_value = InfoDiffEsquema()

        with patch.object(pg_generator_migra.console, "print") as mock_print:
            resultado = pg_generator_migra.generate_migration(
                previous_schema=prev_schema_01,
                new_schema=prev_schema_01,
                print_output=True,
            )

    assert isinstance(resultado, InfoMigracion)
    assert resultado.sql_generado == ""
    assert not resultado.diferencias.tiene_cambios()

    assert mock_print.called
    assert "No changes detected between schemas" in mock_print.call_args[0][0]


@patch.object(PostgreSQLMigrationGenerator, "diff_schemas")
@patch.object(PostgreSQLMigrationGenerator, "generate_sql_migration")
def test_generar_migracion_exitosa(
    mock_generar_sql,
    mock_diff_esquemas,
    pg_generator_migra,
    prev_schema_01,
    new_schema_01,
    simple_differences,
):
    """Prueba generación exitosa de migración."""
    mock_diff_esquemas.return_value = simple_differences
    mock_generar_sql.return_value = "CREATE TABLE Post (id VARCHAR(25));"

    with patch.object(pg_generator_migra.console, "print") as mock_print:
        resultado = pg_generator_migra.generate_migration(
            previous_schema=prev_schema_01,
            new_schema=new_schema_01,
            print_output=True,
            print_sql=False,
        )

    assert isinstance(resultado, InfoMigracion)
    assert resultado.esquema_anterior == prev_schema_01
    assert resultado.esquema_nuevo == new_schema_01
    assert resultado.diferencias == simple_differences
    assert "CREATE TABLE" in resultado.sql_generado
    assert resultado.id_migracion.startswith("migration_")

    mock_diff_esquemas.assert_called_once_with(prev_schema_01, new_schema_01)
    mock_generar_sql.assert_called_once_with(simple_differences)

    assert mock_print.call_count == 3

    args = mock_print.call_args_list
    assert "Generating migration" in args[0][0][0]
    assert "Migration generated successfully" in args[1][0][0]
    assert "Total SQL statements: 2" in args[2][0][0]


def test_generar_migracion_con_id_personalizado(
    pg_generator_migra,
    prev_schema_01,
    new_schema_01,
):
    """Prueba generación con ID personalizado."""
    id_personalizado = "migration_custom_postgresql_123"

    with patch.object(pg_generator_migra, "diff_schemas") as mock_diff:
        mock_diff.return_value = InfoDiffEsquema()

        resultado = pg_generator_migra.generate_migration(
            previous_schema=prev_schema_01,
            new_schema=new_schema_01,
            migration_id=id_personalizado,
            print_output=False,
        )

        assert resultado.id_migracion == id_personalizado


def test_generar_migracion_error_comparacion(
    pg_generator_migra,
    prev_schema_01,
):
    """Prueba manejo de errores en comparación."""
    esquema_invalido = "invalid graphql syntax {"

    with pytest.raises(MigrationError):
        pg_generator_migra.generate_migration(
            previous_schema=prev_schema_01,
            new_schema=esquema_invalido,
            print_output=False,
        )


def test_generar_migracion_procesar_relaciones(
    pg_generator_migra,
    prev_schema_02,
    new_schema_02,
):
    """Prueba generación de migración con procesamiento de relaciones."""
    # pylint: disable=protected-access
    pg_generator_migra._available_enums = {}
    # pylint: enable=protected-access

    with patch.object(pg_generator_migra.console, "print"):
        resultado = pg_generator_migra.generate_migration(
            previous_schema=prev_schema_02,
            new_schema=new_schema_02,
            print_output=False,
            print_sql=False,
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

    # PostgreSQL no usa backticks
    assert "user_id" in sql_generado or "user_A" in sql_generado
    assert "role_id" in sql_generado or "role_B" in sql_generado
    assert "post_id" in sql_generado or "post_A" in sql_generado
    assert "tag_id" in sql_generado or "tag_B" in sql_generado


def test_generar_migracion_relaciones_eliminadas(
    pg_generator_migra,
    prev_schema_03,
    new_schema_03,
):
    """Prueba generación de migración cuando se eliminan relaciones."""

    with patch.object(pg_generator_migra.console, "print"):
        resultado = pg_generator_migra.generate_migration(
            previous_schema=prev_schema_03,
            new_schema=new_schema_03,
            print_output=False,
            print_sql=False,
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
    assert "DROP TABLE IF EXISTS UserRoles" in sql_generado
    assert "DROP COLUMN user_id" in sql_generado


def test_generar_migracion_relaciones_one_to_one_cascade(
    pg_generator_migra,
    prev_schema_04,
    new_schema_04,
):
    """Prueba generación de migración con relaciones one-to-one."""

    with patch.object(pg_generator_migra.console, "print"):
        resultado = pg_generator_migra.generate_migration(
            previous_schema=prev_schema_04,
            new_schema=new_schema_04,
            print_output=False,
            print_sql=False,
        )

    diferencias = resultado.diferencias

    relacion = diferencias.relaciones.agregadas[0]
    assert relacion.tipo_relation == TipoRelacion.ONE_TO_ONE.value
    assert relacion.nombre_relacion == "UserProfile"

    sql_generado = resultado.sql_generado
    assert "UNIQUE" in sql_generado


def test_generar_migracion_relaciones_one_cascade_to_one(
    pg_generator_migra,
    prev_schema_05,
    new_schema_05,
):
    """Prueba generación de migración con relaciones one-to-one con CASCADE."""

    with patch.object(pg_generator_migra.console, "print"):
        resultado = pg_generator_migra.generate_migration(
            previous_schema=prev_schema_05,
            new_schema=new_schema_05,
            print_output=False,
            print_sql=False,
        )

    sql_generado = resultado.sql_generado
    assert "ON DELETE CASCADE" in sql_generado


def test_generar_migracion_relaciones_one_to_one_set_null(
    pg_generator_migra,
    prev_schema_06,
    new_schema_06,
):
    """Prueba generación de migración con relaciones 1:1 con SET NULL."""

    with patch.object(pg_generator_migra.console, "print"):
        resultado = pg_generator_migra.generate_migration(
            previous_schema=prev_schema_06,
            new_schema=new_schema_06,
            print_output=False,
            print_sql=False,
        )

    sql_generado = resultado.sql_generado
    assert "ON DELETE SET NULL" in sql_generado


@pytest.mark.parametrize(
    "prev_schema, new_schema",
    [("prev_schema_07", "new_schema_07")],
)
def test_generar_migracion_relaciones_one_to_many(
    request,
    prev_schema,
    new_schema,
    pg_generator_migra,
):
    """Prueba generación de migración con relaciones one-to-many."""

    prev_schema_fixture = request.getfixturevalue(prev_schema)
    new_schema_fixture = request.getfixturevalue(new_schema)

    with patch.object(pg_generator_migra.console, "print"):
        resultado = pg_generator_migra.generate_migration(
            previous_schema=prev_schema_fixture,
            new_schema=new_schema_fixture,
            print_output=False,
            print_sql=False,
        )

    sql_generado = resultado.sql_generado
    assert 'REFERENCES "User"(id)' in sql_generado


def test_diff_esquemas_procesar_relaciones_auto_relacion(
    pg_generator_migra,
    prev_schema_08,
    new_schema_08,
):
    """Prueba procesamiento de auto-relaciones (self-referencing)."""

    diferencias = pg_generator_migra.diff_schemas(
        previous_schema=prev_schema_08,
        new_schema=new_schema_08,
    )

    assert len(diferencias.relaciones.agregadas) == 1

    relacion = diferencias.relaciones.agregadas[0]
    assert relacion.fuente.tabla_fuente == "Category"
    assert relacion.objetivo.tabla_objetivo == "Category"
    assert relacion.tipo_relation == TipoRelacion.MANY_TO_MANY.value


def test_diff_esquemas_relaciones_con_diferentes_on_delete(
    pg_generator_migra,
    prev_schema_09,
    new_schema_09,
):
    """Prueba procesamiento de relaciones con diferentes políticas onDelete."""

    diferencias = pg_generator_migra.diff_schemas(
        previous_schema=prev_schema_09,
        new_schema=new_schema_09,
    )

    assert len(diferencias.relaciones.agregadas) == 1

    relacion = diferencias.relaciones.agregadas[0]
    assert relacion.fuente.on_delete == OnDelete.SET_NULL.name
    assert relacion.objetivo.on_delete_inverso == OnDelete.CASCADE.value


def test_generar_migracion_eliminar_campos(
    pg_generator_migra,
    prev_schema_10,
    new_schema_10,
):
    """Prueba generación de migración con eliminación de campos."""

    with patch.object(pg_generator_migra.console, "print"):
        resultado = pg_generator_migra.generate_migration(
            previous_schema=prev_schema_10,
            new_schema=new_schema_10,
            print_output=False,
            print_sql=False,
        )

    diferencias = resultado.diferencias

    campos_eliminados = [
        campo.nombre for campo in diferencias.tablas.campos["User"].eliminados
    ]
    assert "email" in campos_eliminados

    sql_generado = resultado.sql_generado
    assert "DROP COLUMN email" in sql_generado


def test_generar_migracion_agregar_campos(
    pg_generator_migra,
    prev_schema_11,
    new_schema_11,
):
    """Prueba generación de migración con agregado de campos."""

    with patch.object(pg_generator_migra.console, "print"):
        resultado = pg_generator_migra.generate_migration(
            previous_schema=prev_schema_11,
            new_schema=new_schema_11,
            print_output=False,
            print_sql=False,
        )

    diferencias = resultado.diferencias

    campos_agregados = [
        campo.nombre for campo in diferencias.tablas.campos["User"].agregados
    ]
    assert "age" in campos_agregados

    sql_generado = resultado.sql_generado
    assert "ADD COLUMN age INT" in sql_generado


def test_generar_migracion_modificar_campos(
    pg_generator_migra,
    prev_schema_12,
    new_schema_12,
):
    """Prueba generación de migración con modificación de campos."""
    with patch.object(pg_generator_migra.console, "print"):
        resultado = pg_generator_migra.generate_migration(
            previous_schema=prev_schema_12,
            new_schema=new_schema_12,
            print_output=False,
            print_sql=False,
        )

    diferencias = resultado.diferencias

    cambios_email = diferencias.tablas.campos["User"].modificados[0]
    assert cambios_email.nombre == "email"
    assert cambios_email.info_antigua.es_requerido is False
    assert cambios_email.info_nueva.es_requerido is True

    sql_generado = resultado.sql_generado
    assert "SET NOT NULL" in sql_generado


def test_generar_migracion_modificar_enum(
    pg_generator_migra,
    prev_schema_13,
    new_schema_13,
):
    """Prueba generación de migración con modificación de enums."""

    with patch.object(pg_generator_migra.console, "print"):
        resultado = pg_generator_migra.generate_migration(
            previous_schema=prev_schema_13,
            new_schema=new_schema_13,
            print_output=True,
            print_sql=True,
        )

    diferencias = resultado.diferencias

    assert len(diferencias.enums.modificados) == 1

    cambio_enum = diferencias.enums.modificados[0]
    assert cambio_enum.nombre == "UserStatus"
    assert cambio_enum.valores_antiguos == ["ACTIVE", "INACTIVE"]
    assert cambio_enum.valores_nuevos == ["ACTIVE", "INACTIVE", "PENDING"]

    sql_generado = resultado.sql_generado
    # PostgreSQL usa un proceso más complejo para modificar enums
    assert "CREATE TYPE UserStatus_enum_new" in sql_generado
    assert "RENAME TO UserStatus_enum" in sql_generado


def test_generar_migracion_nuevo_enum(
    pg_generator_migra,
    prev_schema_14,
    new_schema_14,
):
    """Prueba generación de migración con un nuevo enum agregado."""

    with patch.object(pg_generator_migra.console, "print"):
        resultado = pg_generator_migra.generate_migration(
            previous_schema=prev_schema_14,
            new_schema=new_schema_14,
            print_output=False,
            print_sql=False,
        )

    diferencias = resultado.diferencias

    assert len(diferencias.enums.agregados) == 1

    nuevo_enum = diferencias.enums.agregados[0]
    assert nuevo_enum.nombre == "UserStatus"
    assert set(nuevo_enum.valores) == {"ACTIVE", "INACTIVE"}

    sql_generado = resultado.sql_generado
    assert "CREATE TYPE UserStatus_enum" in sql_generado
    assert "ADD COLUMN status UserStatus_enum" in sql_generado


def test_generar_migracion_eliminar_enum(
    pg_generator_migra,
    prev_schema_15,
    new_schema_15,
):
    """Prueba generación de migración con eliminación de enums."""

    with patch.object(pg_generator_migra.console, "print"):
        resultado = pg_generator_migra.generate_migration(
            previous_schema=prev_schema_15,
            new_schema=new_schema_15,
            print_output=False,
            print_sql=False,
        )

    diferencias = resultado.diferencias

    assert len(diferencias.enums.eliminados) == 1
    assert "UserStatus" in diferencias.enums.eliminados

    sql_generado = resultado.sql_generado
    assert "DROP COLUMN status" in sql_generado


def test_generar_migracion_eliminar_tablas(
    pg_generator_migra,
    prev_schema_16,
    new_schema_16,
):
    """Prueba generación de migración con eliminación de tablas."""

    with patch.object(pg_generator_migra.console, "print"):
        resultado = pg_generator_migra.generate_migration(
            previous_schema=prev_schema_16,
            new_schema=new_schema_16,
            print_output=False,
            print_sql=False,
        )

    diferencias = resultado.diferencias

    assert "Post" in diferencias.tablas.eliminadas

    sql_generado = resultado.sql_generado
    assert "DROP TABLE IF EXISTS Post" in sql_generado


def test_generar_sql_migracion_error_metodo_privado(pg_generator_migra):
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
        pg_generator_migra,
        "_generate_sql_create_table",
        side_effect=GraphQLStoreError("Error for create table"),
    ):
        with pytest.raises(MigrationGenerationError) as exc_info:
            pg_generator_migra.generate_sql_migration(diferencias)

        assert "Error generating SQL: Error for create table" in str(
            exc_info.value,
        )


def test_generar_migracion_con_directivas_avanzadas(
    pg_generator_migra,
    prev_schema_17,
    new_schema_17,
):
    """Prueba generación de migración con directivas avanzadas PostgreSQL."""

    with patch.object(pg_generator_migra.console, "print"):
        resultado = pg_generator_migra.generate_migration(
            previous_schema=prev_schema_17,
            new_schema=new_schema_17,
            print_output=True,
            print_sql=True,
        )

    diferencias = resultado.diferencias

    # Verificar que no se agregó ID manualmente
    campos_agregados = [
        fld.nombre for fld in diferencias.tablas.campos["Employee"].agregados
    ]
    assert "id" not in campos_agregados

    sql_generado = resultado.sql_generado
    # PostgreSQL debería agregar ID automáticamente
    assert "id VARCHAR(25) NOT NULL PRIMARY KEY" in sql_generado
    assert "email VARCHAR(255) UNIQUE" in sql_generado
    assert "name VARCHAR(255) NOT NULL DEFAULT 'emp_123'" in sql_generado
    assert "age INT DEFAULT 18" in sql_generado
    assert "status EmployeeStatus_enum DEFAULT 'CONTRACTED'" in sql_generado
    assert "CREATE TYPE EmployeeStatus_enum" in sql_generado


def test_generar_migracion_campos_jsonb(
    pg_generator_migra,
):
    """Prueba generación de migración con campos JSONB en PostgreSQL."""

    prev_schema_01 = """
    type User {
        id: ID! @id
        name: String!
    }
    """

    new_schema_01 = """
    type User {
        id: ID! @id
        name: String!
        tags: [String]
        scores: [Int]
    }
    """

    with patch.object(pg_generator_migra.console, "print"):
        resultado = pg_generator_migra.generate_migration(
            previous_schema=prev_schema_01,
            new_schema=new_schema_01,
            print_output=False,
            print_sql=False,
        )

    sql_generado = resultado.sql_generado
    # Los campos de lista en PostgreSQL se mapean a JSONB
    assert "tags JSONB" in sql_generado
    assert "scores JSONB" in sql_generado


def test_generar_migracion_enum_con_valor_por_defecto_invalido(
    pg_generator_migra,
):
    """Test handling of error with invalid enum default value."""

    prev_schema_01 = """
    enum UserStatus {
        ACTIVE
        INACTIVE
        PENDING
    }

    type User {
        id: ID! @id
        status: UserStatus @default(value: PENDING)
    }
    """

    new_schema_01 = """
    enum UserStatus {
        ACTIVE
        INACTIVE
    }

    type User {
        id: ID! @id
        status: UserStatus @default(value: PENDING)
    }
    """

    with pytest.raises(MigrationError) as exc_info:
        pg_generator_migra.generate_migration(
            previous_schema=prev_schema_01,
            new_schema=new_schema_01,
            print_output=False,
        )

    assert "Default value 'PENDING'" in str(exc_info.value)
    assert "is not valid for the new enum type" in str(exc_info.value)


def test_generar_migracion_junction_table_postgresql(
    pg_generator_migra,
    prev_schema_18,
    new_schema_18,
):
    """Test handling of junction tables in PostgreSQL."""

    with patch.object(pg_generator_migra.console, "print"):
        resultado = pg_generator_migra.generate_migration(
            previous_schema=prev_schema_18,
            new_schema=new_schema_18,
            print_output=False,
            print_sql=False,
        )

    sql_generado = resultado.sql_generado
    assert "CREATE TABLE IF NOT EXISTS UserRoles" in sql_generado
    assert "user_id VARCHAR(25) NOT NULL" in sql_generado
    assert "role_id VARCHAR(25) NOT NULL" in sql_generado
    assert "PRIMARY KEY(user_id, role_id)" in sql_generado
    assert "ON DELETE CASCADE" in sql_generado
    assert "ON DELETE SET NULL" in sql_generado


def test_get_sql_type_postgresql_specific(pg_generator_migra):
    """Test the mapping of PostgreSQL-specific types."""

    # Test basic types
    field_string = InfoField(
        nombre="test",
        tipo_campo="String",
        es_lista=False,
        es_requerido=True,
        directivas={},
    )

    # pylint: disable=protected-access
    pg_generator_migra._available_enums = {}
    # pylint: enable=protected-access

    assert pg_generator_migra.get_sql_type(field_string) == "VARCHAR(255)"


def test_generar_migracion_rename_column_postgresql(
    pg_generator_migra,
    prev_schema_19,
    new_schema_19,
):
    """Test generation with column renaming using @db(rename)."""

    with patch.object(pg_generator_migra.console, "print"):
        resultado = pg_generator_migra.generate_migration(
            previous_schema=prev_schema_19,
            new_schema=new_schema_19,
            print_output=False,
            print_sql=False,
        )

    sql_generado = resultado.sql_generado
    # Debería renombrar la columna existente
    assert "DROP COLUMN name" in sql_generado
    assert "ADD COLUMN full_name" in sql_generado


def test_generar_migracion_updatedat_createdat_postgresql(
    pg_generator_migra,
    prev_schema_20,
    new_schema_20,
):
    """Test handling of @createdAt and @updatedAt directives in PostgreSQL."""

    with patch.object(pg_generator_migra.console, "print"):
        resultado = pg_generator_migra.generate_migration(
            previous_schema=prev_schema_20,
            new_schema=new_schema_20,
            print_output=False,
            print_sql=False,
        )

    sql_generado = resultado.sql_generado
    # PostgreSQL use CURRENT_TIMESTAMP for both cases (without ON UPDATE)
    assert "createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP" in sql_generado
    assert "updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP" in sql_generado


def test_generate_migration_change_enum_type(
    pg_generator_migra,
    prev_schema_21,
    new_schema_21,
):
    """Test changing enum type in PostgreSQL migration."""

    with patch.object(pg_generator_migra.console, "print"):
        resultado = pg_generator_migra.generate_migration(
            previous_schema=prev_schema_21,
            new_schema=new_schema_21,
            print_output=False,
            print_sql=False,
        )

    sql_generado = resultado.sql_generado
    # PostgreSQL requires creating a new enum type and updating the column
    assert "CREATE TYPE RoleUser_enum" in sql_generado
    assert "ALTER COLUMN role TYPE RoleUser_enum" in sql_generado


def test_generate_migration_change_unique_constraint(
    pg_generator_migra,
    prev_schema_22,
    new_schema_22,
):
    """Test adding and removing unique constraints in PostgreSQL migration."""

    with patch.object(pg_generator_migra.console, "print"):
        resultado = pg_generator_migra.generate_migration(
            previous_schema=prev_schema_22,
            new_schema=new_schema_22,
            print_output=False,
            print_sql=False,
        )

    sql_generado = resultado.sql_generado
    assert "ADD CONSTRAINT token_unique UNIQUE (token)" in sql_generado
    assert "DROP CONSTRAINT IF EXISTS code_unique" in sql_generado
