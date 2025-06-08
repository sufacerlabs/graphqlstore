"""Modulo que define la clase abstracta AdaptadorDatabase."""

from abc import abstractmethod


class AdaptadorDatabase:
    """Clase abstracta para manejar operaciones de base de datos."""

    @abstractmethod
    def conectar(self, config):
        """Conectar a la base de datos usando la configuración \
            proporcionada."""

    @abstractmethod
    def ejecutar_consulta(self, sql: str):
        """Ejecutar una consulta SQL en la base de datos."""

    @abstractmethod
    def cerrar_conexion(self):
        """Cerrar la conexión a la base de datos."""
