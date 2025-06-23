"Modulo CLI para GraphQLStore"

from .servidor.comando_servidor import ComandoServidor
from .migracion.comando_migracion import ComandoMigracion
from .inicializar.comando_inicializar import ComandoInicializar
from .conexion.comando_conexion import ComandoConexion
from .probar_conexion.comando_probar_conexion import ComandoProbarConexion
from .core import ConstructorCLI


class CLI:
    """Clase principal para la interfaz de línea de comandos de GraphQLStore"""

    # pylint: disable=too-many-instance-attributes
    def __init__(self, titulo: str = "GraphQLStore CLI"):
        """Inicializar la interfaz de línea de comandos"""

        # inicializar el constructor/builder
        self.titulo = titulo
        self.constructor = ConstructorCLI(titulo)
        self.args = None
        self.comando_conexion = ComandoConexion()
        self.comando_probar_conexion = ComandoProbarConexion()
        self.comando_inicializar = ComandoInicializar()
        self.comando_migracion = ComandoMigracion()
        self.comando_servidor = ComandoServidor()

    def parsear_comando(self):
        """
        Metodo para parsear/registrar un nuevo comando en \
            la interfaz de línea de comandos."""
        self.constructor.agregar_comando(self.comando_conexion)
        self.constructor.agregar_comando(self.comando_probar_conexion)
        self.constructor.agregar_comando(self.comando_inicializar)
        self.constructor.agregar_comando(self.comando_migracion)
        self.constructor.agregar_comando(self.comando_servidor)

    def lanzamiento_condicionado(self):
        """Metodo que lanza el comando solicitado"""
        self.comando_conexion.contenido_comando(self.args)
        self.comando_probar_conexion.contenido_comando(self.args)
        self.comando_inicializar.contenido_comando(self.args)
        self.comando_migracion.contenido_comando(self.args)
        self.comando_servidor.contenido_comando(self.args)

    def ejecutar(self):
        """Metodo para ejecutar la interfaz de line de comandos"""

        self.parsear_comando()
        # parsear los argumentos de la linea de comandos
        self.args = self.constructor.parsear()

        # si no hay comandos definidos, mostrar ayuda
        if not self.args.comando:
            self.constructor.parser.print_help()
            return

        # ejecutar el comando correspondiente
        self.lanzamiento_condicionado()

    # pylint: enable=too-many-instance-attributes
