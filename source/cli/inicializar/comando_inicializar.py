"""Modulo del comando inicialiazar"""

from ..base import Comando
from .main import inicializar


class ComandoInicializar(Comando):
    """
    Clase que implementa el comando de inicializar de la base de datos
    """

    def crear_comando(self, subparsers):
        htext = "Inicializar una nueva base de datos desde un esquema GraphQL"
        inicializar_parser = subparsers.add_parser(
            "inicializar",
            help=htext,
        )
        inicializar_parser.add_argument(
            "--esquema",
            "-e",
            required=False,
            help="Ruta al archivo de esquema GraphQL",
        )
        inicializar_parser.add_argument(
            "--salida",
            "-s",
            default="generated",
            required=False,
            help="Directorio de salida para los archivos generados",
        )
        inicializar_parser.add_argument(
            "--no-visualizar-salida",
            "-nv",
            default=False,
            action="store_true",
            help="No visualizar salida",
        )
        inicializar_parser.add_argument(
            "--no-visualizar-sql",
            "-nvs",
            default=False,
            action="store_true",
            help="No visualizar salida SQL",
        )

    def contenido_comando(self, args):
        """
        Metodo que se ejecuta al ejecutar el comando inicializar
        Args:
            args (Namespace): Argumentos parseados de la linea de comandos
        """
        if args.comando == "inicializar":
            inicializar(args)
