"""Modulo FileManager"""

from pathlib import Path


class GestorArchivo:
    """Clase utilidad para operaciones de archivo."""

    @staticmethod
    def leer_archivo(ruta_archivo: Path) -> str:
        """Leer el contenido desde un archivo."""
        with open(ruta_archivo, "r", encoding="utf-8") as a:
            return a.read()

    @staticmethod
    def escribir_archivo(contenido: str, ruta_salida: Path):
        """Escribir contenido para un archivo."""
        with open(ruta_salida, "w", encoding="utf-8") as a:
            a.write(contenido)

    @staticmethod
    def asegurar_dir_existe(directorio: Path):
        """Asegurar que el directorio exista, si no, crearlo."""
        if not directorio.exists():
            directorio.mkdir(parents=True, exist_ok=True)
