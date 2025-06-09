# Documentación del comando `probar-conexion` - GraphQLStore CLI

## Resumen

Se ha implementado una nueva característica crítica en GraphQLStore CLI: el **comando `probar-conexion`**, que permite verificar la conectividad y validez de la configuración de base de datos establecida previamente con el comando `conexion`. Esta implementación incluye validación robusta de configuración, diagnóstico detallado de conexión, manejo elegante de errores y una suite completa de pruebas con cobertura del 99%.

## 📋 Características Implementadas

### Funcionalidad Principal

El comando `probar-conexion` proporciona validación completa de la configuración de base de datos:

1. **Validación de Configuración**: Verifica que existe y es válida la configuración previa
2. **Prueba de Conectividad**: Establece conexión real con la base de datos configurada
3. **Modo Verbose**: Ofrece estadísticas detalladas de la base de datos

### Sintaxis del Comando

```bash
# Prueba básica de conexión
graphqlstore probar-conexion

# Prueba con información detallada
graphqlstore probar-conexion --verbose
graphqlstore probar-conexion -v
```

## 🏗️ Arquitectura de la Implementación

### Estructura de Archivos

```
source/cli/
├── main.py                      # Clase CLI principal y orquestación
├── base.py                      # Clase abstracta Comando (patrón Command)
├── core.py                      # ConstructorCLI (patrón Builder)
├── __init__.py                  # Inicialización del módulo
└── probar_conexion/
    ├── __init__.py             # Inicialización del módulo probar_conexion
    ├── main.py                 # Función principal proconexion()
    ├── comando_probar_conexion.py  # Clase ComandoProbarConexion
    └── README.md              # Documentación del comando
```

### Arquitectura Modular

#### Clase Base Abstracta ([`source/cli/base.py`](source/cli/base.py))

```python
class Comando(ABC):
    """Clase abstracta para los comandos"""
    
    @abstractmethod
    def crear_comando(self, subparsers):
        """Registrar el comando en el parser"""
    
    @abstractmethod
    def contenido_comando(self, args):
        """Método que se ejecuta al ejecutar el comando"""
```

#### Clase CLI Principal ([`source/cli/main.py`](source/cli/main.py))

```python
class CLI:
    """Clase principal para la interfaz de línea de comandos de GraphQLStore"""
    
    def __init__(self, titulo: str = "GraphQLStore CLI")
    def parsear_comando(self)          # Registra comandos disponibles
    def lanzamiento_condicionado(self) # Ejecuta el comando solicitado
    def ejecutar(self)                 # Punto de entrada principal
```

#### Clase ConstructorCLI ([`source/cli/core.py`](source/cli/core.py))

```python
class ConstructorCLI:
    """Clase para construir la interfaz de línea de comandos"""
    
    def __init__(self, titulo: str = "GraphQLStore CLI")
    # agregar un comando al parser
    def agregar_comando(self)
    # parsear los argumentos de la línea de comandos
    def parsear(self)
```

#### Clase ComandoProbarConexion ([`source/cli/probar_conexion/comando_probar_conexion.py`](source/cli/probar_conexion/comando_probar_conexion.py))

```python
class ComandoProbarConexion(Comando):
    """Implementación del comando probar-conexion"""
    
    def crear_comando(self, subparsers):     # Configura argumentos del comando
    def contenido_comando(self, args):       # Ejecuta la lógica del comando
```

**Argumentos Soportados:**
- `--verbose, -v`: Mostrar información detallada de la conexión y estadísticas de la base de datos

### Función de Prueba de Conexión ([`source/cli/probar_conexion/main.py`](source/cli/probar_conexion/main.py))

```python
def proconexion(args):
    """Función para comprobar la conexión a la base de datos configurada."""
```

**Flujo de Ejecución:**

1. **Búsqueda de Configuración**: Localiza archivo `.graphqlstore_config.json` en el directorio actual
2. **Carga y Validación**: Carga la configuración y verifica que esten todos los parámetros
3. **Inicialización del Adaptador**: Crea instancia del adaptador MySQL
4. **Conexión a la Base de Datos**: Establece conexión real con los parámetros configurados
5. **Prueba de Conectividad**: Ejecuta verificaciones de estado
6. **Diagnóstico y Reporting**: Proporciona feedback detallado al usuario

## 🧪 Suite de Pruebas

### Cobertura Alcanzada

