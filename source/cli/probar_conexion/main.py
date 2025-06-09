"""Modulo para gestionar la prueba de conexion a \
    la base de datos configurada."""

from pathlib import Path

from ..database.adaptadores.mysql import AdaptadorMySQL
from ..loaders.conf_json_loader import ConfiguracionJsonLoader


def proconexion(args):
    """
    Funcion para comprobar la conexion a la base de datos configurada.
    """

    ruta_archivo = Path.cwd() / ".graphqlstore_config.json"

    # inicializar el loader de configuracion
    loader_json = ConfiguracionJsonLoader(ruta_archivo)

    # cargar la configuracion
    config = loader_json.cargar_configuracion()

    if not config:
        return

    # verificar si la configuracion es correcta
    loader_json.verificar_configuracion()

    # inicializar adaptador de base de datos
    adaptador = AdaptadorMySQL()

    # conectar a la base de datos
    adaptador.conectar(config)

    # probar la conexion
    adaptador.probar_conexion(args.verbose)
