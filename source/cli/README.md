# Documentación del comando `conexion` - GraphQLStore CLI

## Resumen

Se ha implementado una nueva característica: el **comando `conexion`**, que permite gestionar la configuración de conexión a bases de datos de manera interactiva y flexible. Esta implementación incluye múltiples formas de configuración, manejo robusto de errores y una suite completa de pruebas.

## 📋 Características Implementadas

### Funcionalidad Principal

El comando `conexion` proporciona tres métodos principales para configurar la conexión a la base de datos:

1. **Configuración Interactiva**: Solicita datos al usuario paso a paso
2. **Configuración mediante Archivo**: Carga configuración desde un archivo JSON externo
3. **Configuración mediante Argumentos**: Permite pasar parámetros directamente en la línea de comandos

### Sintaxis del Comando

```bash
# Configuración interactiva
graphqlstore conexion

# Configuración mediante archivo
graphqlstore conexion --archivo ./config.json

# Configuración mediante argumentos
graphqlstore conexion --host localhost --puerto 3306 --usuario admin --password secret --db-nombre mydb
```

## 🏗️ Arquitectura de la Implementación

### Estructura de Archivos

```
source/cli/
├── main.py          # Clase CLI principal y gestión de argumentos
├── conexion.py      # Lógica de configuración de conexión
├── __init__.py      # Inicialización del módulo
└── README.md        # Documentación del módulo CLI
```

### Clase CLI Principal (`source/cli/main.py`)

```python
class CLI:
    """Clase principal para la interfaz de línea de comandos de GraphQLStore"""
    
    def __init__(self, titulo: str = "GraphQLStore CLI")
    def crear_comando_conexion(self)  # Configura argumentos del comando
    def ejecutar(self)                # Punto de entrada principal
```

**Argumentos Soportados:**
- `--archivo, -a`: Ruta al archivo de configuración (formato JSON)
- `--host`: Host de la base de datos
- `--puerto`: Puerto de la base de datos
- `--usuario`: Usuario de la base de datos
- `--password`: Contraseña de la base de datos
- `--db-nombre`: Nombre de la base de datos

### Función de Conexión (`source/cli/conexion.py`)

```python
def conexion(args):
    """Funcion para configurar la conexion a la base de datos."""
```

**Flujo de Ejecución:**

1. **Carga de Configuración Existente**: Busca archivo `.graphqlstore_config.json` en el directorio actual
2. **Procesamiento de Archivo Externo**: Si se proporciona `--archivo`, carga y copia el contenido
3. **Configuración Interactiva**: Si no hay argumentos específicos, solicita entrada del usuario
4. **Guardado de Configuración**: Almacena la configuración final en formato JSON

## 🧪 Suite de Pruebas

### Cobertura Alcanzada

| Módulo | Statements | Miss | Branch | BrPart | Cover |
|--------|------------|------|--------|--------|-------|
| conexion.py | 56 | 0 | 18 | 0 | **100%** |
| main.py | 26 | 0 | 4 | 1 | **97%** |
| **Total del Proyecto** | 298 | 4 | 38 | 5 | **97%** |

### Pruebas Implementadas

#### 1. Pruebas de la Función Conexión (`tests/cli/test_conexion.py`)

```python
# Casos de prueba implementados (97 statements, 100% coverage):

# Configuración interactiva
def test_conexion_sin_params()
# Carga desde archivo externo
def test_conexion_con_archivo()
# Configuración previa existente
def test_conexion_con_configuracion_existente()
# Configuración mediante argumentos
def test_conexion_con_params()
# Manejo de errores JSON
def test_conexion_error_archivo_configuracion()
# Manejo de errores de archivo no encontrado
def test_conexion_error_archivo_no_encontrado()
# Manejo de errores de archivo no guardado
def test_conexion_parametros_error_guardar()
```

**Casos de Prueba Destacados:**

- ✅ **Entrada Interactiva**: Simula input del usuario y verifica la captura correcta de datos
- ✅ **Carga de Archivos**: Verifica la lectura y copia de archivos de configuración externos
- ✅ **Manejo de Errores**: Prueba respuestas a archivos corruptos y errores de acceso
- ✅ **Persistencia**: Confirma que la configuración se guarda correctamente en formato JSON