| Módulo | Statements | Miss | Branch | BrPart | Cover |
|--------|------------|------|--------|--------|-------|
| [`source/cli/probar_conexion/comando_probar_conexion.py`](source/cli/probar_conexixon/comando_probar_conexion.py) | 9 | 0 | 2 | 0 | **100%** |
| [`source/cli/probar_conexion/main.py`](source/cli/probar_conexion/main.py) | 13 | 0 | 2 | 0 | **100%** |
| [`source/cli/database/adaptadores/mysql.py`](source/cli/database/adaptadores/mysql.py) | 60 | 0 | 18 | 2 | **97%** |
| [`source/cli/loaders/conf_json_loader.py`](source/cli/loaders/conf_json_loader.py) | 30 | 0 | 4 | 0 | **100%** |
| **Total del Proyecto** | 793 | 7 | 62 | 4 | **99%** |

### Pruebas Implementadas

#### 1. Pruebas de la Función Probar Conexión ([`tests/cli/probar_conexion/test_probar_conexion.py](tests/cli/probar_conexion/test_probar_conexion.py`))

```python
# Casos de prueba implementados (54 statements, 100% coverage):

# Prueba exitosa con verbose=False
def test_proconexion_exitoso_verbose_falso()
# Prueba exitosa con verbose=True
def test_proconexion_exitoso_verbose_verdadero()
# Manejo de configuracion invalida
def test_proconexion_configuracion_invalida()
```

**Casos de Prueba Destacados:**

- ✅ **Modos de Operación**: Confirma funcionamiento correcto en modo básico y verbose
- ✅ **Flujo de Control**: Verifica el orden correcto de operaciones y manejo de dependencias
- ✅ **Casos Edge**: Prueba situaciones límite

#### 2. Pruebas de ComandoProbarConexion (`tests/cli/probar_conexion/test_comando_probar_conexion.py`)

```python
# Casos de prueba implementados (28 statements, 100% coverage):

# comprobar comportamiento  de los argumentos
def test_crear_comando_agregar_argumentos()
# comprobar comportamiento de proconexion
def test_contenido_comando() 
```

#### 3. Pruebas del Adaptador MySQL ([`tests/cli/database/adaptadores/test_mysql.py`](tests/cli/database/adaptadores/test_mysql.py))

```python
# Casos de prueba implementados (139 statements, 99% coverage):

# inicialización del adaptador
def test_inicializacion()
# conexión exitosa
def test_connect_exitoso()
# configuración por defecto
def test_connect_con_configuracion_por_defecto()
# fallo de conexión
def test_conectar_falla_conexion()
# prueba exxxitosa con verbose=False
def test_probar_conexion_exitoso_verbose_falso()
# prueba exitosa con verbose=True
def test_probar_conexion_exitoso_verbose_verdadero()
# fallo de conexión con verbose=Falso
def test_probar_conexion_falla_verbose_falso()
# fallo de conexión con verbose=Verdadero
def test_probar_conexion_falla_verbose_verdadero()
# gestion de cierre sin conexión
def test_cerrar_conexion_sin_conexion()
# gestión de cierre con conexión
def test_cerrar_conexion_con_conexion()
# ejecutar consulta sin conexión
def test_ejecutar_consulta_sin_conexion()
# ejecutar consulta con conexión
def test_ejecutar_consulta_con_conexion()
# probar conexion sin conexion ni cursor
def test_probar_conexion_sin_conexion_ni_cursor()
```

#### 4. Pruebas del Cargador de Configuración (`tests/cli/loaders/test_configuracion_json_loader.py`)

```python
# Casos de prueba implementados (60 statements, 100% coverage):

# inicialización del loader
def test_inicializacion()
# archivo no existe
def test_cargar_config_archivo_no_existe()
# configuracion exitosa
def test_cargar_config_exitosa()
# error JSON en la configuración
def test_cargar_config_error_json()
# verificación exitosa
def test_verificar_configuracion_completa()
# configuración incompleta
def test_verificar_configuracion_faltantes()
```

## 📊 Resultados de Pruebas

### Ejecución Exitosa

