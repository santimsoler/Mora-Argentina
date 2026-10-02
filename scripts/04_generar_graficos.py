#!/usr/bin/env python3
"""
Genera los graficos del articulo como SVG independientes, a partir de los CSV
de la carpeta datos/.

Los SVG son autocontenidos, sin dependencias externas ni fuentes remotas, y
escalan sin perdida. Se abren en un navegador, se insertan en un documento
o se convierten a PNG.

Uso:
    python scripts/04_generar_graficos.py

Salida: graficos/*.svg
No requiere librerias externas.
"""

import csv
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "datos"
SALIDA = RAIZ / "graficos"

TINTA, GRIS, REGLA = "#0B2239", "#5C6E7E", "#C7D2DA"
VERDE, ORO, LADRILLO = "#12695F", "#B07C1E", "#A33B22"
ANCHO_BARRA = 600
FUENTE = "Helvetica, Arial, sans-serif"
MONO = "'IBM Plex Mono', 'DejaVu Sans Mono', monospace"

MESES = ["2026-06", "2026-07", "2026-08"]
ETIQ = {"2026-06": "junio", "2026-07": "julio", "2026-08": "agosto"}
ULTIMO = MESES[-1]


def leer(nombre):
    with open(DATOS / nombre, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(s):
    return float(s) if s not in ("", None) else None


def coma(v, dec=1):
    """Redondeo aritmetico (half-up), no bancario: 14,25 -> 14,3."""
    q = Decimal(str(v)).quantize(Decimal("1." + "0" * dec), rounding=ROUND_HALF_UP)
    return str(q).replace(".", ",")


def color_por_valor(pct):
    if pct >= 35: return LADRILLO
    if pct >= 20: return ORO
    return VERDE


def barras(titulo, subtitulo, items, maximo, nota, archivo):
    """items: lista de (etiqueta, valor_pct) o (etiqueta, valor_pct, color)"""
    alto_fila, y0 = 44, 68
    alto = y0 + len(items) * alto_fila + (56 if nota else 36)
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 {alto}" font-family="{FUENTE}">',
         f'<rect width="760" height="{alto}" fill="#FFFFFF"/>',
         f'<text x="0" y="22" font-size="17" font-weight="700" fill="{TINTA}">{titulo}</text>',
         f'<text x="0" y="42" font-size="11.5" fill="{GRIS}" font-family="{MONO}">{subtitulo}</text>']
    paso = 10 if maximo <= 50 else 20
    v = 0
    while v <= maximo:
        x = v / maximo * ANCHO_BARRA
        p.append(f'<line x1="{x:.0f}" y1="{y0-8}" x2="{x:.0f}" y2="{y0+len(items)*alto_fila-10}" '
                 f'stroke="{REGLA}" stroke-width="1" stroke-dasharray="2 4"/>')
        p.append(f'<text x="{x:.0f}" y="{y0+len(items)*alto_fila+8}" font-size="10" fill="{GRIS}" '
                 f'font-family="{MONO}" text-anchor="middle">{v}%</text>')
        v += paso
    for i, it in enumerate(items):
        etq, val = it[0], it[1]
        col = it[2] if len(it) > 2 else color_por_valor(val)
        y = y0 + i * alto_fila
        ancho = val / maximo * ANCHO_BARRA
        p.append(f'<text x="0" y="{y}" font-size="12.5" font-weight="500" fill="{TINTA}">{etq}</text>')
        p.append(f'<rect x="0" y="{y+6}" width="{ancho:.1f}" height="16" fill="{col}"/>')
        p.append(f'<text x="{ancho+8:.1f}" y="{y+19}" font-size="12" font-weight="600" '
                 f'fill="{col}" font-family="{MONO}">{coma(val)}%</text>')
    if nota:
        p.append(f'<text x="0" y="{alto-14}" font-size="10.5" fill="{GRIS}" font-family="{MONO}">{nota}</text>')
    p.append("</svg>")
    (SALIDA / archivo).write_text("\n".join(p), encoding="utf-8")
    print(f"  {archivo}")


