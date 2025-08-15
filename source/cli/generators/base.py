"""Base module for database schema generators."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from rich.console import Console
from rich.tree import Tree
from rich.syntax import Syntax
from rich.panel import Panel


from ..graphql.configuracion_y_constantes import (
    InfoEnum,
    InfoRelacion,
    InfoTabla,
    DatabaseType,
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
