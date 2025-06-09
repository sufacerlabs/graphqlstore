"""Modulo para adaptador MySQL."""

import traceback
import mysql.connector
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
                port=config.get("DB_PUERTO", "3306"),
                user=config.get("DB_USUARIO", ""),
                password=config.get("DB_PASSWORD", ""),
                database=config.get("DB_NOMBRE", ""),
            )
            self.cursor = self.conexion.cursor()
        except mysql.connector.Error as err:
            self.consola.print(
                "❌ Error al conectar a la base de datos",
                style="red",
            )
            self.consola.print(
                f"Detalles del error: {str(err)}",
                style="red",
            )

    def probar_conexion(self, verbose):
        """Probar la conexión a la base de datos."""
        consola = self.consola
        cursor = self.cursor

        if not self.conexion or not self.cursor:
            return

        try:
            msg = "Intentando conectarse a la base de datos...\n"
            consola.print(msg, style="bold blue")

            db_info, db_name = None, None
            if self.conexion.is_connected():
                db_info = self.conexion.server_info
                self.cursor.execute("SELECT DATABASE();")
                db_name = self.cursor.fetchone()[0]

                msg = "✅ Conectado exitosamente a la base de datos!\n"
                consola.print(msg, style="bold green")

            if verbose:
                consola.print(
                    f"\tVersion del servidor: {db_info}",
                    style="green",
                )
                msg = f"\tConectado a la base de datos: {db_name}"
                consola.print(msg, style="green")

                # get some basic database statistics
                cursor.execute("SHOW TABLES;")
                tablas = cursor.fetchall()
                consola.print(
                    f"\tNumbero de tablas: [{len(tablas)}]",
                    style="green",
                )
                if tablas:
                    consola.print("\tTablas:", style="green")
                    for tabla in tablas:
                        consola.print(f"\t\t- {tabla[0]}", style="green")

                consola.print("\n")
                self.cerrar_conexion()

            return

        except mysql.connector.Error as err:
            msg = f"❌ Fallo la conexion a la base datos: {str(err)}"
            consola.print(msg, style="bold red")
            if verbose:
                consola.print(traceback.format_exc(), style="red")
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
