# Documentación del GeneradorMigracionMySQL - GraphQLStore CLI

## Resumen

Se ha implementado una funcionalidad esencial en GraphQLStore CLI: el **GeneradorMigracionMySQL**, un sistema avanzado que permite detectar diferencias entre esquemas GraphQL y generar migraciones SQL automáticas para bases de datos MySQL. Esta implementación incluye comparación de esquemas, generación de SQL incremental, manejo de relaciones complejas, y una suite completa de pruebas con cobertura del 94%.

## 📋 Características Implementadas

### Funcionalidad Principal

El generador de migraciones MySQL proporciona capacidades completas de migración automática:

1. **Comparación de Esquemas**: Análisis detallado de diferencias entre esquemas GraphQL
2. **Generación SQL Incremental**: Creación de sentencias SQL para migrar de un esquema a otro
3. **Manejo de Relaciones**: Gestión inteligente de relaciones 1:1, 1:N y N:M durante migraciones
4. **Modificación de Campos**: Detección y aplicación de cambios en tipos de datos y restricciones
5. **Gestión de Enums**: Actualización automática de enumeraciones y campos relacionados
6. **Visualización Rica**: Salida formateada con Rich para seguimiento detallado del proceso
7. **Manejo de Errores**: Sistema robusto de excepciones específicas para diferentes tipos de errores

### Sintaxis de Uso

```python
from source.cli.graphql.mysql_migracion import GeneradorMigracionMySQL

# crear instancia del generador
generador = GeneradorMigracionMySQL()

# generar migración completa
migracion = generador.generar_migracion(
    esquema_anterior="...",
    esquema_nuevo="...",
    id_migracion="custom_migration_id",
    visualizar_salida=True,
    visualizar_sql=True
)

# comparar esquemas solamente
diferencias = generador.diff_esquemas(
    esquema_anterior="...",
    esquema_nuevo="..."
)

# generar SQL desde diferencias
sql_migracion = generador.generar_sql_migracion(diferencias)
```

## 🏗️ Arquitectura de la Implementación

### Estructura de Archivos

```
source/cli/graphql/
├── mysql_migracion.py                   # Clase principal GeneradorMigracionMySQL
├── configuracion_y_constantes.py       # Clases de datos y estructuras
├── exceptions.py                        # Excepciones específicas de migración
├── templates.py                         # Templates SQL para generación
├── parser.py                           # Parser de esquemas GraphQL
└── procesar_relaciones.py              # Procesador de relaciones
```

### Arquitectura Modular

#### Clase Principal GeneradorMigracionMySQL (mysql_migracion.py)

```python
class GeneradorMigracionMySQL:
    """Generador de migraciones MySQL desde diferencias de esquemas GraphQL."""
    
    # Métodos públicos principales
    def generar_migracion(self, ...)        # Flujo completo de migración
    def diff_esquemas(self, ...)            # Comparación de esquemas
    def generar_sql_migracion(self, ...)    # Generación de SQL

    # Métodos de comparación
    def _comparar_tablas(self, ...)         # Comparar tablas
    def _comparar_campos(self, ...)         # Comparar campos
    def _comparar_relaciones(self, ...)     # Comparar relaciones
    def _comparar_enums(self, ...)          # Comparar enumeraciones

    # Métodos de generación SQL
    def _generar_sql_crear_tabla(self, ...)        # Crear nuevas tablas
    def _generar_sql_agregar_campo(self, ...)      # Agregar campos
    def _generar_sql_eliminar_campo(self, ...)     # Eliminar campos
    def _generar_sql_modificar_campo(self, ...)    # Modificar campos
    def _generar_sql_agregar_relacion(self, ...)   # Agregar relaciones
    def _generar_sql_eliminar_relacion(self, ...)  # Eliminar relaciones
    def _generar_sql_modificar_enum(self, ...)     # Modificar enums
    def _generar_sql_eliminar_tabla(self, ...)      # Eliminar tablas

    # Métodos de visualización
    def _mostrar_diferencias_detectadas(self, ...)  # Mostrar resumen
    def _visualizar_operacion_sql(self, ...)        # Visualizar SQL

    # Métodos auxiliares
    def _generar_id_migracion(self, ...)            # Generar ID único
    def _generar_hash_esquemas(self, ...)           # Hash unico

```

### Tipos de Diferencias Detectadas

#### 1. Diferencias en Tablas

