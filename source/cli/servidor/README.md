# Comando `servidor` - Generador de Servidor GraphQL

## Índice
- [Descripción](#descripción)
- [Requisitos](#requisitos)
- [Instalación de Dependencias](#instalación-de-dependencias)
- [Uso Básico](#uso-básico)
- [Funcionalidades](#funcionalidades)
- [Estructura del Servidor](#estructura-del-servidor)
- [API GraphQL Generada](#api-graphql-generada)
- [Solución de Problemas](#solución-de-problemas)

---

## Descripción

El comando `servidor` de GraphQLStore CLI genera una estructura completa de servidor GraphQL en JavaScript que posteriormente debe ser ejecutado usando Node.js/NPM. Este comando prepara todos los archivos necesarios para un servidor GraphQL funcional basado en un esquema GraphQL y configuración de base de datos.

### ✨ Características principales

- 📁 **Generación de una estructura de servidor GraphQL** con Apollo Server Express
- 🔄 **Resolvers de ejemplo** proporcionados como plantilla basada en el esquema
- 📝 **Package.json configurado** con todas las dependencias necesarias
- 🗄️ **Configuración MySQL preparada** que usa la configuracion del comando conexion
- 📝 **Queries y mutations de ejemplo** generadas desde el esquema GraphQL
- 🚀 **Scripts NPM configurados** para ejecución fácil con `npm run dev`

### 🎯 Casos de uso

- **Prototipado rápido**: Generar base de servidor GraphQL para desarrollo
- **Testing de esquemas**: Preparar servidor para probar queries y mutaciones
- **Demos y presentaciones**: Crear servidor funcional para demostraciones
- **Aprendizaje**: Entender estructura de servidores GraphQL en JavaScript

---
💡 El comando `servidor` es una herramienta educativa y de prototipado que proporciona ejemplos funcionales de resolvers y queries/mutations basados en un esquema GraphQL. ESTE COMANDO HA SIDO IMPLEMENTADO PARA PODER COMPRENDER LA INTEGRACION DE LA HERRAMIENTA **GRAPHQLSTORE CLI** EN UN BACKEND BASADO EN GRAPHQL.
---

## Requisitos

### Requisitos obligatorios

#### Node.js y NPM
- **Node.js**: Versión 22.16.0 (requerida)
- **NPM**: Incluido con Node.js 22.16.0
- **Sistema operativo**: Linux (recomendado), macOS o Windows 10

### Verificación de requisitos

```bash
# Verificar versión de Node.js (debe ser v22.16.0)
node --version

# Verificar versión de NPM
npm --version
```

---

## Instalación de Dependencias

### Instalación de Node.js v22.16.0

#### Ubuntu/Debian
```bash
# Método 1: Usando NodeSource repository (recomendado)
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verificar instalación
node --version  # Debe mostrar v22.16.0
npm --version
```

#### Windows o macOS
```bash
# Descargar desde el sitio oficial
# https://nodejs.org/en/download/
# Seleccionar versión 22.16.0 LTS

# Verificar en PowerShell/CMD/Terminal
node --version
npm --version
```

## Uso Básico

### Generación del servidor

**El comando `servidor` genera la estructura del servidor GraphQL, no lo ejecuta ni instala dependencias:**

```bash
# Generar estructura del servidor GraphQL
graphqlstore servidor

# El comando crea:
# - Directorio del servidor con todos los archivos necesarios
#   - package.json con dependencias configuradas
#   - Queries y mutations de ejemplo usando el esquema cliente seguro
#   - Resolvers de ejemplo basados en el esquema cliente seguro
#   - Scripts NPM para ejecución posterior
#   - Configuración de Apollo Server Express
```

### Flujo completo después de generar

Una vez generado el servidor, sigue los siguientes pasos para ejecutarlo:

```bash
# 1. Navegar al directorio del servidor generado
cd graphql-server/

# 2. Instalar todas las dependencias NPM
npm install

# 3. Configurar conexión a base de datos
graphqlsstore conexion

# 4. Verificar conectividad
graphqlstore probar-conexion


# 4. Inicializar esquema
graphqlstore incializar

# 5. Ejecutar servidor
npm run dev

# 6. Abrir GraphQL Playground
#    http://localhost:4000/

# 7. Si se desea actualizar el esquema, ejecutar:
graphqlstore migracion

# 8. Modificar los resolvers, queries y mutations SI ES NECESARIO.

# 9. Repetir pasos 8 y 9
```

---

## Funcionalidades

### Generación de resolvers de ejemplo

El servidor proporciona resolvers de ejemplo basados en el esquema GraphQL como plantilla para desarrollo:

#### Queries de ejemplo (Consultas)
```javascript
  Query: {
    users: async (_, __, { db }) => {
      const [rows] = await db.execute('SELECT * FROM User');
      return rows;
    },
    user: async (_, { id }, { loaders }) => {
      const [rows] = await db.execute(
        'SELECT * FROM User WHERE id = ?', [id]
      );
      return rows[0];
    },
    posts: async (_, __, { db }) => {
      const [rows] = await db.execute('SELECT * FROM Post');
      return rows;
    },
    post: async (_, { id }, { loaders }) => {
      const [rows] = await db.execute(
        'SELECT * FROM Post WHERE id = ?', [id]
      );
      return rows[0];
    },
  },
```

#### Mutations de ejemplo (Mutaciones)
```javascript
// Ejemplos generados para operaciones CRUD
  Mutation: {
    createUser: async (_, args, { db, uuid }) => {
      const { name, email, password } = args;
      const id = uuid.generate();
      try {
        await db.execute(`
          INSERT INTO User
          (id, name, email, password)
          VALUES (?, ?, ?, ?)`,
          [id, name, email, password],
        );
        return { id, ...args };
      } catch (error) {
        throw new Error('Error al crear el usuario: ' + error.message);
      }
    },
    deleteUser: async (_, { id }, { db }) => {
      try {
        await db.execute('DELETE FROM User WHERE id = ?', [id]);
        return id;
      } catch (error) {
        throw new Error('Error al eliminar el usuario: ' + error.message);
      }
    },
    createPost: async (_, args, { db,  uuid }) => {
      const { title, content, user_id } = args;
      const id = uuid.generate();
      try {
        await db.execute(
          'INSERT INTO Post (id, title, content, user_id) VALUES (?, ?, ?, ?)',
          [id, title, content, user_id],
        );
        return { id, ...args };
      } catch (error) {
        throw new Error('Error al crear el post: ' + error.message);
      }
    },
    deletePost: async (_, { id }, { db }) => {
      try {
        await db.execute('DELETE FROM Post WHERE id = ?', [id]);
        return id;
      } catch (error) {
        throw new Error('Error al eliminar el post: ' + error.message);
      }
    },
  },
```

#### Resolvers de relaciones de ejemplo
```javascript
// Ejemplos para resolver relaciones entre tipos
  User: {
    posts: async (parent, _, { db }) => {
      const [rows] = await db.execute(
        'SELECT * FROM Post WHERE user_id = ?',
        [parent.id],
      );
      return rows;
    },
  },
  Post: {
    owner: async (parent, _, { db }) => {
      const [rows] = await db.execute(
        'SELECT * FROM User WHERE id = ?',
        [parent.user_id],
      );
      return rows[0];
    },
  },
```

### ⚠️ Importante: Resolvers de ejemplo vs. producción

Los resolvers proporcionados son **ejemplos educativos** que:
- ✅ Muestran la estructura correcta del código
- ✅ Demuestran cómo mapear el esquema GraphQL
- ✅ Sirven como plantilla para implementación real

### GraphQL Playground integrado

Accesible en `http://localhost:4000/graphql`:

- **Explorador de esquema**: Navega tipos, campos y relaciones
- **Autocompletado**: Para queries y mutaciones
- **Documentación**: Descripción de tipos y campos
- **Historial de queries**: Guarda queries ejecutadas
- **Variables**: Soporte para variables en queries

### Conexión MySQL de ejemplo

```javascript
import mysql from 'mysql2/promise';
import { loadSchema } from '@graphql-tools/load';
import path from 'path';
import { GraphQLFileLoader } from '@graphql-tools/graphql-file-loader';
import { addResolversToSchema, mergeSchemas } from '@graphql-tools/schema';
import { ApolloServer } from 'apollo-server';
import short from 'short-uuid';
import resolvers from './resolvers.js';
// Se importa la configuración de la base de datos
import gqlstore_conf from './.graphqlstore_config.json' with { type: 'json' };

async function main() {

  ...

  // Configuración de conexión a MySQL
  const pool = mysql.createPool({
    host: gqlstore_conf.DB_HOST || 'localhost',
    port: gqlstore_conf.DB_PORT || 3306,
    user: gqlstore_conf.DB_USUARIO || 'root',
    password: gqlstore_conf.DB_PASSWORD || 'root',
    database: gqlstore_conf.DB_NOMBRE || 'graphqlstore',
  });
```
---

## Estructura del Servidor

### Archivos generados automáticamente

```
.graphqlstore/
├── index.js                    # Archivo principal del servidor
├── package.json                # Dependencias y scripts NPM
├── queries_mutations.graphql   # Queries y mutations de ejemplo basados en el esquema
└── resolvers.js                # Resolvers de ejemplo basados en el esquema
```

### Código del servidor generado

**index.js** (simplificado):
```javascript
  // fusionar esquemas
  const schema = mergeSchemas({
    schemas: [externalSchema, internalSchemas]
  }) 
  // agregar resolvers al esquema cliente seguro+queries+mutations
  const schemaWithResolvers = addResolversToSchema({
    schema: schema,
    resolvers,
  })

  // crear instancia de un servidor graphql bajo express
  const server = new ApolloServer({
    schema: schemaWithResolvers,
    introspection: true,
    playground: {
      settings: {
        'editor.theme': 'dark',
      },
    },
    context: ({ req, res }) => {
      return {
        req,
        res,
        db: pool,
        uuid: short(),
      };
    },
  });

  server.listen(4000).then(() => {
    console.log('🚀 Servidor listo en el puerto: http://localhost:4000/')
  })
}

```

---

## API GraphQL Generada

### Tipos de Query de ejemplo

Para cada tipo definido en el esquema, se proporcionan queries de ejemplo:

```graphql
# import User from './generated/schema.graphql'
# import Post from './generated/schema.graphql'
# import PostState from './generated/schema.graphql'

"""
Un tipo que muestra las consultas sobre el esquema
"""
type Query {
    "Obtiene un usuario por su ID"
    user(id: ID!): User
    "Obtiene todos los usuarios"
    users: [User]
    "Obtiene un post por su ID"
    post(id: ID!): Post
    "Obtiene todos los posts"
    posts: [Post]
}

```

### Tipos de Mutation de ejemplo

```graphql
"""
Un tipo que muestra las mutaciones sobre el esquema
"""
type Mutation {
    "Crea un nuevo usuario"
    createUser(
        name: String!,
        email: String!,
        password: String!
    ): User!
    "Borrar un usuario por su ID"
    deleteUser(id: ID!): ID!
    "Crea un nuevo post"
    createPost(
        title: String!,
        content: String!,
        user_id: ID!,
        state: PostState!
    ): Post!
    "Actualiza un post existente"
    updatePost(
        id: ID!,
        title: String,
        content: String,
        state: PostState
    ): Post!
    "Elimina un post por su ID"
    deletePost(id: ID!): ID!
}
```


### ⚠️ Nota importante sobre los datos

Los resolvers de ejemplo proporcionan:
- 📝 Una implementacion muy simple para enfocarse solo en realizar consultas y crear registros mediante la interfaz

---

## Solución de Problemas

#### ERROR RELACIONADO AL PUERTO
```bash
Error: listen EADDRINUSE: address already in use :::4000 o similar
```
**Solución**:
```bash
# Opción 2: Matar proceso en puerto 4000
lsof -ti:4000 | xargs kill -9

# Opción 3: Encontrar y terminar proceso
netstat -tlnp | grep :4000
kill -9 <PID>
```

#### ERROR RELACIONADO A LA CONEXIÓN A LA BASE DE DATOS
```bash
Error: ER_ACCESS_DENIED_ERROR o similar
```
**Solución**:
```bash
# Verificar configuración de BD
graphqlstore probar-conexion --verbose

# Reconfigurar si es necesario
graphqlstore conexion
```

#### ERROR RELACIONADO A LAS DEPENDENCIAS
```bash
Error: Failed to install Node.js dependencies o similar
```
**Solución**:
```bash
# Limpiar caché NPM
npm cache clean --force

# Eliminar node_modules y reinstalar
rm -rf .graphqlstore/server_temp/node_modules
rm .graphqlstore/server_temp/package-lock.json
```
---
