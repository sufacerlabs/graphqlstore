# Documentación de ParserGraphQLEsquema - GraphQLStore CLI

## Resumen

Se ha implementado una nueva característica esencial en GraphQLStore CLI: el **ParserGraphQLEsquema**, que permite analizar y procesar esquemas GraphQL para convertirlos en estructuras de datos utilizables. Esta implementación incluye manejo de tipos, directivas, relaciones, enums y una suite completa de pruebas con cobertura del 98%.

## 📋 Características Implementadas

### Funcionalidad Principal

El parser GraphQL proporciona capacidades completas de análisis de esquemas:

1. **Análisis de Tipos**: Procesa tipos GraphQL (ID, String, Int, Boolean, DateTime, Float, JSON)
2. **Manejo de Directivas**: Extrae y procesa directivas con argumentos
3. **Relaciones**: Identifica y procesa relaciones entre tipos
4. **Enumeraciones**: Soporte completo para tipos enum
5. **Validación**: Verificación de sintaxis

### Sintaxis de Uso

```python
from source.cli.graphql import ParserGraphQLEsquema

# crear instancia del parser
parser = ParserGraphQLEsquema()

# ejemplo: parsear un esquema GraphQL simple
esquema_graphql = """
type User {
    id: ID!
    name: String!
    email: String
    posts: [Post!]! @relation(name: "UserPosts")
}

type Post {
    id: ID!
    title: String!
    content: String
    author: User! @relation(name: "UserPosts")
}
"""

# procesar el esquema
resultado = parser.parse_esquema(esquema_graphql)

# acceder a los resultados
tablas = resultado.tablas
enums = resultado.enums
```

## 🏗️ Arquitectura de la Implementación

### Estructura de Archivos

```
source/cli/graphql/
├── __init__.py                          # Inicialización del módulo
├── parser.py                           # Clase principal ParserGraphQLEsquema
├── configuracion_y_constantes.py      # Constantes, enums y clases de datos
├── exceptions.py                       # Excepciones personalizadas
└── docs/
    └── parser.md                      # Documentación del parser
```

### Arquitectura Modular

#### Clase Principal Parser (`source/cli/graphql/parser.py`)

```python
class ParserGraphQLEsquema:
    """Parser para esquemas GraphQL que extrae información de tipos y relaciones"""
    
    # inicialización del parser
    def __init__(self)
    #  mapeo de tipos GraphQL a SQL
    def get_type_mapping(self)
    # funcion principal de parsing
    def parse_esquema(self, esquema: str)
    # parsear definiciones  enum
    def _parse_enum_definition(self, definition)
    # parsear definiciones de tipo
    def _parse_tabla_definition(self, definition)
    # parsear definiciones de campo
    def _parse_field_definition(self, field)
    # parsear el tipo de campo
    def _parse_type(self, type_node)
    # parsear directivas
    def _parse_directives(self, directives)
    # parsear directiva
    def _parse_directive(self, directive)
```

#### Configuración y Constantes (`source/cli/graphql/configuracion_y_constantes.py`)

```python
# Enumeraciones principales
class TipoField(Enum):
    """Tipos de campos soportados"""
    ID = "ID"
    STRING = "String"
    INT = "Int"
    BOOLEAN = "Boolean"
    DATETIME = "DateTime"
    FLOAT = "Float"
    JSON = "JSON"

# Clases de datos
@dataclass
class InfoCampo:
    """Información de un campo de tabla"""
    nombre: str
    tipo_campo: str
    es_requerido: bool
    es_lista: bool
    directivas: Dict[str, 'InfoDirectiva']

@dataclass
class InfoTabla:
    """Información de una tabla generada desde GraphQL"""
    nombre: str
    campos: Dict[str, InfoCampo]

@dataclass
class InfoEnum:
    """Información de un enum de GraphQL"""
    nombre: str
    valores: List[str]

@dataclass
class InfoDirectiva:
    """Información de una directiva de GraphQL"""
    nombre: str
    argumentos: Dict[str, str]

@dataclass
class InfoParseEsquema:
    """Resultado del parsing de un esquema GraphQL"""
    tablas: Dict[str, InfoTabla]
    enums: Dict[str, InfoEnum]
```

