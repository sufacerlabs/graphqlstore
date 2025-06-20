"""Modulo del comando migracion"""

from ..base import Comando
from .main import migracion


class ComandoMigracion(Comando):
    """
    Clase que implementa el comando de migracion de \
        la base de datos
    """

    def crear_comando(self, subparsers):
        htext = "Migrar una base de datos a partir de un esquema GraphQL"
        migracion_parser = subparsers.add_parser(
            "migracion",
            help=htext,
        )
        migracion_parser.add_argument(
            "--esquema",
            "-e",
            required=False,
            help="Ruta al archivo de esquema GraphQL",
        )
        migracion_parser.add_argument(
            "--antiguo-esquema",
            required=False,
            help="Ruta del archivo de esquema GraphQL antiguo",
        )
        migracion_parser.add_argument(
            "--salida",
            "-s",
            default="migraciones",
            required=False,
            help="Directorio de salida para las migraciones generadas",
        )
        migracion_parser.add_argument(
            "--no-visualizar-salida",
            "-nv",
            default=False,
            action="store_true",
            help="No visualizar salida",
        )
        migracion_parser.add_argument(
            "--no-visualizar-sql",
            "-nvs",
            default=False,
            action="store_true",
            help="No visualizar salida SQL",
        )

    def contenido_comando(self, args):
        """
        Metodo que se ejecuta al ejecutar el comando migracion
        Args:
            args (Namespace): Argumentos parseados de la linea de comandos
        """
        if args.comando == "migracion":
            migracion(args)
