"""Plantillas  para la generación de código SQL."""

#  TABLAS

from typing import Optional


TEMPLATE_CREAR_TABLA = (
    "CREATE TABLE {nombre_tabla} (\n{columnas}\n) "
    "ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"
)

TEMPLATE_ELIMINAR_TABLA = "DROP TABLE IF EXISTS `{tabla}`;"


def template_crear_tabla_junction(
    nombre_junction: str,
    tabla_fuente: str,
    sufi_f: str,
    constraint_fuente: str,
    on_delete: str,
    tabla_objetivo: str,
    sufi_o: str,
    constraint_objetivo: Optional[str],
    reverse_on_delete: str,
    engine_setting: str = "",
):
    """Genera una plantilla SQL para crear una tabla junction."""
    tablaf = tabla_fuente
    tabla_fuente = tabla_fuente.lower()
    tablao = tabla_objetivo
    tabla_objetivo = tabla_objetivo.lower()
    return (
        f"CREATE TABLE IF NOT EXISTS {nombre_junction} (\n"
        f"  {tabla_fuente}_{sufi_f} VARCHAR(25) NOT NULL,\n"
        f"  {tabla_objetivo}_{sufi_o} VARCHAR(25) NOT NULL,\n"
        f"  PRIMARY KEY({tabla_fuente}_{sufi_f}, {tabla_objetivo}_{sufi_o}),\n"
        f"  CONSTRAINT {constraint_fuente}\n"
        f"    FOREIGN KEY ({tabla_fuente}_{sufi_f})\n"
        f"    REFERENCES {tablaf}(id) ON DELETE {on_delete},\n"
        f"  CONSTRAINT {constraint_objetivo}\n"
        f"    FOREIGN KEY ({tabla_objetivo}_{sufi_o})\n"
        f"    REFERENCES {tablao}(id) ON DELETE {reverse_on_delete}\n"
        f"){engine_setting};"
    )


# CAMPOS


TEMPLATE_AGREGAR_CAMPO = "ALTER TABLE `{tabla}` ADD COLUMN {definicion};"

TEMPLATE_ELIMINAR_CAMPO = "ALTER TABLE `{tabla}` DROP COLUMN `{campo}`;"

TEMPLATE_MODIFICAR_CAMPO = "ALTER TABLE `{tabla}` MODIFY COLUMN {definicion};"

# FOREIGN KEYS

TEMPLATE_AGREGAR_FK = (
    "ALTER TABLE `{tabla}` ADD CONSTRAINT `{constraint}` "
    "FOREIGN KEY (`{campo}`) REFERENCES `{tabla_ref}`(id) {on_delete};"
)

TEMPLATE_ELIMINAR_FK = "ALTER TABLE `{tabla}` DROP FOREIGN KEY `{constraint}`;"


def template_modificar_fk(
    tabla_fk: str,
    campo_fk: str,
    unique: str,
    constraint: str,
    tabla_ref: str,
    on_delete: str,
):
    """Genera una plantilla SQL para modificar una foreign key."""

    return (
        f"ALTER TABLE {tabla_fk}\n"
        f"  ADD COLUMN {campo_fk}_id VARCHAR(25){unique},\n"
        f"  ADD CONSTRAINT {constraint},\n"
        f"      FOREIGN KEY ({campo_fk}_id)"
        f"      REFERENCES {tabla_ref}(id){on_delete};"
    )


# INDEXES
TEMPLATE_AGREGAR_UNIQUE = "UNIQUE KEY `uk_{uk_nom_columna}` (`{nom_columna}`)"