#### Excepciones Personalizadas (`source/cli/graphql/exceptions.py`)

```python
class GraphQLStoreError(Exception):
    """Excepción base para errores de GraphQLStore"""

class SchemaError(GraphQLStoreError):
    """Error en el parsing o validación de un esquema GraphQL"""
```

## 🧪 Suite de Pruebas

### Cobertura Alcanzada

| Módulo | Statements | Miss | Branch | BrPart | Cover |
|--------|------------|------|--------|--------|-------|
| [`source/cli/graphql/parser.py`](source/cli/graphql/parser.py) | 65 | 1 | 18 | 1 | **98%** |
| [`source/cli/graphql/configuracion_y_constantes.py`](source/cli/graphql/configuracion_y_constantes.py) | 37 | 1 | 0 | 0 | **97%** |
| [`source/cli/graphql/exceptions.py`](source/cli/graphql/exceptions.py) | 2 | 0 | 0 | 0 | **100%** |
| **Total del Módulo GraphQL** | 104 | 2 | 18 | 1 | **98%** |

### Pruebas Implementadas

#### Pruebas del Parser GraphQL (`tests/cli/graphql/test_parser.py`)

```python
# Casos de prueba implementados (133 statements, 100% coverage):

# prueba de mapping de tipos
def test_get_typo_mapping()
# prueba de esquema simple
def test_parse_esquema_simple()
# prueba de esquema con enums
def test_parse_esquema_con_enum()
# prueba de esquema con directivas
def test_parse_esquema_con_directivas()
# prueba de esquema con relaciones
def test_parse_esquema_con_relaciones()
# prueba de esquema complejo
def test_parse_esquema_complejo()
# Esquema con tipos excluidos (Query, Mutation, Subscription)
def test_parse_esquema_con_excluidos()
# Manejo de errores de sintaxis
def test_parse_esquema_invalido()
```

**Casos de Prueba Destacados:**

- ✅ **Tipos Básicos**: Verifica el mapeo correcto de tipos GraphQL a SQL
- ✅ **Enumeraciones**: Procesa correctamente enums con múltiples valores
- ✅ **Directivas**: Extrae directivas con argumentos complejos
- ✅ **Relaciones**: Maneja relaciones bidireccionales entre tipos
- ✅ **Tipos Excluidos**: Filtra correctamente tipos de sistema de GraphQL
- ✅ **Manejo de Errores**: Captura y reporta errores de sintaxis apropiadamente


## 📊 Resultados de Pruebas

### Ejecución Exitosa

```bash
tests/cli/graphql/test_parser.py ........                                [ 41%]

================================ tests coverage ================================
Name                                                        Stmts   Miss Branch BrPart  Cover
---------------------------------------------------------------------------------------------
source/cli/graphql/__init__.py                                  3      0      0      0   100%
source/cli/graphql/configuracion_y_constantes.py               37      1      0      0    97%
source/cli/graphql/exceptions.py                                2      0      0      0   100%
source/cli/graphql/parser.py                                   65      1     18      1    98%
tests/cli/graphql/test_parser.py                              133      0      0      0   100%
---------------------------------------------------------------------------------------------
============================== 8 passed in 1.96s ===============================
```

**Métricas de Calidad:**
- ✅ **8 pruebas pasadas** sin fallos
- ✅ **Cobertura del parser**: 98%
- ✅ **Cobertura de configuración**: 97%
- ✅ **Cobertura de excepciones**: 100%
- ✅ **Cobertura de pruebas**: 100%

### Análisis de Cobertura por Módulo

1. **parser.py**: 98% - Cobertura casi completa con 1 branch no cubierto (caso edge específico)
2. **configuracion_y_constantes.py**: 97% - Alta cobertura con 1 statement no cubierto
3. **exceptions.py**: 100% - Excepción completamente verificada
4. **test_parser.py**: 100% - Suite de pruebas completamente ejecutada

## 🔧 Características del Parser

### Mapeo de Tipos

El parser proporciona mapeo automático de tipos GraphQL a tipos SQL:

