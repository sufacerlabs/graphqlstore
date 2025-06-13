"""Exceptiones personalizadas para GraphQL."""


class GraphQLStoreError(Exception):
    """Excepcion base para errores de GraphQLStore."""


class SchemaError(GraphQLStoreError):
    """Error en el parsing o validacion del esquema GraphQL."""
