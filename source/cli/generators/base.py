"""Base module for database schema generators."""

from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Optional
from rich.console import Console
from rich.tree import Tree
from rich.syntax import Syntax
from rich.panel import Panel

from source.cli.graphql.exceptions import RelationshipError


from ..graphql.configuracion_y_constantes import (
    InfoEnum,
    InfoRelacion,
    InfoTabla,
    DatabaseType,
    OnDelete,
    TipoRelacion,
)


class BaseSchemaGenerator(ABC):
    """Base abstract class for database schema generators."""

    def __init__(self):
        self.console = Console()
        self.schema_sql = []
        self.print_output = None
        self.print_sql = None

    @abstractmethod
    def get_type_mapping(self) -> Dict[str, str]:
        """Return the mapping of GraphQL types to SQL types specific to
        the database engine."""

    @abstractmethod
    def get_engine_specific_settings(self) -> str:
        """Retorna configuraciones específicas del motor de base de datos."""

    @abstractmethod
    def get_table_creation_template(self) -> str:
        """Return the template for creating tables specific \
            to the database engine."""

    @abstractmethod
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
        """Return the template for creating foreign keys specific \
            to the database engine."""

    @abstractmethod
    def get_unique_constraint_template(self) -> str:
        """Return the template for unique constraints specific \
            to the database engine."""

    @abstractmethod
    def get_primary_key_column(self) -> str:
        """Return the definition of primary key column specific \
            to the database engine."""

    @abstractmethod
    def format_enum_values(self, valores: List[str]) -> str:
        """Format enum values specific to the database engine."""

    @abstractmethod
    def get_database_type(self) -> DatabaseType:
        """Return the type of database handled by this generator."""

    def generate_schema(
        self,
        tables: Dict[str, InfoTabla],
        enums: Dict[str, InfoEnum],
        relationships: List[InfoRelacion],
        print_output: bool = True,
        print_sql: bool = True,
    ) -> str:
        # pylint: disable=too-many-arguments,too-many-positional-arguments
        """Generates a database schema from a GraphQL schema."""
        schema_sql = []

        self.print_output = print_output
        self.print_sql = print_sql

        # generate tables
        tabla_sql = self._generate_tables(
            tables,
            enums,
            print_output,
            print_sql,
        )
        schema_sql.append(tabla_sql)

        # generate relationships
        relationships_sql = self._generate_relationships(
            tables,
            relationships,
        )
        schema_sql.append(relationships_sql)

        # join all SQL statements
        join_schema_sql = "\n\n".join(schema_sql)

        return join_schema_sql
        # pylint: enable=too-many-arguments,too-many-positional-arguments

    def get_schema_sql(self) -> str:
        """Get the generated SQL schema."""
        return "\n\n".join(self.schema_sql)

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

    def _generate_relationship_inline(
        self,
        relationship: InfoRelacion,
        tables: Dict[str, InfoTabla],
        get_foreign_key_template: Callable,
    ) -> str:
        """Generar relaciones inline para MySQL."""
        table_fk = self._determine_fk_table(relationship)
        field_fk = self._determine_fk_field(relationship)

        table_ref = (
            relationship.objetivo.tabla_objetivo
            if table_fk == relationship.fuente.tabla_fuente
            else relationship.fuente.tabla_fuente
        )

        current_on_delete = self._get_current_on_delete(relationship)

        rel_type = relationship.tipo_relation
        source_table = relationship.fuente.tabla_fuente
        source_is_list = relationship.fuente.fuente_es_lista
        nom_constraint_source = relationship.fuente.nombre_constraint_fuente
        source_field = relationship.fuente.campo_fuente

        target_table = relationship.objetivo.tabla_objetivo

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

        sql_alter = get_foreign_key_template(
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

    def _get_current_on_delete(
        self,
        relationship: InfoRelacion,
    ) -> Optional[str]:
        """Get the current on_delete action for the relationship."""
        rel_type = relationship.tipo_relation
        on_delete = relationship.fuente.on_delete
        on_delete_inverse = relationship.objetivo.on_delete_inverso

        current_on_delete = None

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
        return current_on_delete

    @abstractmethod
    def _generate_tables(
        self,
        tables: Dict[str, InfoTabla],
        enums: Dict[str, InfoEnum],
        print_output: bool = True,
        print_sql: bool = True,
    ) -> str:
        """Generates the SQL statements to create tables."""

    @abstractmethod
    def _generate_table(
        self,
        table_name: str,
        table_info: InfoTabla,
        enums: Dict[str, InfoEnum],
    ) -> str:
        """Generates the SQL statement to create a table."""

    @abstractmethod
    def _generate_relationships(
        self,
        tables: Dict[str, InfoTabla],
        relationships: List[InfoRelacion],
    ) -> str:
        """Generates the SQL statements to create relationships."""

    @abstractmethod
    def _generate_relationship(
        self,
        relationship: InfoRelacion,
        tables: Dict[str, InfoTabla],
    ) -> Optional[str]:
        """Generates the SQL statement to create a relationship."""

    def _print_output_tables(
        self,
        table_name: str,
        table_info: InfoTabla,
        table_sql: str,
        print_sql: bool = True,
    ) -> None:
        """Print the output of the generated schema (common implementation)."""

        tree_tabla = Tree(
            f"\n [bold green]Creating Type [magenta]{table_name}[/magenta]"
        )

        for nombre_campo, info_campo in table_info.campos.items():
            tree_tabla.add(
                f"Creating Type [magenta]{nombre_campo}[/magenta] "
                f"of type [magenta]{info_campo.tipo_campo}"
            )

        self.console.print(tree_tabla)

        if print_sql:
            syntax = Syntax(
                table_sql,
                "sql",
                theme="monokai",
                line_numbers=True,
            )
            msg_sql = f"SQL for the {table_name} table"
            self.console.print(
                Panel(syntax, title=msg_sql, border_style="blue"),
            )

        msg = f"Type `{table_name}` created successfully :white_check_mark:"
        self.console.print(msg, style="bold green")

    def _print_output_relationships(
        self,
        relationship: InfoRelacion,
        data_sql: str,
        print_output: bool = True,
        print_sql: bool = True,
        sql_name: str | None = None,
    ) -> None:
        # pylint: disable=too-many-arguments, too-many-positional-arguments
        """Visualize the output of the generated relationships \
            (common implementation)."""
        if print_output:
            fuente = relationship.fuente.tabla_fuente
            objetivo = relationship.objetivo.tabla_objetivo
            if relationship.tipo_relation == TipoRelacion.MANY_TO_MANY.value:
                msg_relacion = (
                    f"[bold magenta]{fuente}[/bold magenta] - "
                    f"[bold magenta]{objetivo}[/bold magenta]"
                )
                titulo_sql = f"SQL para la tabla junction {sql_name}"
            elif relationship.tipo_relation in [
                TipoRelacion.ONE_TO_ONE.value,
                TipoRelacion.MANY_TO_ONE.value,
            ]:
                msg_relacion = (
                    f"[bold magenta]{fuente}[/bold magenta] adding to "
                    f"[bold magenta]{objetivo}[/bold magenta] "
                )
                titulo_sql = f"SQL for the relationship in {sql_name}"
            else:  # one to many
                msg_relacion = (
                    f"[bold magenta]{objetivo}[/bold magenta] adding to "
                    f"[bold magenta]{fuente}[/bold magenta] "
                )
                titulo_sql = f"SQL for the {sql_name} relationship"

            tree = Tree(
                f"\n [bold green] Creating relacionship"
                f"([magenta]{relationship.tipo_relation}[/magenta]) "
                f"{msg_relacion}[/bold green]"
            )
            self.console.print(tree)

            if print_sql:
                syntax = Syntax(
                    data_sql,
                    "sql",
                    theme="monokai",
                    line_numbers=True,
                )
                self.console.print(
                    Panel(
                        syntax,
                        title=titulo_sql,
                        border_style="yellow",
                    )
                )

            msg = (
                f"Relationship [magenta]{fuente}[/magenta] - "
                f"[magenta]{objetivo}[/magenta] "
                "created successfull :white_check_mark:"
            )
            self.console.print(msg, style="bold green")
        # pylint: enable=too-many-arguments, too-many-positional-arguments
