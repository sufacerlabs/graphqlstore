"""Modulo GraphQLSchemaParser"""

from typing import Any, Dict
from graphql.language import parse
from graphql.error import GraphQLError
from graphql.language.ast import (
    EnumTypeDefinitionNode,
    ListTypeNode,
    NamedTypeNode,
    NonNullTypeNode,
    ObjectTypeDefinitionNode,
)
from .configuracion_y_constantes import (
    InfoDirectiva,
    InfoEnum,
    InfoField,
    InfoParseEsquema,
    InfoTabla,
    TipoField,
)
from .exceptions import SchemaError


class ParserGraphQLEsquema:
    """Clase para parsear un esquema GraphQL \
        y extraer información relevante."""

    @staticmethod
    def get_type_mapping() -> Dict[str, str]:
        """Retorna un diccionario que mapea tipos GraphQL a tipos SQL."""
        return {
            TipoField.ID.value: "VARCHAR(25)",
            TipoField.STRING.value: "VARCHAR(255)",
            TipoField.INT.value: "INT",
            TipoField.FLOAT.value: "DECIMAL(10, 2)",
            TipoField.BOOLEAN.value: "BOOLEAN",
            TipoField.DATETIME.value: "DATETIME",
            TipoField.JSON.value: "JSON",
        }

    def parse_esquema(self, esquema: str) -> InfoParseEsquema:
        """Parsear el esquema GraphQL y retornar un \
            diccionario con la información extraída."""

        tablas = {}
        enums = {}

        try:
            # parsear el esquema GraphQL usando parser de graphql-core
            # https://github.com/graphql-python/graphql-core/blob/main\
            # /src/graphql/language/parser.py
            ast = parse(esquema)

            # procesar cada definicion del documento AST
            for definition in ast.definitions:
                if isinstance(definition, EnumTypeDefinitionNode):
                    info_enum = self._parse_enum_definition(definition)
                    enums[info_enum.nombre] = info_enum

                if isinstance(
                    definition, ObjectTypeDefinitionNode
                ) and definition.name.value not in [
                    "Query",
                    "Mutation",
                    "Subscription",
                ]:
                    info_tabla = self._parse_tabla_definition(definition)
                    tablas[info_tabla.nombre] = info_tabla

            return InfoParseEsquema(tablas=tablas, enums=enums)
        except GraphQLError as e:
            raise SchemaError(
                f"Error al parsear el esquema GraphQL: {str(e)}",
            ) from e

    def _parse_enum_definition(
        self,
        definition: EnumTypeDefinitionNode,
    ) -> InfoEnum:
        """Parsear una definicion de enum y retornar un objeto InfoEnum."""
        # Extraer el nombre del enum
        name = definition.name.value
        # Extraer los valores del enum
        values = [value.name.value for value in definition.values]

        return InfoEnum(nombre=name, valores=values)

    def _parse_tabla_definition(
        self,
        definition: ObjectTypeDefinitionNode,
    ) -> InfoTabla:
        """Parsear una definicion de ObjectType \
            y retornar un objeto InfoTabla."""

        # Extraer el nombre de la tabla
        nombre = definition.name.value
        # Extraer los campos de la tabla
        fields = {}

        # Procesar cada campo de la tabla
        for field in definition.fields:
            info_field = self._parse_field_definition(field)
            fields[info_field.nombre] = info_field

        return InfoTabla(nombre=nombre, campos=fields)

    def _parse_field_definition(self, field):
        """Parsear una definicion de campo y retornar un objeto InfoField."""
        # extraer el nombre del campo
        nombre = field.name.value
        # extraer el tipo del campo despues de parsear el tipo
        tipo_campo, es_lista, es_requerido = self._parse_type(field.type)
        # extraer las directivas del campo
        directivas = self._parse_directives(field.directives)

        return InfoField(
            nombre=nombre,
            tipo_campo=tipo_campo,
            es_lista=es_lista,
            es_requerido=es_requerido,
            directivas=directivas,
        )

    def _parse_type(self, type_node):
        """Extraer informacion del  tipo de un nodo tipo."""
        es_lista = False
        es_requerido = False

        # Manejar tipo non-null
        if isinstance(type_node, NonNullTypeNode):
            inner_tipo, inner_es_lista, _ = self._parse_type(type_node.type)
            return inner_tipo, inner_es_lista, True

        # Manejar tipo lista
        if isinstance(type_node, ListTypeNode):
            inner_tipo, inner_es_lista, inner_es_requerido = self._parse_type(
                type_node.type,
            )

            return inner_tipo, True, inner_es_requerido

        # Manejar tipo nombre
        if isinstance(type_node, NamedTypeNode):
            return type_node.name.value, es_lista, es_requerido

        return None, es_lista, es_requerido

    def _parse_directives(self, directives) -> Dict[str, Any]:
        """Parsear directivas de un campo y retornar un diccionario."""

        result = {}
        for directive in directives:
            # Parsear cada directiva
            info_directiva = self._parse_directive(directive)
            result[info_directiva.nombre] = info_directiva

        return result

    def _parse_directive(self, directive):
        """Parsear una directiva y retornar un objeto InfoDirectiva."""
        nombre = directive.name.value
        argumentos = {}

        for arg in directive.arguments:
            arg_nombre = arg.name.value
            arg_valor = arg.value.value
            argumentos[arg_nombre] = arg_valor

        return InfoDirectiva(nombre=nombre, argumentos=argumentos)