```bash
=========================== test session starts ===========================
platform linux -- Python 3.10.12, pytest-8.3.5, pluggy-1.6.0
rootdir: /graphqlstore
configfile: pytest.ini
plugins: cov-6.1.1
collected 43 items

tests/cli/database/adaptadores/test_mysql.py .............               [ 30%]
tests/cli/loaders/test_configuracion_json_loader.py ......               [ 44%]
tests/cli/probar_conexion/test_comando_probar_conexion.py ..             [ 48%]
tests/cli/probar_conexion/test_probar_conexion.py ...                    [ 55%]
tests/cli/test_cli.py .......                                            [ 72%]
tests/cli/test_comando_conexion.py ..                                    [ 76%]
tests/cli/test_conexion.py .......                                       [ 93%]
tests/test_main.py ...                                                   [100%]

================================ tests coverage ================================
_______________ coverage: platform linux, python 3.10.12-final-0 _______________

Name                                                        Stmts   Miss Branch BrPart  Cover
---------------------------------------------------------------------------------------------
source/__init__.py                                              1      0      0      0   100%
source/cli/__init__.py                                          0      0      0      0   100%
source/cli/base.py                                              6      0      0      0   100%
source/cli/conexion/__init__.py                                 3      0      0      0   100%
source/cli/conexion/comando_conexion.py                        14      0      2      0   100%
source/cli/conexion/main.py                                    56      0     18      0   100%
source/cli/core.py                                             12      2      0      0    83%
source/cli/database/__init__.py                                 2      0      0      0   100%
source/cli/database/adaptador_database.py                       8      0      0      0   100%
source/cli/database/adaptadores/__init__.py                     2      0      0      0   100%
source/cli/database/adaptadores/mysql.py                       60      0     18      2    97%
source/cli/loaders/__init__.py                                  0      0      0      0   100%
source/cli/loaders/conf_json_loader.py                         30      0      4      0   100%
source/cli/loaders/conf_loader.py                               5      0      0      0   100%
source/cli/main.py                                             23      0      2      0   100%
source/cli/probar_conexion/__init__.py                          3      0      0      0   100%
source/cli/probar_conexion/comando_probar_conexion.py           9      0      2      0   100%
source/cli/probar_conexion/main.py                             13      0      2      0   100%
source/main.py                                                  6      0      2      0   100%
tests/cli/database/adaptadores/test_mysql.py                  139      1      0      0    99%
tests/cli/loaders/test_configuracion_json_loader.py            60      0      0      0   100%
tests/cli/probar_conexion/test_comando_probar_conexion.py      28      0      2      0   100%
tests/cli/probar_conexion/test_probar_conexion.py              54      0      0      0   100%
tests/cli/test_cli.py                                          85      0      0      0   100%
tests/cli/test_comando_conexion.py                             27      0      2      0   100%
tests/cli/test_conexion.py                                     97      0      0      0   100%
tests/test_main.py                                             50      4      8      2    90%
---------------------------------------------------------------------------------------------
TOTAL                                                         793      7     62      4    99%
============================== 43 passed in 2.88s ==============================
```

**Métricas de Calidad:**
- ✅ **43 pruebas pasadas** sin fallos
- ✅ **Tiempo de ejecución**: 2.88 segundos
- ✅ **Cobertura global**: 99%
- ✅ **Cobertura del comando probar-conexion**: 100%
- ✅ **Cobertura del adaptador MySQL**: 97%
- ✅ **Arquitectura modular completamente probada**

### Análisis de Cobertura por Módulo

1. **[`source/cli/probar_conexion/main.py`](source/cli/probar_conexion/main.py)**: 100% - Cobertura completa de todas las rutas de ejecución
2. **[`source/cli/probar_conexion/comando_probar_conexion.py`](source/cli/probar_conexion/comando_probar_conexion.py)**: 100% - Clase comando completamente verificada
3. **[`source/cli/database/adaptadores/mysql.py`](source/cli/database/adaptadores/mysql.py)**: 97% - Alta cobertura con 2 branches no cubiertos (casos edge específicos)
4. **[`source/cli/loaders/conf_json_loader.py`](source/cli/loaders/conf_json_loader.py)**: 100% - Cargador de configuración completamente probado
5. **[`source/cli/base.py`](source/cli/base.py)**: 100% - Clase abstracta completamente verificada
6. **[`source/cli/core.py`](source/cli/core.py)**: 83% - Constructor CLI con alta cobertura
7. **[`source/cli/main/py`](source/cli/main.py)**: 100% - CLI principal completamente probada
8. **[`source/main.py`](source/main.py)**: 100% - Punto de entrada completamente probado

## 🔧 Manejo de Errores

### Errores Implementados y Probados

1. **Configuración Faltante**: Archivo `.graphqlstore_config.json` no existe
2. **Configuración Inválida**: JSON malformado o parámetros faltantes
3. **Errores de Conexión**: Fallo al conectar con la base de datos MySQL
4. **Errores de Autenticación**: Credenciales inválidas o permisos insuficientes
5. **Errores de Base de Datos**: Base de datos no existe o no es accesible

### Ejemplo de Manejo de Errores

```python
def cargar_configuracion():
    if not self.ruta_archivo.exists():
            self.consola.print(
                "❌ Archivo de configuracion no encontrado. "
                "Asegurate de haber ejecutado primeramente "
                "el comando 'conexion'",
                style=self.co_no,
            )
        
    try:
        with open(self.ruta_archivo, "r", encoding="utf-8") as archivo:
            conf = json.load(archivo)
    except (json.JSONDecodeError, OSError) as e:
        msg = f"Error al leer el archivo de configuracion: {str(e)}"
        self.consola.print(msg, style=self.co_no)
```

