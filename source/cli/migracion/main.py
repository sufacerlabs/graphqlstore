"""Modulo para gestionar la migracion de esquemas"""

from pathlib import Path
from rich.console import Console

from ..database.adaptadores.mysql import AdaptadorMySQL

from ..graphql.exceptions import (
    GraphQLStoreError,
    MigrationError,
    RelationshipError,
    SchemaComparisonError,
    SchemaError,
    MigrationGenerationError,
)

from ..graphql.mysql_generador import GeneradorEsquemaMySQL

from ..loaders.conf_json_loader import ConfiguracionJsonLoader

from ..utilidades.gestor_archivo import GestorArchivo
from ..graphql.mysql_migracion import GeneradorMigracionMySQL


def migracion(args):
    """Funcion para generar una migracion de un \
        esquema GraphQL a MySQL"""
    # pylint: disable=too-many-locals, too-many-return-statements
    consola = Console()

    ruta_archivo = Path.cwd() / ".graphqlstore_config.json"
    loader = ConfiguracionJsonLoader(ruta_archivo)
    config = loader.cargar_configuracion()

    if not config:
        return

    esquema_backup = Path.cwd() / "generated" / ".backup.graphql"
    if not esquema_backup.exists():
        consola.print(
            "❌ Error al buscar el esquema inicializado asegúrate de haber "
            "inicializado el esquema o que te encuentras en el directorio"
            "donde configuraste tu proyecto.",
            style="bold red",
        )
        return

    # leer el esquema del archivo de backup
    esquema_antiguo = GestorArchivo.leer_archivo(esquema_backup)

    if not args.esquema:
        # si no se proporciona un esquema, buscar unopor defecto
        # en el directorio actual
        esquema_archivo = next(Path.cwd().glob("*.graphql"), None)

        if esquema_archivo is None:
            consola.print(
                "❌ No se ha proporcionado un esquema y tampoco se ha "
                "encontrado un archivo .graphql en el directorio actual.",
                style="bold red",
            )
            return

        # leer el esquema del archivo
        esquema_nuevo = GestorArchivo.leer_archivo(esquema_archivo)
    else:
        # si se proporciona un esquema, comprobar que exista
        if not Path(args.esquema).exists():
            consola.print(
                f"❌ El archivo de esquema '{args.esquema}' no existe.",
                style="bold red",
            )
            return

        esquema_nuevo = GestorArchivo.leer_archivo(Path(args.esquema))

    consola.print("GraphQLStore CLI v3.0.0", style="bold green")
    consola.print("Desplegando servicio", style="bold green")

    consola.print("\nMIGRANDO ESQUEMA...\n", style="bold magenta")

    try:
        # migrar esquema GraphQL
        generador_migracion_mysql = GeneradorMigracionMySQL()

        migra = generador_migracion_mysql.generar_migracion(
            esquema_anterior=esquema_antiguo,
            esquema_nuevo=esquema_nuevo,
            visualizar_salida=not args.no_visualizar_salida,
            visualizar_sql=not args.no_visualizar_sql,
        )

        if len(migra.sql_generado) == 0:
            return

        adaptador = AdaptadorMySQL()
        adaptador.conectar(config)
        adaptador.ejecutar_consulta("SHOW TABLES;")

        tablas = adaptador.cursor.fetchall()

        if len(tablas) == 0:
            consola.print(
                "\n :cross_mark: ejecuta el comando "
                "[bold green]inicializar[/bold green] "
                "antes de migrar un esquema que no existe.",
                style="bold red",
            )
            return

        adaptador.ejecutar_consulta(migra.sql_generado)
        adaptador.cerrar_conexion()

        # verificar si el directorio de salida existe
        # si no existe, crearlo
        salida_dir = Path.cwd() / args.salida
        GestorArchivo.asegurar_dir_existe(salida_dir)

        archivo_salida = salida_dir / f"{migra.id_migracion}.sql"
        # guardar la migracion en un archivo
        GestorArchivo.escribir_archivo(
            contenido=migra.sql_generado, ruta_salida=archivo_salida
        )

        # si la migracion es exitosa, actualizar el archivo backup
        GestorArchivo.escribir_archivo(
            contenido=esquema_nuevo, ruta_salida=esquema_backup
        )

        # actualizar el esquema cliente graphql
        generador = GeneradorEsquemaMySQL()
        esquema_cliente = generador.transformar_esquema_graphql(
            esquema_nuevo,
        )
        GestorArchivo.escribir_archivo(
            contenido=esquema_cliente,
            ruta_salida=Path.cwd() / "generated" / "schema.graphql",
        )

        consola.print(
            "\n:white_check_mark: GraphQL & DB Sincronizado perfectamente!",
            style="bold green",
        )
        consola.print(
            f":white_check_mark: Migracion SQL guardado: {archivo_salida}\n",
            style="bold green",
        )

        # pylint: enable=too-many-locals, too-many-return-statements
    except (
        GraphQLStoreError,
        SchemaError,
        RelationshipError,
        MigrationError,
        SchemaComparisonError,
        MigrationGenerationError,
        IOError,
        OSError,
    ) as e:
        consola.print(
            "❌ Error inesperado durante la migracion\n"
            f"💡 {str(e)}\n"
            "\n🔧 [bold white]Revisa el error devuelto[/bold white]\n",
            style="bold red",
        )
        return
