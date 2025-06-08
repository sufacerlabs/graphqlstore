"""Modulo para cargar la configuracion"""

from abc import ABC, abstractmethod


class ConfiguracionLoader(ABC):
    """Clase abstracta para cargar configuraciones."""

    @abstractmethod
    def cargar_configuracion(self):
        """Metodo abstracto para cargar la configuracion."""

    def verificar_configuracion(self):
        """Verifica si la configuracion es valida."""
