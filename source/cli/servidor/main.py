"""Modulo para gestionar el servidor"""

import json
from pathlib import Path
from rich.console import Console

from ..loaders.conf_json_loader import ConfiguracionJsonLoader
from ..utilidades.gestor_archivo import GestorArchivo

console = Console()


def servidor():
    """Función para crear plantilla de servidor GraphQL en Node.js"""

    console.print("\n🚀 [bold cyan]GraphQLStore Server[/bold cyan]\n")

    directorio_servidor = Path.cwd() / "graphql-server"

    try:
        # crear directorio del servidor
        GestorArchivo.asegurar_dir_existe(directorio_servidor)
        console.print(
            f"📁 Creando servidor en: {directorio_servidor}",
            style="yellow",
        )

        # Cargar configuración de BD (opcional, para futuras funcionalidades)
        ruta_archivo = Path.cwd() / ".graphqlstore_config.json"

        if ruta_archivo.exists():
            loader = ConfiguracionJsonLoader(ruta_archivo)
            config = loader.cargar_configuracion()
        else:
            config = {
                "DB_HOST": "localhost",
                "DB_PUERTO": 3306,
                "DB_USUARIO": "root",
                "DB_PASSWORD": "root",
                "DB_NOMBRE": "graphqlstore",
            }

        # Generar archivos del servidor
        _generar_package_json(directorio_servidor)
        _generar_index_js(directorio_servidor, config)
        _generar_graphql(directorio_servidor)
        _generar_resolvers(directorio_servidor)

        msg = "Ejecuta tu servidor GraphQL de pruebas"
        console.print(f"\n✅ [bold green]{msg}[/bold green]")
    except (OSError, PermissionError, FileNotFoundError) as e:
        console.print(f"\n❌ [bold red]Error:[/bold red] {str(e)}")


def _generar_package_json(directorio: Path):
    """Generar archivo package.json"""

    package_json = {
        "name": "graphql-server",
        "version": "1.0.0",
        "description": "GraphQLStore CLI + Server",
        "main": "index.js",
        "type": "module",
        "scripts": {
            "start": "node index.js",
            "dev": "nodemon -e js,json,graphql --w . --ignore ./node_modules",
            "test": 'echo "Error: no test specified" && exit 1',
        },
        "keywords": ["graphql", "javascript", "node.js", "graphqlstore"],
        "author": "adg1023",
        "license": "MIT",
        "dependencies": {
            "@graphql-tools/graphql-file-loader": "^8.0.20",
            "@graphql-tools/load": "^8.1.0",
            "apollo-server": "^3.13.0",
            "dataloader": "^2.2.3",
            "graphql": "^16.11.0",
            "graphql-tools": "^9.0.18",
            "mysql2": "^3.14.1",
            "short-uuid": "^5.2.0",
        },
        "devDependencies": {"nodemon": "^3.1.10"},
        "engines": {"node": ">22.16.0"},
    }

    archivo_package = directorio / "package.json"
    contenido_json = json.dumps(package_json, indent=2, ensure_ascii=False)
    GestorArchivo.escribir_archivo(contenido_json, archivo_package)

    console.print("  ✅ package.json generado", style="green")


def _generar_index_js(directorio: Path, conf):
    """Generar archivo index.js con servidor Apollo y MySQL"""

    contenido_js = """import mysql from 'mysql2/promise';
import { loadSchema } from '@graphql-tools/load';
import path from 'path';
import { GraphQLFileLoader } from '@graphql-tools/graphql-file-loader';
import { addResolversToSchema, mergeSchemas } from '@graphql-tools/schema';
import { ApolloServer } from 'apollo-server';
import short from 'short-uuid';
import resolvers from './resolvers.js';

async function main() {

  const externalSchema = await loadSchema(
    path.join(path.resolve('../generated'), './schema.graphql'),
    {
      loaders: [
        new GraphQLFileLoader()
      ]
    }
  )

  const internalSchemas = await loadSchema(
    './*.graphql',
    {
      loaders: [
        new GraphQLFileLoader()
      ]
    }
  )

// Configuración de conexión a MySQL
"""
    contenido_js += f"""
  const pool = mysql.createPool({{
      host: '{conf["DB_HOST"]}',
      port: {conf["DB_PUERTO"]},
      user: '{conf["DB_USUARIO"]}',
      password: '{conf["DB_PASSWORD"]}',
      database: {conf["DB_NOMBRE"]},
  }});

"""
    contenido_js += """
  try {
    const connection = await pool.getConnection();
    await connection.query('SELECT 1');
    connection.release();
    console.log('Conexión a la base de datos establecida correctamente.');
  } catch (error) {
    console.error('Error al conectar a la base de datos:', error);
  }



  const schema = mergeSchemas({
    schemas: [externalSchema, internalSchemas]
  })

  const schemaWithResolvers = addResolversToSchema({
    schema: schema,
    resolvers,
  })

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

main().catch((error) => {
  if (error.code === 'ER_ACCESS_DENIED_ERROR') {
    console.error(
      'Error de acceso a la base de datos. Verifica las credenciales.',
    );
  }
  else if (error.code === 'ER_BAD_DB_ERROR') {
    console.error(
      'Base de datos no encontrada. Verifica el nombre de la base de datos.',
    );
  }
  else if (error.code === 'ERR_SOCKET_BAD_PORT') {
    console.error(
      'Puerto no válido. Verifica el número de puerto.',
    );
  }
  else if (error.code === 'EHOSTUNREACH') {
    console.error(
      'No se puede alcanzar el host. Verifica el host.',
    );
  }
  else {
    console.error(
      'Error al iniciar el servidor:',
      error,
    );
  }

  process.exit(1);
});
"""
    archivo_index = directorio / "index.js"
    GestorArchivo.escribir_archivo(contenido_js, archivo_index)

    console.print("  ✅ index.js generado", style="green")


def _generar_graphql(directorio: Path):
    """Generar archivos GraphQL de ejemplo"""

    contenido_graphql = """# import User from './../generated/schema.graphql'
# import Post from './../generated/schema.graphql'
# import PostState from './../generated/schema.graphql'

\"""
Un tipo que muestra las consultas sobre el esquema
\"""
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

\"""
Un tipo que muestra las mutaciones sobre el esquema
\"""
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
    """
    archivo_graphql = directorio / "queries_mutations.graphql"
    GestorArchivo.escribir_archivo(contenido_graphql, archivo_graphql)

    console.print(
        "  ✅ queries_mutations.graphql generado",
        style="green",
    )


def _generar_resolvers(directorio: Path):
    """Generar archivo resolvers.js con ejemplos de resolvers"""

    contenido_js = """const resolvers = {
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
};

export default resolvers;
    """
    archivo_resolvers = directorio / "resolvers.js"
    GestorArchivo.escribir_archivo(contenido_js, archivo_resolvers)

    console.print("  ✅ resolvers.js generado", style="green")
