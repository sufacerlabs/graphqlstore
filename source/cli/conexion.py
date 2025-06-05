"""Modulo para gestionar la conexión en la CLI."""

import json
from pathlib import Path
from rich.console import Console


def conexion(args):
    """Funcion para configurar la conexion a la base de datos."""
    consola = Console()

    co_si, co_no = "bold green", "bold red"

    consola.print("Configure las base de datos que necesite.", style=co_si)

    # cargar configuracion existente, si existe
    configuracion_archivo = Path.cwd() / ".graphqlstore_config.json"
    conf = {}

    if configuracion_archivo.exists() and not args.archivo:
        # leer archivo existente
        try:
            with open(configuracion_archivo, "r", encoding="utf-8") as f:
                conf = json.load(f)
            msg = "Configuracion cargada desde el archivo existente."
            consola.print(msg, style=co_si)
        except (json.JSONDecodeError, OSError) as e:
            msg = f"Error al leer el archivo de configuracion: {str(e)}"
            consola.print(msg, style=co_no)
            return

    if args.archivo:
        try:
            with open(args.archivo, "r", encoding="utf-8") as f:
                configuracion_archivo.write_text(f.read(), encoding="utf-8")
                msg = "Configuracion cargada con el archivo pasado."
            consola.print(msg, style=co_si)
        except (json.JSONDecodeError, OSError) as e:
            msg = f"Error al leer el archivo de configuracion: {str(e)}"
            consola.print(msg, style=co_no)
            return

    if not configuracion_archivo.exists() and not args.archivo:

        if args.host:
            conf["DB_HOST"] = args.host
        if args.puerto:
            conf["DB_PUERTO"] = args.puerto
        if args.usuario:
            conf["DB_USUARIO"] = args.usuario
        if args.password:
            conf["DB_PASSWORD"] = args.password
        if args.db_nombre:
            conf["DB_NOMBRE"] = args.db_nombre

        # si no se proporciona argumentos especificos
        # ingresar interactivamente
        check_args = [
            args.host,
            args.puerto,
            args.usuario,
            args.password,
            args.db_nombre,
        ]
        if not args.archivo and not any(check_args):
            consola.print("Ingrese los datos de la base de datos:")
            conf["DB_HOST"] = input(
                f"Host (default: {conf.get('DB_HOST', 'localhost')}): "
            ) or conf.get("DB_HOST", "localhost")
            conf["DB_PUERTO"] = input(
                f"Puerto (default: {conf.get('DB_PUERTO', '3306')}): "
            ) or conf.get("DB_PUERTO", "3306")
            conf["DB_USUARIO"] = input(
                f"Usuario [{conf.get('DB_USUARIO', '')}]: "
            ) or conf.get("DB_USUARIO", "")
            conf["DB_PASSWORD"] = input(
                f"Contraseña [{conf.get('DB_PASSWORD', '')}]: "
            ) or conf.get("DB_PASSWORD", "")
            conf["DB_NOMBRE"] = input(
                f"Nombre BD " f"[{conf.get('DB_NOMBRE', '')}]: "
            ) or conf.get("DB_NOMBRE", "")

        # guardar configuracion en el archivo
        try:
            with open(configuracion_archivo, "w", encoding="utf-8") as f:
                json.dump(conf, f, indent=4)
            consola.print(
                "✅ Configuracion de conexion guardado exitosamente",
                style="bold green",
            )
        except OSError as e:
            msg = f"Error al guardar la configuracion: {str(e)}"
            consola.print(msg, style=co_no)
            return
