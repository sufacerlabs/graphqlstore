"""Generator of MySQL schemas."""

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


class GeneratorSchemaMySQL(BaseSchemaGenerator):
    """Generator of specific schemas for MySQL."""

    def get_database_type(self) -> DatabaseType:
        """Return the type of MySQL database."""
        return DatabaseType.MYSQL

    def get_type_mapping(self) -> Dict[str, str]:
        """Return the mapping of GraphQL types to MySQL types."""
        return {
            TipoField.ID.value: "VARCHAR(25)",
            TipoField.STRING.value: "VARCHAR(255)",
            TipoField.INT.value: "INT",
            TipoField.FLOAT.value: "DECIMAL(10, 2)",
            TipoField.BOOLEAN.value: "BOOLEAN",
            TipoField.DATETIME.value: "DATETIME",
            TipoField.JSON.value: "JSON",
        }

    def get_engine_specific_settings(self) -> str:
        """Return MySQL-specific engine settings."""
        return "ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"

    def get_table_creation_template(self) -> str:
        """Return the template for creating tables in MySQL."""
        return "CREATE TABLE {t_name} (\n{columns}\n) {engine_settings};"

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
        # pylint: disable=too-many-arguments, too-many-positional-arguments
        """Return the template for creating foreign keys in MySQL."""
        # constraint = f"ADD CONSTRAINT `{constraint}`" if constraint else ""
        return (
            f"ALTER TABLE `{table_fk}`\n"
            f" ADD COLUMN `{field_fk}_id` VARCHAR(25){unique}{is_null},\n"
            f" ADD CONSTRAINT `{constraint}`"
            f" FOREIGN KEY (`{field_fk}_id`)"
            f" REFERENCES `{table_ref}`(id){on_delete};"
        )
        # pylint: enable=too-many-arguments, too-many-positional-arguments

    def get_unique_constraint_template(self) -> str:
        """Return the template for unique constraints in MySQL."""
        return "UNIQUE KEY `uk_{uk_column_name}` (`{column_name}`)"

    def get_primary_key_column(self) -> str:
        """Return the primary key column definition for MySQL."""
        return "`id` VARCHAR(25) NOT NULL PRIMARY KEY"

    def format_enum_values(self, valores: List[str]) -> str:
        """Formats enum values for MySQL."""
        valores_enum = ", ".join([f"'{valor}'" for valor in valores])
        return f"ENUM({valores_enum})"

    def _generate_tables(
        self,
        tables: Dict[str, InfoTabla],
        enums: Dict[str, InfoEnum],
        print_output: bool = True,
        print_sql: bool = True,
    ) -> str:
        """Generate SQL statements to create tables."""
        schema_tables = []

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

    def _generate_relationships(
        self,
        tables: Dict[str, InfoTabla],
        relationships: List[InfoRelacion],
    ) -> str:
        """Generate SQL statements to create relationships."""
        schema_relationships = []

        for relation in relationships:
            relation_sql = self._generate_relationship(relation, tables)

            if relation_sql:
                schema_relationships.append(relation_sql)

        return "\n\n".join(schema_relationships)

    def _generate_relationship(
        self,
        relationship: InfoRelacion,
        tables: Dict[str, InfoTabla],
    ) -> Optional[str]:
        """Generate the SQL statement to create a relationship."""
        processed_junction_tables: set[str] = set()

        # process the relationship
        rel_type = relationship.tipo_relation
        link_type = relationship.tipo_link

        if (
            rel_type == TipoRelacion.MANY_TO_MANY.value
            and link_type == TipoLink.TABLE.value
        ):
            return self._generate_junction_table_mysql(
                relationship,
                processed_junction_tables,
            )

        if (
            rel_type
            in [
                TipoRelacion.ONE_TO_ONE.value,
                TipoRelacion.MANY_TO_ONE.value,
                TipoRelacion.ONE_TO_MANY.value,
            ]
            and link_type == TipoLink.INLINE.value
        ):
            return self._generate_relationship_inline_mysql(
                relationship,
                tables,
            )
        return None

    def _generate_junction_table_mysql(
        self,
        relationship: InfoRelacion,
        processed_junction_tables: set,
    ) -> Optional[str]:
        """Generate a junction table for many-to-many \
            relationships in MySQL."""

        junction_name = relationship.nombre_relacion

        # skip if it has already been processed
        if junction_name in processed_junction_tables:
            return None

        processed_junction_tables.add(junction_name)

        sql = self.get_junction_table_template(
            relationship,
        )

        self._print_output_relationships(
            relationship=relationship,
            data_sql=sql,
            print_output=self.print_output,
            print_sql=self.print_sql,
            sql_name=junction_name,
        )
        return sql

    def _generate_relationship_inline_mysql(
        self,
        relationship: InfoRelacion,
        tables: Dict[str, InfoTabla],
    ) -> str:
        """Generar relaciones inline para MySQL."""
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
                f"Relationship type not supported: {rel_type} "
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
            relationship=relationship,
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
        """Generate the SQL statement to create a table in MySQL."""
        columns = []
        indexs = []
        has_primary_key = False

        for field_name, field_info in table_info.campos.items():
            field_type = field_info.tipo_campo
            directives = field_info.directivas

            # skip if its a scalar field or enum
            if not TipoField.existe(field_type) and field_type not in enums:
                continue

            column_name = field_name

            if "db" in directives and "rename" in directives["db"].argumentos:
                column_name = directives["db"].argumentos["rename"]

            # define  the SQL data type
            tipo_sql = self.get_type_mapping().get(field_type, "TEXT")
            if field_type in enums:
                tipo_sql = self.format_enum_values(enums[field_type].valores)

            if field_info.es_lista:
                tipo_sql = "JSON"

            # build the column definition
            def_column = f"  `{column_name}` {tipo_sql}"

            # add NOT NULL if required
            if field_info.es_requerido:
                def_column += " NOT NULL"

            if "id" in directives:
                def_column += " PRIMARY KEY"
                has_primary_key = True

            dft = "default" in directives

            if dft and "value" in directives["default"].argumentos:
                if tipo_sql in ("TEXT", "VARCHAR(255)") or (
                    tipo_sql.startswith("ENUM")
                ):
                    def_column += " DEFAULT '"
                    valor_default = directives["default"].argumentos["value"]
                    def_column += f"{valor_default}'"
                else:
                    def_column += (
                        f" DEFAULT {directives['default'].argumentos['value']}"
                    )

            if "createdAt" in directives:
                def_column += " DEFAULT CURRENT_TIMESTAMP"

            if "updatedAt" in directives:
                def_column += " DEFAULT CURRENT_TIMESTAMP "
                def_column += "ON UPDATE CURRENT_TIMESTAMP"

            columns.append(def_column)

            if "unique" in directives:
                sql = self.get_unique_constraint_template().format(
                    uk_column_name=field_name,
                    column_name=column_name,
                )
                indexs.append(sql)

        if not has_primary_key:
            columns.insert(0, f"  {self.get_primary_key_column()}")

        joined_columns = ",\n".join(columns)
        if indexs:
            joined_indexs = ",\n".join(indexs)
            joined_columns += ",\n" + joined_indexs

        table_sql = self.get_table_creation_template().format(
            t_name=table_name,
            columns=joined_columns,
            engine_settings=self.get_engine_specific_settings(),
        )

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