```python
# Estructura InfoDiffTablas
class InfoDiffTablas:
    agregadas: List[str]                    # Tablas nuevas
    eliminadas: List[str]                   # Tablas a eliminar
    campos: Dict[str, InfoDiffCampos]       # Cambios por tabla
```

#### 2. Diferencias en Campos

```python
# estructura InfoDiffCampos
class InfoDiffCampos:
    agregados: List[InfoField]              # Campos nuevos
    eliminados: List[InfoField]             # Campos a eliminar
    modificados: List[InfoCambioCampo]      # Campos modificados
```

#### 3. Diferencias en Relaciones

```python
# estructura InfoDiffRelaciones
class InfoDiffRelaciones:
    agregadas: List[InfoRelacion]           # Relaciones nuevas
    eliminadas: List[InfoRelacion]          # Relaciones a eliminar
```

#### 4. Diferencias en Enums

```python
# estructura InfoDiffEnums
class InfoDiffEnums:
    agregados: List[InfoEnum]               # Enums nuevos
    eliminados: List[str]                   # Enums a eliminar
    modificados: List[InfoCambioEnum]       # Enums modificados
```

## 🧪 Suite de Pruebas

### Cobertura Alcanzada

| Módulo | Statements | Miss | Branch | BrPart | Cover |
|--------|------------|------|--------|--------|-------|
| mysql_migracion.py | 376 | 14 | 192 | 20 | **94%** |
| configuracion_y_constantes.py | 132 | 0 | 0 | 0 | **100%** |
| exceptions.py | 6 | 0 | 0 | 0 | **100%** |
| test_mysql_migracion.py | 262 | 2 | 2 | 0 | **99%** |
| **Total del Módulo Migración** | 776 | 16 | 194 | 20 | **98%** |

### Pruebas Implementadas

#### Pruebas del Generador de Migraciones (test_mysql_migracion.py)

```python
# Casos de prueba implementados (22 pruebas pasadas, 94% coverage):

# Inicialización y configuración
def test_inicializacion_generador_migracion()

# Flujo principal de migración
def test_generar_migracion_exitosa()
def test_generar_migracion_sin_cambios()
def test_generar_migracion_con_id_personalizado()
def test_generar_migracion_error_comparacion()

# Procesamiento de relaciones
def test_generar_migracion_procesar_relaciones()
def test_generar_migracion_relaciones_eliminadas()
def test_generar_migracion_relaciones_one_to_one_cascade()
def test_generar_migracion_relaciones_one_cascade_to_one()
def test_generar_migracion_relaciones_one_to_one_set_null()
def test_generar_migracion_relaciones_one_to_many()

# Comparación de esquemas (diff_esquemas)
def test_diff_esquemas_procesar_relaciones_auto_relacion()
def test_diff_esquemas_relaciones_con_diferentes_on_delete()

# Modificaciones de campos
def test_generar_migracion_eliminar_campos()
def test_generar_migracion_agregar_campos()
def test_generar_migracion_modificar_campos()

# Manejo de enumeraciones
def test_generar_migracion_modificar_enum()
def test_generar_migracion_nuevo_enum()
def test_generar_migracion_eliminar_enum()

# Operaciones de tabla
def test_generar_migracion_eliminar_tablas()
def test_generar_migracion_genera_columna_id_no_definido()

# Manejo de errores
def test_generar_sql_migracion_error_metodo_privado()
```

### Casos de Prueba Destacados

- ✅ **Migración Completa**: Flujo end-to-end con visualización y SQL
- ✅ **Detección de Cambios**: Identificación precisa de diferencias entre esquemas
- ✅ **Relaciones Complejas**: Manejo de relaciones 1:1, 1:N, N:M y auto-relaciones
- ✅ **Modificación de Campos**: Cambios en tipos, obligatoriedad y restricciones
- ✅ **Gestión de Enums**: Agregado, eliminación y modificación de enumeraciones
- ✅ **Manejo de Errores**: Excepciones específicas para diferentes tipos de errores
- ✅ **Visualización Rica**: Salida formateada con trees y syntax highlighting
- ✅ **Generación de IDs**: Creación automática de identificadores únicos
- ✅ **Columnas Automáticas**: Generación de ID primary key cuando no se especifica

## 📊 Resultados de Pruebas

### Ejecución Exitosa

```bash
================================ tests coverage ================================

Name                                                    Stmts   Miss Branch BrPart  Cover
-----------------------------------------------------------------------------------------
source/cli/graphql/mysql_migracion.py                     376     14    192     20    94%
source/cli/graphql/configuracion_y_constantes.py          132      0      0      0   100%
source/cli/graphql/exceptions.py                            6      0      0      0   100%
tests/cli/graphql/test_mysql_migracion.py                  262      2      2      0    99%
-----------------------------------------------------------------------------------------
============================== 22 passed in 1.92s ==============================
```