### Características del Manejo de Errores

- **Mensajes Informativos**: Errores facilmente comprensibles para el usuario
- **Salida Elegante**: El programa no se cierra abruptamente, proporciona feedback útil
- **Códigos de Colores**: Uso de Rich para mensajes visualmente distinguibles
- **Información de Diagnóstico**: Detalles técnicos disponibles en modo verbose

## 📁 Gestión de Configuración

### Dependencia de Configuración Previa

**Prerrequisito**: El comando `probar-conexion` requiere que se haya ejecutado previamente el comando `conexion` para establecer la configuración de base de datos.

**Archivo de Configuración Esperado**: `.graphqlstore_config.json`

**Formato Requerido**:
```json
{
    "DB_HOST": "localhost",
    "DB_PUERTO": "3306",
    "DB_USUARIO": "admin",
    "DB_PASSWORD": "password",
    "DB_NOMBRE": "database_name"
}
```

### Validación de Configuración

El comando verifica la presencia y validez de todos los parámetros requeridos:

- ✅ **DB_HOST**: Dirección del servidor de base de datos
- ✅ **DB_PUERTO**: Puerto de conexión
- ✅ **DB_USUARIO**: Usuario de base de datos
- ✅ **DB_PASSWORD**: Contraseña de acceso
- ✅ **DB_NOMBRE**: Nombre de la base de datos

### Flujo de Validación

1. **Verificación de Archivo**: Confirma existencia del archivo de configuración
2. **Parseo JSON**: Valida formato y estructura del archivo
3. **Completitud**: Verifica presencia de todos los parámetros requeridos
4. **Conectividad**: Prueba conexión real con los parámetros proporcionados

## 🎯 Patrones de Diseño Implementados

### 1. **Patrón Command**
- Clase abstracta `Comando` define la interfaz para comandos
- `ComandoProbarConexion` implementa la interfaz específica

### 2. **Patrón Repositorio**
- `AdaptadorDatabase` repositorio abstractro para operaciones de base de datos
  - `AdaptadorMySQL` para MySQL

### 3. **Patrón Factory Method**
- `ConfigLoader` factory para crear cargadores de configuración específicos
  - `ConfJsonLoader` para JSON

## 🚀 Integración con el Ecosistema

### Dependencias del Comando

1. **Comando `conexion`**: Prerrequisito para establecer configuración
2. **Adaptador MySQL**: Manejo específico de conectividad MySQL
3. **Cargador JSON**: Gestión de archivos de configuración
4. **Rich Console**: Interface de usuario mejorada

### Flujo de Trabajo Típico

```bash
# 1. Configurar conexión (prerrequisito)
graphqlstore conexion --host DOCKER_IP --puerto DOCKER_PORT --usuario MYSQL_USER --password secret MYSQL_SECRET --db-nombre DB_NOMBRE

# 2. Probar la configuración
graphqlstore probar-conexion

# 3. Diagnóstico detallado (opcional)
graphqlstore probar-conexion --verbose
```

### Casos de Uso

- **Verificación Post-Configuración**: Confirmar que la configuración establecida funciona
- **Diagnóstico de Problemas**: Identificar issues de conectividad con detalles

## 🚀 Próximos Pasos

### Mejoras Identificadas

1. **Soporte Multi-Base de Datos**: Extensión para PostgreSQL, Redis, etc.
2. **Métricas de Performance**: Medición de latencia y throughput
4. **Reportes Exportables**: Generación de informes en diferentes formatos

### Comando en Producción

El comando `probar-conexion` está listo para uso en producción con:

- ✅ **Cobertura de pruebas del 99%** (100% en módulos críticos)
- ✅ **Manejo robusto de errores** con casos edge cubiertos
- ✅ **Interfaz usuario intuitiva** con feedback claro y útil
- ✅ **Documentación completa** y actualizada
- ✅ **Arquitectura escalable** para futuras extensiones
- ✅ **Integración con pipeline CI/CD**
- ✅ **Pruebas parametrizadas** con pytest
- ✅ **Patrones de diseño sólidos** para mantenibilidad y extensibilidad
- ✅ **Validación exhaustiva** de configuración y conectividad
- ✅ **Diagnóstico detallado** para troubleshooting efectivo

Esta implementación complementa perfectamente el comando `conexion`, proporcionando un flujo completo de configuración y validación de conectividad de base de datos en GraphQLStore CLI, estableciendo una base sólida y confiable para operaciones críticas de datos.
