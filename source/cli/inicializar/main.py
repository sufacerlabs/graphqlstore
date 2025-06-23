"""Modulo para gestionar la inicializacion en la CLI."""

from pathlib import Path
from rich.console import Console

from ..database.adaptadores import AdaptadorMySQL

from ..loaders.conf_json_loader import ConfiguracionJsonLoader
from ..utilidades import GestorArchivo
from ..graphql import (
    ParserGraphQLEsquema,
    ProcesarRelaciones,
    GeneradorEsquemaMySQL,
)
from ..graphql.exceptions import (
    GraphQLStoreError,
    SchemaError,
    RelationshipError,
)


# pylint: disable=too-many-statements,too-many-locals
def inicializar(args):
    """Funcion para inicializar la base de datos \
        desde un esquema GraphQL.

    Args:
        args (Namespace): Argumentos parseados de \
            la linea de comandos.
    """
    consola = Console()

    # verificar si el directorio de salida existe
    # si no existe, crearlo
    salida_dir = Path.cwd() / args.salida
    GestorArchivo.asegurar_dir_existe(salida_dir)

    if not args.esquema:
        # si no se proporciona un esquema, buscar uno por defecto
        # en el directorio actual
        esquema_archivo = next(Path.cwd().glob("*.graphql"), None)
        if esquema_archivo is None:
            consola.print(
                "No se ha proporcionado un esquema y tampoco se ha "
                "encontrado un archivo .graphql en el directorio actual.",
                style="bold red",
            )
            return
        # leer el esquema del archivo
        esquema_contenido = GestorArchivo.leer_archivo(esquema_archivo)
    else:
        # si se proporciona un esquema, comprobar que exista
        if not Path(args.esquema).exists():
            consola.print(
                f"El archivo de esquema '{args.esquema}' no existe.",
                style="bold red",
            )
            return

        esquema_contenido = GestorArchivo.leer_archivo(Path(args.esquema))

    consola.print("GraphQLStore CLI v3.0.0", style="bold green")
    consola.print("Desplegando servicio", style="bold green")
    consola.print("NUEVO ESQUEMA:\n", style="bold magenta")

    try:
        # parsear esquema GraphQL
        parser = ParserGraphQLEsquema()
        informacion_parseada = parser.parse_esquema(esquema_contenido)
        consola.print("\nEsquema parseado correctamente.", style="bold green")

        procesar_relaciones = ProcesarRelaciones(
            tablas=informacion_parseada.tablas,
            scalar_types=ParserGraphQLEsquema.get_type_mapping(),
            enum_types=informacion_parseada.enums,
        )
        relaciones = procesar_relaciones.procesar_relaciones()
        generador_esquema_mysql = GeneradorEsquemaMySQL()
        sql = generador_esquema_mysql.generar_esquema(
            tablas=informacion_parseada.tablas,
            enums=informacion_parseada.enums,
            relaciones=relaciones,
            visualizar_salida=not args.no_visualizar_salida,
            visualizar_sql=not args.no_visualizar_sql,
        )

        ruta_archivo = Path.cwd() / ".graphqlstore_config.json"
        loader = ConfiguracionJsonLoader(ruta_archivo)
        config = loader.cargar_configuracion()

        if not config:
            return

        adaptador = AdaptadorMySQL()
        adaptador.conectar(config)
        adaptador.ejecutar_consulta("SHOW TABLES;")

        tablas = adaptador.cursor.fetchall()

        if len(tablas) != 0:
            consola.print(
                "\n :cross_mark: ejecuta el comando "
                "[bold green]migracion[/bold green] si deseas "
                "modificar el esquema existente.\n",
                style="bold yellow",
            )
            return

        adaptador.ejecutar_consulta(sql)
        adaptador.cerrar_conexion()

    except (GraphQLStoreError, SchemaError, RelationshipError) as e:
        consola.print(":cross_mark: ERROR AL CREAR EL ESQUEMA\n")
        consola.print(f"Error: {e}", style="bold red")

    try:
        # crear backup del esquema original
        archivo_backup = Path(salida_dir) / ".backup.graphql"
        GestorArchivo.escribir_archivo(esquema_contenido, archivo_backup)

        # escribir esquema MySQL en archivo
        archivo_mysql = Path(salida_dir) / "schema.sql"
        GestorArchivo.escribir_archivo(sql, archivo_mysql)

        # transformar esquema graphql
        graphql_esquema = generador_esquema_mysql.transformar_esquema_graphql(
            esquema_contenido
        )
        archivo_salida = Path(salida_dir) / "cliente.graphql"
        GestorArchivo.escribir_archivo(graphql_esquema, archivo_salida)
    except ValueError as e:
        consola.print(
            ":cross_mark: ERROR AL TRANSFORMAR EL ESQUEMA A CLIENTE GRAPHQL\n"
        )
        consola.print(f"Error: {e}", style="bold red")

    consola.print(
        "\n:rocket: Generando archivos de salida...\n",
        style="bold yellow",
    )

    consola.print(
        ":white_check_mark: GraphQL & DB sincronizado exitosamente!\n",
        style="bold green",
    )
    consola.print(
        ":white_check_mark: Esquema cliente GraphQL generado exitosamente!\n",
        style="bold green",
    )
    consola.print(
        ":white_check_mark: Esquema MySQL generado exitosamente!\n",
        style="bold green",
    )
    consola.print(
        f":file_folder: Archivos generados en: {salida_dir}\n",
        style="bold green",
    )


# pylint: enable=too-many-statements,too-many-locals
