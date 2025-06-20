"""Exceptiones personalizadas para GraphQL."""


class GraphQLStoreError(Exception):
    """Excepcion base para errores de GraphQLStore."""


class SchemaError(GraphQLStoreError):
    """Error en el parsing o validacion del esquema GraphQL."""


class RelationshipError(GraphQLStoreError):
    """Error en la configuracion o validacion de relaciones."""


class MigrationError(GraphQLStoreError):
    """Excepción para errores de migración."""


class SchemaComparisonError(MigrationError):
    """Excepción para errores en comparación de esquemas."""


class MigrationGenerationError(MigrationError):
    """Excepción para errores en generación de SQL de migración."""