```python
@staticmethod
def get_type_mapping(self) -> Dict[str, str]:
    """Obtiene el mapeo de tipos GraphQL a tipos SQL"""
    return {
        TipoField.ID.value: "VARCHAR(25)",
        TipoField.STRING.value: "VARCHAR(255)",
        TipoField.INT.value: "INT",
        TipoField.BOOLEAN.value: "BOOLEAN",
        TipoField.DATETIME.value: "DATETIME",
        TipoField.FLOAT.value: "DECIMAL(10, 2)",
        TipoField.JSON.value: "JSON"
    }
```

### Procesamiento de Directivas

Extrae y procesa directivas con argumentos:

```python
# Ejemplo de directiva procesada
@relation(name: "UserPosts", onDelete: CASCADE, link: TABLE)

# Resultado en InfoDirectiva
InfoDirectiva(
    nombre="relation",
    argumentos={
        "name": "UserPosts",
        "onDelete": "CASCADE",
        "link": "TABLE"
    }
)
```

### Manejo de Relaciones

Identifica relaciones entre tipos automáticamente:

```python
# Relación uno-a-muchos
posts: [Post!]! @relation(name: "UserPosts")

# Relación muchos-a-muchos
houses: [House!]! @relation(name: "UserHouses", link: TABLE)

# Relación uno-a-uno
author: User! @relation(name: "UserPosts", onDelete: CASCADE)
```

### Procesamiento de Enumeraciones

Soporte completo para tipos enum:

```python
enum UserRole {
    ADMIN
    USER
    GUEST
}

# Resultado en InfoEnum
InfoEnum(
    nombre="UserRole",
    valores=["ADMIN", "USER", "GUEST"]
)
```

## 🚀 Casos de Uso

### Esquema Simple

```python
esquema = """
type User {
    id: ID!
    name: String!
    email: String
    age: Int
    active: Boolean
}
"""

resultado = parser.parse_esquema(esquema)
# resultado.tablas["User"] contiene la información de la tabla
# resultado.enums está vacío
```

### Esquema con Relaciones

```python
esquema = """
type User {
    id: ID!
    name: String!
    posts: [Post!]! @relation(name: "UserPosts")
}

type Post {
    id: ID!
    title: String!
    author: User! @relation(name: "UserPosts")
}
"""

resultado = parser.parse_esquema(esquema)
# se procesan lo mencionado anteriormente
# y se procesan las relaciones
```

### Esquema con Enums y Directivas

```python
esquema = """
type User {
    id: ID! @id
    name: String!
    role: UserRole!
    createdAt: DateTime @createdAt
    isActive: Boolean @default(value: "true")
}

enum UserRole {
    ADMIN
    USER
    GUEST
}
"""

resultado = parser.parse_esquema(esquema)
# resultado.enums["UserRole"] contiene los valores del enum
# Las directivas se procesan con sus argumentos
```

## 🔧 Manejo de Errores

### Errores Implementados y Probados

1. **SchemaError**: Errores de sintaxis en el esquema GraphQL

### Ejemplo de Manejo de Errores

```python
try:
    resultado = parser.parse_esquema(esquema_invalido)
except GraphQLError as e:
    raise  SchemaError(f"Error en el esquema GraphQL: {str(e)}")
```

## 🚀 Próximos Pasos

### Mejoras Identificadas

1. **Soporte para Interfaces**: Extensión para interfaces GraphQL
2. **Uniones**: Soporte para tipos union
3. **Validaciones Avanzadas**: Reglas de validación más estrictas

### Parser en Producción

El parser GraphQL está listo para uso en producción con:

- ✅ **Cobertura de pruebas del 98%** (100% en funcionalidad crítica)
- ✅ **Manejo robusto de errores** con excepciones específicas
- ✅ **Procesamiento completo** de tipos, enums, directivas y relaciones
- ✅ **Documentación completa**
- ✅ **Arquitectura escalable** para futuras extensiones
- ✅ **Pruebas parametrizadas** con pytest
- ✅ **Mapeo automático de tipos** GraphQL a MySQL

Esta implementación establece una base sólida para el procesamiento de esquemas GraphQL en GraphQLStore CLI, proporcionando las herramientas necesarias para convertir definiciones GraphQL en estructuras de datos utilizables.
