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
            dest="commando", help="Comando a ejecutar"
        )
        self.args = None

    def crear_comando_conexion(self):
        """Metodo para crear un comando de conexion"""
        conexion_parser = self.subparsers.add_parser(
            "conexion",
            help=(
                "Inicializar un nuevo esquema de base de datos "
                "desde GraphQL y "
                "generar los archivos para el cliente GraphQL"
            ),
        )
        conexion_parser.add_argument(
            "--esquema",
            "-e",
            required=False,
            help="URL del esquema GraphQL \
                a utilizar",
        )
        conexion_parser.add_argument(
            "--salida",
            "-s",
            default="generado",
            required=False,
            help="Directorio de salida para los archivos generados",
        )
        conexion_parser.add_argument(
            "--no-visualizar",
            "-nv",
            default=False,
            action="store_true",
            help="No visualizar resultados en consola",
        )
        conexion_parser.add_argument(
            "--no-graphql",
            "-ng",
            default=False,
            action="store_true",
            help="No visualizar resultados sql en consola",
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
            conexion()
