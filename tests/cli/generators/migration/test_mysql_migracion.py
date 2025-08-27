"""Pruebas para la migracion"""

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
from source.cli.generators.migration import MySQLMigrationGenerator


def test_inicializacion_mysql_generator_migra(mysql_generator_migra):
    """Prueba la inicialización correcta del generador."""
    assert isinstance(mysql_generator_migra, MySQLMigrationGenerator)
    assert mysql_generator_migra.console is not None
    assert mysql_generator_migra.migrations_sql == []
    assert mysql_generator_migra.parser is not None
    assert mysql_generator_migra.print_output is True
    assert mysql_generator_migra.print_sql is True


def test_generar_migracion_sin_cambios(
    mysql_generator_migra,
    prev_schema_01,
):
    """Prueba generación cuando no hay cambios."""
    with patch.object(mysql_generator_migra, "diff_schemas") as mock_diff:
        mock_diff.return_value = InfoDiffEsquema()

        # now mock console print
        with patch.object(
            mysql_generator_migra.console,
            "print",
        ) as mock_print:
            resultado = mysql_generator_migra.generate_migration(
                previous_schema=prev_schema_01,
                new_schema=prev_schema_01,
                print_output=True,
            )

    assert isinstance(resultado, InfoMigracion)
    assert resultado.sql_generado == ""
    assert not resultado.diferencias.tiene_cambios()

    assert mock_print.called
    assert "No changes detected between schemas" in mock_print.call_args[0][0]


