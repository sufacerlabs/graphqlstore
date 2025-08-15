"""Pruebas para el modulo GeneradorEsquemaMySQL."""

from unittest.mock import patch
from source.cli.generators.mysql_generator import GeneratorSchemaMySQL
from source.cli.graphql.configuracion_y_constantes import (
    DatabaseType,
    TipoField,
)


def test_init_success(generador_mysql):
    """Prueba la inicializacion exitosa de GeneradorEsquemaMySQL."""
    assert isinstance(generador_mysql, GeneratorSchemaMySQL)
    assert generador_mysql.console is not None
    assert generador_mysql.schema_sql == []
    assert generador_mysql.print_output is None
    assert generador_mysql.print_sql is None


def test_database_type(generador_mysql):
    """Test that the database type is correctly set to MySQL."""
    assert generador_mysql.get_database_type() == DatabaseType.MYSQL


def test_type_mapping(generador_mysql):
    """Test the type mapping for MySQL."""
    mapping = generador_mysql.get_type_mapping()
    assert mapping[TipoField.ID.value] == "VARCHAR(25)"
    assert mapping[TipoField.STRING.value] == "VARCHAR(255)"
    assert mapping[TipoField.INT.value] == "INT"
    assert mapping[TipoField.FLOAT.value] == "DECIMAL(10, 2)"
    assert mapping[TipoField.BOOLEAN.value] == "BOOLEAN"
    assert mapping[TipoField.DATETIME.value] == "DATETIME"
    assert mapping[TipoField.JSON.value] == "JSON"


def test_get_empty_mysql_schema(generador_mysql):
    """Prueba que el esquema MySQL es vacio cuando no hay \
        relaciones ni tablas."""

    sql = generador_mysql.generate_schema({}, {}, [])

    assert isinstance(sql, str)
    assert sql == "\n\n"


def test_get_esquema_sql(generador_mysql):
    """Prueba que el esquema SQL se obtiene correctamente."""
    generador_mysql.schema_sql = [
        "CREATE TABLE User (id INT PRIMARY KEY, name VARCHAR(100));",
        "CREATE TABLE Post (id INT PRIMARY KEY);",
    ]

    sql = generador_mysql.get_schema_sql()
    assert isinstance(sql, str)
    assert "CREATE TABLE User" in sql
    assert "CREATE TABLE Post" in sql
    # Comprobamos que el esquema SQL tiene 3 líneas
    # (2 tablas + 1 línea vacía al final)
    assert len(sql.split("\n")) == 3


def test_generar_esquema_mto(
    generador_mysql,
    table_with_many_to_one_relation,
    many_to_one_relation,
):
    """Test the complete generation of the schema with N:1 relationship."""
    with patch.object(generador_mysql.console, "print"):
        sql = generador_mysql.generate_schema(
            tables=table_with_many_to_one_relation,
            enums={},
            relationships=many_to_one_relation,
            print_output=False,
            print_sql=False,
        )

    assert (
        "ALTER TABLE `Post`\n"
        " ADD COLUMN `user_id` VARCHAR(25) NOT NULL,\n"
        " ADD CONSTRAINT `fk_User_posts_Post` FOREIGN KEY (`user_id`)"
        " REFERENCES `User`(id) ON DELETE CASCADE;"
    ) in sql
    assert "`hashtags` JSON NOT NULL" in sql
    assert "`createdAt` DATETIME DEFAULT CURRENT_TIMESTAMP" in sql
    assert "`updatedAt` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE" in sql


def test_generar_esquema_otm(
    generador_mysql,
    table_with_one_to_many_relation,
    one_to_many_relation,
):
    """Test the complete generation of the schema with 1:N relationship."""
    with patch.object(generador_mysql.console, "print"):
        sql = generador_mysql.generate_schema(
            tables=table_with_one_to_many_relation,
            enums={},
            relationships=one_to_many_relation,
            print_output=False,
            print_sql=False,
        )

    assert "CREATE TABLE Product" in sql
    assert "CREATE TABLE ProductType" in sql
    assert (
        "ALTER TABLE `Product`\n"
        " ADD COLUMN `productType_id` VARCHAR(25),\n"
        " ADD CONSTRAINT `fk_Product_productType_ProductType` FOREIGN KEY"
        " (`productType_id`) REFERENCES `ProductType`(id) ON DELETE CASCADE;"
    ) in sql