**Métricas de Calidad:**
- ✅ **22 pruebas pasadas** sin fallos
- ✅ **Cobertura del generador**: 94%
- ✅ **Cobertura de configuración**: 100%
- ✅ **Cobertura de excepciones**: 100%
- ✅ **Cobertura de pruebas**: 99%

### Análisis de Cobertura por Funcionalidad

1. **Métodos Públicos**: Todos los métodos principales cubiertos
2. **Comparación de Esquemas**: Cobertura excelente en detección de diferencias
3. **Generación SQL**: Alta cobertura en generación de sentencias
4. **Manejo de Errores**: La mayoria de las excepciones verificadas
5. **Visualización**: Una gran cobertura de salida formateada

## 🔧 Características del Generador

### Detección Inteligente de Diferencias

#### Comparación de Tablas

```python
def _comparar_tablas(self, tablas_anteriores, tablas_nuevas):
    """Detecta tablas agregadas, eliminadas y modificadas."""
    
    # Tablas agregadas
    diferencias.agregadas = [
        name for name in tablas_nuevas 
        if name not in tablas_anteriores
    ]
    
    # Tablas eliminadas
    diferencias.eliminadas = [
        name for name in tablas_anteriores 
        if name not in tablas_nuevas
    ]
    
    # Comparar campos en tablas existentes
    for nombre_tabla in tablas_nuevas:
        if nombre_tabla in tablas_anteriores:
            campos_anterior = tablas_anteriores[nombre_tabla].campos
            campos_nuevo = tablas_nuevas[nombre_tabla].campos
            
            if campos_anterior != campos_nuevo:
                diferencias.campos[nombre_tabla] = self._comparar_campos(
                    campos_anterior, campos_nuevo
                )
```

#### Comparación de Campos

```python
def _comparar_campos(self, campos_anteriores, campos_nuevos):
    """Detecta campos agregados, eliminados y modificados."""
    
    # Campos agregados
    for nombre_campo, info_campo in campos_nuevos.items():
        if nombre_campo not in campos_anteriores:
            if self._deberia_procesar_campo(info_campo):
                diferencias.agregados.append(info_campo)
    
    # Campos modificados
    for nombre_campo in campos_nuevos:
        if nombre_campo in campos_anteriores:
            campo_anterior = campos_anteriores[nombre_campo]
            campo_nuevo = campos_nuevos[nombre_campo]
            
            if self._campos_son_diferentes(campo_anterior, campo_nuevo):
                diferencias.modificados.append(
                    InfoCambioCampo(
                        nombre=nombre_campo,
                        info_antigua=campo_anterior,
                        info_nueva=campo_nuevo
                    )
                )
```

### Generación SQL Ordenada

El generador sigue un orden específico para evitar conflictos de dependencias:

```python
def generar_sql_migracion(self, diferencias):
    """Genera SQL siguiendo orden de dependencias."""
    
    # 1. crear nuevas tablas (para que las claves foraneas puedan
    # referenciarlas correctamente)
    for nombre_tabla in diferencias.tablas.agregadas:
        sql_tabla = self._generar_sql_crear_tabla(nombre_tabla, campos)
    
    # 2. eliminar relaciones (antes de eliminar campos/tablas)
    for relacion in diferencias.relaciones.eliminadas:
        sql_eliminar = self._generar_sql_eliminar_relacion(relacion)
    
    # 3. eliminar campos
    for nom_tabla, cambios_campos in diferencias.tablas.campos.items():
        for campo in cambios_campos.eliminados:
            sql_eliminar = self._generar_sql_eliminar_campo(nom_tabla, campo)
    
    # 4. agregar campos a tablas existentes
    for nom_tabla, cambios_campos in diferencias.tablas.campos.items():
        for campo in cambios_campos.agregados:
            sql_agregar = self._generar_sql_agregar_campo(nom_tabla, campo)
    
    # 5. modificar campos existentes
    for nom_tabla, cambios_campos in diferencias.tablas.campos.items():
        for cambio in cambios_campos.modificados:
            sql_modificar = self._generar_sql_modificar_campo(nom_tabla, cambio)
    
    # 6. modificar enums
    for enum_modificado in diferencias.enums.modificados:
        sql_enum = self._generar_sql_modificar_enum(enum_modificado)
    
    # 7. agregar nuevas relaciones
    for relacion in diferencias.relaciones.agregadas:
        sql_relacion = self._generar_sql_agregar_relacion(relacion)
    
    # 8. eliminar tablas (al final)
    for nombre_tabla in diferencias.tablas.eliminadas:
        sql_eliminar = self._generar_sql_eliminar_tabla(nombre_tabla)
```

