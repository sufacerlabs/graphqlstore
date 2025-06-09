"""Modulo del comando probar-conexion"""

from ..base import Comando
from .main import proconexion


class ComandoProbarConexion(Comando):
    """
    Clase que implementa el comando de probar la conexion de la configuracion
    de la base de datos realizado previamente con el comando conexion
    """

    def crear_comando(self, subparsers):
        probarcon = subparsers.add_parser(
            "probar-conexion",
            help="Probar la conexion a la base de datos configurada",
        )
        probarcon.add_argument(
            "--verbose",
            "-v",
            action="store_true",
            help="Mostrar mas detalles de la informacion de la conexion",
        )

    def contenido_comando(self, args):
        """
        Metodo que se ejecuta al ejecutar el comando probar-conexion
        Args:
            args (Namespace): Argumentos parseados de la linea de comandos
        """
        if args.comando == "probar-conexion":
            proconexion(args)
