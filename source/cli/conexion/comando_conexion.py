"""Modulo del comando conexion"""

from ..base import Comando
from .main import conexion


class ComandoConexion(Comando):
    """
    Clase que implementa el comando de conexion a la base de datos
    """

    def crear_comando(self, subparsers):
        conexion_parser = subparsers.add_parser(
            "conexion", help=("Configurar la conexion a la base de datos")
        )
        conexion_parser.add_argument(
            "--archivo",
            "-a",
            required=False,
            help="Ruta al archivo de configuracion (formato JSON)",
        )
        conexion_parser.add_argument(
            "--host", required=False, help="Host de la base de datos"
        )
        conexion_parser.add_argument(
            "--puerto", required=False, help="Puerto de la base de datos"
        )
        conexion_parser.add_argument(
            "--usuario", required=False, help="Usuario de la base de datos"
        )
        conexion_parser.add_argument(
            "--password", required=False, help="Contraseña de la base de datos"
        )
        conexion_parser.add_argument(
            "--db-nombre", required=False, help="Nombre de la base de datos"
        )

    def contenido_comando(self, args):
        """
        Metodo que se ejecuta al ejecutar el comando conexion
        Args:
            args (Namespace): Argumentos parseados de la linea de comandos
        """
        if args.comando == "conexion":
            conexion(args)
