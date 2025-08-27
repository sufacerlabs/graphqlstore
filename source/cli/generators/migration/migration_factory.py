"""Migration generator factory and wrapper for backward compatibility."""

from typing import Type

from ...graphql.configuracion_y_constantes import DatabaseType

from .migration_base import BaseMigrationGenerator
from .migration_mysql import MySQLMigrationGenerator
from .migration_postgresql import PostgreSQLMigrationGenerator


class MigrationGeneratorFactory:
    """Factory to create appropriate migration generator \
        based on database type."""

    _generators = {
        DatabaseType.MYSQL: MySQLMigrationGenerator,
        DatabaseType.POSTGRESQL: PostgreSQLMigrationGenerator,
    }

    @classmethod
    def create_generator(cls, db_type: DatabaseType) -> BaseMigrationGenerator:
        """Create the appropriate generator based on the type of database."""
        if db_type not in cls._generators:
            tipos_soportados = ", ".join([t.name for t in cls._generators])
            raise ValueError(
                f"Database type not supported: {db_type.value}. "
                f"Database types supported: {tipos_soportados}"
            )

        generator_class = cls._generators[db_type]
        return generator_class()

    @classmethod
    def get_supported_types(cls) -> list[DatabaseType]:
        """Get the list of supported database types."""
        return list(cls._generators.keys())

    @classmethod
    def register_generator(
        cls,
        db_type: DatabaseType,
        class_generator: Type[BaseMigrationGenerator],
    ) -> None:
        """Register a new generator for a database type."""
        cls._generators[db_type] = class_generator
