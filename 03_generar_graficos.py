#!/usr/bin/env python3
"""
Genera los graficos del articulo como SVG independientes, a partir de los CSV
de la carpeta datos/.

Los SVG son autocontenidos, sin dependencias externas ni fuentes remotas, y
escalan sin perdida. Se pueden abrir en un navegador, insertar en un documento
o convertir a PNG.

Uso:
    python scripts/03_generar_graficos.py

Salida: graficos/*.svg

No requiere librerias externas.
"""

import csv
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "datos"
SALIDA = RAIZ / "graficos"

TINTA = "#0B2239"
GRIS = "#5C6E7E"
REGLA = "#C7D2DA"
VERDE = "#12695F"
ORO = "#B07C1E"
LADRILLO = "#A33B22"

ANCHO_BARRA = 600
FUENTE = "Helvetica, Arial, sans-serif"
FUENTE_MONO = "'IBM Plex Mono', 'DejaVu Sans Mono', monospace"


def color_por_valor(pct):
    if pct >= 35:
        return LADRILLO
    if pct >= 20:
        return ORO
    return VERDE


def barras_horizontales(titulo, subtitulo, items, maximo, nota="", archivo="grafico.svg"):
    """items: lista de (etiqueta, valor_pct, color_opcional)"""
    alto_fila = 44
    alto = 70 + len(items) * alto_fila + (60 if nota else 40)
    y0 = 68

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 {alto}" '
         f'font-family="{FUENTE}">']
    p.append(f'<rect width="760" height="{alto}" fill="#FFFFFF"/>')
    p.append(f'<text x="0" y="22" font-size="17" font-weight="700" fill="{TINTA}">{titulo}</text>')
    p.append(f'<text x="0" y="42" font-size="11.5" fill="{GRIS}" '
             f'font-family="{FUENTE_MONO}">{subtitulo}</text>')

    # grilla
    paso = 10
    v = 0
    while v <= maximo:
        x = v / maximo * ANCHO_BARRA
        p.append(f'<line x1="{x:.0f}" y1="{y0 - 8}" x2="{x:.0f}" '
                 f'y2="{y0 + len(items) * alto_fila - 10}" stroke="{REGLA}" '
                 f'stroke-width="1" stroke-dasharray="2 4"/>')
        p.append(f'<text x="{x:.0f}" y="{y0 + len(items) * alto_fila + 8}" font-size="10" '
                 f'fill="{GRIS}" font-family="{FUENTE_MONO}" text-anchor="middle">{v}%</text>')
        v += paso

    for i, item in enumerate(items):
        etiqueta, valor = item[0], item[1]
        color = item[2] if len(item) > 2 else color_por_valor(valor)
        y = y0 + i * alto_fila
        ancho = valor / maximo * ANCHO_BARRA
        p.append(f'<text x="0" y="{y}" font-size="12.5" font-weight="500" '
                 f'fill="{TINTA}">{etiqueta}</text>')
        p.append(f'<rect x="0" y="{y + 6}" width="{ancho:.1f}" height="16" fill="{color}"/>')
        p.append(f'<text x="{ancho + 8:.1f}" y="{y + 19}" font-size="12" font-weight="600" '
                 f'fill="{color}" font-family="{FUENTE_MONO}">'
                 f'{valor:.1f}%'.replace(".", ",") + '</text>')

    if nota:
        p.append(f'<text x="0" y="{alto - 14}" font-size="10.5" fill="{GRIS}" '
                 f'font-family="{FUENTE_MONO}">{nota}</text>')

    p.append("</svg>")
    (SALIDA / archivo).write_text("\n".join(p), encoding="utf-8")
    print(f"  {archivo}")


def leer(nombre):
    with open(DATOS / nombre, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def g1_doble_contabilizacion():
    alto = 210
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 {alto}" '
         f'font-family="{FUENTE}"><rect width="760" height="{alto}" fill="#FFFFFF"/>']
    p.append(f'<text x="0" y="22" font-size="17" font-weight="700" fill="{TINTA}">'
             f'Diez millones de registros, seis millones de personas</text>')
    p.append(f'<text x="0" y="42" font-size="11.5" fill="{GRIS}" font-family="{FUENTE_MONO}">'
             f'Situacion irregular (3, 4 y 5) — junio 2026</text>')

    p.append(f'<text x="0" y="80" font-size="12.5" fill="{TINTA}">'
             f'Registros deudor-entidad en mora</text>')
    p.append(f'<rect x="0" y="88" width="600" height="30" fill="{LADRILLO}" opacity="0.28"/>')
    p.append(f'<rect x="0" y="88" width="600" height="30" fill="none" stroke="{LADRILLO}" '
             f'stroke-width="1.5"/>')
    p.append(f'<text x="610" y="108" font-size="12.5" font-weight="600" fill="{LADRILLO}" '
             f'font-family="{FUENTE_MONO}">10.039.067</text>')

    p.append(f'<text x="0" y="148" font-size="12.5" fill="{TINTA}">'
             f'Personas humanas unicas en mora</text>')
    p.append(f'<rect x="0" y="156" width="351" height="30" fill="{VERDE}"/>')
    p.append(f'<text x="361" y="176" font-size="12.5" font-weight="600" fill="{VERDE}" '
             f'font-family="{FUENTE_MONO}">5.875.113</text>')
    p.append(f'<line x1="351" y1="84" x2="351" y2="192" stroke="{TINTA}" stroke-width="1" '
             f'stroke-dasharray="3 3"/>')
    p.append(f'<text x="0" y="{alto - 8}" font-size="10.5" fill="{GRIS}" '
             f'font-family="{FUENTE_MONO}">La diferencia son personas contadas una vez por '
             f'cada entidad a la que le deben</text>')
    p.append("</svg>")
    (SALIDA / "01-doble-contabilizacion.svg").write_text("\n".join(p), encoding="utf-8")
    print("  01-doble-contabilizacion.svg")


