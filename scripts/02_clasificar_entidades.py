#!/usr/bin/env python3
"""
Clasifica cada entidad acreedora en dos taxonomias paralelas.

1. REGIMEN DE INSCRIPCION (normativo, deducible del codigo de entidad)
   Es objetivo: surge del codigo que el BCRA asigna segun la ley bajo la cual
   la entidad reporta. No admite discrecionalidad.

2. CATEGORIA COMERCIAL (analitica, segun modelo de negocio)
   Es una construccion del autor. Cruza regimenes: "Fintech" incluye entidades
   inscriptas como banco (Uala), como compania financiera (Naranja X) y como
   proveedor no financiero (Mercado Pago).

Criterio de la categoria comercial, en orden de prioridad:
   1. SGR o fondo de garantia            -> por razon social
   2. Retail identificado                 -> por listado explicito
   3. Fideicomiso con mora >= 95%         -> compra de carteras
   4. Mora 100% en monto Y en personas    -> compra de carteras
   5. Fintech verificable (app/billetera) -> por listado explicito
   6. Emisor verificable de plastico      -> por listado explicito
   7. Resto                               -> credito rapido de alto riesgo

La regla 7 es deliberada: ante la duda sobre el modelo de negocio, la entidad
va a credito rapido. Esto evita inflar artificialmente las categorias de fintech
y tarjetas con entidades que solo comparten el nombre.

Uso:
    python 02_clasificar_entidades.py --zip /ruta/a/deudores.zip
"""

import argparse
import csv
import pickle
import zipfile

# --- Listados explicitos ----------------------------------------------------
# Estos listados son juicio del autor y son el punto mas discutible del trabajo.
# Se publican para que puedan ser auditados y corregidos.

FINTECH = {
    "72634",  # MercadoLibre S.R.L. (Mercado Pago)
    "45030",  # Naranja Digital Compania Financiera S.A.U. (Naranja X)
    "00384",  # Uala Bank S.A.U.
    "55085",  # Moni Online S.A.
    "55166",  # Waynicoin S.A.
    "55312",  # Aban Digital S.A.
    "45072",  # Reba Compania Financiera S.A.
    "55386",  # Wibond
}

TARJETA_NO_BANCARIA = {
    "70408", "70224", "70248", "71402", "70301", "70424",
    "72304", "70252", "55514", "70210", "70234", "71101",
    "55213", "45056",
}

RETAIL = {
    "55027", "70147", "55041", "55011", "72308", "70805",
    "55034", "55132", "55336", "55090", "70140", "55092",
    "55030", "55100", "55015", "55134", "72613", "55009", "55068",
}

FINANCIERA_DE_MARCA = {
    "44092", "44093", "44094", "44095", "44096",
    "44098", "44099", "44088", "55319", "55408",
}

BANCOS_PROVINCIALES = {
    "00014", "00020", "00029", "00045", "00065", "00083",
    "00086", "00093", "00094", "00097", "00268", "00309",
    "00311", "00315", "00321", "00330",
}

BANCO_NACION = "00011"

UMBRAL_FIDEICOMISO = 0.95
UMBRAL_CARTERA_COMPRADA = 0.995


def regimen_inscripcion(codigo):
    """Deducido del codigo de entidad. Objetivo, no discrecional."""
    p = codigo[:2]
    if p == "00":
        return "Entidades Financieras - Bancos"
    if p in ("44", "45", "65"):
        return "Entidades Financieras - Companias Financieras y Cajas de Credito"
    if p == "10":
        return "Fideicomisos Financieros"
    if p == "50":
        return "SGR"
    if p == "51":
        return "Fondos de Garantia Publicos"
    if p == "40":
        return "Plataformas de Credito entre Particulares"
    return "Proveedores No Financieros de Credito"


def es_sgr(nombre):
    u = nombre.upper()
    return "SGR" in u or "S.G.R" in u or "GARANT" in u


def es_fideicomiso(nombre):
    u = nombre.upper().replace(".", "").strip()
    return u.startswith("FF") or "FIDEICOMISO" in u or "RECUPERO" in u


def categoria_comercial(codigo, nombre, tasa_monto, tasa_personas):
    if codigo == BANCO_NACION:
        return "Banco Nacion"
    if codigo in BANCOS_PROVINCIALES:
        return "Bancos Provinciales"
    if codigo in FINANCIERA_DE_MARCA:
        return "Financieras de Marca / Prendarias"
    if es_sgr(nombre):
        return "SGR y Fondos de Garantia"
    if codigo in RETAIL:
        return "Vendedores de Electrodomesticos y Retail"
    if es_fideicomiso(nombre) and tasa_monto >= UMBRAL_FIDEICOMISO:
        return "Compra de Carteras en Mora"
    if tasa_monto >= UMBRAL_CARTERA_COMPRADA and tasa_personas >= UMBRAL_CARTERA_COMPRADA:
        return "Compra de Carteras en Mora"
    if codigo in FINTECH:
        return "Fintech y Billeteras"
    if codigo in TARJETA_NO_BANCARIA:
        return "Tarjetas de Credito No Bancarias"
    if codigo.startswith("00"):
        return "Bancos Privados"
    return "Empresas Credito Rapido Alto Riesgo"


def cargar_maestro(ruta_zip, nombre="Maeent.txt"):
    """El maestro viene en latin-1, no en UTF-8."""
    maestro = {}
    with zipfile.ZipFile(ruta_zip, "r") as z:
        with z.open(nombre) as f:
            texto = f.read().decode("latin-1")
    for linea in texto.split("\n"):
        if len(linea) >= 75:
            codigo = linea[:5].strip()
            razon_social = linea[5:75].strip()
            if codigo and razon_social:
                maestro.setdefault(codigo, razon_social)
    return maestro


def main(ruta_zip):
    maestro = cargar_maestro(ruta_zip)
    with open("agregados_por_entidad.pkl", "rb") as f:
        agregados = pickle.load(f)

    filas, excluidas = [], []
    for codigo, a in agregados.items():
        nombre = maestro.get(codigo, f"[sin nombre] {codigo}")

        # Entidades que informan cartera o deudores en cero: no clasificables.
        if a["monto_total"] <= 0 or a["registros_total"] <= 0:
            excluidas.append((codigo, nombre))
            continue

        tm = a["monto_mora"] / a["monto_total"]
        tp = a["registros_mora"] / a["registros_total"]

        filas.append({
            "codigo_entidad": codigo,
            "entidad": nombre,
            "categoria_comercial": categoria_comercial(codigo, nombre, tm, tp),
            "regimen_inscripcion": regimen_inscripcion(codigo),
            "monto_mora": round(a["monto_mora"]),
            "monto_cartera": round(a["monto_total"]),
            "tasa_mora_monto_pct": round(tm * 100, 2),
            "personas_mora": a["registros_mora"],
            "personas_cartera": a["registros_total"],
            "tasa_mora_personas_pct": round(tp * 100, 2),
            "credito_promedio_mora": (round(a["monto_mora"] / a["registros_mora"])
                                      if a["registros_mora"] else ""),
        })

    filas.sort(key=lambda r: -r["monto_mora"])

    with open("entidades-clasificadas.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)

    with open("entidades-excluidas.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["codigo_entidad", "entidad", "motivo"])
        for codigo, nombre in sorted(excluidas):
            w.writerow([codigo, nombre, "informa cartera y/o personas en cero"])

    print(f"Clasificadas: {len(filas)} entidades")
    print(f"Excluidas:    {len(excluidas)} entidades")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--zip", required=True)
    args = ap.parse_args()
    main(args.zip)
