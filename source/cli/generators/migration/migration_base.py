"""Abstract base migration generator class."""

from abc import ABC, abstractmethod
import datetime
import hashlib
from typing import Dict, List, Optional, Set
from rich.console import Console
from rich.tree import Tree
from rich.syntax import Syntax
from rich.panel import Panel

from ...graphql.configuracion_y_constantes import (
    DatabaseType,
    InfoTabla,
    InfoField,
    InfoRelacion,
    InfoEnum,
    InfoDiffEsquema,
    InfoDiffTablas,
    InfoDiffRelaciones,
    InfoDiffEnums,
    InfoDiffCampos,
    InfoCambioCampo,
    InfoCambioEnum,
    InfoMigracion,
    TipoRelacion,
    OnDelete,
)

from ...graphql.exceptions import (
    GraphQLStoreError,
    MigrationError,
    SchemaComparisonError,
    MigrationGenerationError,
)
from ...graphql.parser import ParserGraphQLEsquema
from ...graphql.procesar_relaciones import ProcesarRelaciones


class BaseMigrationGenerator(ABC):
    """Abstract base class for database migration generators."""

    def __init__(self):
        """Initialize the migration generator."""
        self.console = Console()
        self.migrations_sql = []
        self.parser = ParserGraphQLEsquema()
        self.print_output = True
        self.print_sql = True

        self._available_enums = None
        self._existing_tables = None
        self._processed_junction_tables: Set[str] = set()

    def generate_migration(
        self,
        previous_schema: str,
        new_schema: str,
        migration_id: Optional[str] = None,
        print_output: bool = True,
        print_sql: bool = True,
    ) -> InfoMigracion:
        """
        Generate a complete migration from two GraphQL schemas.

        Args:
            previous_schema: Previous GraphQL schema
            new_schema: New GraphQL schema
            migration_id: Custom migration ID
            print_output: Whether to show detailed output
            print_sql: Whether to show generated SQL

        Returns:
            Complete migration information
        """
        self.print_output = print_output
        self.print_sql = print_sql

        try:
            # Generate migration ID if not provided
            if not migration_id:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                hash_schemas = self._generate_hash_schemas(
                    previous_schema,
                    new_schema,
                )
                migration_id = f"migration_{timestamp}_{hash_schemas[:8]}"

            if self.print_output:
                self._show_migration_start(migration_id)

            # Compare schemas
            differences = self.diff_schemas(
                previous_schema,
                new_schema,
            )

            if not differences.tiene_cambios():
                if self.print_output:
                    self.console.print(
                        "\n✅ No changes detected between schemas\n",
                        style="green",
                    )

                return InfoMigracion(
                    id_migracion=migration_id,
                    timestamp=datetime.datetime.now().isoformat(),
                    esquema_anterior=previous_schema,
                    esquema_nuevo=new_schema,
                    diferencias=differences,
                    sql_generado="",
                )

            # Generate migration SQL
            sql_migration = self.generate_sql_migration(differences)

            # Create migration information
            migration = InfoMigracion(
                id_migracion=migration_id,
                timestamp=datetime.datetime.now().isoformat(),
                esquema_anterior=previous_schema,
                esquema_nuevo=new_schema,
                diferencias=differences,
                sql_generado=sql_migration,
            )

            if self.print_output:
                self._show_migration_summary(len(sql_migration.split(";")))

            return migration

        except GraphQLStoreError as e:
            raise MigrationError(
                f"Error generating migration: {str(e)}",
            ) from e

    def diff_schemas(
        self,
        previous_schema: str,
        new_schema: str,
    ) -> InfoDiffEsquema:
        """
        Compare two GraphQL schemas and detect differences.

        Args:
            previous_schema: Previous schema
            new_schema: New schema

        Returns:
            Detected differences
        """
        try:
            # Parse previous schema
            prev_info = self.parser.parse_esquema(previous_schema)
            prev_processor = ProcesarRelaciones(
                tablas=prev_info.tablas,
                scalar_types=ParserGraphQLEsquema.get_type_mapping(),
                enum_types=prev_info.enums,
            )
            prev_relations = prev_processor.procesar_relaciones()

            # Parse new schema
            new_info = self.parser.parse_esquema(new_schema)
            new_processor = ProcesarRelaciones(
                tablas=new_info.tablas,
                scalar_types=ParserGraphQLEsquema.get_type_mapping(),
                enum_types=new_info.enums,
            )
            new_relations = new_processor.procesar_relaciones()

            self._available_enums = {}
            self._available_enums.update(prev_info.enums)
            self._available_enums.update(new_info.enums)

            # Compare and generate differences
            differences = InfoDiffEsquema()

            # Compare tables and fields
            differences.tablas = self._compare_tables(
                prev_info.tablas,
                new_info.tablas,
            )

            # Filter existing tables and update with new information
            self._existing_tables = {}
            for t, i in prev_info.tablas.items():
                if t not in differences.tablas.eliminadas:
                    if t in new_info.tablas:
                        self._existing_tables[t] = new_info.tablas[t]
                    else:
                        self._existing_tables[t] = i

            # Compare relations
            differences.relaciones = self._compare_relations(
                prev_relations, new_relations
            )

            # Compare enums
            differences.enums = self._compare_enums(
                prev_info.enums,
                new_info.enums,
            )

            if self.print_output:
                self._show_detected_differences(differences)

            return differences

        except GraphQLStoreError as e:
            raise SchemaComparisonError(
                f"Error comparing schemas: {str(e)}",
            ) from e

    def generate_sql_migration(self, differences: InfoDiffEsquema) -> str:
        """
        Generate migration SQL from detected differences.

        Args:
            differences: Differences between schemas

        Returns:
            Complete migration SQL
        """
        try:
            sql_statements = []

            # Migration header
            sql_statements.extend(self._generate_migration_header())

            # 1. Create new tables (so foreign keys can reference them
            # correctly)
            for table_name in differences.tablas.agregadas:
                if table_name in differences.tablas.campos:
                    fields = differences.tablas.campos[table_name].agregados
                    sql_table = self._generate_sql_create_table(
                        table_name,
                        fields,
                    )
                    sql_statements.append(sql_table)

            # 2. Remove relationships (before removing fields/tables)
            for relation in differences.relaciones.eliminadas:
                sql_remove = self._generate_sql_remove_relation(relation)
                sql_statements.append(sql_remove)

            # 3. Remove fields
            for table_name, field_changes in differences.tablas.campos.items():
                if table_name not in differences.tablas.agregadas:
                    for field in field_changes.eliminados:
                        sql_remove = self._generate_sql_remove_field(
                            table_name,
                            field,
                        )
                        sql_statements.append(sql_remove)

            # 4. Add fields to existing tables
            for table_name, field_changes in differences.tablas.campos.items():
                if table_name not in differences.tablas.agregadas:
                    for field in field_changes.agregados:
                        sql_add = self._generate_sql_add_field(
                            table_name,
                            field,
                        )
                        sql_statements.append(sql_add)

            # 5. Modify existing fields
            for table_name, field_changes in differences.tablas.campos.items():
                for change in field_changes.modificados:
                    sql_modify = self._generate_sql_modify_field(
                        table_name,
                        change,
                    )
                    sql_statements.append(sql_modify)

            # 6. Modify enums
            for enum_modified in differences.enums.modificados:
                sql_enum = self._generate_sql_modify_enum(enum_modified)
                sql_statements.extend(sql_enum)

            # 7. Add new relationships
            for relation in differences.relaciones.agregadas:
                sql_relation = self._generate_sql_add_relation(relation)
                sql_statements.append(sql_relation)

            # 8. Remove tables (at the end, since foreign keys are already
            # removed)
            for table_name in differences.tablas.eliminadas:
                sql_remove = self._generate_sql_remove_table(table_name)
                sql_statements.append(sql_remove)

            # Filter empty statements and join
            filtered_stmts = [sql for sql in sql_statements if sql.strip()]
            return "\n\n".join(filtered_stmts)

        except GraphQLStoreError as e:
            raise MigrationGenerationError(
                f"Error generating SQL: {str(e)}",
            ) from e

    def _compare_tables(
        self,
        previous_tables: Dict[str, InfoTabla],
        new_tables: Dict[str, InfoTabla],
    ) -> InfoDiffTablas:
        """Compare tables between schemas."""
        differences = InfoDiffTablas()

        # Added tables
        differences.agregadas = [
            name for name in new_tables if name not in previous_tables
        ]

        # Removed tables
        differences.eliminadas = [
            name for name in previous_tables if name not in new_tables
        ]

        # Compare fields in existing tables
        for table_name in new_tables:
            if table_name in previous_tables:
                prev_fields = previous_tables[table_name].campos
                new_fields = new_tables[table_name].campos

                if prev_fields == new_fields:
                    continue

                differences.campos[table_name] = self._compare_fields(
                    prev_fields,
                    new_fields,
                )
            elif table_name in differences.agregadas:
                # For new tables, all fields are added
                differences.campos[table_name] = InfoDiffCampos(
                    agregados=list(new_tables[table_name].campos.values())
                )

        return differences

    def _compare_fields(
        self,
        previous_fields: Dict[str, InfoField],
        new_fields: Dict[str, InfoField],
    ) -> InfoDiffCampos:
        """Compare fields between tables."""
        differences = InfoDiffCampos()

        # Added fields
        for field_name, field_info in new_fields.items():
            if field_name not in previous_fields:
                if self._should_process_field(field_info):
                    differences.agregados.append(field_info)

        # Removed fields
        for field_name, field_info in previous_fields.items():
            if field_name not in new_fields:
                if self._should_process_field(field_info):
                    differences.eliminados.append(field_info)

        # Modified fields
        for field_name in new_fields:
            if field_name in previous_fields:
                prev_field = previous_fields[field_name]
                new_field = new_fields[field_name]

                if self._should_process_field(
                    new_field,
                ) and self._fields_are_different(prev_field, new_field):
                    differences.modificados.append(
                        InfoCambioCampo(
                            nombre=field_name,
                            info_antigua=prev_field,
                            info_nueva=new_field,
                        )
                    )

        return differences

    def _compare_relations(
        self,
        previous_relations: List[InfoRelacion],
        new_relations: List[InfoRelacion],
    ) -> InfoDiffRelaciones:
        """Compare relations between schemas."""
        differences = InfoDiffRelaciones()

        # Create sets of unique keys for comparison
        prev_keys = {
            self._generate_relation_key(
                rel,
            ): rel
            for rel in previous_relations
        }
        new_keys = {
            self._generate_relation_key(
                rel,
            ): rel
            for rel in new_relations
        }
        # Added relations
        for key, relation in new_keys.items():
            if key not in prev_keys:
                differences.agregadas.append(relation)

        # Removed relations
        for key, relation in prev_keys.items():
            if key not in new_keys:
                differences.eliminadas.append(relation)

        return differences

    def _compare_enums(
        self,
        previous_enums: Dict[str, InfoEnum],
        new_enums: Dict[str, InfoEnum],
    ) -> InfoDiffEnums:
        """Compare enums between schemas."""
        differences = InfoDiffEnums()

        # Added enums
        for enum_name, enum_info in new_enums.items():
            if enum_name not in previous_enums:
                differences.agregados.append(enum_info)

        # Removed enums
        for enum_name in previous_enums:
            if enum_name not in new_enums:
                differences.eliminados.append(enum_name)

        # Modified enums
        for enum_name in new_enums:
            if enum_name in previous_enums:
                prev_values = set(previous_enums[enum_name].valores)
                new_values = set(new_enums[enum_name].valores)

                if prev_values != new_values:
                    differences.modificados.append(
                        InfoCambioEnum(
                            nombre=enum_name,
                            valores_antiguos=list(sorted(prev_values)),
                            valores_nuevos=list(sorted(new_values)),
                            valores_agregados=list(
                                sorted(new_values - prev_values),
                            ),
                            valores_eliminados=list(
                                sorted(prev_values - new_values),
                            ),
                        )
                    )

        return differences

    def _should_process_field(
        self,
        field: InfoField,
    ) -> bool:
        """Check if a field is scalar or enum."""
        if field.tipo_campo in self.parser.get_type_mapping():
            return True

        ed = self._available_enums
        if ed and field.tipo_campo in ed:
            return True

        # Check for a relation directive with link: INLINE
        directives = field.directivas.get("relation", None)
        if directives is not None:
            if directives.argumentos.get("link", None) == "INLINE":
                return True

        return False

    def _fields_are_different(
        self,
        field1: InfoField,
        field2: InfoField,
    ) -> bool:
        """Check if two fields are different."""
        return (
            field1.tipo_campo != field2.tipo_campo
            or field1.es_lista != field2.es_lista
            or field1.es_requerido != field2.es_requerido
            or field1.directivas != field2.directivas
        )

    def _generate_relation_key(self, relation: InfoRelacion) -> str:
        """Generate unique key for a relation."""
        return (
            f"{relation.fuente.tabla_fuente}:"
            f"{relation.fuente.campo_fuente}:"
            f"{relation.objetivo.tabla_objetivo}:"
            f"{relation.nombre_relacion}"
        )

    def _show_migration_start(self, migration_id: str) -> None:
        """Show start of migration process."""
        self.console.print(
            f"\n🔄 Generating migration: {migration_id}", style="bold blue"
        )

    def _show_detected_differences(
        self,
        differences: InfoDiffEsquema,
    ) -> None:
        """Show differences detected between schemas."""
        tree = Tree("\n📋 Detected differences", style="bold green")

        # Tables
        if differences.tablas.agregadas:
            tree.add(
                f"➕ Added tables: {len(differences.tablas.agregadas)}",
            )
        if differences.tablas.eliminadas:
            tree.add(
                f"➖ Removed tables: {len(differences.tablas.eliminadas)}",
            )

        # Fields
        total_added_fields = sum(
            len(c.agregados) for c in differences.tablas.campos.values()
        )
        total_removed_fields = sum(
            len(c.eliminados) for c in differences.tablas.campos.values()
        )
        total_modified_fields = sum(
            len(c.modificados) for c in differences.tablas.campos.values()
        )

        if total_added_fields:
            tree.add(f"🔹 Added fields: {total_added_fields}")
        if total_removed_fields:
            tree.add(f"🔹 Removed fields: {total_removed_fields}")
        if total_modified_fields:
            tree.add(f"🔹 Modified fields: {total_modified_fields}")

        # Relations
        df = differences.relaciones
        if df.agregadas:
            tree.add(f"🔗 Added relations: {len(df.agregadas)}")
        if df.eliminadas:
            tree.add(f"🔗 Removed relations: {len(df.eliminadas)}")

        self.console.print(tree)

    def _show_migration_summary(self, num_statements: int) -> None:
        """Show final migration summary."""
        self.console.print(
            "\n✅ Migration generated successfully",
            style="bold green",
        )
        self.console.print(
            f"📊 Total SQL statements: {num_statements}",
            style="blue",
        )

    def _visualize_sql_operation(
        self, operation_type: str, description: str, sql: str
    ) -> None:
        """Visualize a specific SQL operation."""
        if self.print_output:
            tree = Tree(f"🔧 {operation_type}")
            tree.add(description)
            self.console.print(tree)

            if self.print_sql:
                syntax = Syntax(sql, "sql", theme="monokai", line_numbers=True)
                self.console.print(
                    Panel(
                        syntax,
                        title=f"SQL - {operation_type}",
                        border_style="yellow",
                    )
                )

    def _visualize_field_requirement(
        self,
        required: bool,
    ) -> str:
        """Visualize if a field is required or not."""
        if required:
            return ":exclamation_mark:"
        return ":question_mark:"

    def _generate_hash_schemas(self, schema1: str, schema2: str) -> str:
        """Generate unique hash for a pair of schemas."""
        content = f"{schema1}{schema2}"
        return hashlib.md5(content.encode("utf-8")).hexdigest()

    def _generate_migration_header(self) -> List[str]:
        """Generate migration header."""
        timestamp = datetime.datetime.now().isoformat()
        return [
            "-- Migration generated automatically",
            f"-- Date: {timestamp}",
            f"-- Database Type: {self.get_database_type().name}",
            "-- GraphQLStore CLI v3.0.0",
            "",
        ]

    def _determine_fk_table(self, relation: InfoRelacion) -> str:
        """Determine which table gets the foreign key."""
        if relation.tipo_relation in [
            TipoRelacion.MANY_TO_ONE.value,
            TipoRelacion.ONE_TO_MANY.value,
        ]:
            return (
                relation.objetivo.tabla_objetivo
                if relation.fuente.fuente_es_lista
                else relation.fuente.tabla_fuente
            )

        if relation.tipo_relation == TipoRelacion.ONE_TO_ONE.value:
            if relation.fuente.on_delete == OnDelete.CASCADE.value:
                return relation.fuente.tabla_fuente

            return relation.objetivo.tabla_objetivo

        return relation.fuente.tabla_fuente

    def _determine_fk_field(self, relation: InfoRelacion) -> str:
        """Determine the name of the foreign key field."""
        field_fk = relation.fuente.campo_fuente
        source_table = relation.fuente.tabla_fuente

        if relation.tipo_relation in [
            TipoRelacion.MANY_TO_ONE.value,
            TipoRelacion.ONE_TO_MANY.value,
        ]:
            field_fk = (
                source_table[0].lower() + source_table[1:]
                if relation.fuente.fuente_es_lista
                else relation.fuente.campo_fuente
            )
        else:
            if relation.fuente.on_delete == OnDelete.CASCADE.value and (
                relation.objetivo.on_delete_inverso != OnDelete.CASCADE.value
            ):
                field_fk = (
                    relation.fuente.campo_fuente
                    if not relation.objetivo.campo_inverso
                    else source_table[0].lower() + source_table[1:]
                )
            elif relation.fuente.on_delete != OnDelete.CASCADE.value and (
                relation.objetivo.on_delete_inverso == OnDelete.CASCADE.value
            ):
                if relation.objetivo.campo_inverso:
                    field_fk = relation.objetivo.campo_inverso
                else:
                    field_fk = relation.fuente.campo_fuente
        return field_fk

    def _search_tables_using_enum(
        self,
        enum_name: str,
    ) -> Dict[str, List[InfoField]]:
        """Find all tables and fields that use a specific enum."""
        tables_with_enum = {}

        for table_name, table_info in self._existing_tables.items():
            fields_with_enum = []

            for field in table_info.campos.values():
                if (
                    self._should_process_field(
                        field,
                    )
                    and field.tipo_campo == enum_name
                ):
                    fields_with_enum.append(field)

            if fields_with_enum:
                tables_with_enum[table_name] = fields_with_enum

        return tables_with_enum

    # Abstract methods that must be implemented by subclasses
    @abstractmethod
    def get_database_type(self) -> DatabaseType:
        """Get the database type for this generator."""

    @abstractmethod
    def _generate_sql_create_table(
        self, table_name: str, fields: List[InfoField]
    ) -> str:
        """Generate SQL to create a new table."""

    @abstractmethod
    def _generate_sql_add_field(
        self,
        table_name: str,
        field: InfoField,
    ) -> str:
        """Generate SQL to add a field."""

    @abstractmethod
    def _generate_sql_remove_field(
        self,
        table_name: str,
        field: InfoField,
    ) -> str:
        """Generate SQL to remove a field."""

    @abstractmethod
    def _generate_sql_modify_field(
        self, table_name: str, change: InfoCambioCampo
    ) -> str:
        """Generate SQL to modify a field."""

    @abstractmethod
    def _generate_sql_add_relation(self, relation: InfoRelacion) -> str:
        """Generate SQL to add a relation."""

    @abstractmethod
    def _generate_sql_remove_relation(self, relation: InfoRelacion) -> str:
        """Generate SQL to remove a relation."""

    @abstractmethod
    def _generate_sql_modify_enum(
        self,
        enum_modified: InfoCambioEnum,
    ) -> List[str]:
        """Generate SQL to modify an enum."""

    @abstractmethod
    def _generate_sql_remove_table(self, table_name: str) -> str:
        """Generate SQL to remove a table."""

    @abstractmethod
    def get_sql_type(self, field: InfoField) -> str:
        """Get SQL type for a field."""

    @abstractmethod
    def _generate_field_definition(self, field: InfoField) -> str:
        """Generate complete field definition."""

    @abstractmethod
    def _generate_sql_junction_table(self, relation: InfoRelacion) -> str:
        """Generate SQL for a junction table (N:M relation)."""

    @abstractmethod
    def _generate_sql_foreign_key(self, relation: InfoRelacion) -> str:
        """Generate SQL for a foreign key (1:1 and 1:N relations)."""
