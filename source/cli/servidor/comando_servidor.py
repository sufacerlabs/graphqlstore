"""Modulo del comando servidor"""

from ..base import Comando
from .main import servidor


class ComandoServidor(Comando):
    """
    Clase que implementa el comando de servidor
    """

    def crear_comando(self, subparsers):
        htext = "Iniciar un servidor GraphQL"
        subparsers.add_parser(
            "servidor",
            help=htext,
        )

    def contenido_comando(self, args):
        """
        Metodo que se ejecuta al ejecutar el comando servidor
        Args:
            args (Namespace): Argumentos parseados de la linea de comandos
        """
        if args.comando == "servidor":
            servidor()
