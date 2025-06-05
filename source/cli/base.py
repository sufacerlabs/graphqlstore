"""Modulo base para crear comandos"""

from abc import ABC, abstractmethod


class Comando(ABC):
    """
    Clase abstracta para los comandos
    """

    @abstractmethod
    def crear_comando(self, subparsers):
        """Registrar el comando en el parser"""

    @abstractmethod
    def contenido_comando(self, args):
        """Metodo que se ejecuta al ejecutar el comando"""
