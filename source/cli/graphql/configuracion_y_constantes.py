"""Modulo que contiene las configuraciones y constantes \
    para el CLI de GraphQL."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


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


class TipoRelacion(Enum):
    """Enumeración para los tipos de relaciones soportadas."""

    ONE_TO_ONE = "1:1"
    ONE_TO_MANY = "1:N"
    MANY_TO_MANY = "N:M"


class TipoLink(Enum):
    """Enumeración para los tipos de enlaces soportados."""

    INLINE = "INLINE"
    TABLE = "TABLE"


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


@dataclass
class FuenteRelacion:
    """Clase para almacenar información de la fuente de una relación."""

    tabla_fuente: str
    campo_fuente: str
    fuente_es_lista: bool
    nombre_constraint_fuente: str
    on_delete: str


@dataclass
class ObjetivoRelacion:
    """Clase para almacenar información del objetivo de una relación."""

    tabla_objetivo: str
    campo_inverso: Optional[str]
    nombre_constraint_objetivo: Optional[str]
    on_delete_inverso: str


@dataclass
class InfoRelacion:
    """Clase para almacenar información de una relación."""

    fuente: FuenteRelacion
    objetivo: ObjetivoRelacion
    tipo_relation: str
    nombre_relacion: str
    tipo_link: str
