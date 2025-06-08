"""Modulo para adaptador MySQL."""

import traceback
import mysql
from rich.console import Console
from ..adaptador_database import AdaptadorDatabase


class AdaptadorMySQL(AdaptadorDatabase):
    """Adaptador para bases de datos MySQL."""

    def __init__(self):
        """Implementacion del adaptador MySQL."""
        self.conexion = None
        self.cursor = None
        self.consola = Console()

    def conectar(self, config) -> None:
        """Conectar a la base de datos MySQL."""
        try:
            self.conexion = mysql.connector.connect(
                host=config.get("DB_HOST", "localhost"),
                port=config.get("DB_PORT", "3306"),
                user=config.get("DB_USER", ""),
                password=config.get("DB_PASSWORD", ""),
                database=config.get("DB_NAME", ""),
            )
            self.cursor = self.conexion.cursor()
        except mysql.connector.Error as err:
            raise ValueError(
                f"Fallo de conexion de la base de datos. \
                    Porfavor verifica tu configuracion. Error: {err}"
            ) from err

    def probar_conexion(self, verbose):
        """Probar la conexión a la base de datos."""
        consola = self.consola
        cursor = self.cursor

        try:
            style = "bold blue"
            msg = "Intentando conectarse a la base de datos...\n"
            consola.print(msg, style)

            db_info, db_name = None, None
            if self.conexion.is_connected():
                db_info = self.conexion.server_info
                self.cursor.execute("SELECT DATABASE();")
                db_name = self.cursor.fetchone()[0]

                style = "bold green"
                msg = "✅ Conectado exitosamente a la base de datos!\n"
                consola.print(msg, style)

            if verbose:
                style = "green"
                consola.print(f"\tVersion del servidor: {db_info}", style)
                msg = f"\tConectado a la base de datos: {db_name}"
                consola.print(msg, style)

                # get some basic database statistics
                cursor.execute("SHOW TABLES;")
                tablas = cursor.fetchall()
                consola.print(f"\tNumbero de tablas: [{len(tablas)}]", style)
                if tablas:
                    consola.print("\tTablas:", style)
                    for tabla in tablas:
                        consola.print(f"\t\t- {tabla[0]}", style)

                consola.print("\n")
                self.cerrar_conexion()

            return

        except mysql.connector.Error as err:
            style = "bold red" if not verbose else "red"
            msg = f"❌ Fallo la conexion a la base datos: {str(err)}"
            consola.print(msg, style)
            if verbose:
                consola.print(traceback.format_exc(), style)
            return

    def ejecutar_consulta(self, sql: str) -> None:
        """Ejecutar una consulta SQL en la base de datos."""
        if not self.cursor:
            raise ValueError("Base de datos no conectada.")
        self.cursor.execute(sql)

    def cerrar_conexion(self) -> None:
        """Cerrar la conexión a la base de datos."""
        if self.cursor:
            self.cursor.close()
        if self.conexion:
            self.conexion.close()