def g1_doble_contabilizacion():
    s = {r["mes"]: r for r in leer("serie-sistema.csv")}[ULTIMO]
    reg, pers = int(s["registros_en_mora"]), int(s["ph_en_mora"])
    ancho_pers = 600 * pers / reg
    alto = 210
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 {alto}" font-family="{FUENTE}">',
         f'<rect width="760" height="{alto}" fill="#FFFFFF"/>',
         f'<text x="0" y="22" font-size="17" font-weight="700" fill="{TINTA}">'
         f'Diez millones de registros, seis millones de personas</text>',
         f'<text x="0" y="42" font-size="11.5" fill="{GRIS}" font-family="{MONO}">'
         f'Situacion irregular (3, 4 y 5) — agosto 2026</text>',
         f'<text x="0" y="80" font-size="12.5" fill="{TINTA}">Registros deudor-entidad en mora</text>',
         f'<rect x="0" y="88" width="600" height="30" fill="{LADRILLO}" opacity="0.28"/>',
         f'<rect x="0" y="88" width="600" height="30" fill="none" stroke="{LADRILLO}" stroke-width="1.5"/>',
         f'<text x="610" y="108" font-size="12.5" font-weight="600" fill="{LADRILLO}" '
         f'font-family="{MONO}">{reg:,}</text>'.replace(",", "."),
         f'<text x="0" y="148" font-size="12.5" fill="{TINTA}">Personas humanas unicas en mora</text>',
         f'<rect x="0" y="156" width="{ancho_pers:.0f}" height="30" fill="{VERDE}"/>',
         f'<text x="{ancho_pers+10:.0f}" y="176" font-size="12.5" font-weight="600" fill="{VERDE}" '
         f'font-family="{MONO}">{pers:,}</text>'.replace(",", "."),
         f'<line x1="{ancho_pers:.0f}" y1="84" x2="{ancho_pers:.0f}" y2="192" stroke="{TINTA}" '
         f'stroke-width="1" stroke-dasharray="3 3"/>',
         f'<text x="0" y="{alto-8}" font-size="10.5" fill="{GRIS}" font-family="{MONO}">'
         f'La diferencia son personas contadas una vez por cada entidad a la que le deben</text>',
         "</svg>"]
    (SALIDA / "01-doble-contabilizacion.svg").write_text("\n".join(p), encoding="utf-8")
    print("  01-doble-contabilizacion.svg")


def g2_por_categoria():
    excluir = {"Compra de Carteras en Mora", "SGR y Fondos de Garantía"}
    items = [(r["categoria"], num(r["tasa_mora_monto_pct"]))
             for r in leer("serie-por-categoria.csv")
             if r["mes"] == ULTIMO and r["categoria"] not in excluir and r["tasa_mora_monto_pct"]]
    items.sort(key=lambda x: -x[1])
    barras("Tasa de mora por tipo de prestamista",
           "Solo personas humanas · monto irregular sobre monto prestado · agosto 2026",
           items, 50,
           "Se excluyen fideicomisos de recupero y SGR: sus tasas no miden desempeno crediticio",
           "02-mora-por-categoria.svg")


def g3_por_regimen():
    orden = ["Entidades Financieras - Bancos",
             "Entidades Financieras - Companias Financieras",
             "Proveedores No Financieros de Credito"]
    filas = {r["regimen"]: r for r in leer("serie-por-regimen.csv") if r["mes"] == ULTIMO}
    items = [(n.replace("Entidades Financieras - ", ""), num(filas[n]["ph_tasa_mora_monto_pct"]))
             for n in orden if n in filas]
    barras("Tasa de mora segun regimen de inscripcion ante el BCRA",
           "Solo personas humanas · agosto 2026", items, 40,
           "Los proveedores no financieros no tienen exigencia de capital ni previsionamiento prudencial",
           "03-mora-por-regimen.svg")


def g4_mercado_pago():
    filas = {r["codigo_entidad"]: r for r in leer("entidades-202608.csv")}
    foco = [("72634", "Mercado Pago"), ("00072", "Banco Santander"), ("00017", "BBVA Argentina"),
            ("00007", "Banco Galicia"), ("00384", "Uala Bank"), ("00143", "Brubank"),
            ("45030", "Naranja X")]
    items = [(e, num(filas[c]["ph_tasa_mora_personas_pct"]))
             for c, e in foco if c in filas and filas[c]["ph_tasa_mora_personas_pct"]]
    items.sort(key=lambda x: x[1])
    barras("Proporcion de clientes en mora",
           "Solo personas humanas · deudores irregulares sobre total de deudores · agosto 2026",
           items, 40, "Mercado Pago registra la proporcion mas baja del grupo",
           "04-mercado-pago-vs-bancos.svg")


def g5_retail():
    items = [(r["entidad"][:28], num(r["ph_tasa_mora_monto_pct"]))
             for r in leer("entidades-202608.csv")
             if r["categoria_comercial"].startswith("Vendedores")
             and r["ph_tasa_mora_monto_pct"] and float(r["ph_monto_mora"]) > 10e9]
    items.sort(key=lambda x: -x[1])
    barras("Mora en el retail de electrodomesticos",
           "Solo personas humanas · monto irregular sobre monto financiado · agosto 2026",
           items[:10], 80, "Entidades con mas de $10.000 millones en mora",
           "05-retail-electrodomesticos.svg")


