# Documentación del comando `inicializar` - GraphQLStore CLI

## 📖 Resumen

El comando `inicializar` es el núcleo de GraphQLStore  (junto con el comando `migracion`), diseñado para transformar esquemas GraphQL en bases de datos MySQL completamente funcionales. Este comando analiza un esquema GraphQL, procesa las relaciones entre tipos, genera el código SQL necesario y opcionalmente ejecuta la inicialización de la base de datos. Por lo tanto, esta implementacion integra varios subsistemas y proporciona una suite completa de pruebas con una cobertura del 97%.

Este comando es ideal para desarrolladores que buscan una forma rápida y eficiente de configurar bases de datos a partir de esquemas GraphQL, facilitando el desarrollo de APIs y aplicaciones basadas en GraphQL.

## 📋 Características Implementadas

### 🎯 Funcionalidad Principal
- **Inicialización de Base de Datos**: Crea tablas y relaciones en MySQL a partir de un esquema GraphQL

### Características Clave
- **🔄 Transformación GraphQL → MySQL**: Convierte tipos GraphQL en tablas MySQL optimizadas
- **🔗 Procesamiento de Relaciones**: Maneja relaciones 1:1, 1:N y N:M automáticamente
- **📁 Generación de Archivos**: Crea esquemas SQL, clientes GraphQL y backups
- **🗄️ Inicialización de BD**: ejecuta el SQL generado en MySQL
- **⚡ Detección Inteligente**: Encuentra esquemas GraphQL automáticamente
- **🛡️ Validación Robusta**: Verifica configuración y estado de la base de datos

## 🚀 Sintaxis del Comando

### Sintaxis Básica
```bash
graphqlstore inicializar [OPCIONES]
```

### Opciones Disponibles

| Opción | Alias | Tipo | Descripción |
|--------|-------|------|-------------|
| `--esquema` | `-e` | `str` | Ruta al archivo de esquema GraphQL |
| `--salida` | `-s` | `str` | Directorio de salida (default: `generated`) |
| `--no-visualizar-salida` | `-nv` | `flag` | Ocultar información detallada durante generación |
| `--no-visualizar-sql` | `-nvs` | `flag` | Ocultar el SQL generado en consola |

### Ejemplos de Uso

#### 1. Inicialización Básica
```bash
# Con esquema específico
graphqlstore inicializar --esquema mi_esquema.graphql

# Búsqueda automática de .graphql en directorio actual
graphqlstore inicializar
```

#### 2. Configuración de Salida
```bash
# Directorio personalizado
graphqlstore inicializar --esquema schema.graphql --salida migra

# Salida silenciosa
graphqlstore inicializar --no-visualizar-salida --no-visualizar-sql
graphqlstore inicializar --esquema schema.graphql -nv -nvs
```

## 🏗️ Arquitectura de la Implementación

### Estructura  de Archivos

```
source/cli/
├── main.py                      # Clase CLI principal y orquestación
├── base.py                      # Clase abstracta Comando (patron Command)
├── core.py                      # ConstructorCLI (patron Builder)
├── __init__.py                  # Inicialización del módulo
└── inicializar/
    ├── __init__.py             # Inicialización del módulo conexion
    ├── main.py                 # Función principal inicializar()
    ├── comando_inicializar.py     # Clase ComandoInicializar
    └── README.md              # Documentación del comando
```

### Arquitectura Modular

#### Función Principal ([`source/cli/inicializar/main.py`](source/cli/inicializar/main.py))

```python
def inicializar(args):
    """Función para inicializar la base de datos desde un esquema GraphQL."""
```

**Responsabilidades:**
1. **Gestión de Esquemas**: Localiza y lee archivos GraphQL
2. **Coordinación de Procesamiento**: Orquesta parser, relaciones y generador
3. **Interfaz con Base de Datos**: Maneja conexión y ejecución SQL
4. **Generación de Archivos**: Crea archivos de salida y backups
5. **Manejo de Errores**: Proporciona feedback detallado sobre fallos

