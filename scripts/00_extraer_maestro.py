#!/usr/bin/env python3
"""
Extrae el maestro de entidades (Maeent.txt) desde el .7z mensual del BCRA.

El maestro asocia cada codigo de entidad con su razon social. Viene codificado
en LATIN-1, no en UTF-8: leerlo como UTF-8 devuelve un maestro vacio o
corrupto, que es el error mas facil de cometer con esta base.

Uso:
    python scripts/00_extraer_maestro.py /ruta/202608DEUDORES.7Z maestro.pkl

Para unificar varios meses (el padron cambia mes a mes), ejecutarlo sobre cada
archivo y combinar los diccionarios: el del mes mas reciente tiene prioridad.
"""

import ctypes
import pickle
import sys

ANCHO_CODIGO = 5
ANCHO_LINEA_MINIMO = 75


def abrir_archivo_interno(ruta, sufijo):
    """Posiciona un lector de libarchive en la primera entrada que termina en `sufijo`."""
    lib = ctypes.CDLL("libarchive.so.13")
    lib.archive_read_new.restype = ctypes.c_void_p
    lib.archive_read_support_filter_all.argtypes = [ctypes.c_void_p]
    lib.archive_read_support_format_all.argtypes = [ctypes.c_void_p]
    lib.archive_read_open_filename.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t]
    lib.archive_read_next_header.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
    lib.archive_entry_pathname.argtypes = [ctypes.c_void_p]
    lib.archive_entry_pathname.restype = ctypes.c_char_p
    lib.archive_read_data.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]
    lib.archive_read_data.restype = ctypes.c_ssize_t

    a = lib.archive_read_new()
    lib.archive_read_support_filter_all(a)
    lib.archive_read_support_format_all(a)
    if lib.archive_read_open_filename(a, ruta.encode(), 1024 * 1024) != 0:
        raise RuntimeError(f"no se pudo abrir {ruta}")
    ent = ctypes.c_void_p()
    while lib.archive_read_next_header(a, ctypes.byref(ent)) == 0:
        if lib.archive_entry_pathname(ent).decode("latin-1").endswith(sufijo):
            return lib, a
    raise RuntimeError(f"{sufijo} no esta dentro de {ruta}")


def extraer_maestro(ruta):
    lib, a = abrir_archivo_interno(ruta, "Maeent.txt")
    buf = ctypes.create_string_buffer(4 * 1024 * 1024)
    datos = b""
    while True:
        n = lib.archive_read_data(a, buf, len(buf))
        if n <= 0:
            break
        datos += buf.raw[:n]

    maestro = {}
    for linea in datos.decode("latin-1").split("\n"):   # latin-1, no UTF-8
        if len(linea) >= ANCHO_LINEA_MINIMO:
            codigo = linea[:ANCHO_CODIGO].strip()
            razon_social = linea[ANCHO_CODIGO:ANCHO_LINEA_MINIMO].strip()
            if codigo and razon_social:
                maestro.setdefault(codigo, razon_social)
    return maestro


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    m = extraer_maestro(sys.argv[1])
    pickle.dump(m, open(sys.argv[2], "wb"))
    print(f"{sys.argv[2]}: {len(m)} entidades")