def test_generar_esquema_mtm(
    generador_mysql,
    table_with_many_to_many_relation,
    many_to_many_relation,
):
    """Prueba la generacion completa del esquema con rel N:M."""
    with patch.object(generador_mysql.console, "print"):
        sql = generador_mysql.generate_schema(
            tables=table_with_many_to_many_relation,
            enums={},
            relationships=many_to_many_relation,
            print_output=False,
            print_sql=False,
        )

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
    table_with_one_to_one_relation,
    basic_enums,
    one_to_one_relation,
):
    """Prueba la generacion completa del esquema con rel 1:1."""
    with patch.object(generador_mysql.console, "print"):
        sql = generador_mysql.generate_schema(
            tables=table_with_one_to_one_relation,
            enums=basic_enums,
            relationships=one_to_one_relation,
            print_output=False,
            print_sql=False,
        )
    assert "ALTER TABLE `Profile`\n" in sql
    assert "`status` ENUM('ACTIVE', 'INACTIVE')\n" in sql
    assert (
        "ADD CONSTRAINT `fk_User_profile_Profile` FOREIGN KEY (`user_id`) "
        "REFERENCES `User`(id) ON DELETE CASCADE;"
    ) in sql


def test_generar_esquema_oto_with_cascade_source(
    generador_mysql,
    table_with_one_to_one_relation_with_cascade_source,
    one_to_one_relation_with_cascade_source,
):
    """Prueba la generacion del esquema con rel 1:1 y fuente CASCADE."""
    with patch.object(generador_mysql.console, "print"):
        sql = generador_mysql.generate_schema(
            tables=table_with_one_to_one_relation_with_cascade_source,
            enums={},
            relationships=one_to_one_relation_with_cascade_source,
            print_output=False,
            print_sql=False,
        )
    assert "ALTER TABLE `User`\n" in sql
    assert (
        "ADD CONSTRAINT `fk_User_profile_Profile` FOREIGN KEY (`user_id`) "
        "REFERENCES `Profile`(id) ON DELETE CASCADE;"
    ) in sql


def test_generar_esquema_oto_without_inverse_field(
    generador_mysql,
    table_with_one_to_one_relation_without_inverse_field,
    one_to_one_relation_without_inverse_field,
):
    """Prueba la generacion del esquema con rel 1:1 sin campo inverso."""
    with patch.object(generador_mysql.console, "print"):
        sql = generador_mysql.generate_schema(
            tables=table_with_one_to_one_relation_without_inverse_field,
            enums={},
            relationships=one_to_one_relation_without_inverse_field,
            print_output=False,
            print_sql=False,
        )

    assert "ALTER TABLE `User`\n" in sql
    assert (
        "ADD CONSTRAINT `fk_User_profile_Profile` FOREIGN KEY (`profile_id`) "
        "REFERENCES `Profile`(id) ON DELETE CASCADE;"
    ) in sql
    assert (
        "ADD CONSTRAINT `fk_User_public_profile_Profile_1` FOREIGN KEY "
        "(`public_profile_id`) REFERENCES `Profile`(id) ON DELETE CASCADE;"
    ) in sql


def test_generar_esquema_con_directivas_avanzadas(
    generador_mysql,
    simple_tables,
):
    """Prueba la generacion del esquema con directivas avanzadas."""
    with patch.object(generador_mysql.console, "print") as mock_print:
        sql = generador_mysql.generate_schema(
            tables=simple_tables,
            enums={},
            relationships=[],
            print_output=True,
            print_sql=True,
        )
    assert "CREATE TABLE User" in sql
    assert "`name` VARCHAR(255) NOT NULL DEFAULT 'Anonymous'" in sql
    assert "`hashtags` JSON NOT NULL" in sql
    assert "`age` INT DEFAULT 18" in sql
    assert "UNIQUE KEY `uk_email` (`email`)" in sql
    assert mock_print.called


def test_visualizar_salida_relaciones_mto(
    generador_mysql,
    many_to_one_relation,
):
    """Test the visualization of output for N:1 relationships."""
    with patch.object(generador_mysql.console, "print") as mock_print:
        # pylint: disable=protected-access
        generador_mysql._print_output_relationships(
            relationship=many_to_one_relation[0],
            data_sql="ALTER TABLE Post ADD COLUMN posts_id VARCHAR(25);",
            print_output=True,
            print_sql=True,
            sql_name="Post",
        )
        # pylint: enable=protected-access
    assert mock_print.called
    assert mock_print.call_count >= 3


def test_generate_schema_with_self_relation(
    generador_mysql, self_relation, table_with_self_relations
):
    """Prueba la generacion del esquema MySQL con relaciones de tipo itself."""
    with patch.object(generador_mysql.console, "print"):
        sql = generador_mysql.generate_schema(
            relationships=self_relation,
            tables=table_with_self_relations,
            enums={},
        )
    assert "CREATE TABLE UserToFriends" in sql
    assert "PRIMARY KEY (`user_A`, `user_B`)" in sql
    assert "CONSTRAINT `fk_User_friends_User_friends`" in sql
    assert "Y (`user_A`) REFERENCES `User`(id) ON DELETE CASCADE" in sql
    assert "CONSTRAINT `fk_User_friends_User`" in sql
    assert "Y (`user_B`) REFERENCES `User`(id) ON DELETE CASCADE" in sql
