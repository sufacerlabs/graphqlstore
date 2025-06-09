"""Modulo para construir el parser (modularmente) al agregar comandos"""

import argparse

from .base import Comando


class ConstructorCLI:
    """Clase constructor para construir y parsear los comandos"""

    def __init__(self, titulo: str = "GraphQLStore CLI"):
        self.titulo = titulo
        self.parser = argparse.ArgumentParser(description=self.titulo)
        self.subparsers = self.parser.add_subparsers(
            dest="comando", help="Comando a ejecutar"
        )

    def agregar_comando(self, comando: Comando):
        """Metodo para agregar un comando al parser

        Args:
            comando (Comando): Instancia de la clase Comando que \
                se desea agregar al parser
        """
        comando.crear_comando(self.subparsers)

    def parsear(self):
        """Metodo para parsear los argumentos de la linea de comandos"""
        args = self.parser.parse_args()
        return args
