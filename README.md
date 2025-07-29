
[<p  align="center"><img src="./graphqlstore.png" alt="GraphQLStore CLI" width="300"></p>]()
# GraphQLStore

<div align="center">

[![PyPI version](https://badge.fury.io/py/graphqlstore.svg)](https://badge.fury.io/py/graphqlstore)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Private](https://img.shields.io/badge/License-Private-red.svg)](LICENSE)
[![CI](https://github.com/adg1023/graphqlstore/actions/workflows/ci.yml/badge.svg)](https://github.com/adg1023/graphqlstore/actions/workflows/ci.yml)
[![CD](https://github.com/adg1023/graphqlstore/actions/workflows/cd.yml/badge.svg)](https://github.com/adg1023/graphqlstore/actions/workflows/cd.yml)
[![coverage](https://img.shields.io/badge/coverage-97%25-brightgreen.svg)](https://github.com/your-username/graphqlstore)
[![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen.svg)](https://pre-commit.com)
[![pytest](https://img.shields.io/badge/pytest-8.3.5-brightgreen.svg)](https://docs.pytest.org/en/stable/)
[![rich](https://img.shields.io/badge/Rich-14.0.0-blue.svg)](https://rich.readthedocs.io/en/stable/introduction.html)

**🚀 Herramienta CLI avanzada para gestionar esquemas GraphQL y base de datos de manera sincronizada**

📖 Documentación • ⚡ Inicio Rápido • 🎯 Características • 📊 Ejemplos

</div>

---

## 🌟 Descripción

GraphQLStore CLI es una herramienta de línea de comandos profesional que automatiza la gestión de bases de datos MySQL a partir de esquemas GraphQL. Transforma definiciones GraphQL en estructuras de base de datos completamente funcionales con soporte para relaciones complejas, migraciones automáticas y visualización rica.

### ✨ ¿Por qué GraphQLStore CLI?

- 🔄 **Transformación Automática**: Convierte esquemas GraphQL a MySQL sin configuración manual
- 🛡️ **Migraciones Seguras**: Evoluciona tu base de datos preservando la integridad de los datos
- 🎨 **Visualización Amigable**: Interfaz amigable con Rich Console y syntax highlighting
- ⚡ **Detección Inteligente**: Encuentra y procesa esquemas automáticamente
- 🔗 **Relaciones Avanzadas**: Soporte completo para relaciones 1:1, N:1, 1:N y N:M
- 📊 **Producción Ready**: 97% de cobertura de tests y arquitectura escalable

---

## 🎯 Características

### 🏗️ Comandos Principales

| Comando | Descripción | Estado |
|---------|-------------|--------|
| `conexion` | Configurar conexión a base de datos MySQL | ✅  |
| `probar-conexion` | Verificar conectividad y diagnósticos | ✅ |
| `inicializar` | Crear base de datos desde esquema GraphQL | ✅  |
| `migracion` | Evolucionar esquemas existentes | ✅ |
| `server` | Genera una estructura de un servidor GraphQL de pruebas en JavaScript | ✅ |

### 🔧 Características Técnicas

- **🔍 Parser GraphQL**: Análisis completo de esquemas
- **🔗 Procesador de Relaciones**: Manejo inteligente de relaciones
- **🗄️ Generador MySQL**: Conversión optimizada GraphQL → SQL
- **📈 Sistema de Migraciones**: Evolución segura de esquemas

### 🎨 Tipos de Datos Soportados

| GraphQL | MySQL | Características |
|---------|-------|----------------|
| `ID` | `VARCHAR(25)` | Primary keys automáticos |
| `String` | `VARCHAR(255)` | Soporte UTF-8 completo |
| `Int` | `INT` | Enteros |
| `Boolean` | `BOOLEAN` | Valores true/false |
| `DateTime` | `DATETIME` | Timestamps con @createdAt/@updatedAt |
| `Float` | `DECIMAL(10,2)` | Precisión decimal |
| `JSON` | `JSON` | Objetos complejos nativos |
| `[]` | `JSON` | Listas de valores |
| `Enum` | `ENUM(...)` | Enumeraciones tipo-seguras |
| `!` | `NOT NULL` | Validación de campos obligatorios |
| sin `!` | `NULL` | Campos opcionales |

### 📜 Directivas Soportadas
| Directiva | Descripción | Argumentos |
|-----------|-------------|------------|
| `@id` | Define un campo como clave primaria | Ninguno |
| `@unique` | Asegura que el campo sea único | Ninguno |
| `@default` | Establece un valor por defecto para el campo | `value` |
| `@db` | Renombra el campo en la base de datos | `rename` |
| `@protected` | Oculta el campo en el esquema cliente | Ninguno |
| `@relation` | Define relaciones entre tipos  | `name`, `type`, `onDelete` |
| `@createdAt` | Marca el campo con la fecha de creación | Ninguno |
| `@updatedAt` | Marca el campo con la fecha de actualización | Ninguno |

#### Directiva @id - Clave 
La directiva `@id` define un campo como clave primaria en la base de datos:

**Sintaxis**:
```graphql
id: ID! @id
```

**Ejemplo**:
```graphql
type User {
  id: ID! @id
  nombre: String!
}
```

**SQL generado**:
```sql
CREATE TABLE User (
  id VARCHAR(25) NOT NULL PRIMARY KEY,
  nombre VARCHAR(255) NOT NULL
);
```

#### Directiva @unique - Campos Únicos
La directiva `@unique` asegura que un campo de tipo escalar tenga valores únicos en la base de datos:

**Sintaxis**:
```graphql
campo: Tipo! @unique
```

#### Directiva @default - Valores por defecto

La directiva `@default` permite establecer valores por defecto para campos escalares:

**Sintaxis**:
```graphql
campo: Tipo! @default(value: "valor_por_defecto")
```

**Ejemplos**:
```graphql
type User {
  active: Boolean! @default(value: "true")
  age: Int! @default(value: 18)
  role: UserRole! @default(value: "ADMIN")
}
```

**SQL generado**:
```sql
CREATE TABLE User (
  active BOOLEAN NOT NULL DEFAULT true,
  age INT NOT NULL DEFAULT 18,
  role ENUM('ADMIN', 'AUTHOR', 'USER') NOT NULL DEFAULT 'ADMIN'
);
```

#### Directiva @db - Renombrado de columnas

La directiva `@db` permite usar nombres diferentes entre GraphQL y la base de datos:

**Sintaxis**:
```graphql
campo: Tipo! @db(rename: "nombre_columna_sql")
```

**Ejemplos**:
```graphql
type User {
   fullName: String! @db(rename: "full_name")
   email: String! @db(rename: "email_address")
   phone: String @db(rename: "phone_number")
}
```

**SQL generado**:
```sql
CREATE TABLE User (
  full_name VARCHAR(255) NOT NULL,
  email_address VARCHAR(255) NOT NULL,
  phone_number VARCHAR(255)
);
```

#### Directiva @relation - Relaciones avanzadas

La directiva `@relation` gestiona relaciones complejas entre tipos con control granular:

**Sintaxis**:
```graphql
campo: [Tipo] @relation(name: "NombreRelacion", type: TIPO_RELACION, onDelete: ACCION)
```

**Argumentos**:
- `name`: Nombre único de la relación (requerido para toda relacion)
- `type`: Tipo de relación física
  - `INLINE`: Opcional para relaciones 1:1, N:1 y 1:N (clave foránea)
  - `TABLA`: Requerido para relaciones N:M (tabla intermedia)
- `onDelete`: Acción al eliminar registro padre
  - `CASCADE`: Eliminación en cascada (elimina registros hijos)
  - `SET_NULL`: Establece NULL en registros hijos (no elimina)

**Ejemplos de relaciones N:1 con INLINE**:
```graphql
type User {
   id: ID! @id
   email: String! @unique
   posts: [Post] @relation(name: "UserPosts")
}

type Post {
   id: ID! @id
   title: String!
   author: User! @relation(name: "UserPosts", onDelete: CASCADE)
}
```

**SQL generado para N:1**:
```sql
-- Tabla User
CREATE TABLE User (
   id VARCHAR(25) NOT NULL PRIMARY KEY,
   email VARCHAR(255) NOT NULL UNIQUE
   );

-- Tabla Post con clave foránea
CREATE TABLE Post (
   id VARCHAR(25) NOT NULL PRIMARY KEY,
   author_id VARCHAR(25) NOT NULL,
   FOREIGN KEY (author_id) REFERENCES User(id) ON DELETE CASCADE
);
```

**Ejemplos de relaciones 1:N con INLINE**:
```graphql
type Product {
   id: ID! @id
   name: String!
   productType: ProductType! @relation(name: "ProductTypeProducts", onDelete: CASCADE)
}

type ProductType {
   id: ID! @id
   name: String! @unique
   products: [Product] @relation(name: "ProductTypeProducts", onDelete: CASCADE)
}
```

**SQL generado para 1:N**:
```sql
-- Tabla ProductType
CREATE TABLE ProductType (
   id VARCHAR(25) NOT NULL PRIMARY KEY,
   name VARCHAR(255) NOT NULL
);

-- Tabla Product con clave foránea
CREATE TABLE Product (
   id VARCHAR(25) NOT NULL PRIMARY KEY,
   name VARCHAR(255) NOT NULL,
   product_type_id VARCHAR(25) NOT NULL,
   FOREIGN KEY (product_type_id) REFERENCES ProductType(id) ON DELETE CASCADE
);
```


**Ejemplos de relaciones N:M con TABLA**:
```graphql
type Post {
   id: ID! @id
   title: String!
   tags: [Tag] @relation(name: "PostTags", type: TABLA, onDelete: CASCADE)
}

type Tag {
   id: ID! @id
   name: String! @unique
   posts: [Post] @relation(name: "PostTags", type: TABLA, onDelete: CASCADE)
}
```

**SQL generado para N:M**:
```sql
-- Tabla Post
CREATE TABLE Post (
   id VARCHAR(25) NOT NULL PRIMARY KEY,
   title VARCHAR(255) NOT NULL
);

-- Tabla Tag
CREATE TABLE Tag (
   id VARCHAR(25) NOT NULL PRIMARY KEY,
   name VARCHAR(255) NOT NULL UNIQUE
);

-- Tabla intermedia PostTags
CREATE TABLE PostTags (
   post_id VARCHAR(25) NOT NULL,
   tag_id VARCHAR(25) NOT NULL,
   PRIMARY KEY (post_id, tag_id),
   FOREIGN KEY (post_id) REFERENCES Post(id) ON DELETE CASCADE,
   FOREIGN KEY (tag_id) REFERENCES Tag(id) ON DELETE CASCADE
);
```

---

## ⚡ Inicio Rápido

### 📦 Instalación

#### Desde PyPI (Recomendado)
```bash
pip install graphqlstore
```

#### Desde Código Fuente
```bash
git clone https://github.com/your-username/graphqlstore.git
cd graphqlstore
pipenv install --dev
```

### 🚀 Flujo Básico

#### 1. **Configurar Conexión**
```bash
# Configuración interactiva
graphqlstore conexion

# O con parámetros directos
graphqlstore conexion \
  --host localhost \
  --puerto 3306 \
  --usuario admin \
  --password secret \
  --base-datos mi_app
```

#### 2. **Verificar Conexión**
```bash
graphqlstore probar-conexion --verbose
```

#### 3. ***Diseñar Esquema GraphQL**
```graphq
type User {
   id: ID! @id
   username: String!
   email: String! @unique
}
```

#### 3. **Inicializar Base de Datos**
```bash
# Desde archivo específico
# NOTA: Es necesario indicar el esquema si hay varios archivos .graphql
# en el directorio actual
graphqlstore inicializar --esquema schema.graphql

# Detección automática
graphqlstore inicializar
```

#### 4. **Evolucionar Esquema** 
```bash
# Migración automática
# NOTA: Es necesario indicar el esquema si hay varios archivos .graphql
# en el directorio actual
graphqlstore migracion --esquema schema.graphql
```

**NOTA: SI DESEAS COMPROBAR O INTEGRAR LA HERRAMIENTA EN BACKEND CON ARQUITECTURA GRAPHQL, SERA NECESARIO EJECUTAR PRIMERO `graphqlstore servidor` PARA GENERAR LA ESTRUCTURA DEL SERVIDOR.**

```bash
graphqlstore servidor
```

PARA MAYOR INFORMACIÓN SOBRE EL COMANDO `servidor`, CONSULTE LA DOCUMENTACIÓN DEL COMANDO [servidor](source/cli/servidor/README.md).

---

## 📊 Ejemplos

### 🎮 Esquema GraphQL de Ejemplo

```graphql
scalar Json
scalar DateTime

type User {
  id: ID! @id
  username: String! @unique
  email: String! @unique
  role: UserRole!
  posts: [Post!]! @relation(name: "UserPosts")
  profile: Profile @relation(name: "UserProfile")
  createdAt: DateTime @createdAt
  updatedAt: DateTime @updatedAt
}

type Post {
  id: ID! @id
  title: String!
  content: String
  published: Boolean! @default(value: "false")
  tags: [String!]!
  author: User! @relation(name: "UserPosts", onDelete: CASCADE)
  createdAt: DateTime @createdAt
}

type Profile {
  id: ID! @id
  bio: String
  avatar: String
  user: User! @relation(name: "UserProfile", onDelete: CASCADE)
}

enum UserRole {
  ADMIN
  AUTHOR
  USER
}
```

### 🗄️ SQL Generado Automáticamente

```sql
-- Tabla User con constraints
CREATE TABLE User (
  `id` VARCHAR(25) NOT NULL PRIMARY KEY,
  `username` VARCHAR(255) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `role` ENUM('ADMIN','AUTHOR','USER') NOT NULL,
  `createdAt` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updatedAt` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `uk_username` (`username`),
  UNIQUE KEY `uk_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Relaciones con foreign keys
ALTER TABLE `Post`
ADD COLUMN `author_id` VARCHAR(25) NOT NULL,
ADD CONSTRAINT `fk_User_posts_Post` FOREIGN KEY (`author_id`) 
REFERENCES `User`(id) ON DELETE CASCADE;

ALTER TABLE `Profile`
ADD COLUMN `user_id` VARCHAR(25) UNIQUE,
ADD CONSTRAINT `fk_User_profile_Profile` FOREIGN KEY (`user_id`) 
REFERENCES `User`(id) ON DELETE CASCADE;
```

### 📈 Visualización Amigable

```bash
GraphQLStore CLI v3.0.0
Desplegando servicio

📋 Diferencias detectadas
├── ➕ Tablas agregadas: 1
├── 🔹 Campos agregados: 3
└── 🔗 Relaciones agregadas: 2

🔧 CREAR TABLA
├── Creando tabla Profile

🔧 AGREGAR RELACIÓN
├── Agregando relación UserProfile

✅ Migración generada exitosamente
📊 Total de sentencias SQL: 5
```

---

## 🏗️ Arquitectura

### 📁 Estructura del Proyecto

```
graphqlstore/
├── 📂 source/cli/
│   ├── 🔌 conexion/          # Gestión de configuración BD
│   ├── 🩺 probar_conexion/   # Diagnósticos y validación
│   ├── 🚀 inicializar/       # Inicialización de esquemas
│   ├── 📈 migracion/         # Sistema de migraciones
│   ├── 🔍 graphql/           # Motor GraphQL
│   │   ├── parser.py         # Parser de esquemas
│   │   ├── mysql_generador.py # Generador SQL
│   │   ├── mysql_migracion.py # Motor de migraciones
│   │   └── procesar_relaciones.py # Procesador de relaciones
│   ├── 🗄️ database/         # Adaptadores de BD
│   └── 🛠️ utilidades/       # Herramientas auxiliares
├── 📂 tests/                 # Suite de pruebas (97% cobertura)
└── 📂 .github/workflows/     # CI/CD automatizado
├── 📄 README.md              # Documentación principal
├── 📄 LICENSE                # Licencia del proyecto
├── 📄 setup.py               # Configuración del paquete
├── 📄 requirements.txt       # Dependencias del proyecto
├── 📄 requirements-dev.txt   # Dependencias de desarrollo
├── 📄 .pre-commit-config.yaml # Configuración de pre-commit
├── 📄 Pipfile                # Gestión de dependencias con Pipenv
├── 📄 pyproject.toml         # Configuración del proyecto
├── 📄 .pylintrc           # Configuración de pylint
```

### 🔧 Componentes Principales

#### 🔍 **Parser GraphQL** ([`source/cli/graphql/docs/parser.md`](source/cli/graphql/docs/parser.md))
- Análisis de esquemas GraphQL
- Extracción de tipos, campos y directivas
- Validación de sintaxis y semántica

#### 🔗 **Procesador de Relaciones** ([`source/cli/graphql/docs/procesar_relaciones.md`](source/cli/graphql/docs/procesar_relaciones.md))
- Detección automática de relaciones
- Clasificación 1:1, 1:N, N:M
- Generación de constraints

#### 🗄️ **Generador MySQL** ([`source/cli/graphql/docs/mysql_generador.md`](source/cli/graphql/docs/mysql_generador.md))
- Transformación GraphQL → SQL
- Generación de DDL completo

#### 📈 **Sistema de Migraciones** ([`source/cli/graphql/docs/mysql_migracion.md`](source/cli/graphql/docs/mysql_migracion.md))
- Detección inteligente de cambios
- Generación de SQL incremental
- Preservación de integridad referencial

---

## 🛠️ Entorno de Desarrollo

### 📋 Requisitos
- **Python**: 3.10+
- **MySQL**: 8.0+
- **Pipenv**: Para gestión de dependencias

### 🔧 Herramientas de Calidad

| Herramienta | Propósito | Estado |
|-------------|-----------|--------|
| **pytest** | Testing framework | ✅ 97% cobertura |
| **black** | Formateo de código | ✅ Configurado |
| **flake8** | Linting (ligero) | ✅ Configurado |
| **pylint** | Linting (exhausto) | ✅ Configurado |
| **mypy** | Type checking | ✅ Configurado |
| **pre-commit** | Git hooks | ✅ Configurado |


## 📊 Cobertura y Calidad

### 🎯 Métricas de Cobertura

| Módulo | Statements | Miss | Branch | BrPart | Cover |
|--------|------------|------|--------|--------|-------|
| **Parser GraphQL** | 67 | 1 | 18 | 1 | **98%** |
| **Procesador Relaciones** | 96 | 4 | 38 | 6 | **93%** |
| **Generador MySQL** | 237 | 5 | 94 | 11 | **95%** |
| **Sistema Migraciones** | 396 | 17 | 208 | 23 | **93%** |
| **Comandos CLI** | 271 | 11 | 52 | 3 | **100%** |
| **🎯 TOTAL PROYECTO** | **3151** | **62** | **482** | **53** | **🏆 97%** |

### ✅ Suite de Pruebas (TOTAL PROYECTO)

- **📈 128 pruebas** ejecutándose en **4.54 segundos**
- **🎯 97% cobertura global** con **0 fallos**
- **🔍 Casos edge** y **integración completa**
- **🚀 CI/CD automatizado** en GitHub Actions

---

## 🔄 CI/CD Pipeline

### 🛠️ Flujo Automatizado

### 🔍 **CI Pipeline** (`.github/workflows/ci.yml`)

**🔄 Flujo de Integración Continua:**

```
📋 Entrada (Push/PR) 
   ↓
🔧 Instalación de Dependencias
   ↓
🎯 Pre-commit Hooks
   ├── ⚫ Black (Formateo)
   ├── 🔍 Flake8 (Linting ligero)
   ├── 📋 Pylint (Análisis exhaustivo)
   └── 🔤 Mypy (Type checking)
   ↓
🧪 Testing Suite + Cobertura
   ↓
✅ Pipeline Completo
```

| Etapa | Proceso | Estado |
|-------|---------|--------|
| **🔧 Setup** | Instalación de dependencias | ✅ |
| **🎯 Quality** | Pre-commit hooks completos | ✅ |
| **⚫ Black** | Formateo automático de código | ✅ |
| **🔍 Flake8** | Linting ligero y rápido | ✅ |
| **📋 Pylint** | Análisis exhaustivo de código | ✅ |
| **🔤 Mypy** | Verificación estática de tipos | ✅ |
| **🧪 Testing** | Suite completa con cobertura | ✅ |

### 🚀 **CD Pipeline** (`.github/workflows/cd.yml`)

**📦 Flujo de Despliegue Continuo:**

```
🏷️ Release Tag
   ↓
🛠️ Configuración Build Tools
   ↓
📦 Empaquetado Multi-formato
   ├── 🎯 Wheel Distribution
   └── 📄 Source Distribution
   ↓
🚀 Publicación PyPI
   ↓
📋 GitHub Release + Artifacts
   ↓
✅ Deploy Completo
```

| Etapa | Proceso | Descripción |
|-------|---------|-------------|
| **🛠️ Setup** | Configuración de herramientas | Preparación del entorno de build |
| **📦 Build** | Empaquetado multi-formato | Wheel + Source distributions |
| **🎯 Wheel** | Distribución binaria | Instalación rápida optimizada |
| **📄 Source** | Distribución de código fuente | Máxima compatibilidad |
| **🚀 PyPI** | Publicación automática | Deploy en nuevas versiones |
| **📋 GitHub** | Release + artifacts | Documentación y archivos |

### ⚡ **Pipeline Triggers**
- **CI**: `push`, `pull_request` → `main`
- **CD**: `release` → `published` → PyPI + GitHub Release

### 📦 Releases

| Versión | Estado | Características |
|---------|--------|----------------|
| **v0.x.0** | ✅ | Despligue funcionamiento correcto |
| **v1.0.0** | ✅ | Core completo |
| **v2.0.0** | ✅ | Directivas avanzadas |
| **v3.0.0** | ✅ | Generador de servidor GraphQL en JavaScript |
| **v3.x.0** | 🎯 **Actual** | Bugs, mejoras y documentación |
---

## 📚 Documentación

### 📖 Guías Detalladas

- 🔌 **[Comando `conexion`](source/cli/conexion/README_latest.md)** - Configuración de base de datos
- 🩺 **[Comando `probar-conexion`](source/cli/probar_conexion/README.md)** - Diagnósticos y validación de base de datos
- 🚀 **[Comando `inicializar`](source/cli/inicializar/README.md)** - Inicialización de esquemas
- 📈 **[Comando `migracion`](source/cli/migracion/README.md)** - Sistema de migraciones
- 🔍 **[Comando `servidor`](source/cli/servidor/README.md)** - Generador de servidor GraphQL en JavaScript

### 🔧 Documentación Técnica

- 🔍 **[Parser GraphQL](source/cli/graphql/docs/parser.md)** - Motor de análisis
- 🔗 **[Procesador de Relaciones](source/cli/graphql/docs/procesar_relaciones.md)** - Gestión de relaciones
- 🗄️ **[Generador MySQL](source/cli/graphql/docs/mysql_generador.md)** - Transformación SQL
- 📈 **[Sistema de Migraciones](source/cli/graphql/docs/mysql_migracion.md)** - Evolución de esquemas

---

## 🎯 Casos de Uso

### 🚀 **Desarrollo de APIs**
```bash
# Inicialización completa de proyecto
graphqlstore conexion
graphqlstore inicializar
# ✅ Base de datos lista para desarrollo
```

### 🔄 **Evolución de Esquemas**
```bash
# Migración automática
graphqlstore migracion
# ✅ Esquema actualizado preservando datos (de tablas y relaciones existentes)
```

### 🏭 **Integración CI/CD**
```bash
# Modo silencioso para pipelines
graphqlstore migracion \
  --esquema schemas/production.graphql \
  --no-visualizar-salida \
  --no-visualizar-sql
```

---

## 🤝 Contribuir

### 🐛 Reportar Issues

### muy pronto

### 📝 Desarrollo Local

### muy pronto

---

## 🗺️ Roadmap

### 🚀 **v1.0.0** - Core
- [x] `conexion` - Configuración de conexión a MySQL
- [x] `probar-conexion` - Verificación de conectividad
- [x] `inicializar` - Inicialización de base de datos desde esquema GraphQL
- [x] `migracion` - Sistema de migraciones automático

### 🎯 **v2.0.0** - Directivas Avanzadas
- [x] `@unique` - Campos únicos
- [x] `@default` - Valores por defecto
- [x] `@db` - Renombrado de campos
- [x] `@protected` - Campos protegidos

### 🚀 **v3.0.0** - GraphQL Server
- [x]  `server` - Genera estructura de servidor GraphQL en JavaScript

### 🏭 **v3.x.0** - Bugs, mejoras y documentacion
- [x] Arreglar bugs y maltipados
- [x] Mejorar el flujo de funcionamiento del comando conexión
- [x] Mejorar las funcionalidades del core
- [x] Agregar documentación del comando `servidor`
- [x] Mejorar toda documentación
- [x] Mejorar la implementación del servidor GraphQL.js
- [ ] Implementar comando de inicio de sesion
- [ ] Implementar comando logout
- [ ] Implementar comando para gestionar la creacion de base de datos

### 🏭 **v4.0.0** - Multi-Database
- [ ] Refactorizar modulos `GeneradorEsquemaMySQL` y `GenerarMigracionMySQL` implementando patrones de diseño para escalar el codigo y mejorar la mantenibilidad, sobre todo para implementar la funcionalidad multi-base de datos.
- [ ] Implementar soporte PostgreSQL
- [ ] Implementar soporte a Redis
---


## 📜 Licencia

Este proyecto utiliza una **Licencia Privada** que prohíbe:
- ❌ Redistribución en cualquier forma
- ❌ Modificación del software
- ❌ Creación de obras derivadas
- ❌ Uso comercial no autorizado
- ❌ Compartición pública

Ver LICENSE para detalles completos.

---

<div align="center">

### 🚀 **¡Transforma tus esquemas GraphQL en bases de datos MySQL con un solo comando!**

[![Get Started](https://img.shields.io/badge/Get%20Started-brightgreen?style=for-the-badge&logo=rocket)](https://pypi.org/project/graphqlstore/)
[![Documentation](https://img.shields.io/badge/Documentation-blue?style=for-the-badge&logo=book)](source/cli/)
[![GitHub](https://img.shields.io/badge/GitHub-black?style=for-the-badge&logo=github)](https://github.com/adg1023/graphqlstore)

---

**📧 ¿Preguntas?** • **🐛 ¿Problemas?** • **💡 ¿Ideas?**

MUY PRONTO

</div>
