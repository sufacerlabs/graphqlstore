"""MySQL-specific migration generator."""

from typing import List

from ...graphql.configuracion_y_constantes import (
    DatabaseType,
    InfoCambioEnum,
    InfoCambioCampo,
    InfoField,
    InfoRelacion,
    TipoRelacion,
    OnDelete,
)
from ...graphql.exceptions import RelationshipError
from ...graphql.templates import (
    TEMPLATE_CREAR_TABLA,
    TEMPLATE_AGREGAR_CAMPO,
    TEMPLATE_ELIMINAR_CAMPO,
    TEMPLATE_MODIFICAR_CAMPO,
    TEMPLATE_ELIMINAR_FK,
    TEMPLATE_ELIMINAR_TABLA,
    template_crear_tabla_junction,
    template_modificar_fk,
)

from .migration_base import BaseMigrationGenerator


class MySQLMigrationGenerator(BaseMigrationGenerator):
    """MySQL-specific implementation of the migration generator."""

    def get_database_type(self) -> DatabaseType:
        """Get the database type for this generator."""
        return DatabaseType.MYSQL

    def get_sql_type(self, field: InfoField) -> str:
        """Get SQL type for a field."""
        if field.es_lista:
            return "JSON"

        sql_type = self.parser.get_type_mapping().get(field.tipo_campo, "TEXT")

        # Check if it's an enum
        ed = self._available_enums
        if field.tipo_campo in ed:
            enum_values = ", ".join(map(repr, ed[field.tipo_campo].valores))
            sql_type = f"ENUM({enum_values})"

        return sql_type

    def _generate_field_definition(self, field: InfoField) -> str:
        """Generate complete field definition for MySQL."""
        sql_type = self.get_sql_type(field)

        column_name = field.nombre

        db = "db" in field.directivas
        if db and "rename" in field.directivas["db"].argumentos:
            column_name = field.directivas["db"].argumentos["rename"]

        definition = f"`{column_name}` {sql_type}"

        # Add constraints
        if field.es_requerido:
            definition += " NOT NULL"

        if "unique" in field.directivas:
            definition += " UNIQUE"

        if "id" in field.directivas:
            definition += " PRIMARY KEY"

        df = "default" in field.directivas
        if df and "value" in field.directivas["default"].argumentos:
            default_value = field.directivas["default"].argumentos["value"]
            lst = ("TEXT", "VARCHAR(255)")
            if sql_type in lst or (sql_type.startswith("ENUM")):
                definition += " DEFAULT '"
                definition += f"{default_value}'"
            else:
                definition += f" DEFAULT {default_value}"

        if "createdAt" in field.directivas:
            definition += " DEFAULT CURRENT_TIMESTAMP"

        if "updatedAt" in field.directivas:
            definition += " DEFAULT CURRENT_TIMESTAMP "
            definition += "ON UPDATE CURRENT_TIMESTAMP"

        return definition

    def _generate_sql_create_table(
        self, table_name: str, fields: List[InfoField]
    ) -> str:
        """Generate SQL to create a new table in MySQL."""
        columns = []
        has_primary_key = False

        for field in fields:
            if not self._should_process_field(field):
                continue

            column_def = self._generate_field_definition(field)
            columns.append(f"  {column_def}")

            # Check if it's a primary key
            if "id" in field.directivas:
                has_primary_key = True

        # Add automatic ID if no primary key exists
        if not has_primary_key:
            columns.insert(0, "  `id` VARCHAR(25) NOT NULL PRIMARY KEY")

        # Join columns
        table_content = ",\n".join(columns)

        sql = TEMPLATE_CREAR_TABLA.format(
            nombre_tabla=table_name, columnas=table_content
        )

        if self.print_output:
            self._visualize_sql_operation(
                "CREATE TABLE", f"Creating table {table_name}", sql
            )

        return f"-- Create table {table_name}\n{sql}"

    def _generate_sql_add_field(
        self,
        table_name: str,
        field: InfoField,
    ) -> str:
        """Generate SQL to add a field in MySQL."""
        definition = self._generate_field_definition(field)
        emoji = self._visualize_field_requirement(field.es_requerido)
        sql = TEMPLATE_AGREGAR_CAMPO.format(
            tabla=table_name,
            definicion=definition,
        )

        if self.print_output:
            self._visualize_sql_operation(
                "ADD FIELD",
                f"Adding field {field.nombre}{emoji} to {table_name}",
                sql,
            )

        return f"-- Add field {field.nombre} to {table_name}\n{sql}"

    def _generate_sql_remove_field(
        self,
        table_name: str,
        field: InfoField,
    ) -> str:
        """Generate SQL to remove a field in MySQL."""
        sql = TEMPLATE_ELIMINAR_CAMPO.format(
            tabla=table_name,
            campo=field.nombre,
        )
        emoji = self._visualize_field_requirement(field.es_requerido)

        if self.print_output:
            self._visualize_sql_operation(
                "REMOVE FIELD",
                f"Removing field {field.nombre}{emoji} from {table_name}",
                sql,
            )

        return f"-- Remove field {field.nombre} from {table_name}\n{sql}"

    def _generate_sql_modify_field(
        self, table_name: str, change: InfoCambioCampo
    ) -> str:
        """Generate SQL to modify a field in MySQL."""
        definition = self._generate_field_definition(change.info_nueva)

        sql = TEMPLATE_MODIFICAR_CAMPO.format(
            tabla=table_name,
            definicion=definition,
        )

        if self.print_output:
            self._visualize_sql_operation(
                "MODIFY FIELD",
                f"Modifying field {change.nombre} in {table_name}",
                sql,
            )

        return f"-- Modify field {change.nombre} in {table_name}\n{sql}"

    def _generate_sql_add_relation(self, relation: InfoRelacion) -> str:
        """Generate SQL to add a relation in MySQL."""
        if relation.tipo_relation == TipoRelacion.MANY_TO_MANY.value:
            return self._generate_sql_junction_table(relation)
        return self._generate_sql_foreign_key(relation)

    def _generate_sql_remove_relation(self, relation: InfoRelacion) -> str:
        """Generate SQL to remove a relation in MySQL."""
        if relation.tipo_relation == TipoRelacion.MANY_TO_MANY.value:
            sql = TEMPLATE_ELIMINAR_TABLA.format(
                tabla=relation.nombre_relacion,
            )
            r = f"-- Remove relation {relation.nombre_relacion}\n{sql}"
            return r

        constraint_name = relation.fuente.nombre_constraint_fuente
        tabla = self._determine_fk_table(relation)

        sql_drop_fk = TEMPLATE_ELIMINAR_FK.format(
            tabla=tabla, constraint=constraint_name
        )
        sql_drop_col = TEMPLATE_ELIMINAR_CAMPO.format(
            tabla=tabla, campo=f"{self._determine_fk_field(relation)}_id"
        )

        r = f"-- Remove relation {relation.nombre_relacion}\n"
        r += f"{sql_drop_fk}\n{sql_drop_col}"
        return r

    def _generate_sql_modify_enum(
        self,
        enum_modified: InfoCambioEnum,
    ) -> List[str]:
        """Generate SQL to modify an enum in MySQL."""
        statements: List[str] = []

        # Get all tables and fields using this enum
        tables_with_enum = self._search_tables_using_enum(
            enum_modified.nombre,
        )

        if not tables_with_enum:
            return statements

        # Update tables
        for table_name, fields in tables_with_enum.items():
            for field in fields:

                if "default" in field.directivas:
                    continue

                definition = self._generate_field_definition(
                    field,
                )

                sql_modify = TEMPLATE_MODIFICAR_CAMPO.format(
                    tabla=table_name,
                    definicion=definition,
                )

                enum_name = enum_modified.nombre
                msg = f"-- Update enum {enum_name} in {table_name}"
                statements.append(f"{msg}\n" f"{sql_modify}")

                if self.print_output:
                    self._visualize_sql_operation(
                        "MODIFY ENUM",
                        f"Updating enum {enum_name} in {table_name}",
                        sql_modify,
                    )

        return statements

    def _generate_sql_remove_table(self, table_name: str) -> str:
        """Generate SQL to remove a table in MySQL."""
        sql = TEMPLATE_ELIMINAR_TABLA.format(tabla=table_name)

        if self.print_output:
            self._visualize_sql_operation(
                "REMOVE TABLE", f"Removing table {table_name}", sql
            )

        return f"-- Remove table {table_name}\n{sql}"

    def _generate_sql_junction_table(self, relation: InfoRelacion) -> str:
        """Generate SQL for a junction table (N:M relation) in MySQL."""
        source_table = relation.fuente.tabla_fuente
        target_table = relation.objetivo.tabla_objetivo
        junction_name = relation.nombre_relacion

        # Skip if already processed
        if junction_name in self._processed_junction_tables:
            return ""

        self._processed_junction_tables.add(junction_name)

        is_self_relation = source_table == target_table

        source_suffix = "id" if not is_self_relation else "A"
        target_suffix = "id" if not is_self_relation else "B"

        on_delete = (
            OnDelete.SET_NULL.value
            if (relation.fuente.on_delete == "SET NULL")
            else OnDelete.CASCADE.value
        )
        reverse_on_delete = (
            OnDelete.SET_NULL.value
            if (relation.objetivo.on_delete_inverso == "SET_NULL")
            else OnDelete.CASCADE.value
        )

        sql = template_crear_tabla_junction(
            nombre_junction=junction_name,
            tabla_fuente=source_table,
            sufi_f=source_suffix,
            constraint_fuente=relation.fuente.nombre_constraint_fuente,
            on_delete=on_delete,
            tabla_objetivo=target_table,
            sufi_o=target_suffix,
            constraint_objetivo=relation.objetivo.nombre_constraint_objetivo,
            reverse_on_delete=reverse_on_delete,
            engine_setting="ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
        )

        if self.print_output:
            self._visualize_sql_operation(
                "CREATE JUNCTION TABLE",
                f"Creating junction table {junction_name} for N:M relation",
                sql,
            )

        return f"-- Create junction table {junction_name}\n{sql}"

    def _generate_sql_foreign_key(self, relation: InfoRelacion) -> str:
        """Generate SQL for a foreign key (1:1 and 1:N relations) in MySQL."""
        fk_table = self._determine_fk_table(relation)
        fk_field = self._determine_fk_field(relation)
        ref_table = (
            relation.objetivo.tabla_objetivo
            if fk_table == relation.fuente.tabla_fuente
            else relation.fuente.tabla_fuente
        )

        actual_on_delete = "SET NULL"
        if relation.tipo_relation == TipoRelacion.MANY_TO_ONE.value:
            actual_on_delete = relation.objetivo.on_delete_inverso
        elif relation.tipo_relation == TipoRelacion.ONE_TO_MANY.value:
            actual_on_delete = relation.fuente.on_delete
        elif relation.tipo_relation == TipoRelacion.ONE_TO_ONE.value:
            if relation.fuente.on_delete == OnDelete.CASCADE.value and (
                relation.objetivo.on_delete_inverso != OnDelete.CASCADE.value
            ):
                actual_on_delete = relation.fuente.on_delete
            elif relation.fuente.on_delete != OnDelete.CASCADE.value and (
                relation.objetivo.on_delete_inverso == OnDelete.CASCADE.value
            ):
                actual_on_delete = relation.objetivo.on_delete_inverso
        else:
            raise RelationshipError(
                f"Relationship type not supported: {relation.tipo_relation}",
                f"for {relation.nombre_relacion}",
            )

        if actual_on_delete == OnDelete.CASCADE.value:
            on_delete_action = "ON DELETE CASCADE"
        else:
            on_delete_action = "ON DELETE SET NULL"

        rt = relation.tipo_relation
        unique = " UNIQUE" if rt == TipoRelacion.ONE_TO_ONE.value else ""
        sql = template_modificar_fk(
            tabla_fk=fk_table,
            campo_fk=fk_field,
            unique=unique,
            constraint=relation.fuente.nombre_constraint_fuente,
            tabla_ref=ref_table,
            on_delete=on_delete_action,
        )

        if self.print_output:
            self._visualize_sql_operation(
                "ADD FOREIGN KEY",
                f"Adding foreign key {fk_field}_id in {fk_table}",
                sql,
            )

        return f"-- Add foreign key {fk_field}_id in {fk_table}\n{sql}"
