"""Modulo ProcesarRelaciones"""

from typing import Dict, List, Optional, Tuple

from .exceptions import RelationshipError

from .configuracion_y_constantes import (
    FuenteRelacion,
    InfoDirectiva,
    InfoEnum,
    InfoField,
    InfoRelacion,
    InfoTabla,
    ObjetivoRelacion,
    TipoField,
    TipoLink,
    TipoRelacion,
)


class ProcesarRelaciones:
    """Clase para procesar relaciones entre entidades."""

    def __init__(
        self,
        tablas: Dict[str, InfoTabla],
        scalar_types: Dict[str, str],
        enum_types: Dict[str, InfoEnum],
    ):
        """
        Inicializa la clase con las tablas y tipos escalares.

        :param tablas: Diccionario con las tablas y su información.
        :param scalar_types: Diccionario con los tipos escalares.
        :param enum_types: Diccionario con los tipos enumerados.
        """
        self.tablas = tablas
        self.scalar_types = scalar_types
        self.enum_types = enum_types
        self.relaciones: List[InfoRelacion] = []
        # mantener el seguimiento de las relaciones procesadas
        self.relaciones_procesadas: set[Tuple[str, ...]] = set()
        # mantener el seguimiento de nombres constraint usados
        self.nombres_constraint_usados: set[str] = set()

    def procesar_relaciones(self) -> List[InfoRelacion]:
        """
        Procesa las relaciones entre las tablas y \
            devuelve una lista de InfoRelacion.

        :return: Lista de InfoRelacion con la información de las relaciones.
        """
        # procesar todas las relacines entre las tablas
        for nombre_tabla, info_tabla in self.tablas.items():
            for nombre_campo, info_campo in info_tabla.campos.items():
                relacion = self._procesar_si_es_relacion(
                    nombre_tabla,
                    nombre_campo,
                    info_campo,
                )
                if relacion:
                    self.relaciones.append(relacion)

        # validar las relaciones procesadas
        self._validar_relaciones()
        return self.relaciones

    # pylint: disable=too-many-locals
    def _procesar_si_es_relacion(
        self,
        nombre_tabla: str,
        nombre_campo: str,
        info_campo: InfoField,
    ) -> Optional[InfoRelacion]:
        """
        Procesa si un campo es una relación y \
            devuelve la información de la relación.

        :param nombre_tabla: Nombre de la tabla.
        :param nombre_campo: Nombre del campo.
        :param info_campo: Información del campo.
        :return: InfoRelacion si es una relación, None en caso contrario.
        """

        # skip si el campo no es una relación
        tipo_campo = info_campo.tipo_campo
        if TipoField.existe(tipo_campo) or tipo_campo in self.enum_types:
            return None

        # es una relación, procesar la información
        tabla_objetivo = tipo_campo
        info_relacion: InfoDirectiva = info_campo.directivas.get(
            "relation",
            InfoDirectiva(
                nombre="relation",
                argumentos={},
            ),
        )
        nombre_relacion: Optional[str] = info_relacion.argumentos.get("name")
        # tipo de enlace de relacion por defecto es INLINE
        tipo_link: str = info_relacion.argumentos.get("link", "INLINE")
        # action on delete por defecto es SET_NULL
        on_delete: str = info_relacion.argumentos.get("onDelete", "SET_NULL")

        if not nombre_relacion:
            msg = (
                "Configuracion de relacion incorrecta: "
                "Falta un nombre para la relacion "
                f"entre {nombre_tabla}.{nombre_campo} "
                f"y {tabla_objetivo}."
            )
            raise RelationshipError(msg)

        # buscar la relacion inversa if existe
        campo_inverso, on_delete_inverso = self._buscar_relacion_inversa(
            nombre_tabla,
            nombre_relacion,
            tabla_objetivo,
        )

        # determinar tipo de relacion
        tipo_relacion = self._determinar_tipo_relacion(
            tabla_objetivo,
            campo_inverso,
            info_campo,
        )

        # verificar si la relacion debe ser procesada o
        procesa = self._deberia_procesar_relacion(
            nombre_tabla,
            nombre_campo,
            tabla_objetivo,
            campo_inverso,
        )
        if not procesa:
            # si la relacion ya fue procesada, retornar None
            return None

        # generar nombres constraint pra el campo fuente y objetivo
        nombre_constraint_fuente, nombre_constraint_objetivo = (
            self._generar_nombres_constraint(
                nombre_tabla,
                nombre_campo,
                tabla_objetivo,
                campo_inverso,
                tipo_relacion,
            )
        )

        # retornar la relacion procesada
        return InfoRelacion(
            fuente=FuenteRelacion(
                tabla_fuente=nombre_tabla,
                campo_fuente=nombre_campo,
                fuente_es_lista=info_campo.es_lista,
                nombre_constraint_fuente=nombre_constraint_fuente,
                on_delete=on_delete,
            ),
            objetivo=ObjetivoRelacion(
                tabla_objetivo=tabla_objetivo,
                campo_inverso=campo_inverso,
                nombre_constraint_objetivo=nombre_constraint_objetivo,
                on_delete_inverso=on_delete_inverso,
            ),
            tipo_relation=tipo_relacion,
            nombre_relacion=nombre_relacion,
            tipo_link=tipo_link,
        )

    # pylint: enable=too-many-locals

    def _buscar_relacion_inversa(
        self,
        nombre_tabla: str,
        nombre_relacion: str,
        tabla_objetivo: str,
    ) -> Tuple[Optional[str], str]:
        """
        Busca la relación inversa en la tabla objetivo.

        :param nombre_tabla: Nombre de la tabla fuente.
        :param nombre_relacion: Nombre de la relación.
        :param tabla_objetivo: Nombre de la tabla objetivo.
        :return: Tupla con el campo inverso y el on_delete inverso.
        """

        campo_inverso: Optional[str] = None
        on_delete_inverso: str = "SET_NULL"

        if tabla_objetivo in self.tablas:
            for nombre_campo_inverso, info_campo_inverso in self.tablas[
                tabla_objetivo
            ].campos.items():
                if info_campo_inverso.tipo_campo == nombre_tabla:
                    directivas = info_campo_inverso.directivas
                    info_rel_inver: InfoDirectiva = directivas.get(
                        "relation",
                        InfoDirectiva(
                            nombre="relation",
                            argumentos={},
                        ),
                    )
                    args_rel_inver = info_rel_inver.argumentos
                    nombre_rel_inver: Optional[str] = args_rel_inver.get(
                        "name",
                    )

                    if (
                        nombre_relacion
                        and nombre_rel_inver
                        and nombre_relacion == nombre_rel_inver
                    ):
                        campo_inverso = nombre_campo_inverso
                        on_delete_inverso = args_rel_inver.get(
                            "onDelete",
                            "SET_NULL",
                        )
                        break

        return campo_inverso, on_delete_inverso

    def _determinar_tipo_relacion(
        self,
        tabla_objetivo: str,
        campo_inverso: Optional[str],
        info_campo: InfoField,
    ) -> str:
        """
        Determina el tipo de relación entre las tablas.

        :param tabla_objetivo: Nombre de la tabla objetivo.
        :param campo_inverso: Nombre del campo inverso si existe.
        :param info_campo: Información del campo de la tabla fuente.
        :return: TipoRelacion.value que representa el tipo de relación.
        """

        tipo_relacion = TipoRelacion.ONE_TO_ONE.value
        if (info_campo.es_lista and campo_inverso) and self.tablas[
            tabla_objetivo
        ].campos[campo_inverso].es_lista:
            tipo_relacion = TipoRelacion.MANY_TO_MANY.value
        elif (
            info_campo.es_lista
            or campo_inverso
            and self.tablas[tabla_objetivo].campos[campo_inverso].es_lista
        ):
            tipo_relacion = TipoRelacion.ONE_TO_MANY.value

        return tipo_relacion

    def _deberia_procesar_relacion(
        self,
        nombre_tabla: str,
        nombre_campo: str,
        tabla_objetivo: str,
        campo_inverso: Optional[str],
    ) -> bool:
        """
        Verifica si la relación ya ha sido procesada.

        :param nombre_tabla: Nombre de la tabla fuente.
        :param nombre_campo: Nombre del campo de la tabla fuente.
        :param tabla_objetivo: Nombre de la tabla objetivo.
        :param campo_inverso: Nombre del campo inverso si existe.
        :return: True si la relación ya ha sido procesada, \
            False en caso contrario.
        """
        relacion_par: Tuple[str, ...] = tuple(
            sorted(
                [
                    f"{nombre_tabla}.{nombre_campo}",
                    (
                        f"{tabla_objetivo}.{campo_inverso}"
                        if campo_inverso
                        else f"{tabla_objetivo}"
                    ),
                ]
            )
        )

        if relacion_par in self.relaciones_procesadas:
            return False

        # agregar la relacion procesada
        self.relaciones_procesadas.add(relacion_par)
        return True

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-positional-arguments
    def _generar_nombres_constraint(
        self,
        nombre_tabla: str,
        nombre_campo: str,
        tabla_objetivo: str,
        campo_inverso: Optional[str],
        tipo_relacion: str,
    ) -> Tuple[str, Optional[str]]:
        """
        Genera nombres únicos para las constraints de la relación.

        :param nombre_tabla: Nombre de la tabla fuente.
        :param nombre_campo: Nombre del campo de la tabla fuente.
        :param tabla_objetivo: Nombre de la tabla objetivo.
        :param campo_inverso: Nombre del campo inverso si existe.
        :param tipo_relacion: Tipo de relación
        :return: Tupla con los nombres de las constraints \
            para fuente y objetivo.
        """

        nom_con_fue = f"fk_{nombre_tabla}_{nombre_campo}_{tabla_objetivo}"
        if campo_inverso:
            nom_con_fue += f"_{campo_inverso}"

        contador_constraint = 1
        while nom_con_fue in self.nombres_constraint_usados:
            nom_con_fue = f"fk_{nombre_tabla}_{nombre_campo}_{tabla_objetivo}"
            contador_constraint += 1

        self.nombres_constraint_usados.add(nom_con_fue)

        nombre_constraint_objetivo: Optional[str] = None
        if tipo_relacion == TipoRelacion.MANY_TO_MANY.value and campo_inverso:
            nombre_constraint_objetivo = (
                f"fk_{tabla_objetivo}_{campo_inverso}_{nombre_tabla}"
            )
            contador_constraint = 1
            while nombre_constraint_objetivo in self.nombres_constraint_usados:
                nombre_constraint_objetivo = (
                    f"fk_{tabla_objetivo}_{campo_inverso}_"
                    f"{nombre_tabla}_{contador_constraint}"
                )
                contador_constraint += 1

            self.nombres_constraint_usados.add(nombre_constraint_objetivo)

        return nom_con_fue, nombre_constraint_objetivo

    # pylint: enable=too-many-arguments
    # pylint: enable=too-many-positional-arguments

    def _validar_relaciones(self) -> None:
        """Validar que la configuracion de relacion es correcta."""

        for relacion in self.relaciones:
            tabla_fuente = relacion.fuente.tabla_fuente
            campo_fuente = relacion.fuente.campo_fuente
            tabla_objetivo = relacion.objetivo.tabla_objetivo
            tipo_relacion = relacion.tipo_relation
            tipo_link = relacion.tipo_link
            # nombre_relacion = relacion.nombre_relacion

            if (
                tipo_relacion == TipoRelacion.MANY_TO_MANY.value
                and tipo_link != TipoLink.TABLE.value
            ):
                msg = (
                    "Configuracion de relacion incorrecta: "
                    "Para relaciones N:M "
                    f"entre {tabla_fuente}.{campo_fuente} y {tabla_objetivo} "
                    "debe usarse tipo de link TABLE."
                )
                raise RelationshipError(msg)

    def get_relaciones(self) -> List[InfoRelacion]:
        """
        Obtiene la lista de relaciones procesadas.

        :return: Lista de InfoRelacion con la información de las relaciones.
        """
        return self.relaciones
