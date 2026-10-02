#!/usr/bin/env python3
"""
Genera las placas verticales 1080x1920 del reel de divulgacion.

Las placas se superponen sobre el video mientras el autor habla, asi que el
audio no se corta. Los tiempos de entrada y salida estan en docs/GUION-REEL.md.

Las cifras se leen de los CSV de datos/, de modo que al actualizar un mes las
placas se regeneran con los numeros nuevos sin rehacer el diseno.

Uso:
    python scripts/05_generar_placas_reel.py

Salida: placas-reel/*.png
Requiere: Pillow
"""

import csv
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "datos"
SALIDA = RAIZ / "placas-reel"

W, H = 1080, 1920
FD = "/usr/share/fonts/truetype/dejavu/"
B = lambda s: ImageFont.truetype(FD + "DejaVuSans-Bold.ttf", s)
R = lambda s: ImageFont.truetype(FD + "DejaVuSans.ttf", s)
M = lambda s: ImageFont.truetype(FD + "DejaVuSansMono-Bold.ttf", s)
MR = lambda s: ImageFont.truetype(FD + "DejaVuSansMono.ttf", s)

TINTA, PAPEL, BLANCO = "#0B2239", "#EFF2F4", "#FFFFFF"
VERDE, ORO, LADRILLO, GRIS, REGLA = "#12695F", "#B07C1E", "#A33B22", "#5C6E7E", "#C7D2DA"

MES_ETIQUETA = "agosto 2026"
PIE = "BCRA · Central de Deudores · agosto 2026"


