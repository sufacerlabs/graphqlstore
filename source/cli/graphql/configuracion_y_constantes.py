"""Modulo que contiene las configuraciones y constantes \
    para el CLI de GraphQL."""

from dataclasses import dataclass, field
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


class OnDelete(Enum):
    """Enumeración para las acciones de eliminación soportadas."""

    CASCADE = "CASCADE"
    SET_NULL = "SET_NULL"


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


@dataclass
class InfoCambioCampo:
    """Información sobre cambios en un campo."""

    nombre: str
    info_antigua: InfoField
    info_nueva: InfoField


@dataclass
class InfoDiffCampos:
    """Información sobre diferencias en campos."""

    agregados: List[InfoField] = field(default_factory=list)
    eliminados: List[InfoField] = field(default_factory=list)
    modificados: List[InfoCambioCampo] = field(default_factory=list)


@dataclass
class InfoDiffTablas:
    """Información sobre diferencias en tablas."""

    agregadas: List[str] = field(default_factory=list)
    eliminadas: List[str] = field(default_factory=list)
    campos: Dict[str, InfoDiffCampos] = field(default_factory=dict)


@dataclass
class InfoDiffRelaciones:
    """Información sobre diferencias en relaciones."""

    agregadas: List[InfoRelacion] = field(default_factory=list)
    eliminadas: List[InfoRelacion] = field(default_factory=list)


@dataclass
class InfoCambioEnum:
    """Información sobre cambios en enums."""

    nombre: str
    valores_antiguos: List[str]
    valores_nuevos: List[str]
    valores_agregados: List[str]
    valores_eliminados: List[str]


@dataclass
class InfoDiffEnums:
    """Información sobre diferencias en enums."""

    agregados: List[InfoEnum] = field(default_factory=list)
    eliminados: List[str] = field(default_factory=list)
    modificados: List[InfoCambioEnum] = field(default_factory=list)


@dataclass
class InfoDiffEsquema:
    """Información completa sobre diferencias entre esquemas."""

    tablas: InfoDiffTablas = field(default_factory=InfoDiffTablas)
    relaciones: InfoDiffRelaciones = field(default_factory=InfoDiffRelaciones)
    enums: InfoDiffEnums = field(default_factory=InfoDiffEnums)

    def tiene_cambios(self) -> bool:
        """Verificar si hay cambios en el esquema."""
        return (
            bool(self.tablas.agregadas)
            or bool(self.tablas.eliminadas)
            or bool(self.tablas.campos)
            or bool(self.relaciones.agregadas)
            or bool(self.relaciones.eliminadas)
            or bool(self.enums.agregados)
            or bool(self.enums.eliminados)
            or bool(self.enums.modificados)
        )


@dataclass
class InfoMigracion:
    """Información de una migración."""

    id_migracion: str
    timestamp: str
    esquema_anterior: str
    esquema_nuevo: str
    diferencias: InfoDiffEsquema
    sql_generado: str


class TipoOperacionMigracion(Enum):
    """Tipos de operaciones de migración."""

    CREAR_TABLA = "CREATE_TABLE"
    ELIMINAR_TABLA = "DROP_TABLE"
    AGREGAR_CAMPO = "ADD_COLUMN"
    ELIMINAR_CAMPO = "DROP_COLUMN"
    MODIFICAR_CAMPO = "MODIFY_COLUMN"
    AGREGAR_RELACION = "ADD_RELATION"
    ELIMINAR_RELACION = "DROP_RELATION"
    CREAR_ENUM = "CREATE_ENUM"
    MODIFICAR_ENUM = "MODIFY_ENUM"
    ELIMINAR_ENUM = "DROP_ENUM"


class EstadoMigracion(Enum):
    """Estados de una migración."""

    PENDIENTE = "PENDING"
    APLICADA = "APPLIED"
    FALLIDA = "FAILED"
    REVERTIDA = "REVERTED"


DIRECTIVAS_TEMPORALES = {"createdAt", "updatedAt"}
DIRECTIVAS_CONSTRAINS = {"unique", "id"}
DIRECTIVAS_BASE_DATOS = {"db", "default"}