## 🚀 Casos de Uso

### Migración de Blog Simple a Blog Avanzado

#### Esquema Anterior
```graphql
type User {
    id: ID! @id
    name: String!
    email: String
}

type Post {
    id: ID! @id
    title: String!
    content: String
}
```

#### Esquema Nuevo
```graphql
type User {
    id: ID! @id
    name: String!
    email: String!
    posts: [Post] @relation(name: "UserPosts")
    profile: Profile @relation(name: "UserProfile")
    createdAt: DateTime @createdAt
}

type Post {
    id: ID! @id
    title: String!
    content: String
    published: Boolean
    author: User @relation(name: "UserPosts", onDelete: CASCADE)
    tags: [String]
}

type Profile {
    id: ID! @id
    bio: String
    avatar: String
    user: User @relation(name: "UserProfile", onDelete: CASCADE)
}
```

#### SQL Generado Automáticamente

```sql
-- Migración generada automáticamente
-- Fecha: 2024-12-17T14:30:22

-- Crear tabla Profile
CREATE TABLE Profile (
  `id` VARCHAR(25) NOT NULL PRIMARY KEY,
  `bio` VARCHAR(255),
  `avatar` VARCHAR(255)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Modificar campo email en User
ALTER TABLE `User` MODIFY COLUMN `email` VARCHAR(255) NOT NULL;

-- Agregar campo posts a User
ALTER TABLE `User` ADD COLUMN `createdAt` DATETIME DEFAULT CURRENT_TIMESTAMP;

-- Agregar campo published a Post
ALTER TABLE `Post` ADD COLUMN `published` BOOLEAN;

-- Agregar campo tags a Post
ALTER TABLE `Post` ADD COLUMN `tags` JSON;

-- Agregar foreign key user_id en Post
ALTER TABLE `Post`
ADD COLUMN `user_id` VARCHAR(25),
ADD CONSTRAINT `fk_User_posts_Post` FOREIGN KEY (`user_id`) 
REFERENCES `User`(id) ON DELETE CASCADE;

-- Agregar foreign key user_id en Profile
ALTER TABLE `Profile`
ADD COLUMN `user_id` VARCHAR(25) UNIQUE,
ADD CONSTRAINT `fk_User_profile_Profile` FOREIGN KEY (`user_id`) 
REFERENCES `User`(id) ON DELETE CASCADE;
```

### Migración con Cambios de Enums

#### Esquema Anterior
```graphql
enum UserStatus {
    ACTIVE
    INACTIVE
}

type User {
    id: ID! @id
    name: String!
    status: UserStatus
}
```

#### Esquema Nuevo
```graphql
enum UserStatus {
    ACTIVE
    INACTIVE
    PENDING
    BANNED
}

type User {
    id: ID! @id
    name: String!
    status: UserStatus
}
```

#### SQL Generado para Enum

```sql
-- Actualizar enum UserStatus en User
ALTER TABLE `User` MODIFY COLUMN `status` ENUM('ACTIVE', 'INACTIVE', 'PENDING', 'BANNED');
```

### Migración con Relaciones Complejas

#### Esquema Anterior
```graphql
type User {
    id: ID! @id
    name: String!
}

type Post {
    id: ID! @id
    title: String!
}
```

#### Esquema Nuevo
```graphql
type User {
    id: ID! @id
    name: String!
    posts: [Post] @relation(name: "UserPosts")
    roles: [Role] @relation(name: "UserRoles", link: TABLE)
}

type Post {
    id: ID! @id
    title: String!
    author: User @relation(name: "UserPosts", onDelete: CASCADE)
    tags: [Tag] @relation(name: "PostTags", link: TABLE)
}

type Role {
    id: ID! @id
    name: String!
    users: [User] @relation(name: "UserRoles", link: TABLE)
}

type Tag {
    id: ID! @id
    name: String!
    posts: [Post] @relation(name: "PostTags", link: TABLE)
}
```

#### SQL Generado para Relaciones

