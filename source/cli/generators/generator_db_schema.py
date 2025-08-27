"""Refactored module that maintains backward compatibility."""

from typing import Dict, List
from ..graphql.configuracion_y_constantes import (
    InfoEnum,
    InfoRelacion,
    InfoTabla,
    DatabaseType,
)
from .factory import GeneratorSchemaFactory


class GeneratorDBSchema:
    """Class to generate schemas for databases (refactored).

    This class keep backward compatibility while using internally
    the new pattern-based generator system.
    """

    def __init__(self, db_type: DatabaseType = DatabaseType.MYSQL):
        """Inicializate the generator with the specified database type."""
        self._generator = GeneratorSchemaFactory.create_generator(db_type)
        self.db_type = db_type

    @property
    def console(self):
        """Access to the internal generator console."""
        return self._generator.console

    @property
    def schema_sql(self):
        """Access to the generated SQL schema (maintains original name)."""
        return self._generator.schema_sql

    @property
    def print_output(self):
        """Access to the output display configuration."""
        return self._generator.print_output

    @print_output.setter
    def print_output(self, value):
        """Configure the output display setting."""
        self._generator.print_output = value

    @property
    def print_sql(self):
        """Access to the SQL display configuration \
            (maintains original name)."""
        return self._generator.print_sql

    @print_sql.setter
    def print_sql(self, value):
        """Configure the SQL display setting."""
        self._generator.print_sql = value

    def generate_schema(
        self,
        tables: Dict[str, InfoTabla],
        enums: Dict[str, InfoEnum],
        relationships: List[InfoRelacion],
        print_output: bool = True,
        print_sql: bool = True,
    ) -> str:
        # pylint: disable=too-many-arguments, too-many-positional-arguments
        """Generate database schema from a GraphQL schema."""
        return self._generator.generate_schema(
            tables=tables,
            enums=enums,
            relationships=relationships,
            print_output=print_output,
            print_sql=print_sql,
        )

    def get_schema_sql(self) -> str:
        """Get the generated SQL schema."""
        return self._generator.get_schema_sql()

    @classmethod
    def create_for_mysql(cls):
        """Create a generator specifically for MySQL."""
        return cls(DatabaseType.MYSQL)

    @classmethod
    def create_for_postgresql(cls):
        """Create a generator specifically for PostgreSQL."""
        return cls(DatabaseType.POSTGRESQL)

    def get_db_type(self) -> DatabaseType:
        """Get the  database type of the generator."""
        return self.db_type
