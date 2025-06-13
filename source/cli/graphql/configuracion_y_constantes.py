"""Modulo que contiene las configuraciones y constantes \
    para el CLI de GraphQL."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List


class TipoField(Enum):
    """Enumeración para los tipos de campos soportados."""

    ID = "ID"
    STRING = "String"
    INT = "Int"
    FLOAT = "Float"
    BOOLEAN = "Boolean"
    DATETIME = "DateTime"
    JSON = "Json"

    @classmethod
    def existe(cls, value):
        """Verifica si un tipo de campo existe en la enumeración."""
        return value in cls._value2member_map_


@dataclass
class InfoDirectiva:
    """Clase para almacenar información de una directiva."""

    nombre: str
    argumentos: Dict[str, Any]


@dataclass
class InfoField:
    """Clase para almacenar información de un campo."""

    nombre: str
    tipo_campo: str
    es_lista: bool
    es_requerido: bool
    directivas: Dict[str, InfoDirectiva]


@dataclass
class InfoTabla:
    """Clase para almacenar informacion de una tabla."""

    nombre: str
    campos: Dict[str, InfoField]


@dataclass
class InfoEnum:
    """Clase para almacenar información de un enum."""

    nombre: str
    valores: List[str]


@dataclass
class InfoParseEsquema:
    """Clase para almacenar informacion del esquema parseado."""

    enums: Dict[str, InfoEnum]
    tablas: Dict[str, InfoTabla]