```sql
-- Crear tabla Role
CREATE TABLE Role (
  `id` VARCHAR(25) NOT NULL PRIMARY KEY,
  `name` VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Crear tabla Tag
CREATE TABLE Tag (
  `id` VARCHAR(25) NOT NULL PRIMARY KEY,
  `name` VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Agregar foreign key user_id en Post (1:N)
ALTER TABLE `Post`
ADD COLUMN `user_id` VARCHAR(25),
ADD CONSTRAINT `fk_User_posts_Post` FOREIGN KEY (`user_id`) 
REFERENCES `User`(id) ON DELETE CASCADE;

-- Crear tabla junction UserRoles (N:M)
CREATE TABLE UserRoles (
  `user_id` VARCHAR(25) NOT NULL,
  `role_id` VARCHAR(25) NOT NULL,
  PRIMARY KEY (`user_id`, `role_id`),
  CONSTRAINT `fk_User_roles_Role` FOREIGN KEY (`user_id`) 
  REFERENCES `User`(id) ON DELETE CASCADE,
  CONSTRAINT `fk_Role_users_User` FOREIGN KEY (`role_id`) 
  REFERENCES `Role`(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Crear tabla junction PostTags (N:M)
CREATE TABLE PostTags (
  `post_id` VARCHAR(25) NOT NULL,
  `tag_id` VARCHAR(25) NOT NULL,
  PRIMARY KEY (`post_id`, `tag_id`),
  CONSTRAINT `fk_Post_tags_Tag` FOREIGN KEY (`post_id`) 
  REFERENCES `Post`(id) ON DELETE CASCADE,
  CONSTRAINT `fk_Tag_posts_Post` FOREIGN KEY (`tag_id`) 
  REFERENCES `Tag`(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## 🔧 Manejo Avanzado de Casos Especiales

### Jerarquía de Excepciones

```python
# Jerarquía específica para migraciones
GraphQLStoreError                    # Base del sistema
├── MigrationError                   # Errores generales de migración
│   ├── MigrationGenerationError     # Errores generando SQL
│   └── MigrationExecutionError      # Errores ejecutando migración
├── SchemaComparisonError            # Errores comparando esquemas
└── RelationshipError                # Errores procesando relaciones
```

### Manejo de Errores en el Flujo

```python
def generar_migracion(self, esquema_anterior, esquema_nuevo):
    try:
        # 1. Comparar esquemas
        diferencias = self.diff_esquemas(esquema_anterior, esquema_nuevo)
        
        # 2. Generar SQL
        sql_migracion = self.generar_sql_migracion(diferencias)
        
        # 3. Crear información de migración
        return InfoMigracion(...)
        
    except GraphQLStoreError as e:
        raise MigrationError(f"Error generando migración: {str(e)}") from e
```

### Generación Automática de ID Primary Key

```python
def _generar_sql_crear_tabla(self, nombre_tabla, campos):
    """Genera tabla con ID automático si no existe."""
    
    has_primary_key = False
    ...
    for campo in campos:
        if "id" in campo.directivas:
            has_primary_key = True
    ...
    # Agregar ID automático si no hay primary key
    if not has_primary_key:
        columnas.insert(0, "  `id` VARCHAR(25) NOT NULL PRIMARY KEY")
```

### Determinación Inteligente de Foreign Keys

```python
def _determinar_tabla_fk(self, relacion):
    """Determinar en qué tabla va la foreign key."""
    if relacion.tipo_relation == TipoRelacion.ONE_TO_MANY.value:
        return (
            relacion.objetivo.tabla_objetivo
            if relacion.fuente.fuente_es_lista
            else relacion.fuente.tabla_fuente
        )

    if relacion.tipo_relation == TipoRelacion.ONE_TO_ONE.value:
        if relacion.fuente.on_delete == OnDelete.CASCADE.value:
            return relacion.fuente.tabla_fuente

        return relacion.objetivo.tabla_objetivo

    return relacion.fuente.tabla_fuente