#### Clase ComandoInicializar ([`source/cli/inicializar/commando_inicializar.py`](source/cli/inicializar/comando_inicializar.py))

```python
class ComandoInicializar(Comando):
    """Comando para inicializar bases de datos desde esquemas GraphQL."""
```

**Funcionalidades:**
- **Configuración de Argumentos**: Define opciones de línea de comandos
- **Ejecución del Comando**: Llama a la función `inicializar()` con argumentos

## 🔧 Integración con Componentes

### Dependencias del Sistema


#### Parser GraphQL (`source/cli/graphql/parser.py`)
- **Análisis de Esquemas**: Extrae tipos, campos, directivas
- **Validación de Sintaxis**: Verifica esquemas GraphQL válidos
- **Extracción de Información**: Genera estructuras de datos procesables

#### Procesador de Relaciones (`source/cli/graphql/procesar_relaciones.py`)
- **Detección de Relaciones**: Identifica conexiones entre tipos
- **Clasificación**: Determina tipos de relación (1:1, 1:N, N:M)
- **Generación de Constraints**: Crea foreign keys y validaciones

#### Generador MySQL (`source/cli/graphql/mysql_generador.py`)
- **Transformación de Tipos**: Convierte tipos GraphQL a MySQL
- **Generación de DDL**: Crea sentencias SQL (CREATE, ALTER, COLUMNS, etc.)

#### Adaptador MySQL (`source/cli/database/adaptadores/mysql.py`)
- **Gestión de Conexiones**: Establece, comprueba y mantiene conexiones BD
- **Ejecución de Consultas**: Ejecuta SQL generado

#### Gestor de Archivos (`source/cli/utilidades/gestor_archivo.py`)
- **Operaciones de E/S**: Lee esquemas y escribe archivos generados
- **Gestión de Directorios**: Crea estructura de directorios necesaria

## 🧪 Suite de Pruebas

### Cobertura Alcanzada

| Módulo | Statements | Miss | Branch | BrPart | Cover |
|--------|------------|------|--------|--------|-------|
| comando_inicializar.py | 13 | 0 | 2 | 0 | **100%** |
| main.py | 65 | 6 | 10 | 0 | **92%** |
| gestor_archivo.py | 14 | 0 | 2 | 0 | **100%** |
| **Total del Comando Inicializar** | 92 | 6 | 14 | 0 | **97%** |

### Pruebas Implementadas

#### 1. Pruebas del Comando Inicializar (`tests/cli/inicializar/test_comando_inicializar.py`)

```python
# Casos de prueba implementados (31 statements, 100% coverage):

# Configuración de argumentos
def test_crear_comando_agregar_argumentos()
# Ejecución del comando
def test_contenido_comando_ejecuta_inicializar()
```

**Casos de Prueba Destacados:**
- ✅ **Configuración de Parser**: Verifica argumentos y opciones correctas
- ✅ **Integración con Función**: Confirma llamada correcta a `inicializar()`
- ✅ **Manejo de Parámetros**: Valida paso correcto de argumentos

#### 2. Pruebas de la Función Inicializar (`tests/cli/inicializar/test_inicializar.py`)

```python
# Casos de prueba implementados (112 statements, 100% coverage):

# Inicialización exitosa
def test_inicializar_con_esquema_especificado_exitoso()
def test_inicializar_sin_esquema_encuentra_archivo_graphql()

# Manejo de errores
def test_inicializar_falla_sin_esquema_y_sin_archivo_graphql()
def test_inicializar_falla_esquema_no_existe()

# Interacción con base de datos
def test_inicializar_sin_configuracion_db()
def test_inicializar_db_con_tablas_existentes()
```

**Casos de Prueba Destacados:**
- ✅ **Flujos Exitosos**: Verifica inicialización completa con y sin esquema especificado
- ✅ **Detección de Esquemas**: Confirma búsqueda automática de archivos `.graphql`
- ✅ **Validación de Errores**: Prueba manejo de esquemas faltantes o inválidos
- ✅ **Estados de BD**: Verifica comportamiento con BD vacías vs. con tablas existentes
- ✅ **Configuración**: Valida manejo de configuraciones faltantes o inválidas
- ✅ **Integración Completa**: Prueba coordinación entre todos los componentes

