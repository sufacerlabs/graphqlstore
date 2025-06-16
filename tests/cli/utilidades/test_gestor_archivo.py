"""Pruebas para GestorArchivo"""

import os
import tempfile
from pathlib import Path
from source.cli.utilidades.gestor_archivo import GestorArchivo


def test_leer_archivo_exitoso():
    """Prueba de lectura exitosa de un archivo"""
    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, encoding="utf-8"
    ) as archivo_temp:
        contenido_test = "Contenido de prueba"
        archivo_temp.write(contenido_test)
        archivo_temp.flush()

        try:
            resultado = GestorArchivo.leer_archivo(Path(archivo_temp.name))
            assert resultado == contenido_test
        finally:
            os.unlink(archivo_temp.name)


def test_escribir_archivo_nuevo():
    """Prueba de escritura en un archivo nuevo"""
    with tempfile.TemporaryDirectory() as dir_temp:
        archivo_test = Path(dir_temp) / "test_file.txt"
        contenido_test = "Contenido de prueba"

        GestorArchivo.escribir_archivo(contenido_test, archivo_test)

        # verificar que el archivo fue creado
        # y contiene el contenido esperado
        assert archivo_test.exists()
        with open(archivo_test, "r", encoding="utf-8") as f:
            assert f.read() == contenido_test


def test_asegurar_dir_existe_crear_nuevo():
    """Prueba de creación de un nuevo directorio"""
    with tempfile.TemporaryDirectory() as dir_temp:
        nuevo_dir = Path(dir_temp) / "nuevo_directorio"

        # verificar que el directorio no existe inicialmente
        assert not nuevo_dir.exists()

        GestorArchivo.asegurar_dir_existe(nuevo_dir)

        # verificar que el directorio fue creado
        assert nuevo_dir.exists()
        assert nuevo_dir.is_dir()


def test_asegurar_dir_existe_ya_existe():
    """Prueba para asegurar que un directorio \
        ya existe"""

    with tempfile.TemporaryDirectory() as dir_temp:
        directorio_existente = Path(dir_temp)

        # verificar que el directorio ya existe
        assert directorio_existente.exists()

        # no debería lanzar ningún error
        GestorArchivo.asegurar_dir_existe(directorio_existente)

        # debe seguir existiendo
        assert directorio_existente.exists()
        assert directorio_existente.is_dir()
