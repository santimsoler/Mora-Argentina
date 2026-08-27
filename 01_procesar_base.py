#!/usr/bin/env python3
"""
Procesa la base completa de la Central de Deudores del BCRA.

Lee el archivo de ancho fijo `deudores.txt` (dentro del ZIP descargado del BCRA)
y produce dos salidas intermedias:

  - agregados_por_entidad.pkl : monto y cantidad de registros, en mora y totales,
                                agrupados por codigo de entidad.
  - personas_unicas.pkl       : conteo de personas unicas (deduplicado por CUIT),
                                total del sistema y por entidad.

La distincion entre ambas salidas es la clave metodologica del trabajo: la Central
registra RELACIONES deudor-entidad, no personas. Sumar registros sobreestima la
cantidad de deudores en aproximadamente 1,7 veces.

Uso:
    python 01_procesar_base.py --zip /ruta/a/deudores.zip

Requisitos: numpy
Tiempo aproximado: 3-5 minutos para ~41 millones de registros.
"""

import argparse
import pickle
import time
import zipfile
from collections import defaultdict

import numpy as np

# --- Layout del archivo (posiciones de ancho fijo, base 0) -------------------
# Ver "LEAME DEUDORES.pdf" incluido en la descarga del BCRA.
POS_ENTIDAD = (0, 5)
POS_IDENTIF = (13, 24)   # CUIT / CUIL / CDI del deudor
POS_SITUAC = (27, 29)    # 1 a 5, o 9 = no aplicable
POS_MONTO = (29, 41)     # en miles de pesos, coma decimal

# Situaciones consideradas irregulares:
#   3 = con problemas / riesgo medio
#   4 = con alto riesgo de insolvencia
#   5 = irrecuperable
SITUACION_MORA_DESDE = 3

LONGITUD_MINIMA = 41
MAX_REGISTROS = 45_000_000


def parsear_monto(texto):
    """El monto viene en miles de pesos con coma decimal. Devuelve pesos."""
    texto = texto.strip()
    if not texto:
        return 0.0
    try:
        return float(texto.replace(",", ".")) * 1000
    except ValueError:
        return 0.0


def procesar(ruta_zip, nombre_interno="deudores.txt"):
    entidades = defaultdict(
        lambda: {"monto_mora": 0.0, "monto_total": 0.0,
                 "registros_mora": 0, "registros_total": 0}
    )

    cuits = np.zeros(MAX_REGISTROS, dtype=np.int64)
    en_mora = np.zeros(MAX_REGISTROS, dtype=bool)

    n = 0
    descartados = 0
    inicio = time.time()

    with zipfile.ZipFile(ruta_zip, "r") as z:
        with z.open(nombre_interno) as f:
            for crudo in f:
                linea = crudo.decode("utf-8", errors="ignore")
                if len(linea) < LONGITUD_MINIMA:
                    descartados += 1
                    continue

                codigo = linea[POS_ENTIDAD[0]:POS_ENTIDAD[1]].strip()
                identif = linea[POS_IDENTIF[0]:POS_IDENTIF[1]].strip()
                situac = linea[POS_SITUAC[0]:POS_SITUAC[1]].strip()
                monto = parsear_monto(linea[POS_MONTO[0]:POS_MONTO[1]])

                if not identif.isdigit():
                    descartados += 1
                    continue

                mora = situac.isdigit() and int(situac) >= SITUACION_MORA_DESDE

                e = entidades[codigo]
                e["monto_total"] += monto
                e["registros_total"] += 1
                if mora:
                    e["monto_mora"] += monto
                    e["registros_mora"] += 1

                cuits[n] = int(identif)
                en_mora[n] = mora
                n += 1

                if n % 5_000_000 == 0:
                    print(f"  {n:,} registros ({time.time() - inicio:.0f}s)")

    cuits = cuits[:n]
    en_mora = en_mora[:n]

    personas_total = len(np.unique(cuits))
    personas_mora = len(np.unique(cuits[en_mora]))
    registros_mora = int(en_mora.sum())

    print(f"\nProcesados {n:,} registros en {time.time() - inicio:.0f}s "
          f"({descartados:,} descartados)")
    print(f"Entidades: {len(entidades)}")
    print(f"\nRegistros en mora (relaciones): {registros_mora:,}")
    print(f"Personas unicas en mora:        {personas_mora:,}")
    print(f"Factor de sobreconteo:          {registros_mora / personas_mora:.2f}x")
    print(f"Tasa de mora sobre personas:    {personas_mora / personas_total * 100:.1f}%")

    with open("agregados_por_entidad.pkl", "wb") as f:
        pickle.dump(dict(entidades), f)

    with open("personas_unicas.pkl", "wb") as f:
        pickle.dump({"cuits": cuits, "en_mora": en_mora,
                     "personas_total": personas_total,
                     "personas_mora": personas_mora}, f)

    print("\nSalidas: agregados_por_entidad.pkl, personas_unicas.pkl")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--zip", required=True, help="ruta al ZIP descargado del BCRA")
    ap.add_argument("--archivo", default="deudores.txt",
                    help="nombre del archivo dentro del ZIP")
    args = ap.parse_args()
    procesar(args.zip, args.archivo)