#### 3. Pruebas del Gestor de Archivos (`tests/cli/utilidades/test_gestor_archivo.py`)

```python
# Casos de prueba implementados (35 statements, 100% coverage):

# Operaciones de lectura
def test_leer_archivo_exitoso()
def test_leer_archivo_no_existe()

# Operaciones de escritura
def test_escribir_archivo_exitoso()
def test_escribir_archivo_crea_directorio()

# Gestión de directorios
def test_asegurar_dir_existe_crear_nuevo()
def test_asegurar_dir_existe_ya_existe()
```

**Casos de Prueba Destacados:**
- ✅ **Operaciones de E/S**: Verifica lectura y escritura de archivos
- ✅ **Gestión de Errores**: Maneja archivos inexistentes y permisos
- ✅ **Creación de Estructura**: Confirma creación automática de directorios
- ✅ **Casos Edge**: Prueba situaciones límite y errores de sistema

## 📊 Resultados de Pruebas

### Ejecución Exitosa

```bash
================================ tests coverage ================================
_______________ coverage: platform linux, python 3.10.12-final-0 _______________

Name                                                        Stmts   Miss Branch BrPart  Cover
---------------------------------------------------------------------------------------------
source/cli/inicializar/__init__.py                              3      0      0      0   100%
source/cli/inicializar/comando_inicializar.py                  13      0      2      0   100%
source/cli/inicializar/main.py                                 65      6     10      0    92%
source/cli/utilidades/__init__.py                               2      0      0      0   100%
source/cli/utilidades/gestor_archivo.py                        14      0      2      0   100%
tests/cli/inicializar/test_comando_inicializar.py              31      0      2      0   100%
tests/cli/inicializar/test_inicializar.py                     112      0      0      0   100%
tests/cli/utilidades/test_gestor_archivo.py                    35      0      0      0   100%
---------------------------------------------------------------------------------------------
TOTAL                                                         275      6     16      0    99%
============================== 14 passed in 1.24s ==============================
```

**Métricas de Calidad:**
- ✅ **14 pruebas pasadas** sin fallos
- ✅ **Tiempo de ejecución**: 1.24 segundos
- ✅ **Cobertura global**: 99%
- ✅ **Cobertura del comando inicializar**: 100%
- ✅ **Cobertura de la función principal**: 92%
- ✅ **Cobertura del gestor de archivos**: 100%
- ✅ **Arquitectura modular completamente comprobada**

### Análisis de Cobertura por Módulo

1. **comando_inicializar.py**: 100% - Comando completamente verificado
2. **main.py**: 92% - Alta cobertura con 6 statements no cubiertos (casos edge específicos)
3. **gestor_archivo.py**: 100% - Utilidades completamente probadas
4. **Suites de pruebas**: 100% - Todas las pruebas completamente ejecutadas

Estos representan casos edge muy específicos que no afectan la funcionalidad principal.


### Archivos Generados

#### 1. `schema.sql`
```sql
-- Esquema MySQL completo generado
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Foreign keys y constraints
ALTER TABLE posts ADD CONSTRAINT fk_posts_user_id 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
```

#### 2. `schema.graphql`
```graphql
# Esquema GraphQL transformado para cliente
type User {
  id: ID!
  name: String!
  email: String!
  posts: [Post!]!
}
```

#### 3. `.backup.graphql`
```graphql
# Copia de seguridad del esquema original
# Generado automáticamente por GraphQLStore CLI

type User {
  id: ID!
  name: String!
  email: String!
  posts: [Post!]! @relation(name: "UserPosts")
}

type Post {
  id: ID!
  title: String!
  content: String
  user: User! @relation(name: "UserPosts", onDelete: CASCADE)
}
```

## ⚡ Características Avanzadas

