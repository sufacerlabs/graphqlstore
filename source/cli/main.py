"Modulo CLI para GraphQLStore"

import argparse
from rich.console import Console
from .conexion import conexion


class CLI:
    """Clase principal para la interfaz de línea de comandos de GraphQLStore"""

    def __init__(self, titulo: str = "GraphQLStore CLI"):
        self.consola = Console()
        self.titulo = titulo
        self.parser = argparse.ArgumentParser(description=self.titulo)
        self.subparsers = self.parser.add_subparsers(
            dest="comando", help="Comando a ejecutar"
        )
        self.args = None

    def crear_comando_conexion(self):
        """Metodo para crear un comando de conexion"""
        conexion_parser = self.subparsers.add_parser(
            "conexion", help=("onfigurar la conexion a la base de datos")
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

    def ejecutar(self):
        """Metodo para ejecutar la interfaz de line de comandos"""

        self.crear_comando_conexion()

        # parsear los argumentos de la linea de comandos
        self.args = self.parser.parse_args()

        # si no hay comandos definidos, mostrar ayuda
        if not self.args.comando:
            self.parser.print_help()
            return

        # ejecutar el comando correspondiente
        if self.args.comando == "conexion":
            conexion(self.args)
