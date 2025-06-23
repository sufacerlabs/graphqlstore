"""Modulo GeneradorMigracionMySQL para GraphQL Store."""

import datetime
import hashlib
from typing import Dict, List, Optional
from rich.console import Console
from rich.tree import Tree
from rich.syntax import Syntax
from rich.panel import Panel

from .configuracion_y_constantes import (
    InfoTabla,
    InfoField,
    InfoRelacion,
    InfoEnum,
    InfoDiffEsquema,
    InfoDiffTablas,
    InfoDiffRelaciones,
    InfoDiffEnums,
    InfoDiffCampos,
    InfoCambioCampo,
    InfoCambioEnum,
    InfoMigracion,
    TipoRelacion,
    OnDelete,
)

from .templates import (
    TEMPLATE_CREAR_TABLA,
    TEMPLATE_AGREGAR_CAMPO,
    TEMPLATE_ELIMINAR_CAMPO,
    TEMPLATE_MODIFICAR_CAMPO,
    TEMPLATE_ELIMINAR_FK,
    TEMPLATE_ELIMINAR_TABLA,
    template_crear_tabla_junction,
    template_modificar_fk,
)
from .exceptions import (
    GraphQLStoreError,
    MigrationError,
    SchemaComparisonError,
    MigrationGenerationError,
)
from .parser import ParserGraphQLEsquema
from .procesar_relaciones import ProcesarRelaciones


