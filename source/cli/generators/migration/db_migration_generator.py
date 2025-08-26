""" Wrapper for backward compatibility with original \
    mysql_migracion module. """

from typing import Optional

from .migration_factory import MigrationGeneratorFactory
from ...graphql.configuracion_y_constantes import (
    DatabaseType,
    InfoDiffEsquema,
    InfoMigracion,
)


class GeneratorDBMigration:
    """Wrapper for backward compatibility with original \
        mysql_migracion module."""

    def __init__(self, db_type: DatabaseType = DatabaseType.MYSQL):
        """Initialize the migration generator with the specified \
            database type."""
        self._generator = MigrationGeneratorFactory.create_generator(db_type)
        self.db_type = db_type

    @property
    def console(self):
        """Access to the internal generator console."""
        return self._generator.console

    @property
    def migration_sql(self):
        """Access to the generated SQL migration (maintains original name)."""
        return self._generator.migration_sql

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

    def generar_migracion(
        self,
        previous_schema: str,
        new_schema: str,
        migration_id: Optional[str] = None,
        print_output: bool = True,
        print_sql: bool = True,
    ) -> InfoMigracion:
        """Generate migration for backward compatibility."""
        return self._generator.generate_migration(
            previous_schema,
            new_schema,
            migration_id,
            print_output,
            print_sql,
        )

    def diff_schemas(
        self,
        schema_actual: str,
        schema_nuevo: str,
    ) -> InfoDiffEsquema:
        """Compare schemas for backward compatibility."""
        return self._generator.diff_schemas(schema_actual, schema_nuevo)

    def generar_sql_migracion(self, diff_schema: InfoDiffEsquema) -> str:
        """Generate SQL migration for backward compatibility."""
        return self._generator.generate_sql_migration(diff_schema)

    def get_migration_sql(self) -> list:
        """Get the generated SQL migration."""
        return self._generator.migrations_sql

    def get_db_type(self) -> DatabaseType:
        """Get the database type."""
        return self.db_type

    @classmethod
    def create_for_mysql(cls):
        """Create a migration generator specifically for MySQL."""
        return cls(DatabaseType.MYSQL)

    @classmethod
    def create_for_postgresql(cls):
        """Create a migration generator specifically for PostgreSQL."""
        return cls(DatabaseType.POSTGRESQL)
