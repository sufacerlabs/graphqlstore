"""Modulo para cargar el  archivo de configuracion en formato JSON."""

import json
from rich.console import Console
from .conf_loader import ConfiguracionLoader


class ConfiguracionJsonLoader(ConfiguracionLoader):
    """Clase para cargar configuraciones desde un archivo JSON."""

    def __init__(self, ruta_archivo):
        self.ruta_archivo = ruta_archivo
        self.consola = Console()
        self.co_si = "bold green"
        self.co_no = "bold red"
        self.conf = None

    def cargar_configuracion(self):
        """Carga la configuracion desde un archivo JSON."""
        conf = {}
        if not self.ruta_archivo.exists():
            self.consola.print(
                "❌ Archivo de configuracion no encontrado. "
                "Asegurate de haber ejecutado primeramente "
                "el comando 'conexion'",
                style=self.co_no,
            )
            return conf

        try:
            with open(self.ruta_archivo, "r", encoding="utf-8") as archivo:
                conf = json.load(archivo)
        except (json.JSONDecodeError, OSError) as e:
            msg = f"Error al leer el archivo de configuracion: {str(e)}"
            self.consola.print(msg, style=self.co_no)

        self.conf = conf
        return self.conf

    def verificar_configuracion(self):
        """Verifica que la configuracion cargada sea valida."""

        # verificar si todos los campos necesarios estan presentes
        param_req = [
            "DB_HOST",
            "DB_PUERTO",
            "DB_USUARIO",
            "DB_PASSWORD",
            "DB_NOMBRE",
        ]
        faltantes = [param for param in param_req if param not in self.conf]

        if faltantes:
            self.consola.print(
                "❌ Faltan los siguientes parametros en la configuracion: "
                f"{', '.join(faltantes)}",
                style=self.co_no,
            )
            return

        return
