"""Generador de esquemas PostgreSQL."""

from typing import Dict, List, Optional
from ..graphql.configuracion_y_constantes import (
    InfoEnum,
    InfoRelacion,
    InfoTabla,
    TipoField,
    TipoLink,
    TipoRelacion,
    OnDelete,
    DatabaseType,
)
from ..graphql.exceptions import RelationshipError
from .base import BaseSchemaGenerator


class GeneratorSchemaPostgreSQL(BaseSchemaGenerator):
    """Generator of specific schemas for PostgreSQL."""

    def get_database_type(self) -> DatabaseType:
        """Return the database type PostgreSQL."""
        return DatabaseType.POSTGRESQL

    def get_type_mapping(self) -> Dict[str, str]:
        """Return the mapping of GraphQL types to PostgreSQL types."""
        return {
            TipoField.ID.value: "VARCHAR(25)",
            TipoField.STRING.value: "VARCHAR(255)",
            TipoField.INT.value: "INTEGER",
            TipoField.FLOAT.value: "DECIMAL(10, 2)",
            TipoField.BOOLEAN.value: "BOOLEAN",
            TipoField.DATETIME.value: "TIMESTAMP",
            TipoField.JSON.value: "JSONB",
        }

    def get_engine_specific_settings(self) -> str:
        """Return specific settings for PostgreSQL."""
        # PostgreSQL does not require additional settings
        return ""

    def get_table_creation_template(self) -> str:
        """Return the template for creating tables in PostgreSQL."""
        return "CREATE TABLE {table_name} (\n{columns}\n);"

    def get_junction_table_template(
        self,
        rel: InfoRelacion,
    ) -> str:
        """Return the template for creating junction tables in MySQL."""
        source_rel, target_rel = rel.fuente, rel.objetivo
        source_table = source_rel.tabla_fuente
        target_table = target_rel.tabla_objetivo

        s_t_fld = source_table[0].lower() + source_table[1:]
        t_t_fld = target_table[0].lower() + target_table[1:]

        is_self_relation = source_table == target_table

        s_t_sfx = "id" if not is_self_relation else "A"
        t_t_sfx = "id" if not is_self_relation else "B"

        on_delete = source_rel.on_delete
        on_delete_inv = target_rel.on_delete_inverso

        return (
            f"CREATE TABLE {rel.nombre_relacion} ("
            f"  `{s_t_fld}_{s_t_sfx}` VARCHAR(25) NOT NULL,\n"
            f"  `{t_t_fld}_{t_t_sfx}` VARCHAR(25) NOT NULL,\n"
            f"PRIMARY KEY (`{s_t_fld}_{s_t_sfx}`, `{t_t_fld}_{t_t_sfx}`),\n"
            f"CONSTRAINT `{source_rel.nombre_constraint_fuente}`"
            f" FOREIGN KEY (`{s_t_fld}_{s_t_sfx}`)"
            f" REFERENCES `{source_table}`(id) ON DELETE {on_delete},\n"
            f"CONSTRAINT `{target_rel.nombre_constraint_objetivo}`"
            f" FOREIGN KEY (`{t_t_fld}_{t_t_sfx}`)"
            f" REFERENCES `{target_table}`(id) ON DELETE {on_delete_inv}\n"
            f") {self.get_engine_specific_settings()};"
        )

    def get_foreign_key_template(
        self,
        table_fk: str,
        field_fk: str,
        unique: str,
        constraint: str,
        table_ref: str,
        on_delete: str,
        is_null: str,
    ) -> str:
        """Return the template for creating foreign keys in PostgreSQL."""
        return (
            f"ALTER TABLE `{table_fk}`\n"
            f" ADD COLUMN `{field_fk}_id` VARCHAR(25){unique}{is_null},\n"
            f" ADD CONSTRAINT `{constraint}`"
            f" FOREIGN KEY (`{field_fk}_id`)"
            f" REFERENCES `{table_ref}`(id){on_delete};"
        )

    def get_unique_constraint_template(self) -> str:
        """Return the template for unique constraints in PostgreSQL."""
        return "CONSTRAINT uk_{uk_column_name} UNIQUE ({column_name})"

    def get_primary_key_column(self) -> str:
        """Return the primary key column definition for PostgreSQL."""
        return "id VARCHAR(25) NOT NULL PRIMARY KEY"

    def format_enum_values(self, valores: List[str]) -> str:
        """Format enum values for PostgreSQL."""
        # PostgreSQL mange enums of a different way
        # created them as custom types
        return "VARCHAR(50)"  # Fallback a VARCHAR for simplicity

    def _generate_tables(
        self,
        tables: Dict[str, InfoTabla],
        enums: Dict[str, InfoEnum],
        print_output: bool = True,
        print_sql: bool = True,
    ) -> str:
        """Generate the table definitions for PostgreSQL."""
        schema_tables = []

        # first generate enum types if they exist
        for enum_name, enum_info in enums.items():
            enum_sql = self._generate_enum_type(enum_name, enum_info)
            schema_tables.append(enum_sql)

        # then generate the tables
        for table_name, table_info in tables.items():
            table_sql = self._generate_table(table_name, table_info, enums)

            if table_sql:
                schema_tables.append(table_sql)

                if print_output:
                    self._print_output_tables(
                        table_name,
                        table_info,
                        table_sql,
                        print_sql,
                    )

        return "\n\n".join(schema_tables)

    def _generate_enum_type(self, enum_name: str, enum_info: InfoEnum) -> str:
        """Generate a custom ENUM type for PostgreSQL."""
        enm_vls = ", ".join([f"'{valor}'" for valor in enum_info.valores])
        return f"CREATE TYPE {enum_name.lower()}_type AS ENUM " f"({enm_vls});"

    def _generate_relationships(
        self,
        tables: Dict[str, InfoTabla],
        relationships: List[InfoRelacion],
    ) -> str:
        """Generate the SQL statements to create relationships."""
        scheme_relationships = []

        for relationship in relationships:
            relation_sql = self._generate_relationship(relationship, tables)

            if relation_sql:
                scheme_relationships.append(relation_sql)

        return "\n\n".join(scheme_relationships)

    def _generate_relationship(
        self,
        relationship: InfoRelacion,
        tables: Dict[str, InfoTabla],
    ) -> Optional[str]:
        """Generate the SQL statement to create a relationship \
            in PostgreSQL."""
        processed_junction_tables: set[str] = set()

        # process relationship
        relation_type = relationship.tipo_relation
        link_type = relationship.tipo_link

        if (
            relation_type == TipoRelacion.MANY_TO_MANY.value
            and link_type == TipoLink.TABLE.value
        ):
            return self._generate_table_junction_postgresql(
                relationship,
                processed_junction_tables,
            )

        if (
            relation_type
            in [
                TipoRelacion.ONE_TO_ONE.value,
                TipoRelacion.MANY_TO_ONE.value,
                TipoRelacion.ONE_TO_MANY.value,
            ]
            and link_type == TipoLink.INLINE.value
        ):
            return self._generate_relationships_inline_postgresql(
                relationship,
                tables,
            )

        return None

    def _generate_table_junction_postgresql(
        self,
        relationship: InfoRelacion,
        processed_junction_tables: set,
    ) -> Optional[str]:
        """Generate a junction table for many-to-many relationships \
            in PostgreSQL."""

        junction_name = relationship.nombre_relacion

        # skip if already processed
        if junction_name in processed_junction_tables:
            return None

        processed_junction_tables.add(junction_name)

        sql = self.get_junction_table_template(relationship)

        self._print_output_relationships(
            relationship,
            data_sql=sql,
            print_output=self.print_output,
            print_sql=self.print_sql,
            sql_name=junction_name,
        )

        return sql

    def _generate_relationships_inline_postgresql(
        self,
        relationship: InfoRelacion,
        tables: Dict[str, InfoTabla],
    ) -> str:
        """Generar relaciones inline para PostgreSQL."""
        table_fk = self._determine_fk_table(relationship)
        field_fk = self._determine_fk_field(relationship)

        table_ref = (
            relationship.objetivo.tabla_objetivo
            if table_fk == relationship.fuente.tabla_fuente
            else relationship.fuente.tabla_fuente
        )

        current_on_delete = None

        rel_type = relationship.tipo_relation
        source_table = relationship.fuente.tabla_fuente
        source_is_list = relationship.fuente.fuente_es_lista
        nom_constraint_source = relationship.fuente.nombre_constraint_fuente
        source_field = relationship.fuente.campo_fuente
        on_delete = relationship.fuente.on_delete

        target_table = relationship.objetivo.tabla_objetivo
        on_delete_inverse = relationship.objetivo.on_delete_inverso

        if rel_type == TipoRelacion.MANY_TO_ONE.value:
            current_on_delete = on_delete_inverse
        elif rel_type == TipoRelacion.ONE_TO_MANY.value:
            current_on_delete = on_delete
        elif rel_type == TipoRelacion.ONE_TO_ONE.value:
            if (
                on_delete == OnDelete.CASCADE.value
                and on_delete_inverse != OnDelete.CASCADE.value
            ):
                current_on_delete = on_delete
            elif (
                on_delete != OnDelete.CASCADE.value
                and on_delete_inverse == OnDelete.CASCADE.value
            ):
                current_on_delete = on_delete_inverse
        else:
            raise RelationshipError(
                f"Relation type don't supported: {rel_type} "
                f"for {relationship.nombre_relacion}"
            )

        if current_on_delete == OnDelete.CASCADE.value:
            on_delete_action = " ON DELETE CASCADE"
        else:
            on_delete_action = " ON DELETE SET NULL"

        unique = " UNIQUE" if rel_type == TipoRelacion.ONE_TO_ONE.value else ""

        # verify if the field is required
        is_required = False
        if rel_type == TipoRelacion.MANY_TO_ONE.value and source_is_list:
            if (
                relationship.objetivo.campo_inverso
                and tables[target_table]
                .campos[relationship.objetivo.campo_inverso]
                .es_requerido
            ):
                is_required = True
        elif (
            not source_is_list
            and tables[source_table].campos[source_field].es_requerido
        ):
            is_required = True

        is_null = "" if not is_required else " NOT NULL"

        sql_alter = self.get_foreign_key_template(
            table_fk=table_fk,
            field_fk=field_fk,
            unique=unique,
            constraint=nom_constraint_source,
            table_ref=table_ref,
            on_delete=on_delete_action,
            is_null=is_null,
        )

        self._print_output_relationships(
            relationship,
            data_sql=sql_alter,
            print_output=self.print_output,
            print_sql=self.print_sql,
            sql_name=table_fk,
        )

        return sql_alter

    def _generate_table(
        self,
        table_name: str,
        table_info: InfoTabla,
        enums: Dict[str, InfoEnum],
    ) -> str:
        """Generate the SQL statement to create a table in PostgreSQL."""
        columns = []
        indexs = []
        has_primary_key = False

        table_sql = f"CREATE TABLE {table_name} (\n"

        for field_name, info_campo in table_info.campos.items():
            field_type = info_campo.tipo_campo
            directivas = info_campo.directivas

            # skip if not a scalar field or enum
            if not TipoField.existe(field_type) and field_type not in enums:
                continue

            column_name = field_name

            if "db" in directivas and "rename" in directivas["db"].argumentos:
                column_name = directivas["db"].argumentos["rename"]

            # define the SQL type based on the field type
            sql_type = self.get_type_mapping().get(field_type, "TEXT")
            if field_type in enums:
                # Usar el tipo personalizado de enum
                sql_type = f"{field_type.lower()}_enum_type"

            if info_campo.es_lista:
                sql_type = "JSONB"

            # build the column definition
            def_column = f"  {column_name} {sql_type}"

            # add NOT NULL if required
            if info_campo.es_requerido:
                def_column += " NOT NULL"

            if "id" in directivas:
                def_column += " PRIMARY KEY"
                has_primary_key = True

            dft = "default" in directivas

            if dft and "value" in directivas["default"].argumentos:
                if sql_type in (
                    "TEXT",
                    "VARCHAR(255)",
                ) or ("_enum_type" in sql_type):
                    def_column += " DEFAULT '"
                    valor_default = directivas["default"].argumentos["value"]
                    def_column += f"{valor_default}'"
                else:
                    def_column += (
                        f" DEFAULT {directivas['default'].argumentos['value']}"
                    )

            if "createdAt" in directivas:
                def_column += " DEFAULT CURRENT_TIMESTAMP"

            if "updatedAt" in directivas:
                def_column += " DEFAULT CURRENT_TIMESTAMP"
                # PostgreSQL usa triggers para auto-update

            columns.append(def_column)

            if "unique" in directivas:
                sql = self.get_unique_constraint_template().format(
                    uk_column_name=column_name,
                    column_name=column_name,
                )
                indexs.append(sql)

        if not has_primary_key:
            columns.insert(0, f"  {self.get_primary_key_column()}")

        table_sql += ",\n".join(columns)
        if indexs:
            table_sql += ",\n" + ",\n".join(indexs)
        table_sql += "\n);"

        self.schema_sql.append(table_sql)

        return table_sql

    def _determine_fk_table(self, relation: InfoRelacion) -> str:
        """Determinar en qué tabla va la foreign key."""
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
        """Determinar nombre del campo foreign key."""
        fk_field = relation.fuente.campo_fuente
        source_table = relation.fuente.tabla_fuente

        if relation.tipo_relation in [
            TipoRelacion.MANY_TO_ONE.value,
            TipoRelacion.ONE_TO_MANY.value,
        ]:
            fk_field = (
                source_table[0].lower() + source_table[1:]
                if relation.fuente.fuente_es_lista
                else relation.fuente.campo_fuente
            )
        else:
            if relation.fuente.on_delete == OnDelete.CASCADE.value and (
                relation.objetivo.on_delete_inverso != OnDelete.CASCADE.value
            ):
                fk_field = (
                    relation.fuente.campo_fuente
                    if not relation.objetivo.campo_inverso
                    else source_table[0].lower() + source_table[1:]
                )
            elif relation.fuente.on_delete != OnDelete.CASCADE.value and (
                relation.objetivo.on_delete_inverso == OnDelete.CASCADE.value
            ):
                if relation.objetivo.campo_inverso:
                    fk_field = relation.objetivo.campo_inverso
                else:
                    fk_field = relation.fuente.campo_fuente
        return fk_field