def g2_por_categoria():
    filas = leer("resumen-por-categoria-comercial.csv")
    excluir = {"Compra de Carteras en Mora", "SGR y Fondos de Garantia",
               "SGR y Fondos de Garantía"}
    items = []
    for r in filas:
        c = r["categoria"]
        if c.startswith("TOTAL") or c in excluir or not r["ph_tasa_mora_monto_pct"]:
            continue
        items.append((c, float(r["ph_tasa_mora_monto_pct"])))
    items.sort(key=lambda x: -x[1])
    barras_horizontales(
        "Tasa de mora por tipo de prestamista",
        "Solo personas humanas · monto irregular sobre monto prestado · junio 2026",
        items, 50,
        "Se excluyen fideicomisos de recupero y SGR: sus tasas no miden desempeno crediticio",
        "02-mora-por-categoria.svg")


def g3_por_regimen():
    filas = leer("resumen-por-regimen-inscripcion.csv")
    orden = ["Entidades Financieras - Bancos",
             "Entidades Financieras - Companias Financieras",
             "Proveedores No Financieros de Credito"]
    items = []
    for nombre in orden:
        for r in filas:
            if r["regimen_inscripcion"] == nombre and r["ph_tasa_mora_monto_pct"]:
                items.append((nombre.replace("Entidades Financieras - ", ""),
                              float(r["ph_tasa_mora_monto_pct"])))
    barras_horizontales(
        "Tasa de mora segun regimen de inscripcion ante el BCRA",
        "Solo personas humanas · junio 2026",
        items, 40,
        "Los proveedores no financieros no tienen exigencia de capital ni previsionamiento prudencial",
        "03-mora-por-regimen.svg")


def g4_mercado_pago():
    filas = {r["codigo_entidad"]: r for r in leer("entidades-clasificadas.csv")}
    foco = [("72634", "Mercado Pago"), ("00072", "Banco Santander"),
            ("00017", "BBVA Argentina"), ("00007", "Banco Galicia"),
            ("00384", "Uala Bank"), ("00143", "Brubank"), ("45030", "Naranja X")]
    items = []
    for cod, etiqueta in foco:
        if cod in filas and filas[cod]["ph_tasa_mora_personas_pct"]:
            items.append((etiqueta, float(filas[cod]["ph_tasa_mora_personas_pct"])))
    items.sort(key=lambda x: x[1])
    barras_horizontales(
        "Proporcion de clientes en mora",
        "Solo personas humanas · deudores irregulares sobre total de deudores",
        items, 40,
        "Mercado Pago registra la proporcion mas baja del grupo",
        "04-mercado-pago-vs-bancos.svg")


def g5_retail():
    filas = leer("entidades-clasificadas.csv")
    items = []
    for r in filas:
        if r["categoria_comercial"].startswith("Vendedores") and r["ph_tasa_mora_monto_pct"]:
            if float(r["ph_monto_mora"]) > 10_000_000_000:
                items.append((r["entidad"][:28], float(r["ph_tasa_mora_monto_pct"])))
    items.sort(key=lambda x: -x[1])
    barras_horizontales(
        "Mora en el retail de electrodomesticos",
        "Solo personas humanas · monto irregular sobre monto financiado",
        items[:10], 80,
        "Entidades con mas de $10.000 millones en mora",
        "05-retail-electrodomesticos.svg")


def g6_denominadores():
    filas = leer("denominadores.csv")
    items = []
    for r in filas:
        if r["denominador"] == "Registros deudor-entidad":
            continue
        items.append((r["denominador"], float(r["tasa_pct"])))
    barras_horizontales(
        "La misma mora medida sobre cuatro denominadores distintos",
        "Cada denominador sostiene una afirmacion diferente",
        items, 30,
        "El denominador correcto depende de que se quiera afirmar",
        "06-denominadores.svg")


if __name__ == "__main__":
    SALIDA.mkdir(exist_ok=True)
    print("Generando graficos en graficos/")
    g1_doble_contabilizacion()
    g2_por_categoria()
    g3_por_regimen()
    g4_mercado_pago()
    g5_retail()
    g6_denominadores()
    print("Listo.")