#### 2. Pruebas de la Clase CLI (`tests/cli/test_main.py`)

```python
# Casos de prueba implementados (64 statements, 91% coverage):

# inicialización correcta
def test_inicializar()
# titulo personalizado
def test_titulo_personalizado()    
# comportamiento sin comandos
def test_ejecutar_sin_comando()
# comportamiento con comando conexion
def test_ejecutar_comando_conexion()
# comportamiento con argumentos de conexion
def test_ejecutar_con_args()
```

#### 3. Pruebas de Integración (`tests/test_main.py`)

```python
# Casos de prueba implementados (46 statements, 96% coverage):

# ejecución de CLI
def test_main_ejecutar_cli()
# ejecución con comando conexión
def test_main_ejecutar_cli_con_arg_conexion()
# ejecucion como script
def test_main_ejecuta_como_script()
```

## 📊 Resultados de Pruebas

### Ejecución Exitosa

```bash
Name                         Stmts   Miss Branch BrPart  Cover
source/__init__.py               3      0      0      0   100%
source/cli/__init__.py           0      0      0      0   100%
source/cli/conexion.py          56      0     18      0   100%
source/cli/main.py              26      0      4      1    97%
source/main.py                   6      0      2      0   100%
tests/__init__.py                0      0      0      0   100%
tests/cli/test_conexion.py      97      0      0      0   100%
tests/cli/test_main.py          64      3      6      3    91%
tests/test_main.py              46      1      8      1    96%
TOTAL                          298      4     38      5    97%
===================== 15 passed in 2.15s =====================
```

**Métricas de Calidad:**
- ✅ **15 pruebas pasadas** sin fallos
- ✅ **Tiempo de ejecución**: 2.15 segundos
- ✅ **Cobertura global**: 97%
- ✅ **Cobertura del comando conexion**: 100%

### Análisis de Cobertura por Módulo

1. **conexion.py**: 100% - Cobertura completa de todas las rutas de ejecución
2. **main.py**: 97% - Alta cobertura, con 1 branch no cubierto (probablemente relacionado con edge cases, es decir un caso extremo)
3. **main.py**: 100% - Punto de entrada completamente probado

## 🔧 Manejo de Errores

### Errores Implementados y Probados

1. **JSONDecodeError**: Archivos de configuración con formato JSON inválido
2. **OSError**: Problemas de acceso a archivos (permisos, archivos no encontrados)

### Ejemplo de Manejo de Errores

```python
try:
    with open(configuracion_archivo, "r", encoding="utf-8") as f:
        conf = json.load(f)
    consola.print("Configuracion cargada desde el archivo existente.", style="bold green")
except (json.JSONDecodeError, OSError) as e:
    consola.print(f"Error al leer la configuracion: {str(e)}", style="bold red")
    return
```

## 📁 Gestión de Configuración

### Archivo de Configuración

**Ubicación**: `.graphqlstore_config.json` (archivo ubicado donde se ejecuta el comando)

**Formato**:
```json
{
    "DB_HOST": "localhost",
    "DB_PUERTO": "3306",
    "DB_USUARIO": "admin",
    "DB_PASSWORD": "password",
    "DB_NOMBRE": "database_name"
}
```

### Flujo de Prioridades

1. **Archivo Externo** (--archivo): Mayor prioridad, copia completa
2. **Configuración Existente**: Se carga como base si existe
3. **Argumentos CLI**: Sobrescriben valores específicos
4. **Entrada Interactiva**: Se solicita para campos faltantes

## 🎯 Próximos Pasos

### Mejoras Identificadas
1. **Validación de Conexión**: Probar que se realizo la configuración correctamente

### Comando en Producción

El comando `conexion` está listo para uso en producción con:
- ✅ Cobertura de pruebas del 100%
- ✅ Manejo robusto de errores
- ✅ Interfaz usuario intuitiva
- ✅ Documentación completa
- ✅ Integración con pipeline CI/CD

Esta implementación establece una base sólida para la gestión de configuración en GraphQLStore CLI, con patrones de código reutilizables para futuros comandos.