@patch.object(MySQLMigrationGenerator, "diff_schemas")
@patch.object(MySQLMigrationGenerator, "generate_sql_migration")
def test_generar_migracion_exitosa(
    mock_generar_sql,
    mock_diff_esquemas,
    mysql_generator_migra,
    prev_schema_01,
    new_schema_01,
    simple_differences,
):
    """Prueba generación exitosa de migración."""
    # pylint: disable=too-many-arguments,too-many-positional-arguments

    mock_diff_esquemas.return_value = simple_differences
    mock_generar_sql.return_value = "CREATE TABLE Post (id VARCHAR(25));"

    with patch.object(mysql_generator_migra.console, "print") as mock_print:

        resultado = mysql_generator_migra.generate_migration(
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

    # verificar que se llamaron ambos prints
    assert mock_print.call_count == 3

    args = mock_print.call_args_list

    assert "Generating migration" in args[0][0][0]
    assert "Migration generated successfully" in args[1][0][0]
    assert "Total SQL statements: 2" in args[2][0][0]
    # pylint: enable=too-many-arguments,too-many-positional-arguments


def test_generar_migracion_con_id_personalizado(
    mysql_generator_migra,
    prev_schema_01,
    new_schema_01,
):
    """Prueba generación con ID personalizado."""
    id_personalizado = "migration_custom_test_123"

    with patch.object(mysql_generator_migra, "diff_schemas") as mock_diff:
        mock_diff.return_value = InfoDiffEsquema()

        resultado = mysql_generator_migra.generate_migration(
            previous_schema=prev_schema_01,
            new_schema=new_schema_01,
            migration_id=id_personalizado,
            print_output=False,
        )

        assert resultado.id_migracion == id_personalizado


def test_generar_migracion_error_comparacion(
    mysql_generator_migra,
    prev_schema_01,
):
    """Prueba manejo de errores en comparación."""
    esquema_invalido = "invalid graphql syntax {"

    with pytest.raises(MigrationError):
        mysql_generator_migra.generate_migration(
            previous_schema=prev_schema_01,
            new_schema=esquema_invalido,
            print_output=False,
        )


def test_generar_migracion_procesar_relaciones(
    mysql_generator_migra,
    prev_schema_02,
    new_schema_02,
):
    """Prueba generación de migración con procesamiento
    de relaciones completo."""
    # pylint: disable=protected-access
    mysql_generator_migra._available_enums = {}
    # pylint: enable=protected-access

    with patch.object(mysql_generator_migra.console, "print"):
        resultado = mysql_generator_migra.generate_migration(
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

    assert "user_id" in sql_generado or "user_A" in sql_generado
    assert "role_id" in sql_generado or "role_B" in sql_generado
    assert "post_id" in sql_generado or "post_A" in sql_generado
    assert "tag_id" in sql_generado or "tag_B" in sql_generado


def test_generar_migracion_relaciones_eliminadas(
    mysql_generator_migra,
    prev_schema_03,
    new_schema_03,
):
    """Prueba generación de migración cuando se eliminan relaciones."""

    with patch.object(mysql_generator_migra.console, "print"):
        resultado = mysql_generator_migra.generate_migration(
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
    assert "DROP FOREIGN KEY" in sql_generado or "DROP TABLE" in sql_generado


def test_generar_migracion_relaciones_one_to_one_cascade(
    mysql_generator_migra,
    prev_schema_04,
    new_schema_04,
):
    """Prueba generación de migración con relaciones one-to-one."""

    with patch.object(mysql_generator_migra.console, "print"):
        resultado = mysql_generator_migra.generate_migration(
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
    mysql_generator_migra,
    prev_schema_05,
    new_schema_05,
):
    """Prueba generación de migración con relaciones one-to-one con CASCADE."""

    with patch.object(mysql_generator_migra.console, "print"):
        resultado = mysql_generator_migra.generate_migration(
            previous_schema=prev_schema_05,
            new_schema=new_schema_05,
            print_output=False,
            print_sql=False,
        )

    sql_generado = resultado.sql_generado
    assert "ON DELETE CASCADE" in sql_generado


def test_generar_migracion_relaciones_one_to_one_set_null(
    mysql_generator_migra,
    prev_schema_06,
    new_schema_06,
):
    """Prueba generación de migración con relaciones
    one-to-one con SET NULL."""

    with patch.object(mysql_generator_migra.console, "print"):
        resultado = mysql_generator_migra.generate_migration(
            previous_schema=prev_schema_06,
            new_schema=new_schema_06,
            print_output=False,
            print_sql=False,
        )

    sql_generado = resultado.sql_generado
    assert "ON DELETE SET NULL" in sql_generado


@pytest.mark.parametrize(
    "prev_schema,new_schema",
    [
        ("prev_schema_07", "new_schema_07"),
        ("prev_schema_07", "new_schema_07b"),
    ],
)
def test_generate_migration_bidirectional_one_to_many_relation(
    request,
    prev_schema,
    new_schema,
    mysql_generator_migra,
):
    """Prueba generación de migración con relaciones one-to-many."""

    prev_schema_fixture = request.getfixturevalue(prev_schema)
    new_schema_fixture = request.getfixturevalue(new_schema)

    with patch.object(mysql_generator_migra.console, "print"):
        resultado = mysql_generator_migra.generate_migration(
            previous_schema=prev_schema_fixture,
            new_schema=new_schema_fixture,
            print_output=False,
            print_sql=False,
        )

    sql_generado = resultado.sql_generado
    assert "REFERENCES User(id)" in sql_generado


def test_diff_esquemas_procesar_relaciones_auto_relacion(
    mysql_generator_migra,
    prev_schema_08,
    new_schema_08,
):
    """Prueba procesamiento de auto-relaciones (self-referencing)."""

    diferencias = mysql_generator_migra.diff_schemas(
        previous_schema=prev_schema_08,
        new_schema=new_schema_08,
    )

    assert len(diferencias.relaciones.agregadas) == 1

    relacion = diferencias.relaciones.agregadas[0]
    assert relacion.fuente.tabla_fuente == "Category"
    assert relacion.objetivo.tabla_objetivo == "Category"
    assert relacion.tipo_relation == TipoRelacion.MANY_TO_MANY.value


def test_diff_esquemas_relaciones_con_diferentes_on_delete(
    mysql_generator_migra,
    prev_schema_09,
    new_schema_09,
):
    """Prueba procesamiento de relaciones con diferentes políticas onDelete."""

    diferencias = mysql_generator_migra.diff_schemas(
        previous_schema=prev_schema_09,
        new_schema=new_schema_09,
    )

    assert len(diferencias.relaciones.agregadas) == 1

    relacion = diferencias.relaciones.agregadas[0]
    assert relacion.fuente.on_delete == OnDelete.SET_NULL.name
    assert relacion.objetivo.on_delete_inverso == OnDelete.CASCADE.value


def test_generar_migracion_eliminar_campos(
    mysql_generator_migra,
    prev_schema_10,
    new_schema_10,
):
    """Prueba generación de migración con eliminación de campos."""

    with patch.object(mysql_generator_migra.console, "print"):
        resultado = mysql_generator_migra.generate_migration(
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
    assert "DROP COLUMN `email`" in sql_generado


def test_generar_migracion_agregar_campos(
    mysql_generator_migra,
    prev_schema_11,
    new_schema_11,
):
    """Prueba generación de migración con agregado de campos."""

    with patch.object(mysql_generator_migra.console, "print"):
        resultado = mysql_generator_migra.generate_migration(
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
    assert "ADD COLUMN `age` INT" in sql_generado


def test_generar_migracion_modificar_campos(
    mysql_generator_migra,
    prev_schema_12,
    new_schema_12,
):
    """Prueba generación de migración con modificación de campos."""

    with patch.object(mysql_generator_migra.console, "print"):
        resultado = mysql_generator_migra.generate_migration(
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
    assert "MODIFY COLUMN `email` VARCHAR(255) NOT NULL" in sql_generado


def test_generar_migracion_modificar_enum(
    mysql_generator_migra,
    prev_schema_13,
    new_schema_13,
):
    """Prueba generación de migración con modificación de enums
    en una tabla existente."""

    with patch.object(mysql_generator_migra.console, "print"):
        resultado = mysql_generator_migra.generate_migration(
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
    assert "ENUM('ACTIVE', 'INACTIVE', 'PENDING')" in sql_generado


def test_generar_migracion_nuevo_enum(
    mysql_generator_migra,
    prev_schema_14,
    new_schema_14,
):
    """Prueba generación de migración con un nuevo enum agregado."""

    with patch.object(mysql_generator_migra.console, "print"):
        resultado = mysql_generator_migra.generate_migration(
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
    assert "ADD COLUMN `status` ENUM('ACTIVE', 'INACTIVE')" in sql_generado


def test_generar_migracion_eliminar_enum(
    mysql_generator_migra,
    prev_schema_15,
    new_schema_15,
):
    """Prueba generación de migración con eliminación de enums."""

    with patch.object(mysql_generator_migra.console, "print"):
        resultado = mysql_generator_migra.generate_migration(
            previous_schema=prev_schema_15,
            new_schema=new_schema_15,
            print_output=False,
            print_sql=False,
        )

    diferencias = resultado.diferencias

    assert len(diferencias.enums.eliminados) == 1
    assert "UserStatus" in diferencias.enums.eliminados

    sql_generado = resultado.sql_generado
    assert "DROP COLUMN `status`" in sql_generado


def test_generar_migracion_eliminar_tablas(
    mysql_generator_migra,
    prev_schema_16,
    new_schema_16,
):
    """Prueba generación de migración con eliminación de tablas."""

    with patch.object(mysql_generator_migra.console, "print"):
        resultado = mysql_generator_migra.generate_migration(
            previous_schema=prev_schema_16,
            new_schema=new_schema_16,
            print_output=False,
            print_sql=False,
        )

    diferencias = resultado.diferencias

    assert "Post" in diferencias.tablas.eliminadas

    sql_generado = resultado.sql_generado
    assert "DROP TABLE IF EXISTS `Post`" in sql_generado


def test_generar_sql_migracion_error_metodo_privado(mysql_generator_migra):
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
        mysql_generator_migra,
        "_generate_sql_create_table",
        side_effect=GraphQLStoreError("Error for create table"),
    ):
        with pytest.raises(MigrationGenerationError) as exc_info:
            mysql_generator_migra.generate_sql_migration(diferencias)

        assert "Error generating SQL: Error for create table" in str(
            exc_info.value,
        )


def test_generar_migracion_con_directivas_avanzadas(
    mysql_generator_migra,
    prev_schema_17,
    new_schema_17,
):
    """Prueba generación de migración cuando no se define columna ID."""

    with patch.object(mysql_generator_migra.console, "print"):
        resultado = mysql_generator_migra.generate_migration(
            previous_schema=prev_schema_17,
            new_schema=new_schema_17,
            print_output=True,
            print_sql=True,
        )

    diferencias = resultado.diferencias

    assert "id" not in diferencias.tablas.campos["Employee"].agregados

    sql_generado = resultado.sql_generado
    assert "`id` VARCHAR(25) NOT NULL PRIMARY KEY" in sql_generado
    assert "`email` VARCHAR(255) UNIQUE" in sql_generado
    assert "`name` VARCHAR(255) NOT NULL DEFAULT 'emp_123'" in sql_generado
    assert "`age` INT DEFAULT 18" in sql_generado
    assert "TIVE', 'FIRED', 'CONTRACTED') DEFAULT 'CONTRACTED'" in sql_generado
