"""Modulo GeneradorEsquemaMySQL"""

from typing import Dict, List, Optional
from graphql.error import GraphQLError
from graphql.language import parse
from graphql.language.ast import DirectiveNode, FieldDefinitionNode
from graphql.language.printer import print_ast
from graphql.language.visitor import IDLE, REMOVE, Visitor, visit
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.tree import Tree

from .templates import TEMPLATE_AGREGAR_UNIQUE

from .configuracion_y_constantes import (
    InfoEnum,
    InfoRelacion,
    InfoTabla,
    TipoField,
    TipoLink,
    TipoRelacion,
    OnDelete,
)
from .exceptions import RelationshipError
from .parser import ParserGraphQLEsquema


class GeneradorEsquemaMySQL:
    """Clase para generar un esquema de base \
        de datos MySQL a partir de un esquema GraphQL."""

    def __init__(self):
        self.consola = Console()
        self.esquema_mysql = []
        self.visualizar_salida = None
        self.visualizar_sql = None

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def generar_esquema(
        self,
        tablas: Dict[str, InfoTabla],
        enums: Dict[str, InfoEnum],
        relaciones: List[InfoRelacion],
        visualizar_salida: bool = True,
        visualizar_sql: bool = True,
    ) -> str:
        """Generar esquema MySQL desde un esquema GraphQL."""

        esquema_mysql = []

        self.visualizar_salida = visualizar_salida
        self.visualizar_sql = visualizar_sql

        # generar tablas
        tabla_sql = self._generar_tablas(
            tablas,
            enums,
            visualizar_salida,
            visualizar_sql,
        )
        esquema_mysql.append(tabla_sql)

        # generar relaciones
        relaciones_sql = self._generar_relaciones(
            tablas,
            relaciones,
        )
        esquema_mysql.append(relaciones_sql)

        # unir todo el esquema
        esquema_mysql_unido = "\n\n".join(esquema_mysql)

        return esquema_mysql_unido

    def get_esquema_sql(self) -> str:
        """Obtener el esquema SQL generado."""
        return "\n\n".join(self.esquema_mysql)

    def _generar_tablas(
        self,
        tablas: Dict[str, InfoTabla],
        enums: Dict[str, InfoEnum],
        visualizar_salida: bool = True,
        visualizar_sql: bool = True,
    ) -> str:
        """Generar las definiciones de tablas."""

        esquema_tablas = []

        for nombre_tabla, info_tabla in tablas.items():
            tabla_sql = self._generar_tabla(nombre_tabla, info_tabla, enums)

            if tabla_sql:
                esquema_tablas.append(tabla_sql)

                if visualizar_salida:
                    self._visualizar_salida_tablas(
                        nombre_tabla,
                        info_tabla,
                        tabla_sql,
                        visualizar_sql,
                    )

        return "\n\n".join(esquema_tablas)

    def _generar_relaciones(
        self,
        tablas: Dict[str, InfoTabla],
        relaciones: List[InfoRelacion],
    ) -> str:
        """Generar las sentencias SQL para crear las relaciones."""

        esquema_relaciones = []

        for relacion in relaciones:
            relacion_sql = self._generar_relacion(relacion, tablas)

            if relacion_sql:
                # si la relacion no ha sido procesada, agregarla al esquema
                esquema_relaciones.append(relacion_sql)
        return "\n\n".join(esquema_relaciones)

    # pylint: disable=too-many-locals,too-many-branches
    # pylint: disable=too-many-statements
    def _generar_relacion(
        self,
        relacion: InfoRelacion,
        tablas: Dict[str, InfoTabla],
    ) -> Optional[str]:
        """Generar la sentencia SQL para crear una relacion."""

        tablas_juntion_procesados = set()

        # procesar relacion
        tabla_fuente = relacion.fuente.tabla_fuente
        tabla_objetivo = relacion.objetivo.tabla_objetivo
        campo_fuente = relacion.fuente.campo_fuente
        tipo_relacion = relacion.tipo_relation
        tipo_link = relacion.tipo_link
        on_delete = relacion.fuente.on_delete
        on_delete_inverso = relacion.objetivo.on_delete_inverso
        fue_es_list = relacion.fuente.fuente_es_lista
        nombre_relacion = relacion.nombre_relacion
        nom_constraint_fuente = relacion.fuente.nombre_constraint_fuente
        nom_constraint_obj = relacion.objetivo.nombre_constraint_objetivo

        if (
            tipo_relacion == TipoRelacion.MANY_TO_MANY.value
            and tipo_link == TipoLink.TABLE.value
        ):
            # crear tabla junction para relaciones many-to-many
            nombre_junction = nombre_relacion

            # skip if ya ha sido procesado
            if nombre_junction in tablas_juntion_procesados:
                return None

            tablas_juntion_procesados.add(nombre_junction)

            t_fuente = tabla_fuente.lower()
            t_objetivo = tabla_objetivo.lower()

            es_relacion_self = tabla_fuente == tabla_objetivo

            sql = f"CREATE TABLE {nombre_junction} (\n"

            if es_relacion_self:
                sql += f"  `{t_fuente}_A` VARCHAR(25) NOT NULL,\n"
                sql += f"  `{t_fuente}_B` VARCHAR(25) NOT NULL,\n"
                sql += f"  PRIMARY KEY (`{t_fuente}_A`, `{t_fuente}_B`),\n"
                sql += f"  CONSTRAINT `{nom_constraint_fuente}`"
                a = t_fuente + "_A"
                sql += f" FOREIGN KEY (`{a}`) REFERENCES `{tabla_fuente}`(id)"
            else:
                tf_id, to_id = t_fuente + "_id", t_objetivo + "_id"

                sql += f"  `{tf_id}_id` VARCHAR(25) NOT NULL,\n"
                sql += f"  `{to_id}_id` VARCHAR(25) NOT NULL,\n"
                sql += f"  PRIMARY KEY (`{tf_id}`, `{to_id}`),\n"
                sql += f"  CONSTRAINT `{nom_constraint_fuente}`"
                tablaf = tabla_fuente
                sql += f" FOREIGN KEY (`{tf_id}`) REFERENCES `{tablaf}`(id)"

            if on_delete == OnDelete.CASCADE.value:
                sql += " ON DELETE CASCADE,\n"
            else:
                sql += " ON DELETE SET NULL,\n"

            if es_relacion_self:
                sql += f"  CONSTRAINT `{nom_constraint_obj}`"
                sql += (
                    f" FOREIGN KEY (`{t_objetivo}_B`) "
                    f"REFERENCES `{tabla_objetivo}`(id)"
                )
            else:
                sql += f"  CONSTRAINT `{nom_constraint_obj}`"
                sql += (
                    f" FOREIGN KEY (`{t_objetivo}_id`) "
                    f"REFERENCES `{tabla_objetivo}`(id)"
                )

            if (
                relacion.objetivo.campo_inverso
                and "relation"
                in tablas[tabla_objetivo]
                .campos[relacion.objetivo.campo_inverso]
                .directivas
            ):
                on_delete_inverso = (
                    tablas[tabla_objetivo]
                    .campos[relacion.objetivo.campo_inverso]
                    .directivas["relation"]
                    .argumentos.get(
                        "onDelete",
                        "SET_NULL",
                    )
                )

                if on_delete_inverso == "CASCADE":
                    sql += " ON DELETE CASCADE"
                else:
                    sql += " ON DELETE SET NULL"
            else:
                sql += " ON DELETE SET NULL"

            sql += "\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"

            self._visualizar_salida_relaciones(
                relacion=relacion,
                data_sql=sql,
                visualizar_salida=self.visualizar_salida,
                visualizar_sql=self.visualizar_sql,
                nombre_sql=nombre_junction,
            )

            return sql

        if (
            tipo_relacion
            in [
                TipoRelacion.ONE_TO_ONE.value,
                TipoRelacion.ONE_TO_MANY.value,
            ]
            and tipo_link == TipoLink.INLINE.value
        ):
            tabla_fk = None
            tabla_ref = None
            campo_fk = None
            actual_on_delete = None

            if tipo_relacion == TipoRelacion.ONE_TO_MANY.value:
                # si la fuente tiene [Target] entonces la clave
                # foranea va en la tabla objetivo
                tabla_fk = tabla_objetivo
                tabla_ref = tabla_fuente
                campo_fk = tabla_fuente.lower()
                actual_on_delete = on_delete_inverso

            # si es una relacion 1:1, la clave foranea va en el lado
            # del onDelete: CASCADE
            elif (
                on_delete == OnDelete.CASCADE.value
                and on_delete_inverso != OnDelete.CASCADE.value
            ):
                # la fuente tiene CASCADE, target no
                tabla_fk = tabla_fuente
                tabla_ref = tabla_objetivo
                campo_fk = tabla_fuente.lower()
                actual_on_delete = on_delete

                if not relacion.objetivo.campo_inverso:
                    campo_fk = campo_fuente
            elif (
                on_delete != OnDelete.CASCADE.value
                and on_delete_inverso == OnDelete.CASCADE.value
            ):
                # la fuente no tiene CASCADE, target
                if relacion.objetivo.campo_inverso:
                    tabla_fk = tabla_objetivo
                    tabla_ref = tabla_fuente
                    # usamos el  nombre del campo actual
                    # desde la tabla objetivo
                    campo_fk = relacion.objetivo.campo_inverso
                    actual_on_delete = on_delete_inverso
            else:
                # ambos tienen cascade or ninguno has cascade (ambiguidad)
                raise RelationshipError(
                    "Configuracion de relacion ambigua ",
                    f"para {nombre_relacion} Ambos lados ",
                    "tienen onDelete: CASCADE o ninguno lo tiene. ",
                )

            # agregar llave foranea para la tabla que
            # contiene el campo relacion
            sql_alter = f"ALTER TABLE `{tabla_fk}`\n"

            if tipo_relacion == TipoRelacion.ONE_TO_ONE.value:
                sql_alter += f"ADD COLUMN `{campo_fk}_id` VARCHAR(25) UNIQUE"
            else:
                sql_alter += f"ADD COLUMN `{campo_fk}_id` VARCHAR(25)"

            # verificar si el campo es requerido
            es_requerido = False
            if tipo_relacion == TipoRelacion.ONE_TO_MANY.value and fue_es_list:
                # verificar si la referencia del objetivo
                # a la fuente es requerida
                if (
                    relacion.objetivo.campo_inverso
                    and tablas[tabla_objetivo]
                    .campos[relacion.objetivo.campo_inverso]
                    .es_requerido
                ):
                    es_requerido = True
            elif (
                not fue_es_list
                and tablas[tabla_fuente].campos[campo_fuente].es_requerido
            ):
                es_requerido = True

            if es_requerido:
                sql_alter += " NOT NULL"

            sql_alter += ",\n"
            sql_alter += (
                f"ADD CONSTRAINT `{nom_constraint_fuente}` FOREIGN KEY "
                f"(`{campo_fk}_id`) REFERENCES `{tabla_ref}` (id)"
            )

            if actual_on_delete == OnDelete.CASCADE.value:
                sql_alter += " ON DELETE CASCADE;"
            else:
                sql_alter += " ON DELETE SET NULL;"

            self._visualizar_salida_relaciones(
                relacion=relacion,
                data_sql=sql_alter,
                visualizar_salida=self.visualizar_salida,
                visualizar_sql=self.visualizar_sql,
                nombre_sql=tabla_fk,
            )

            return sql_alter
        return None

    # pylint: enable=too-many-arguments,too-many-positional-arguments

    # pylint: disable=too-many-locals,too-many-branches
    def _generar_tabla(
        self,
        nombre_tabla: str,
        info_tabla: InfoTabla,
        enums: Dict[str, InfoEnum],
    ) -> str:
        """Generar la sentencia SQL para crear una tabla."""

        columnas = []
        indices = []
        has_primary_key = False

        tabla_sql = f"CREATE TABLE {nombre_tabla} (\n"

        for nombre_campo, info_campo in info_tabla.campos.items():
            tipo_campo = info_campo.tipo_campo
            directivas = info_campo.directivas

            # skip si no es un campo escalar o enum
            if not TipoField.existe(tipo_campo) and tipo_campo not in enums:
                continue

            nombre_columna = nombre_campo

            if "db" in directivas and "rename" in directivas["db"].argumentos:
                nombre_columna = directivas["db"].argumentos["rename"]

            # definir el tipo de dato sql
            tipo_sql = ParserGraphQLEsquema.get_type_mapping().get(
                tipo_campo,
                "TEXT",
            )
            if tipo_campo in enums:
                # crear tipo ENUM
                valores_enum = ", ".join(
                    [f"'{valor}'" for valor in enums[tipo_campo].valores]
                )
                tipo_sql = f"ENUM({valores_enum})"

            if info_campo.es_lista:
                tipo_sql = "JSON"

            # constuir la definicion de la columna
            def_columna = f"  `{nombre_columna}` {tipo_sql}"

            # agregar NOT NULL si es requerido
            if info_campo.es_requerido:
                def_columna += " NOT NULL"

            if "id" in directivas:
                def_columna += " PRIMARY KEY"
                has_primary_key = True

            dft = "default" in directivas

            if dft and "value" in directivas["default"].argumentos:
                if tipo_sql in ("TEXT", "VARCHAR(255)") or (
                    tipo_sql.startswith("ENUM")
                ):
                    def_columna += " DEFAULT '"
                    valor_default = directivas["default"].argumentos["value"]
                    def_columna += f"{valor_default}'"
                else:
                    def_columna += (
                        f" DEFAULT {directivas['default'].argumentos['value']}"
                    )

            if "createdAt" in directivas:
                def_columna += " DEFAULT CURRENT_TIMESTAMP"

            if "updatedAt" in directivas:
                def_columna += " DEFAULT CURRENT_TIMESTAMP "
                def_columna += "ON UPDATE CURRENT_TIMESTAMP"

            columnas.append(def_columna)

            if "unique" in directivas:
                sql = TEMPLATE_AGREGAR_UNIQUE.format(
                    uk_nom_columna=nombre_columna,
                    nom_columna=nombre_columna,
                )
                indices.append(sql)

        if not has_primary_key:
            columnas.insert(0, "  `id` VARCHAR(25) NOT NULL PRIMARY KEY")

        tabla_sql += ",\n".join(columnas)
        if indices:
            tabla_sql += ",\n" + ",\n".join(indices)
        tabla_sql += "\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"

        self.esquema_mysql.append(tabla_sql)

        return tabla_sql

    # pylint: enable=too-many-locals,too-many-branches

    def _visualizar_salida_tablas(
        self,
        nom_tabla: str,
        info_tabla: InfoTabla,
        tabla_sql: str,
        visualizar_sql: bool = True,
    ) -> None:
        """Visualizar la salida del esquema generado."""

        tree_tabla = Tree(
            "\n [bold green]Creating Type " f"[magenta]{nom_tabla}[/magenta]"
        )

        for nombre_campo, info_campo in info_tabla.campos.items():
            tree_tabla.add(
                f"Creando tipo [magenta]{nombre_campo}[/magenta] "
                f"de tipo [magenta]{info_campo.tipo_campo}"
            )

        self.consola.print(tree_tabla)

        if visualizar_sql:
            syntax = Syntax(
                tabla_sql,
                "sql",
                theme="monokai",
                line_numbers=True,
            )
            msg_sql = f"SQL para la tabla {nom_tabla}"
            self.consola.print(
                Panel(syntax, title=msg_sql, border_style="blue"),
            )

        msg = f"Type `{nom_tabla}` created successfully :white_check_mark:"
        self.consola.print(msg, style="bold green")

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def _visualizar_salida_relaciones(
        self,
        relacion: InfoRelacion,
        data_sql: str,
        visualizar_salida: bool = True,
        visualizar_sql: bool = True,
        nombre_sql: str | None = None,
    ) -> None:
        """Visualizar la salida de las relaciones generadas."""

        if visualizar_salida:
            fuente = relacion.fuente.tabla_fuente
            objetivo = relacion.objetivo.tabla_objetivo
            if relacion.tipo_relation == TipoRelacion.MANY_TO_MANY.value:
                msg_relacion = (
                    f"[bold magenta]{fuente}[/bold magenta] - "
                    f"[bold magenta]{objetivo}[/bold magenta]"
                )
                titulo_sql = f"SQL para la tabla junction {nombre_sql}"
            else:
                msg_relacion = (
                    f"[bold magenta]{fuente}[/bold magenta] agregar a "
                    f"[bold magenta]{objetivo}[/bold magenta] "
                )
                titulo_sql = f"SQL para la relacion en {nombre_sql}"

            tree = Tree(
                "\n [bold green] Creando relacion"
                f"([magenta]{relacion.tipo_relation}[/magenta]) "
                f"{msg_relacion}[/bold green]"
            )
            self.consola.print(tree)

            if visualizar_sql:
                syntax = Syntax(
                    data_sql,
                    "sql",
                    theme="monokai",
                    line_numbers=True,
                )
                self.consola.print(
                    Panel(
                        syntax,
                        title=titulo_sql,
                        border_style="yellow",
                    )
                )

            msg = (
                f"Relacion [magenta]{fuente}[/magenta] - "
                f"[magenta]{objetivo}[/magenta] "
                "creada correctamente :white_check_mark:"
            )
            self.consola.print(msg, style="bold green")

    # pylint: enable=too-many-arguments,too-many-positional-arguments

    def transformar_esquema_graphql(self, schema: str) -> str:
        """Transformar esquema graphql para esquema cliente."""
        try:
            ast = parse(schema)

            class RemoveDirectivesVisitor(Visitor):
                """Remover directiva visitor del ast y campos protegidos."""

                def enter(self, node, *_):
                    """Entrar nodo en el traversal"""
                    if isinstance(node, DirectiveNode):
                        return REMOVE

                    # remover campo
                    if isinstance(node, FieldDefinitionNode):
                        for directive in node.directives:
                            if directive.name.value == "protected":
                                return REMOVE

                    return IDLE

            new_ast = visit(ast, RemoveDirectivesVisitor())

            return print_ast(new_ast)
        except GraphQLError as e:
            raise ValueError(f"Error al transformar esquema: {str(e)}") from e
