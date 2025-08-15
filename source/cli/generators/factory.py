"""Factory para crear generadores de esquemas de base de datos."""

from typing import Type
from ..graphql.configuracion_y_constantes import DatabaseType
from .base import BaseSchemaGenerator
from .mysql_generator import GeneratorSchemaMySQL
from .postgresql_generator import GeneratorSchemaPostgreSQL


class GeneratorSchemaFactory:
    """Factory for creating database schema generators based \
        on the type of database."""

    _generators = {
        DatabaseType.MYSQL: GeneratorSchemaMySQL,
        DatabaseType.POSTGRESQL: GeneratorSchemaPostgreSQL,
    }

    @classmethod
    def create_generator(cls, db_type: DatabaseType) -> BaseSchemaGenerator:
        """Create the appropriate generator based on the type of database."""
        if db_type not in cls._generators:
            tipos_soportados = ", ".join([t.name for t in cls._generators])
            raise ValueError(
                f"Database type not supported: {db_type.value}. "
                f"Database types supported: {tipos_soportados}"
            )

        generador_class = cls._generators[db_type]
        return generador_class()

    @classmethod
    def get_supported_types(cls) -> list[DatabaseType]:
        """Get the list of supported database types."""
        return list(cls._generators.keys())

    @classmethod
    def register_generator(
        cls,
        db_type: DatabaseType,
        class_generator: Type[GeneratorSchemaMySQL],
    ) -> None:
        """Register a new generator for a database type."""
        cls._generators[db_type] = class_generator