### 1. Detección Inteligente de Esquemas
- **Búsqueda Automática**: Encuentra archivos `.graphql` en el directorio actual
- **Priorización**: Usa esquema especificado o busca automáticamente

### 2. Procesamiento de Relaciones Avanzado
- **Relaciones 1:1**: Maneja campos opcionales y obligatorios
- **Relaciones 1:N**: Crea foreign keys
- **Relaciones N:M**: Genera tablas de relacion automáticamente
- **Auto-relaciones**: Procesa relaciones reflexivas correctamente

### 3. Generación SQL
- **Tipos de Datos**: Mapeo optimizado GraphQL → MySQL
- **Constraints**: Aplica validaciones de integridad referencial
- **Encoding**: Usa UTF-8 para soporte internacional completo

### 4. Integración con Base de Datos
- **Verificación de Estado**: Comprueba si la BD ya tiene tablas
- **Ejecución Segura**: Solo ejecuta en bases de datos vacías
- **Manejo de Errores**: Proporciona feedback detallado sobre fallos de BD
- **Limpieza**: Cierra conexiones automáticamente

## 🛡️ Manejo de Errores

### Categorías de Errores

#### 1. Errores de Esquema
```bash
El archivo de esquema 'schema.graphql' no existe.
```

#### 2. Errores de Base de Datos
```bash
❌ ERROR AL CREAR EL ESQUEMA
Error: ...
```

#### 3. Errores de Configuración
```bash
❌ Archivo de configuracion no encontrado. Asegurate de haber ejecutado primeramente el comando 'conexion'
```

#### 4. Errores de Archivos
```bash
❌ ERROR AL TRANSFORMAR EL ESQUEMA A CLIENTE GRAPHQL
Error: ...
```

## 🎯 Casos de Uso Comunes

### 1. Desarrollo de Nueva API
```bash
# Paso 1: Configurar conexión a BD
graphqlstore conexion

# Paso 2: Probar conexion a BD
graphqlstore probar-conexion --verbose

# Paso 3: Inicializar desde esquema
graphqlstore inicializar --esquema api_schema.graphql --salida ./migra

# Resultado: BD inicializada + archivos generados listos
```

### 2. Prototipado Rápido
```bash
# Esquema en directorio actual como 'schema.graphql'
graphqlstore inicializar
```

### 3. Integración en CI/CD
```bash
# Modo silencioso para pipelines automatizados
graphqlstore inicializar \
  --esquema schemas/production.graphql \
  --salida build/database \
  --no-visualizar-salida \
  --no-visualizar-sql
```

### 4. Desarrollo Multi-Entorno
```bash
# Desarrollo
graphqlstore inicializar -e dev_schema.graphql -s dev_build

# Staging
graphqlstore inicializar -e staging_schema.graphql -s staging_build

# Producción
graphqlstore inicializar -e prod_schema.graphql -s prod_build -nv -nvs
```

## 🚀 Próximos Pasos

### Extensiones Futuras Planificadas

1. **🔄 Comando de Migración**: Para actualizar esquemas existentes
3. **📊 Estadísticas de BD**: Análisis post-inicialización
4. **🎨 Personalización de Tipos**: Mapeos personalizados GraphQL → MySQL
5. **📱 Soporte Multi-BD**: Extensión a PostgreSQL y otros motores

### Comando en Producción

El comando `inicializar` está listo para uso en producción con:

- ✅ **Cobertura de pruebas del 97%** (100% en módulos críticos)
- ✅ **Manejo robusto de errores**
- ✅ **Interfaz usuario intuitiva** con múltiples opciones de configuración
- ✅ **Documentación completa**
- ✅ **Arquitectura escalable** para futuras extensiones
- ✅ **Patrones de diseño sólidos** para mantenibilidad y extensibilidad
- ✅ **Transformación completa GraphQL → MySQL**
- ✅ **Procesamiento avanzado de relaciones**


---

**📝 Nota**: Esta documentación corresponde a GraphQLStore CLI v3.0.0 y se actualiza continuamente con nuevas características y mejoras.