def leer(nombre):
    with open(DATOS / nombre, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def miles(n):
    return f"{int(n):,}".replace(",", ".")


def coma(v, dec=1):
    """Redondeo aritmetico (half-up), no bancario: 14,25 -> 14,3."""
    q = Decimal(str(v)).quantize(Decimal("1." + "0" * dec), rounding=ROUND_HALF_UP)
    return str(q).replace(".", ",")


def lienzo(bg=PAPEL):
    im = Image.new("RGB", (W, H), bg)
    return im, ImageDraw.Draw(im)


def centro(d, y, txt, f, fill, ancho=W):
    x0, y0, x1, y1 = d.textbbox((0, 0), txt, font=f)
    d.text(((ancho - (x1 - x0)) / 2 - x0, y), txt, font=f, fill=fill)
    return y1 - y0


def envolver(d, txt, f, maxw):
    lineas, cur = [], ""
    for palabra in txt.split():
        t = (cur + " " + palabra).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            lineas.append(cur); cur = palabra
    if cur:
        lineas.append(cur)
    return lineas


def bloque(d, y, txt, f, fill, maxw=W - 140, lh=1.28):
    for l in envolver(d, txt, f, maxw):
        centro(d, y, l, f, fill)
        y += int(f.size * lh)
    return y


def pie(d, extra=None):
    d.line([(70, H - 140), (W - 70, H - 140)], fill=REGLA, width=2)
    d.text((70, H - 115), extra or PIE, font=MR(26), fill=GRIS)


def main():
    SALIDA.mkdir(exist_ok=True)
    sistema = {r["mes"]: r for r in leer("serie-sistema.csv")}
    ult = max(sistema)
    s = sistema[ult]
    cats = {r["categoria"]: r for r in leer("serie-por-categoria.csv") if r["mes"] == ult}
    ents = {r["codigo_entidad"]: r for r in leer("entidades-202608.csv")}
    adultos = 34_970_989

    # ---------- 1. GANCHO ----------
    im, d = lienzo(TINTA)
    centro(d, 300, "TE DIJERON QUE HAY", M(38), "#7FA8C4")
    f = B(124)
    reg = miles(s["registros_en_mora"])
    centro(d, 390, reg, f, "#8FA8BC")
    tw = d.textlength(reg, font=f)
    d.line([((W - tw) / 2 - 34, 456), ((W + tw) / 2 + 34, 456)], fill=LADRILLO, width=13)
    centro(d, 600, "MOROSOS", M(38), "#7FA8C4")
    centro(d, 760, "▼", B(90), "#4A6B85")
    centro(d, 900, "SON", M(38), "#9FC4D8")
    centro(d, 970, miles(s["ph_en_mora"]), B(138), BLANCO)
    centro(d, 1180, "PERSONAS", M(44), "#9FC4D8")
    d.line([(340, 1320), (740, 1320)], fill=VERDE, width=6)
    bloque(d, 1380, "La base del Banco Central cuenta deudas, no personas.", R(46), "#C8D8E4", W - 200)
    pie(d)
    im.save(SALIDA / "01-gancho.png")

    # ---------- 2. POR QUE ----------
    im, d = lienzo()
    centro(d, 240, "POR QUÉ ESTABA MAL", M(36), LADRILLO)
    bloque(d, 340, "Si debés en un banco, en una billetera y en una casa de electrodomésticos…",
           B(62), TINTA, W - 160)
    for i, (t, c) in enumerate([("BANCO", VERDE), ("BILLETERA", ORO), ("ELECTRO", LADRILLO)]):
        x, yy = 110 + i * 300, 780
        d.rounded_rectangle([x, yy, x + 260, yy + 180], 28, fill=c)
        for txt, ff, y2 in (("1", B(72), yy + 22), (t, M(24), yy + 120)):
            d.text((x + 130 - d.textlength(txt, font=ff) / 2, y2), txt, font=ff, fill=BLANCO)
    centro(d, 1060, "aparecés 3 veces", B(70), LADRILLO)
    d.line([(200, 1230), (880, 1230)], fill=REGLA, width=3)
    centro(d, 1300, "Deduplicando por CUIT:", R(48), GRIS)
    centro(d, 1390, miles(s["ph_en_mora"]), B(134), VERDE)
    centro(d, 1570, "personas humanas en mora", M(34), GRIS)
    pie(d)
    im.save(SALIDA / "02-por-que.png")

    # ---------- 3. ESCALA ----------
    im, d = lienzo()
    centro(d, 260, "LA ESCALA REAL", M(36), VERDE)
    centro(d, 360, coma(s["morosos_sobre_adultos_pct"]) + "%", B(220), TINTA)
    bloque(d, 640, "de los adultos del país está en mora", R(56), TINTA, W - 180)
    d.line([(200, 880), (880, 880)], fill=REGLA, width=3)
    centro(d, 950, miles(s["ph_en_mora"]), M(58), TINTA)
    centro(d, 1030, f"sobre {miles(adultos)} adultos", R(40), GRIS)
    d.rounded_rectangle([90, 1180, W - 90, 1560], 24, fill="#E3E8EC")
    bloque(d, 1230, "No es la mitad del país.", B(52), TINTA, W - 220)
    bloque(d, 1330, "Y no son diez millones de personas: son deudas contadas más de una vez.",
           R(42), GRIS, W - 220)
    pie(d, "INDEC · proyecciones Censo 2022 · BCRA agosto 2026")
    im.save(SALIDA / "03-escala.png")

    # ---------- 4. SIN CREDITO ----------
    sin_credito = adultos - int(s["ph_registradas"])
    im, d = lienzo(TINTA)
    centro(d, 230, "EL DATO DEL QUE NADIE HABLA", M(34), "#7FA8C4")
    for fila in range(2):
        for i in range(5):
            x, yy = 115 + i * 180, 330 + fila * 210
            col = LADRILLO if (fila * 5 + i) < 4 else "#2C4A63"
            d.rounded_rectangle([x, yy, x + 140, yy + 170], 22, fill=col)
    centro(d, 800, "4 de cada 10", B(110), BLANCO)
    bloque(d, 950, "adultos argentinos no tienen crédito de ningún tipo", R(52), "#C8D8E4", W - 180)
    d.line([(340, 1180), (740, 1180)], fill=LADRILLO, width=6)
    centro(d, 1250, miles(sin_credito), M(72), LADRILLO)
    centro(d, 1360, "personas", R(40), "#8FA8BC")
    bloque(d, 1480, "No es que no lo pagan. No lo tienen.", B(50), BLANCO, W - 180)
    pie(d, "INDEC · Censo 2022 · BCRA agosto 2026")
    im.save(SALIDA / "04-sin-credito.png")

    # ---------- 5. DONDE ESTA ----------
    im, d = lienzo()
    centro(d, 200, "¿DÓNDE EXPLOTÓ LA MORA?", M(34), LADRILLO)
    centro(d, 280, "Cartera de familias", R(38), GRIS)
    peor = max((r for r in leer("entidades-202608.csv")
                if r["categoria_comercial"].startswith("Vendedores") and r["ph_tasa_mora_monto_pct"]),
               key=lambda r: float(r["ph_tasa_mora_monto_pct"]))
    reg = {r["regimen"]: r for r in leer("serie-por-regimen.csv") if r["mes"] == ult}
    datos = [("Bancos", float(reg["Entidades Financieras - Bancos"]["ph_tasa_mora_monto_pct"]), VERDE),
             ("Crédito no bancario", float(reg["Proveedores No Financieros de Credito"]["ph_tasa_mora_monto_pct"]), ORO),
             ("Electrodomésticos", float(cats["Vendedores de Electrodomésticos y Retail"]["tasa_mora_monto_pct"]), LADRILLO),
             (peor["entidad"].split()[0].title(), float(peor["ph_tasa_mora_monto_pct"]), LADRILLO)]
    y, mx, bw = 440, 75.0, W - 220
    for nom, v, c in datos:
        d.text((110, y), nom, font=B(44), fill=TINTA)
        d.rectangle([110, y + 74, 110 + bw, y + 156], fill="#DDE4E9")
        d.rectangle([110, y + 74, 110 + int(bw * v / mx), y + 156], fill=c)
        txt, fv = coma(v) + "%", M(54)
        x = 110 + int(bw * v / mx) + 20 if v < 60 else 110 + int(bw * v / mx) - d.textlength(txt, font=fv) - 20
        d.text((x, y + 90), txt, font=fv, fill=BLANCO if v >= 60 else c)
        y += 225
    d.rounded_rectangle([90, 1400, W - 90, 1660], 24, fill="#E3E8EC")
    bloque(d, 1450, "Hay cadenas con más del 70% de lo que financiaron sin cobrar.", B(46), TINTA, W - 220)
    pie(d)
    im.save(SALIDA / "05-donde.png")

    # ---------- 6. MERCADO PAGO ----------
    im, d = lienzo()
    centro(d, 190, "AL QUE LE PEGARON TODO AGOSTO", M(32), LADRILLO)
    bloque(d, 270, "Mora en cartera de familias", B(56), TINTA)
    foco = [("72634", "Mercado Pago", True), ("00007", "Banco Galicia", False),
            ("00072", "Banco Santander", False), ("00143", "Brubank", False),
            ("45030", "Naranja X", False)]
    y = 470
    for cod, nom, dest in foco:
        if cod not in ents:
            continue
        v = float(ents[cod]["ph_tasa_mora_monto_pct"])
        c = VERDE if dest else (LADRILLO if v > 20 else TINTA)
        if dest:
            d.rounded_rectangle([80, y - 16, W - 80, y + 92], 18, fill="#D7E6E3")
        d.text((120, y + 10), nom, font=B(48) if dest else R(46), fill=c)
        val = coma(v) + "%"
        d.text((W - 120 - d.textlength(val, font=M(52)), y + 8), val, font=M(52), fill=c)
        y += 138
    d.line([(110, 1180), (W - 110, 1180)], fill=REGLA, width=3)
    bloque(d, 1250, "Prácticamente la misma mora que los bancos.", B(54), TINTA, W - 180)
    bloque(d, 1420, "Y menos clientes en mora que Galicia y BBVA, prestando con muchos menos requisitos.",
           R(44), GRIS, W - 180)
    pie(d)
    im.save(SALIDA / "06-mercado-pago.png")

    # ---------- 7. CIERRE ----------
    n_ent = sum(1 for _ in leer("entidades-202608.csv"))
    im, d = lienzo(TINTA)
    centro(d, 320, "ESTÁ TODO PUBLICADO", M(36), "#7FA8C4")
    centro(d, 440, miles(s["registros"]), B(120), BLANCO)
    centro(d, 600, "registros procesados", R(44), "#9FC4D8")
    d.line([(340, 720), (740, 720)], fill=VERDE, width=6)
    centro(d, 790, str(n_ent), B(120), BLANCO)
    centro(d, 950, "entidades clasificadas", R(44), "#9FC4D8")
    d.rounded_rectangle([90, 1120, W - 90, 1420], 26, fill="#123049")
    bloque(d, 1170, "Los datos, el código y el análisis completo, abiertos en GitHub.",
           R(44), "#C8D8E4", W - 220)
    bloque(d, 1320, "Si encontrás un error, avisame.", B(42), BLANCO, W - 220)
    centro(d, 1520, "LINK EN LA BIO", M(54), VERDE)
    pie(d, "Lic. Pablo Santiago Martínez Soler · Economista (UBA)")
    im.save(SALIDA / "07-cierre.png")

    print(f"7 placas generadas en {SALIDA}")


if __name__ == "__main__":
    main()