def g6_denominadores():
    items = [(r["denominador"], num(r["tasa_pct"])) for r in leer("denominadores-202608.csv")
             if r["denominador"] != "Registros deudor-entidad"]
    barras("La misma mora medida sobre cuatro denominadores distintos",
           "Cada denominador sostiene una afirmacion diferente · agosto 2026",
           items, 30, "El denominador correcto depende de que se quiera afirmar",
           "06-denominadores.svg")


def g7_evolucion():
    """Serie mensual por categoria: lineas."""
    datos = {}
    for r in leer("serie-por-categoria.csv"):
        datos.setdefault(r["categoria"], {})[r["mes"]] = num(r["tasa_mora_monto_pct"])
    series = [("Electrodomésticos y retail", "Vendedores de Electrodomésticos y Retail", LADRILLO),
              ("Crédito rápido", "Empresas Crédito Rápido Alto Riesgo", "#C4613F"),
              ("Tarjetas no bancarias", "Tarjetas de Crédito No Bancarias", ORO),
              ("Fintech y billeteras", "Fintech y Billeteras", "#CBA13C"),
              ("Bancos privados", "Bancos Privados", VERDE),
              ("Bancos provinciales", "Bancos Provinciales", "#2E8B7F"),
              ("Banco Nación", "Banco Nación", "#5FA89C")]
    W, H, L, R, T, B = 830, 520, 72, 252, 66, 54
    xs = [L + i * (W - L - R) / (len(MESES) - 1) for i in range(len(MESES))]
    ymax = 50
    def y(v): return T + (H - T - B) * (1 - v / ymax)
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="{FUENTE}">',
         f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>',
         f'<text x="0" y="22" font-size="17" font-weight="700" fill="{TINTA}">'
         f'Evolucion de la mora por tipo de prestamista</text>',
         f'<text x="0" y="42" font-size="11.5" fill="{GRIS}" font-family="{MONO}">'
         f'Solo personas humanas · monto irregular sobre monto prestado</text>']
    for v in range(0, ymax + 1, 10):
        p.append(f'<line x1="{L}" y1="{y(v):.1f}" x2="{W-R}" y2="{y(v):.1f}" stroke="{REGLA}" '
                 f'stroke-width="1" stroke-dasharray="2 4"/>')
        p.append(f'<text x="{L-10}" y="{y(v)+4:.1f}" font-size="10" fill="{GRIS}" '
                 f'font-family="{MONO}" text-anchor="end">{v}%</text>')
    for xi, m in zip(xs, MESES):
        p.append(f'<text x="{xi:.1f}" y="{H-B+22}" font-size="12" fill="{TINTA}" '
                 f'text-anchor="middle">{ETIQ[m]}</text>')
    # separacion minima entre etiquetas del margen derecho
    finales = sorted(((datos[k][ULTIMO], n, c) for n, k, c in series), reverse=True)
    usados = []
    for val, nom, col in finales:
        yy = y(val)
        while any(abs(yy - u) < 15 for u in usados):
            yy += 15
        usados.append(yy)
        vs = [datos[dict((n, k) for n, k, _ in series)[nom]][m] for m in MESES]
        pts = " ".join(f"{x:.1f},{y(v):.1f}" for x, v in zip(xs, vs))
        p.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2.6" '
                 f'stroke-linejoin="round"/>')
        for x, v in zip(xs, vs):
            p.append(f'<circle cx="{x:.1f}" cy="{y(v):.1f}" r="4" fill="{col}"/>')
        p.append(f'<text x="{W-R+14}" y="{yy+4:.1f}" font-size="11.5" font-weight="600" '
                 f'fill="{col}">{nom}</text>')
        p.append(f'<text x="{W-14}" y="{yy+4:.1f}" font-size="11" fill="{col}" '
                 f'font-family="{MONO}" text-anchor="end" opacity="0.85">{coma(val)}%</text>')
    p.append(f'<text x="0" y="{H-8}" font-size="10" fill="{GRIS}" font-family="{MONO}">'
             f'BCRA · Central de Deudores · junio a agosto 2026</text>')
    p.append("</svg>")
    (SALIDA / "07-evolucion-mensual.svg").write_text("\n".join(p), encoding="utf-8")
    print("  07-evolucion-mensual.svg")


if __name__ == "__main__":
    SALIDA.mkdir(exist_ok=True)
    print("Generando graficos en graficos/")
    g1_doble_contabilizacion(); g2_por_categoria(); g3_por_regimen()
    g4_mercado_pago(); g5_retail(); g6_denominadores(); g7_evolucion()
    print("Listo.")