class GeneradorMigracionMySQL:
    """Generador de migraciones MySQL desde diferencias de esquemas GraphQL."""

    def __init__(self):
        """Inicializar el generador de migracion."""
        self.consola = Console()
        self.migraciones_sql = []
        self.parser = ParserGraphQLEsquema()
        self.visualizar_salida = True
        self.visualizar_sql = True

        self._enums_disponibles = None
        self._tablas_existentes = None

    def generar_migracion(
        self,
        esquema_anterior: str,
        esquema_nuevo: str,
        id_migracion: Optional[str] = None,
        visualizar_salida: bool = True,
        visualizar_sql: bool = True,
    ) -> InfoMigracion:
        """
        Generar migracion completa desde dos esquemas GraphQL.

        :param esquema_anterior: Esquema GraphQL anterior
        :param esquema_nuevo: Esquema GraphQL nuevo
        :param id_migracion: ID personalizado de migracion
        :param visualizar_salida: Si mostrar salida detallada
        :param visualizar_sql: Si mostrar SQL generado
        :return: Informacion completa de la migracion
        """
        # pylint: disable=too-many-arguments,too-many-positional-arguments
        self.visualizar_salida = visualizar_salida
        self.visualizar_sql = visualizar_sql

        try:
            # generar id de migracion si no se proporciona
            if not id_migracion:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                hash_schemas = self._generar_hash_esquemas(
                    esquema_anterior,
                    esquema_nuevo,
                )
                id_migracion = f"migration_{timestamp}_{hash_schemas[:8]}"

            if self.visualizar_salida:
                self._mostrar_inicio_migracion(id_migracion)

            # comparar esquemas
            diferencias = self.diff_esquemas(
                esquema_anterior,
                esquema_nuevo,
            )

            if not diferencias.tiene_cambios():
                if self.visualizar_salida:
                    self.consola.print(
                        "\n✅ No se detectaron cambios entre los esquemas\n",
                        style="green",
                    )

                return InfoMigracion(
                    id_migracion=id_migracion,
                    timestamp=datetime.datetime.now().isoformat(),
                    esquema_anterior=esquema_anterior,
                    esquema_nuevo=esquema_nuevo,
                    diferencias=diferencias,
                    sql_generado="",
                )

            # generar SQL de migracion
            sql_migracion = self.generar_sql_migracion(diferencias)

            # crear informacion de migracion
            migracion = InfoMigracion(
                id_migracion=id_migracion,
                timestamp=datetime.datetime.now().isoformat(),
                esquema_anterior=esquema_anterior,
                esquema_nuevo=esquema_nuevo,
                diferencias=diferencias,
                sql_generado=sql_migracion,
            )

            if self.visualizar_salida:
                self._mostrar_resumen_migracion(len(sql_migracion.split(";")))

            return migracion

        except GraphQLStoreError as e:
            raise MigrationError(
                f"Error generando migracion: {str(e)}",
            ) from e
        # pylint: enable=too-many-arguments,too-many-positional-arguments

    def diff_esquemas(
        self, esquema_anterior: str, esquema_nuevo: str
    ) -> InfoDiffEsquema:
        """
        Comparar dos esquemas GraphQL y detectar diferencias.

        :param esquema_anterior: Esquema anterior
        :param esquema_nuevo: Esquema nuevo
        :return: Diferencias detectadas
        """
        try:
            # parsear esquema anterior
            info_anterior = self.parser.parse_esquema(esquema_anterior)
            procesador_anterior = ProcesarRelaciones(
                tablas=info_anterior.tablas,
                scalar_types=ParserGraphQLEsquema.get_type_mapping(),
                enum_types=info_anterior.enums,
            )
            relaciones_anterior = procesador_anterior.procesar_relaciones()

            # parsear esquema nuevo
            info_nuevo = self.parser.parse_esquema(esquema_nuevo)
            procesador_nuevo = ProcesarRelaciones(
                tablas=info_nuevo.tablas,
                scalar_types=ParserGraphQLEsquema.get_type_mapping(),
                enum_types=info_nuevo.enums,
            )
            relaciones_nuevo = procesador_nuevo.procesar_relaciones()

            self._enums_disponibles = {}
            self._enums_disponibles.update(info_anterior.enums)
            self._enums_disponibles.update(info_nuevo.enums)

            # comparar y generar diferencias
            diferencias = InfoDiffEsquema()

            # comparar tablas y campos
            diferencias.tablas = self._comparar_tablas(
                info_anterior.tablas,
                info_nuevo.tablas,
            )

            # filtrar tablas existentes y actualizarlas con nueva información
            self._tablas_existentes = {}
            for t, i in info_anterior.tablas.items():
                if t not in diferencias.tablas.eliminadas:
                    if t in info_nuevo.tablas:
                        self._tablas_existentes[t] = info_nuevo.tablas[t]
                    else:
                        self._tablas_existentes[t] = i

            # comparar relaciones
            diferencias.relaciones = self._comparar_relaciones(
                relaciones_anterior, relaciones_nuevo
            )

            # comparar enums
            diferencias.enums = self._comparar_enums(
                info_anterior.enums, info_nuevo.enums
            )

            if self.visualizar_salida:
                self._mostrar_diferencias_detectadas(diferencias)

            return diferencias

        except GraphQLStoreError as e:
            raise SchemaComparisonError(
                f"Error comparando esquemas: {str(e)}",
            ) from e

    def generar_sql_migracion(self, diferencias: InfoDiffEsquema) -> str:
        """
        Generar SQL de migracion desde diferencias detectadas.

        :param diferencias: Diferencias entre esquemas
        :return: SQL de migracion completo
        """
        # pylint: disable=too-many-branches,too-many-locals
        try:
            sentencias_sql = []

            # encabezado de migracion
            sentencias_sql.extend(self._generar_encabezado_migracion())

            # 1. Crear nuevas tablas (para que las claves foraneas puedan
            # referenciarlas correctamente)
            for nombre_tabla in diferencias.tablas.agregadas:
                if nombre_tabla in diferencias.tablas.campos:
                    campos = diferencias.tablas.campos[nombre_tabla].agregados
                    sql_tabla = self._generar_sql_crear_tabla(
                        nombre_tabla,
                        campos,
                    )
                    sentencias_sql.append(sql_tabla)

            # 2. eliminar relaciones (antes de eliminar campos/tablas)
            for relacion in diferencias.relaciones.eliminadas:
                sql_eliminar = self._generar_sql_eliminar_relacion(relacion)
                sentencias_sql.append(sql_eliminar)

            # 3. eliminar campos
            for nom_tabla, cambios_campos in diferencias.tablas.campos.items():
                if nom_tabla not in diferencias.tablas.agregadas:
                    for campo in cambios_campos.eliminados:
                        sql_eliminar = self._generar_sql_eliminar_campo(
                            nom_tabla, campo
                        )
                        sentencias_sql.append(sql_eliminar)

            # 4. agregar campos a tablas existentes
            for nom_tabla, cambios_campos in diferencias.tablas.campos.items():
                if nom_tabla not in diferencias.tablas.agregadas:
                    for campo in cambios_campos.agregados:
                        sql_agregar = self._generar_sql_agregar_campo(
                            nom_tabla,
                            campo,
                        )
                        sentencias_sql.append(sql_agregar)

            # 5. modificar campos existentes
            for nom_tabla, cambios_campos in diferencias.tablas.campos.items():
                for cambio in cambios_campos.modificados:
                    sql_modificar = self._generar_sql_modificar_campo(
                        nom_tabla,
                        cambio,
                    )
                    sentencias_sql.append(sql_modificar)

            # 6. modificar enums
            for enum_modificado in diferencias.enums.modificados:
                sql_enum = self._generar_sql_modificar_enum(enum_modificado)
                sentencias_sql.extend(sql_enum)

            # 7. agregar nuevas relaciones
            for relacion in diferencias.relaciones.agregadas:
                sql_relacion = self._generar_sql_agregar_relacion(relacion)
                sentencias_sql.append(sql_relacion)

            # 8. eliminar tablas (al final, ya que se eliminaron las
            #  foreign keys)
            for nombre_tabla in diferencias.tablas.eliminadas:
                sql_eliminar = self._generar_sql_eliminar_tabla(nombre_tabla)
                sentencias_sql.append(sql_eliminar)

            # filtrar sentencias vacías y unir
            filters_sentencias = [sql for sql in sentencias_sql if sql.strip()]
            return "\n\n".join(filters_sentencias)

        except GraphQLStoreError as e:
            raise MigrationGenerationError(
                f"Error generando SQL: {str(e)}",
            ) from e
        # pylint: enable=too-many-branches,too-many-locals

    def _comparar_tablas(
        self,
        tablas_anteriores: Dict[str, InfoTabla],
        tablas_nuevas: Dict[str, InfoTabla],
    ) -> InfoDiffTablas:
        """Comparar tablas entre esquemas."""
        diferencias = InfoDiffTablas()

        # tablas agregadas
        diferencias.agregadas = [
            name for name in tablas_nuevas if name not in tablas_anteriores
        ]

        # tablas eliminadas
        diferencias.eliminadas = [
            name for name in tablas_anteriores if name not in tablas_nuevas
        ]

        # comparar campos en tablas existentes
        for nombre_tabla in tablas_nuevas:
            if nombre_tabla in tablas_anteriores:
                campos_anterior = tablas_anteriores[nombre_tabla].campos
                campos_nuevo = tablas_nuevas[nombre_tabla].campos

                if campos_anterior == campos_nuevo:
                    continue

                diferencias.campos[nombre_tabla] = self._comparar_campos(
                    campos_anterior,
                    campos_nuevo,
                )
            elif nombre_tabla in diferencias.agregadas:
                # Para tablas nuevas, todos los campos son agregados
                diferencias.campos[nombre_tabla] = InfoDiffCampos(
                    agregados=list(tablas_nuevas[nombre_tabla].campos.values())
                )

        return diferencias

    def _comparar_campos(
        self,
        campos_anteriores: Dict[str, InfoField],
        campos_nuevos: Dict[str, InfoField],
    ) -> InfoDiffCampos:
        """Comparar campos entre tablas."""
        diferencias = InfoDiffCampos()

        # campos agregados
        for nombre_campo, info_campo in campos_nuevos.items():
            if nombre_campo not in campos_anteriores:
                if self._deberia_procesar_campo(info_campo):
                    diferencias.agregados.append(info_campo)

        # campos eliminados
        for nombre_campo, info_campo in campos_anteriores.items():
            if nombre_campo not in campos_nuevos:
                if self._deberia_procesar_campo(info_campo):
                    diferencias.eliminados.append(info_campo)

        # campos modificados
        for nombre_campo in campos_nuevos:
            if nombre_campo in campos_anteriores:
                campo_anterior = campos_anteriores[nombre_campo]
                campo_nuevo = campos_nuevos[nombre_campo]

                if self._deberia_procesar_campo(
                    campo_nuevo,
                ) and self._campos_son_diferentes(campo_anterior, campo_nuevo):
                    diferencias.modificados.append(
                        InfoCambioCampo(
                            nombre=nombre_campo,
                            info_antigua=campo_anterior,
                            info_nueva=campo_nuevo,
                        )
                    )

        return diferencias

    def _comparar_relaciones(
        self,
        relaciones_anteriores: List[InfoRelacion],
        relaciones_nuevas: List[InfoRelacion],
    ) -> InfoDiffRelaciones:
        """Comparar relaciones entre esquemas."""
        diferencias = InfoDiffRelaciones()

        # crear sets de claves únicas para comparación
        claves_anteriores = {
            self._generar_clave_relacion(
                rel,
            ): rel
            for rel in relaciones_anteriores
        }
        claves_nuevas = {
            self._generar_clave_relacion(rel): rel for rel in relaciones_nuevas
        }
        # relaciones agregadas
        for clave, relacion in claves_nuevas.items():
            if clave not in claves_anteriores:
                diferencias.agregadas.append(relacion)

        # relaciones eliminadas
        for clave, relacion in claves_anteriores.items():
            if clave not in claves_nuevas:
                diferencias.eliminadas.append(relacion)

        return diferencias

    def _comparar_enums(
        self,
        enums_anteriores: Dict[str, InfoEnum],
        enums_nuevos: Dict[str, InfoEnum],
    ) -> InfoDiffEnums:
        """Comparar enums entre esquemas."""
        diferencias = InfoDiffEnums()

        # enums agregados
        for nombre_enum, info_enum in enums_nuevos.items():
            if nombre_enum not in enums_anteriores:
                diferencias.agregados.append(info_enum)

        # enums eliminados
        for nombre_enum in enums_anteriores:
            if nombre_enum not in enums_nuevos:
                diferencias.eliminados.append(nombre_enum)

        # enums modificados
        for nombre_enum in enums_nuevos:
            if nombre_enum in enums_anteriores:
                valores_anteriores = set(enums_anteriores[nombre_enum].valores)
                valores_nuevos = set(enums_nuevos[nombre_enum].valores)

                if valores_anteriores != valores_nuevos:
                    diferencias.modificados.append(
                        InfoCambioEnum(
                            nombre=nombre_enum,
                            valores_antiguos=list(sorted(valores_anteriores)),
                            valores_nuevos=list(sorted(valores_nuevos)),
                            valores_agregados=list(
                                sorted(valores_nuevos - valores_anteriores),
                            ),
                            valores_eliminados=list(
                                sorted(valores_anteriores - valores_nuevos)
                            ),
                        )
                    )

        return diferencias

    def _generar_sql_crear_tabla(
        self, nombre_tabla: str, campos: List[InfoField]
    ) -> str:
        """Generar SQL para crear una nueva tabla."""
        columnas = []
        has_primary_key = False

        for campo in campos:
            if not self._deberia_procesar_campo(campo):
                continue

            def_columna = self._generar_definicion_columna(campo)
            columnas.append(f"  {def_columna}")

            # verificar si es primary key
            if "id" in campo.directivas:
                has_primary_key = True

        # agregar ID automático si no hay primary key
        if not has_primary_key:
            columnas.insert(0, "  `id` VARCHAR(25) NOT NULL PRIMARY KEY")

        # juntar columnas
        contenido_tabla = ",\n".join(columnas)

        sql = TEMPLATE_CREAR_TABLA.format(
            nombre_tabla=nombre_tabla, columnas=contenido_tabla
        )

        if self.visualizar_salida:
            self._visualizar_operacion_sql(
                "CREAR TABLA", f"Creando tabla {nombre_tabla}", sql
            )

        return f"-- Crear tabla {nombre_tabla}\n{sql}"

    def _generar_sql_agregar_campo(
        self,
        nombre_tabla: str,
        campo: InfoField,
    ) -> str:
        """Generar SQL para agregar un campo."""
        definicion = self._generar_definicion_columna(campo)
        emoji = self._visualizar_obligacion_campo(campo.es_requerido)
        sql = TEMPLATE_AGREGAR_CAMPO.format(
            tabla=nombre_tabla,
            definicion=definicion,
        )

        if self.visualizar_salida:
            self._visualizar_operacion_sql(
                "AGREGAR CAMPO",
                f"Agregando campo {campo.nombre}{emoji} a {nombre_tabla}",
                sql,
            )

        return f"-- Agregar campo {campo.nombre} a {nombre_tabla}\n{sql}"

    def _generar_sql_eliminar_campo(
        self,
        nombre_tabla: str,
        campo: InfoField,
    ) -> str:
        """Generar SQL para eliminar un campo."""
        sql = TEMPLATE_ELIMINAR_CAMPO.format(
            tabla=nombre_tabla,
            campo=campo.nombre,
        )
        emoji = self._visualizar_obligacion_campo(campo.es_requerido)

        if self.visualizar_salida:
            self._visualizar_operacion_sql(
                "ELIMINAR CAMPO",
                f"Eliminando campo {campo.nombre}{emoji} de {nombre_tabla}",
                sql,
            )

        return f"-- Eliminar campo {campo.nombre} de {nombre_tabla}\n{sql}"

    def _generar_sql_modificar_campo(
        self, nombre_tabla: str, cambio: InfoCambioCampo
    ) -> str:
        """Generar SQL para modificar un campo."""
        definicion = self._generar_definicion_columna(cambio.info_nueva)

        sql = TEMPLATE_MODIFICAR_CAMPO.format(
            tabla=nombre_tabla,
            definicion=definicion,
        )

        if self.visualizar_salida:
            self._visualizar_operacion_sql(
                "MODIFICAR CAMPO",
                f"Modificando campo {cambio.nombre} en {nombre_tabla}",
                sql,
            )

        return f"-- Modificar campo {cambio.nombre} en {nombre_tabla}\n{sql}"

    def _generar_sql_agregar_relacion(self, relacion: InfoRelacion) -> str:
        """Generar SQL para agregar una relacion."""
        if relacion.tipo_relation == TipoRelacion.MANY_TO_MANY.value:
            return self._generar_sql_tabla_junction(relacion)
        return self._generar_sql_foreign_key(relacion)

    def _generar_sql_eliminar_relacion(self, relacion: InfoRelacion) -> str:
        """Generar SQL para eliminar una relacion."""
        if relacion.tipo_relation == TipoRelacion.MANY_TO_MANY.value:
            sql = TEMPLATE_ELIMINAR_TABLA.format(
                tabla=relacion.nombre_relacion,
            )
            r = f"-- Eliminar relacion {relacion.nombre_relacion}\n{sql}"
            return r

        constraint_name = relacion.fuente.nombre_constraint_fuente
        tabla = self._determinar_tabla_fk(relacion)

        sql_drop_fk = TEMPLATE_ELIMINAR_FK.format(
            tabla=tabla, constraint=constraint_name
        )
        sql_drop_col = TEMPLATE_ELIMINAR_CAMPO.format(
            tabla=tabla, campo=f"{self._determinar_campo_fk(relacion)}_id"
        )

        r = f"-- Eliminar relacion {relacion.nombre_relacion}\n"
        r += f"{sql_drop_fk}\n{sql_drop_col}"
        return r

    def _deberia_procesar_campo(
        self,
        campo: InfoField,
    ) -> bool:
        """Verificar si un campo es escalar o enum."""
        if campo.tipo_campo in self.parser.get_type_mapping():
            return True

        ed = self._enums_disponibles
        if ed and campo.tipo_campo in ed:
            return True

        # verificar para una directiva relacion con link: INLINE
        directivas = campo.directivas.get("relacion", None)
        if directivas is not None:
            if directivas.argumentos.get("link", None) == "INLINE":
                return True

        return False

    def _campos_son_diferentes(
        self,
        campo1: InfoField,
        campo2: InfoField,
    ) -> bool:
        """Verificar si dos campos son diferentes."""
        return (
            campo1.tipo_campo != campo2.tipo_campo
            or campo1.es_lista != campo2.es_lista
            or campo1.es_requerido != campo2.es_requerido
            or campo1.directivas != campo2.directivas
        )

    def _generar_clave_relacion(self, relacion: InfoRelacion) -> str:
        """Generar clave única para una relacion."""
        return (
            f"{relacion.fuente.tabla_fuente}:"
            f"{relacion.fuente.campo_fuente}:"
            f"{relacion.objetivo.tabla_objetivo}:"
            f"{relacion.nombre_relacion}"
        )

    def _obtener_tipo_sql(self, campo: InfoField) -> str:
        """Obtener tipo SQL para un campo."""
        if campo.es_lista:
            return "JSON"

        tipo_sql = self.parser.get_type_mapping().get(campo.tipo_campo, "TEXT")

        # verificiar si es enum
        ed = self._enums_disponibles
        if campo.tipo_campo in ed:
            valores_enum = ", ".join(map(repr, ed[campo.tipo_campo].valores))
            tipo_sql = f"ENUM({valores_enum})"

        return tipo_sql

    def _generar_definicion_columna(self, campo: InfoField) -> str:
        """Generar definicion completa de columna."""
        tipo_sql = self._obtener_tipo_sql(campo)

        nombre_columna = campo.nombre

        db = "db" in campo.directivas
        if db and "rename" in campo.directivas["db"].argumentos:
            nombre_columna = campo.directivas["db"].argumentos["rename"]

        definicion = f"`{nombre_columna}` {tipo_sql}"

        # Agregar constrains
        if campo.es_requerido:
            definicion += " NOT NULL"

        if "unique" in campo.directivas:
            definicion += " UNIQUE"

        if "id" in campo.directivas:
            definicion += " PRIMARY KEY"

        df = "default" in campo.directivas
        if df and "value" in campo.directivas["default"].argumentos:
            valor_default = campo.directivas["default"].argumentos["value"]
            lst = ("TEXT", "VARCHAR(255)")
            if tipo_sql in lst or (tipo_sql.startswith("ENUM")):
                definicion += " DEFAULT '"
                definicion += f"{valor_default}'"
            else:
                definicion += f" DEFAULT {valor_default}"

        if "createdAt" in campo.directivas:
            definicion += " DEFAULT CURRENT_TIMESTAMP"

        if "updatedAt" in campo.directivas:
            definicion += " DEFAULT CURRENT_TIMESTAMP "
            definicion += "ON UPDATE CURRENT_TIMESTAMP"

        return definicion

    def _mostrar_inicio_migracion(self, id_migracion: str) -> None:
        """Mostrar inicio de proceso de migracion."""
        self.consola.print(
            f"\n🔄 Generando migracion: {id_migracion}", style="bold blue"
        )

    def _mostrar_diferencias_detectadas(
        self,
        diferencias: InfoDiffEsquema,
    ) -> None:
        """Mostrar diferencias detectadas entre esquemas."""
        tree = Tree("\n📋 Diferencias detectadas", style="bold green")

        # Tablas
        if diferencias.tablas.agregadas:
            tree.add(
                f"➕ Tablas agregadas: {len(diferencias.tablas.agregadas)}",
            )
        if diferencias.tablas.eliminadas:
            tree.add(
                f"➖ Tablas eliminadas: {len(diferencias.tablas.eliminadas)}",
            )

        # Campos
        total_campos_agregados = sum(
            len(c.agregados) for c in diferencias.tablas.campos.values()
        )
        total_campos_eliminados = sum(
            len(c.eliminados) for c in diferencias.tablas.campos.values()
        )
        total_campos_modificados = sum(
            len(c.modificados) for c in diferencias.tablas.campos.values()
        )

        if total_campos_agregados:
            tree.add(f"🔹 Campos agregados: {total_campos_agregados}")
        if total_campos_eliminados:
            tree.add(f"🔹 Campos eliminados: {total_campos_eliminados}")
        if total_campos_modificados:
            tree.add(f"🔹 Campos modificados: {total_campos_modificados}")

        # Relaciones
        df = diferencias.relaciones
        if df.agregadas:
            tree.add(f"🔗 Relaciones agregadas: {len(df.agregadas)}")
        if df.eliminadas:
            tree.add(f"🔗 Relaciones eliminadas: {len(df.eliminadas)}")

        self.consola.print(tree)

    def _mostrar_resumen_migracion(self, num_sentencias: int) -> None:
        """Mostrar resumen final de migracion."""
        self.consola.print(
            "\n✅ Migracion generada exitosamente",
            style="bold green",
        )
        self.consola.print(
            f"📊 Total de sentencias SQL: {num_sentencias}", style="blue"
        )

    def _visualizar_operacion_sql(
        self, tipo_operacion: str, descripcion: str, sql: str
    ) -> None:
        """Visualizar una operacion SQL especifica."""
        if self.visualizar_salida:
            tree = Tree(f"🔧 {tipo_operacion}")
            tree.add(descripcion)
            self.consola.print(tree)

            if self.visualizar_sql:
                syntax = Syntax(sql, "sql", theme="monokai", line_numbers=True)
                self.consola.print(
                    Panel(
                        syntax,
                        title=f"SQL - {tipo_operacion}",
                        border_style="yellow",
                    )
                )

    def _visualizar_obligacion_campo(
        self,
        requerido: bool,
    ):
        """Visualizar si un campo es obligatorio o no."""
        if requerido:
            return ":exclamation_mark:"
        return ":question_mark:"

    def _generar_hash_esquemas(self, esquema1: str, esquema2: str) -> str:
        """Generar hash unico para par de esquemas."""
        contenido = f"{esquema1}{esquema2}"
        return hashlib.md5(contenido.encode("utf-8")).hexdigest()

    def _generar_encabezado_migracion(self) -> List[str]:
        """Generar encabezado de migracion."""
        timestamp = datetime.datetime.now().isoformat()
        return [
            "-- Migracion generada automaticamente",
            f"-- Fecha: {timestamp}",
            "-- GraphQLStore CLI v3.0.0",
            "",
        ]

    def _determinar_tabla_fk(self, relacion: InfoRelacion) -> str:
        """Determinar en qué tabla va la foreign key."""
        if relacion.tipo_relation == TipoRelacion.ONE_TO_MANY.value:
            return (
                relacion.objetivo.tabla_objetivo
                if relacion.fuente.fuente_es_lista
                else relacion.fuente.tabla_fuente
            )

        if relacion.tipo_relation == TipoRelacion.ONE_TO_ONE.value:
            if relacion.fuente.on_delete == OnDelete.CASCADE.value:
                return relacion.fuente.tabla_fuente

            return relacion.objetivo.tabla_objetivo

        return relacion.fuente.tabla_fuente

    def _determinar_campo_fk(self, relacion: InfoRelacion) -> str:
        """Determinar nombre del campo foreign key."""
        campo_fk = relacion.fuente.campo_fuente
        if relacion.tipo_relation == TipoRelacion.ONE_TO_MANY.value:
            campo_fk = (
                relacion.fuente.tabla_fuente.lower()
                if relacion.fuente.fuente_es_lista
                else relacion.fuente.campo_fuente
            )
        else:
            if relacion.fuente.on_delete == OnDelete.CASCADE.value and (
                relacion.objetivo.on_delete_inverso != OnDelete.CASCADE.value
            ):
                campo_fk = (
                    relacion.fuente.campo_fuente
                    if not relacion.objetivo.campo_inverso
                    else relacion.fuente.tabla_fuente.lower()
                )
            elif relacion.fuente.on_delete != OnDelete.CASCADE.value and (
                relacion.objetivo.on_delete_inverso == OnDelete.CASCADE.value
            ):
                if relacion.objetivo.campo_inverso:
                    campo_fk = relacion.objetivo.campo_inverso
                else:
                    campo_fk = relacion.fuente.campo_fuente
        return campo_fk

    def _generar_sql_tabla_junction(self, relacion: InfoRelacion) -> str:
        """Generar SQL para tabla junction (relacion N:M)."""
        tabla_fuente = relacion.fuente.tabla_fuente
        tabla_objetivo = relacion.objetivo.tabla_objetivo
        nombre_junction = relacion.nombre_relacion

        es_auto_relacion = tabla_fuente == tabla_objetivo

        sufijo_fuente = "id" if not es_auto_relacion else "A"
        sufijo_objetivo = "id" if not es_auto_relacion else "B"

        on_delete = (
            OnDelete.SET_NULL.value
            if (relacion.fuente.on_delete == "SET_NULL")
            else OnDelete.CASCADE.value
        )
        reverse_on_delete = (
            OnDelete.SET_NULL.value
            if (relacion.objetivo.on_delete_inverso == "SET_NULL")
            else OnDelete.CASCADE.value
        )

        sql = template_crear_tabla_junction(
            nombre_junction=nombre_junction,
            tabla_fuente=tabla_fuente,
            sufi_f=sufijo_fuente,
            constraint_fuente=relacion.fuente.nombre_constraint_fuente,
            on_delete=on_delete,
            tabla_objetivo=tabla_objetivo,
            sufi_o=sufijo_objetivo,
            constraint_objetivo=relacion.objetivo.nombre_constraint_objetivo,
            reverse_on_delete=reverse_on_delete,
        )

        if self.visualizar_salida:
            self._visualizar_operacion_sql(
                "CREAR TABLA JUNCTION",
                f"Creando tabla junction {nombre_junction} para relacion N:M",
                sql,
            )

        return f"-- Crear tabla junction {nombre_junction}\n{sql}"

    def _generar_sql_foreign_key(self, relacion: InfoRelacion) -> str:
        """Generar SQL para foreign key (relaciones 1:1 y 1:N)."""
        tabla_fk = self._determinar_tabla_fk(relacion)
        campo_fk = self._determinar_campo_fk(relacion)
        tabla_ref = (
            relacion.objetivo.tabla_objetivo
            if tabla_fk == relacion.fuente.tabla_fuente
            else relacion.fuente.tabla_fuente
        )

        # determinar ON DELETE

        actual_on_delete = "SET NULL"
        if relacion.tipo_relation == TipoRelacion.ONE_TO_MANY.value:
            actual_on_delete = relacion.objetivo.on_delete_inverso
        else:
            if relacion.fuente.on_delete == OnDelete.CASCADE.value and (
                relacion.objetivo.on_delete_inverso != OnDelete.CASCADE.value
            ):
                actual_on_delete = relacion.fuente.on_delete
            elif relacion.fuente.on_delete != OnDelete.CASCADE.value and (
                relacion.objetivo.on_delete_inverso == OnDelete.CASCADE.value
            ):
                actual_on_delete = relacion.objetivo.on_delete_inverso

        if actual_on_delete == OnDelete.CASCADE.value:
            accion_on_delete = "ON DELETE CASCADE"
        else:
            accion_on_delete = "ON DELETE SET NULL"

        # determinar si es UNIQUE (para relaciones 1:1)
        rt = relacion.tipo_relation
        unique = " UNIQUE" if rt == TipoRelacion.ONE_TO_ONE.value else ""
        sql = template_modificar_fk(
            tabla_fk=tabla_fk,
            campo_fk=campo_fk,
            unique=unique,
            constraint=relacion.fuente.nombre_constraint_fuente,
            tabla_ref=tabla_ref,
            on_delete=accion_on_delete,
        )

        if self.visualizar_salida:
            self._visualizar_operacion_sql(
                "AGREGAR FOREIGN KEY",
                f"Agregando foreign key {campo_fk}_id en {tabla_fk}",
                sql,
            )

        return f"-- Agregar foreign key {campo_fk}_id en {tabla_fk}\n{sql}"

    def _generar_sql_modificar_enum(
        self,
        enum_modificado: InfoCambioEnum,
    ) -> List[str]:
        """Generar SQL para modificar un enum."""
        sentencias: List[str] = []

        # obtener todas las tablas y campos que usan este enum
        tablas_con_enum = self._buscar_tablas_que_usan_enum(
            enum_modificado.nombre,
        )

        if not tablas_con_enum:
            return sentencias

        # actualizar tablas
        for nom_tabla, campos in tablas_con_enum.items():
            for campo in campos:

                if "default" in campo.directivas:
                    continue

                definicion = self._generar_definicion_columna(
                    campo,
                )

                sql_modify = TEMPLATE_MODIFICAR_CAMPO.format(
                    tabla=nom_tabla,
                    definicion=definicion,
                )

                nom_enum = enum_modificado.nombre
                msg = f"-- Actualizar enum {nom_enum} en {nom_tabla}"
                sentencias.append(f"{msg}\n" f"{sql_modify}")

                if self.visualizar_salida:
                    self._visualizar_operacion_sql(
                        "MODIFICAR ENUM",
                        f"Actualizando enum {nom_enum} en {nom_tabla}",
                        sql_modify,
                    )

        return sentencias

    def _buscar_tablas_que_usan_enum(
        self,
        nombre_enum: str,
    ) -> Dict[str, List[InfoField]]:
        """Buscar todas las tablas y campos que usan un enum específico."""
        tablas_con_enum = {}

        for nombre_tabla, info_tabla in self._tablas_existentes.items():
            campos_con_enum = []

            for campo in info_tabla.campos.values():
                if (
                    self._deberia_procesar_campo(campo)
                    and campo.tipo_campo == nombre_enum
                ):
                    campos_con_enum.append(campo)

            if campos_con_enum:
                tablas_con_enum[nombre_tabla] = campos_con_enum

        return tablas_con_enum

    def _generar_sql_eliminar_tabla(self, nombre_tabla: str) -> str:
        """Generar SQL para eliminar una tabla."""
        sql = TEMPLATE_ELIMINAR_TABLA.format(tabla=nombre_tabla)

        if self.visualizar_salida:
            self._visualizar_operacion_sql(
                "ELIMINAR TABLA", f"Eliminando tabla {nombre_tabla}", sql
            )

        return f"-- Eliminar tabla {nombre_tabla}\n{sql}"