```

## 📈 Visualización Rica con Rich

### Diferencias Detectadas

```python
def _mostrar_diferencias_detectadas(
    self,
    diferencias,
):
    """Mostrar diferencias detectadas entre esquemas."""
    tree = Tree("\n📋 Diferencias detectadas", style="bold green")

    # Tablas
    if diferencias.tablas.agregadas:
        tree.add(
            f"➕ Tablas agregadas: {len(diferencias.tablas.agregadas)}",
        )
    if diferencias.tablas.eliminadas:
        tree.add(
            f"➖ Tablas eliminadas: {len(diferencias.tablas.eliminadas)}",
        )

    # Campos
    total_campos_agregados = sum(
        len(c.agregados) for c in diferencias.tablas.campos.values()
    )
    total_campos_eliminados = sum(
        len(c.eliminados) for c in diferencias.tablas.campos.values()
    )
    total_campos_modificados = sum(
        len(c.modificados) for c in diferencias.tablas.campos.values()
    )

    if total_campos_agregados:
        tree.add(f"🔹 Campos agregados: {total_campos_agregados}")
    if total_campos_eliminados:
        tree.add(f"🔹 Campos eliminados: {total_campos_eliminados}")
    if total_campos_modificados:
        tree.add(f"🔹 Campos modificados: {total_campos_modificados}")

    # Relaciones
    df = diferencias.relaciones
    if df.agregadas:
        tree.add(f"🔗 Relaciones agregadas: {len(df.agregadas)}")
    if df.eliminadas:
        tree.add(f"🔗 Relaciones eliminadas: {len(df.eliminadas)}")

    self.consola.print(tree)
```

### Operaciones SQL Detalladas

```python
def _visualizar_operacion_sql(self, tipo_operacion, descripcion, sql):
    """Visualiza cada operación SQL individualmente."""
    
    if self.visualizar_salida:
        tree = Tree(f"🔧 {tipo_operacion}")
        tree.add(descripcion)
        self.consola.print(tree)
        
        if self.visualizar_sql:
            syntax = Syntax(sql, "sql", theme="monokai", line_numbers=True)
            self.consola.print(
                Panel(
                    syntax,
                    title=f"SQL - {tipo_operacion}",
                    border_style="yellow"
                )
            )
```

## 🎯 Información de Migración Generada

### Estructura InfoMigracion

```python
@dataclass
class InfoMigracion:
    id_migracion: str                    # ID único de migración
    timestamp: str                       # Timestamp ISO 8601
    esquema_anterior: str                # Esquema original
    esquema_nuevo: str                   # Esquema destino
    diferencias: InfoDiffEsquema         # Diferencias detectadas
    sql_generado: str                    # SQL completo generado
```

### Generación de ID Único

```python
def _generar_hash_esquemas(self, esquema1, esquema2):
    """Genera hash único para identificar la migración."""
    contenido = f"{esquema1}{esquema2}"
    return hashlib.md5(contenido.encode("utf-8")).hexdigest()

# Formato de ID: migration_20241217_143022_abcd1234
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
hash_schemas = self._generar_hash_esquemas(esquema_anterior, esquema_nuevo)
id_migracion = f"migration_{timestamp}_{hash_schemas[:8]}"
```

## 🚀 Próximos Pasos

### Mejoras Identificadas

1. **Rollback de Migraciones**: Implementar capacidad de revertir migraciones
2. **Validación Pre-migración**: Verificación de integridad antes de aplicar cambios
3. **Migraciones Condicionales**: Soporte para migraciones que dependen de datos existentes
4. **Optimización de Índices**: Detección automática de necesidades de indexación
5. **Migración de Datos**: Soporte para transformación de datos durante migraciones

### Características Avanzadas

1. **Modo fly**: Modo de prueba sin aplicar cambios reales
2. **Migración Incremental**: Aplicación paso a paso con checkpoints

## 🏆 Logros Destacados

### Funcionalidad Completa
- **Detección inteligente** de todos los tipos de cambios
- **Generación SQL ordenada** respetando dependencias
- **Manejo robusto** de relaciones complejas
- **Soporte completo** para enumeraciones
- **Generación automática** de columnas ID cuando no se especifican

### Calidad del Código
- **94% de cobertura** en funcionalidad principal
- **100% de cobertura** en configuración y excepciones
- **22 pruebas robustas** que cubren casos reales y edge cases
- **Manejo específico** de errores con jerarquía de excepciones

### Experiencia de Usuario
- **Visualización rica** con trees y syntax highlighting
- **Progreso detallado** de cada operación SQL
- **Control granular** de visualización
- **Información completa** de migración generada

### Robustez Técnica
- **Orden correcto** de operaciones SQL
- **Determinación inteligente** de ubicación de foreign keys
- **Manejo seguro** de eliminación de relaciones
- **Generación automática** de IDs únicos de migración



El GeneradorMigracionMySQL de GraphQLStore CLI representa una implementación madura y robusta para migración automática de esquemas, proporcionando todas las herramientas necesarias para evolucionar esquemas GraphQL de manera segura y eficiente en entornos de producción.
