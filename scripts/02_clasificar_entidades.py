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
   1. Banco Nacion
   2. Bancos provinciales            -> listado explicito
   3. Financieras de marca            -> listado explicito
   4. SGR o fondo de garantia         -> por razon social
   5. Retail identificado             -> listado explicito
   6. Fideicomiso con mora >= 95%     -> compra de carteras
   7. Mora 100% en monto Y personas   -> compra de carteras
   8. Fintech verificable             -> listado explicito
   9. Emisor verificable de plastico  -> listado explicito
  10. Codigo 00xxx restante           -> bancos privados
  11. Resto                           -> credito rapido de alto riesgo

La regla 11 es deliberada: ante la duda sobre el modelo de negocio, la entidad
va a credito rapido. Esto evita inflar las categorias de fintech y tarjetas con
entidades que solo comparten el nombre comercial.

IMPORTANTE: la categoria se fija con el PRIMER mes en que aparece la entidad y
se mantiene en los meses siguientes. Evaluarla mes a mes haria que una entidad
saltara de categoria al cruzar el umbral de las reglas 6 y 7, rompiendo la
comparabilidad de la serie.

Uso:
    python scripts/02_clasificar_entidades.py maestro.pkl d06.pkl d07.pkl d08.pkl
"""

import pickle
import sys
from collections import Counter

# --- Listados explicitos -----------------------------------------------------
# Son juicio del autor y el punto mas discutible del trabajo. Se publican para
# que puedan ser auditados y corregidos.

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

ORDEN = [
    "Banco Nación", "Bancos Provinciales", "Bancos Privados",
    "Fintech y Billeteras", "Tarjetas de Crédito No Bancarias",
    "Vendedores de Electrodomésticos y Retail",
    "Empresas Crédito Rápido Alto Riesgo",
    "Financieras de Marca / Prendarias",
    "SGR y Fondos de Garantía", "Compra de Carteras en Mora",
]


def regimen(codigo):
    """Deducido del codigo de entidad. Objetivo, no discrecional."""
    p = codigo[:2]
    if p == "00":
        return "Entidades Financieras - Bancos"
    if p in ("44", "45", "65"):
        return "Entidades Financieras - Companias Financieras"
    if p == "10":
        return "Fideicomisos Financieros"
    if p == "50":
        return "SGR"
    if p == "51":
        return "Fondos de Garantia Publicos"
    if p == "40":
        return "Plataformas P2P"
    return "Proveedores No Financieros de Credito"


def es_sgr(nombre):
    u = nombre.upper()
    return "SGR" in u or "S.G.R" in u or "GARANT" in u


def es_fideicomiso(nombre):
    u = nombre.upper().replace(".", "").strip()
    return u.startswith("FF") or "FIDEICOMISO" in u or "RECUPERO" in u


def categoria(codigo, nombre, tasa_monto, tasa_personas):
    if codigo == BANCO_NACION:
        return "Banco Nación"
    if codigo in BANCOS_PROVINCIALES:
        return "Bancos Provinciales"
    if codigo in FINANCIERA_DE_MARCA:
        return "Financieras de Marca / Prendarias"
    if es_sgr(nombre):
        return "SGR y Fondos de Garantía"
    if codigo in RETAIL:
        return "Vendedores de Electrodomésticos y Retail"
    if es_fideicomiso(nombre) and tasa_monto >= UMBRAL_FIDEICOMISO:
        return "Compra de Carteras en Mora"
    if tasa_monto >= UMBRAL_CARTERA_COMPRADA and tasa_personas >= UMBRAL_CARTERA_COMPRADA:
        return "Compra de Carteras en Mora"
    if codigo in FINTECH:
        return "Fintech y Billeteras"
    if codigo in TARJETA_NO_BANCARIA:
        return "Tarjetas de Crédito No Bancarias"
    if codigo.startswith("00"):
        return "Bancos Privados"
    return "Empresas Crédito Rápido Alto Riesgo"


def clasificar(maestro, meses):
    """meses: lista de dicts de 01_procesar_mes.py, en orden cronologico."""
    cat = {}
    for mes in meses:
        for codigo, d in mes["entidades"].items():
            if codigo in cat:
                continue                      # ya fijada por un mes anterior
            nombre = maestro.get(codigo, f"[{codigo}]")
            tm = d["f_mm"] / d["f_mc"] if d["f_mc"] else 0
            tp = d["f_pm"] / d["f_pc"] if d["f_pc"] else 0
            cat[codigo] = categoria(codigo, nombre, tm, tp)
    return cat


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    maestro = pickle.load(open(sys.argv[1], "rb"))
    meses = [pickle.load(open(f, "rb")) for f in sys.argv[2:]]
    cat = clasificar(maestro, meses)
    pickle.dump(cat, open("categorias.pkl", "wb"))
    print(f"Entidades clasificadas: {len(cat)}\n")
    for c, n in sorted(Counter(cat.values()).items(), key=lambda x: ORDEN.index(x[0])):
        print(f"  {c:<44} {n:>4}")
