"""PostgreSQL-specific migration generator."""

from typing import List
from ...graphql.configuracion_y_constantes import (
    DatabaseType,
    InfoCambioEnum,
    InfoCambioCampo,
    InfoField,
    InfoRelacion,
    TipoRelacion,
)
from ...graphql.exceptions import (
    MigrationGenerationError,
)
from .migration_base import BaseMigrationGenerator


class PostgreSQLMigrationGenerator(BaseMigrationGenerator):
    """PostgreSQL-specific implementation of the migration generator."""

    def get_database_type(self) -> DatabaseType:
        """Get the database type for this generator."""
        return DatabaseType.POSTGRESQL

    def get_sql_type(self, field: InfoField) -> str:
        """Get SQL type for a field."""
        if field.es_lista:
            return "JSONB"

        sql_type = self.parser.get_type_mapping().get(field.tipo_campo, "TEXT")

        if sql_type == "DATETIME":
            sql_type = "TIMESTAMP"

        # Check if it's an enum
        if field.tipo_campo in self._available_enums:
            # PostgreSQL uses custom types for enums
            sql_type = f"{field.tipo_campo}_enum"

        return sql_type

    def get_foreign_key_template(
        self,
        tabla_fk: str,
        campo_fk: str,
        unique: str,
        constraint: str,
        tabla_ref: str,
        on_delete: str,
    ):
        """Template to modify a foreign key in MySQL."""
        return (
            f'ALTER TABLE "{tabla_fk}"\n'
            f"  ADD COLUMN {campo_fk}_id VARCHAR(25){unique},\n"
            f"  ADD CONSTRAINT {constraint},\n"
            f"      FOREIGN KEY ({campo_fk}_id)"
            f'      REFERENCES "{tabla_ref}"(id){on_delete};'
        )

    def _generate_field_definition(self, field: InfoField) -> str:
        """Generate complete field definition for PostgreSQL."""
        sql_type = self.get_sql_type(field)

        column_name = field.nombre

        db = "db" in field.directivas
        if db and "rename" in field.directivas["db"].argumentos:
            column_name = field.directivas["db"].argumentos["rename"]

        definition = f"{column_name} {sql_type}"

        # add constraints
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
            if sql_type in lst or "_enum" in sql_type:
                definition += " DEFAULT '"
                definition += f"{default_value}'"
            else:
                definition += f" DEFAULT {default_value}"

        if "createdAt" in field.directivas:
            definition += " DEFAULT CURRENT_TIMESTAMP"

        if "updatedAt" in field.directivas:
            # PostgreSQL doesn't have ON UPDATE CURRENT_TIMESTAMP
            # It uses triggers instead
            definition += " DEFAULT CURRENT_TIMESTAMP"

        return definition

    def _generate_sql_create_table(
        self, table_name: str, fields: List[InfoField]
    ) -> str:
        """Generate SQL to create a new table in PostgreSQL."""
        # first check if we need to create any enum types
        enum_types_sql = []
        enum_fields = [
            f
            for f in fields
            if self._should_process_field(
                f,
            )
            and f.tipo_campo in self._available_enums
        ]

        for field in enum_fields:
            enum_name = field.tipo_campo
            enum_values = self._available_enums[enum_name].valores
            enum_sql = self._generate_enum_type_sql(enum_name, enum_values)
            if enum_sql not in enum_types_sql:
                enum_types_sql.append(enum_sql)

        # Now create the table
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
            columns.insert(0, "  id VARCHAR(25) NOT NULL PRIMARY KEY")

        # Join columns
        table_content = ",\n".join(columns)

        sql = f"CREATE TABLE {table_name} (\n{table_content}\n);"

        # Combine enum types and table creation
        full_sql = "\n\n".join(filter(None, [*enum_types_sql, sql]))

        if self.print_output:
            self._visualize_sql_operation(
                "CREATE TABLE", f"Creating table {table_name}", full_sql
            )

        return f"-- Create table {table_name}\n{full_sql}"

    def _generate_enum_type_sql(
        self,
        enum_name: str,
        enum_values: List[str],
    ) -> str:
        """Generate SQL for creating an enum type in PostgreSQL."""
        values_sql = ", ".join(f"'{val}'" for val in enum_values)
        return f"CREATE TYPE {enum_name}_enum AS ENUM ({values_sql});\n"

    def _generate_sql_add_field(
        self,
        table_name: str,
        field: InfoField,
    ) -> str:
        """Generate SQL to add a field in PostgreSQL."""
        # Check if we need to create an enum type first
        enum_sql = ""
        if field.tipo_campo in self._available_enums:
            enum_name = field.tipo_campo
            enum_values = self._available_enums[enum_name].valores
            enum_sql = self._generate_enum_type_sql(enum_name, enum_values)

        definition = self._generate_field_definition(field)
        emoji = self._visualize_field_requirement(field.es_requerido)

        sql = f"ALTER TABLE {table_name} ADD COLUMN {definition};"

        full_sql = enum_sql + sql

        if self.print_output:
            self._visualize_sql_operation(
                "ADD FIELD",
                f"Adding field {field.nombre}{emoji} to {table_name}",
                full_sql,
            )

        return f"-- Add field {field.nombre} to {table_name}\n{full_sql}"

    def _generate_sql_remove_field(
        self,
        table_name: str,
        field: InfoField,
    ) -> str:
        """Generate SQL to remove a field in PostgreSQL."""
        sql = f"ALTER TABLE {table_name} DROP COLUMN {field.nombre};"
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
        """Generate SQL to modify a field in PostgreSQL."""

        # Handle column name
        old_column_name = change.info_antigua.nombre
        new_column_name = change.info_nueva.nombre

        if (
            "db" in change.info_nueva.directivas
            and "rename" in change.info_nueva.directivas["db"].argumentos
        ):
            directives = change.info_nueva.directivas
            new_column_name = directives["db"].argumentos["rename"]

        # Handle column type change
        old_type = self.get_sql_type(change.info_antigua)
        new_type = self.get_sql_type(change.info_nueva)

        # Need to create enum type if it's a new enum
        enum_sql = ""
        if (
            change.info_nueva.tipo_campo in self._available_enums
            and change.info_antigua.tipo_campo != change.info_nueva.tipo_campo
        ):
            enum_name = change.info_nueva.tipo_campo
            enum_values = self._available_enums[enum_name].valores
            enum_sql = self._generate_enum_type_sql(enum_name, enum_values)

        # Build the ALTER TABLE statements
        statements = []

        # Add enum creation if needed
        if enum_sql:
            statements.append(enum_sql)

        # Handle column rename if needed
        if old_column_name != new_column_name:
            statements.append(
                f"ALTER TABLE {table_name} RENAME COLUMN "
                f"{old_column_name} TO {new_column_name};"
            )

        # Handle type change if needed
        if old_type != new_type:
            statements.append(
                f"ALTER TABLE {table_name} ALTER COLUMN {new_column_name} "
                f"TYPE {new_type} USING {new_column_name}::{new_type};"
            )

        # Handle nullability changes
        if change.info_antigua.es_requerido != change.info_nueva.es_requerido:
            if change.info_nueva.es_requerido:
                statements.append(
                    f"ALTER TABLE {table_name} ALTER COLUMN {new_column_name} "
                    "SET NOT NULL;"
                )
            else:
                statements.append(
                    f"ALTER TABLE {table_name} ALTER COLUMN {new_column_name} "
                    "DROP NOT NULL;"
                )

        # Handle uniqueness changes
        old_has_unique = "unique" in change.info_antigua.directivas
        new_has_unique = "unique" in change.info_nueva.directivas

        if old_has_unique != new_has_unique:
            if new_has_unique:
                statements.append(
                    f"ALTER TABLE {table_name} ADD CONSTRAINT "
                    f"{new_column_name}_unique UNIQUE ({new_column_name});"
                )
            else:
                statements.append(
                    f"ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS "
                    f"{old_column_name}_unique;"
                )

        # Handle default value changes
        old_default = None
        if "default" in change.info_antigua.directivas:
            args = change.info_antigua.directivas["default"].argumentos
            if "value" in args:
                old_default = args["value"]

        new_default = None
        if "default" in change.info_nueva.directivas:
            args = change.info_nueva.directivas["default"].argumentos
            if "value" in args:
                new_default = args["value"]

        if old_default != new_default:
            if new_default is not None:
                if new_type in ("TEXT", "VARCHAR(255)") or "_enum" in new_type:
                    statements.append(
                        f"ALTER TABLE {table_name} ALTER COLUMN "
                        f"{new_column_name} SET DEFAULT '{new_default}';"
                    )
                else:
                    statements.append(
                        f"ALTER TABLE {table_name} ALTER COLUMN "
                        f"{new_column_name} SET DEFAULT {new_default};"
                    )

        sql = "\n".join(statements)

        if self.print_output:
            self._visualize_sql_operation(
                "MODIFY FIELD",
                f"Modifying field {change.nombre} in {table_name}",
                sql,
            )

        return f"-- Modify field {change.nombre} in {table_name}\n{sql}"

    def _generate_sql_add_relation(self, relation: InfoRelacion) -> str:
        """Generate SQL to add a relation in PostgreSQL."""
        if relation.tipo_relation == TipoRelacion.MANY_TO_MANY.value:
            return self._generate_sql_junction_table(relation)
        return self._generate_sql_foreign_key(
            relation,
            self.get_foreign_key_template,
        )

    def _generate_sql_remove_relation(self, relation: InfoRelacion) -> str:
        """Generate SQL to remove a relation in PostgreSQL."""
        if relation.tipo_relation == TipoRelacion.MANY_TO_MANY.value:
            sql = f"DROP TABLE IF EXISTS {relation.nombre_relacion};"
            r = f"-- Remove relation {relation.nombre_relacion}\n{sql}"
            return r

        constr_name = relation.fuente.nombre_constraint_fuente
        table = self._determine_fk_table(relation)
        field = self._determine_fk_field(relation)

        sql_drop_fk = f'ALTER TABLE "{table}" DROP FOREIGN KEY {constr_name};'

        sql_drop_col = f'ALTER TABLE "{table}" DROP COLUMN {field}_id;'

        r = f"-- Remove relation {relation.nombre_relacion}\n"
        r += f"{sql_drop_fk}\n{sql_drop_col}"
        return r

    def _generate_sql_modify_enum(
        self,
        enum_modified: InfoCambioEnum,
    ) -> List[str]:
        """Generate SQL to modify an enum in PostgreSQL."""
        statements = []
        print("Modifying enum:", enum_modified)
        # PostgreSQL handles enums differently - we need to create a new type
        # and migrate the data
        enum_name = enum_modified.nombre
        old_type_name = f"{enum_name}_enum"
        temp_type_name = f"{enum_name}_enum_new"

        # Create the new enum type
        values = enum_modified.valores_nuevos
        enum_vls = ", ".join(f"'{val}'" for val in values)
        create_new_type = f"CREATE TYPE {temp_type_name} AS ENUM ({enum_vls});"

        # Find tables using this enum
        tables_with_enum = self._search_tables_using_enum(enum_name)
        print("Tables using enum:", tables_with_enum)
        for table_name, fields in tables_with_enum.items():
            for field in fields:
                # PostgreSQL requires a complex migration for enum changes
                # 1. Create a new enum type
                # 2. Add a temporary column with the new type
                # 3. Copy and convert data from the old column
                # 4. Drop the old column
                # 5. Rename the new column to the original name
                # 6. Drop the old enum type
                # 7. Rename the new enum type to the old name

                column_name = field.nombre
                # Check if the field has a default value
                has_default = "default" in field.directivas
                def_clause = ""

                if has_default:
                    args = field.directivas["default"].argumentos
                else:
                    args = {}

                if has_default and "value" in args:
                    default_value = args["value"]
                    # Ensure the default value exists in the new enum
                    if default_value in enum_modified.valores_nuevos:
                        def_clause = f" DEFAULT {default_value}"
                    else:
                        raise MigrationGenerationError(
                            f"Default value '{default_value}' for field "
                            f"{column_name} in table {table_name} "
                            "is not valid for the new enum type."
                        )

                # Generate migration SQL
                migration_sql = [
                    f"-- Update enum {enum_name} in {table_name}",
                    create_new_type,
                    f"ALTER TABLE {table_name} "
                    f"ADD COLUMN {column_name}_new "
                    f"{temp_type_name}{def_clause};",
                ]

                if field.es_requerido:
                    migration_sql.append(
                        f"UPDATE {table_name} SET {column_name}_new = "
                        f"{column_name}::{temp_type_name} "
                        f"WHERE {column_name} IS NOT NULL;"
                    )

                # If the field is required, we need to add NOT NULL constraint
                if field.es_requerido:
                    migration_sql.append(
                        f"ALTER TABLE {table_name} "
                        f"ALTER COLUMN {column_name}_new SET NOT NULL;"
                    )

                # Drop old column and rename new one
                migration_sql.extend(
                    [
                        f"ALTER TABLE {table_name} DROP COLUMN {column_name};",
                        f"ALTER TABLE {table_name} "
                        f"RENAME COLUMN {column_name}_new TO {column_name};",
                        f"DROP TYPE {old_type_name};",
                    ]
                )

                # rename the new enum type to the old name
                migration_sql.append(
                    f"ALTER TYPE {temp_type_name} RENAME TO {old_type_name};"
                )

                # Combine all statements
                full_sql = "\n".join(migration_sql)
                statements.append(full_sql)

                if self.print_output:
                    self._visualize_sql_operation(
                        "MODIFY ENUM",
                        f"Updating enum {enum_name} in {table_name}",
                        full_sql,
                    )

        return statements

    def _generate_sql_remove_table(self, table_name: str) -> str:
        """Generate SQL to remove a table in PostgreSQL."""
        sql = f"DROP TABLE IF EXISTS {table_name};"

        if self.print_output:
            self._visualize_sql_operation(
                "REMOVE TABLE", f"Removing table {table_name}", sql
            )

        return f"-- Remove table {table_name}\n{sql}"
