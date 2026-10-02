#!/usr/bin/env python3
"""
Genera los CSV de datos/ a partir de los .pkl mensuales y de categorias.pkl.

Produce dos familias de archivos:

  serie-*.csv        la evolucion mes a mes (sistema, categoria, regimen, entidad)
  *-202608.csv       el detalle completo del ultimo mes disponible

Todas las cifras de hogares corresponden a personas humanas (prefijo de CUIT
20/23/24/27). Las de sociedades van en columnas aparte con el prefijo pj_.

Uso:
    python scripts/03_generar_salidas.py

Espera encontrar en el directorio de trabajo: maestro.pkl, categorias.pkl y
los d06.pkl / d07.pkl / d08.pkl que produce 01_procesar_mes.py.
"""
import pickle, csv, sys
from collections import defaultdict
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from importlib import import_module
_cl = import_module("02_clasificar_entidades")
ORDEN, regimen = _cl.ORDEN, _cl.regimen

DEST = str(__import__("pathlib").Path(__file__).resolve().parent.parent / "datos")
maestro=pickle.load(open("maestro.pkl","rb")); cat=pickle.load(open("categorias.pkl","rb"))
MESES=("06","07","08"); ETIQ={"06":"2026-06","07":"2026-07","08":"2026-08"}
M={m:pickle.load(open(f"d{m}.pkl","rb")) for m in MESES}
ULT="08"; ADULTOS=34_970_989
def p(a,b): return round(a/b*100,2) if b else ""

def agr(m,key):
    r=defaultdict(lambda:[0.0,0.0,0,0])
    for c,d in M[m]["entidades"].items():
        k=key(c)
        if k is None: continue
        a=r[k]; a[0]+=d["f_mm"]; a[1]+=d["f_mc"]; a[2]+=d["f_pm"]; a[3]+=d["f_pc"]
    return r
def agrj(m,key):
    r=defaultdict(lambda:[0.0,0.0,0])
    for c,d in M[m]["entidades"].items():
        k=key(c)
        if k is None: continue
        a=r[k]; a[0]+=d["j_mm"]; a[1]+=d["j_mc"]; a[2]+=d["j_pm"]
    return r

# ---- 1. serie del sistema
with open(f"{DEST}/serie-sistema.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["mes","registros","registros_en_mora","ph_registros","ph_registros_en_mora",
      "ph_registradas","ph_en_mora","ph_tasa_mora_personas_pct","ph_monto_mora","ph_monto_cartera",
      "ph_tasa_mora_monto_pct","ph_credito_promedio_mora","morosos_sobre_adultos_pct",
      "adultos_sin_credito_pct","pj_registros","pj_registradas","pj_en_mora","pj_monto_mora",
      "pj_monto_cartera","pj_tasa_mora_monto_pct"])
    for m in MESES:
        x=M[m]; F=x["fisicas"]; J=x["juridicas"]
        w.writerow([ETIQ[m],x["registros"],x["registros_mora"],
            x.get("registros_fisicas",""),x.get("registros_mora_fisicas",""),
            F["pu"],F["pm"],p(F["pm"],F["pu"]),
            round(F["mm"]),round(F["mc"]),p(F["mm"],F["mc"]),round(F["mm"]/F["pm"]),
            p(F["pm"],ADULTOS),p(ADULTOS-F["pu"],ADULTOS),
            x.get("registros_juridicas",""),J["pu"],J["pm"],round(J["mm"]),round(J["mc"]),p(J["mm"],J["mc"])])

# ---- 2. serie por categoria
G={m:agr(m,lambda c:cat.get(c)) for m in MESES}
with open(f"{DEST}/serie-por-categoria.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["categoria","mes","monto_mora","monto_cartera","tasa_mora_monto_pct",
      "personas_mora","personas_cartera","tasa_mora_personas_pct","credito_promedio_mora"])
    for c in ORDEN:
        for m in MESES:
            a=G[m].get(c)
            if not a: continue
            w.writerow([c,ETIQ[m],round(a[0]),round(a[1]),p(a[0],a[1]),a[2],a[3],p(a[2],a[3]),
                        round(a[0]/a[2]) if a[2] else ""])

# ---- 3. serie por regimen
R={m:agr(m,regimen) for m in MESES}; RJ={m:agrj(m,regimen) for m in MESES}
with open(f"{DEST}/serie-por-regimen.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["regimen","mes","ph_monto_mora","ph_monto_cartera",
      "ph_tasa_mora_monto_pct","ph_personas_mora","pj_monto_mora","pj_monto_cartera","pj_tasa_mora_monto_pct"])
    for k in sorted({regimen(c) for c in cat}):
        for m in MESES:
            a=R[m].get(k); b=RJ[m].get(k,[0,0,0])
            if not a: continue
            w.writerow([k,ETIQ[m],round(a[0]),round(a[1]),p(a[0],a[1]),a[2],
                        round(b[0]),round(b[1]),p(b[0],b[1])])

# ---- 4. serie por entidad
with open(f"{DEST}/serie-por-entidad.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["codigo_entidad","entidad","categoria_comercial","regimen",
      "jun_tasa_mora_pct","jul_tasa_mora_pct","ago_tasa_mora_pct","delta_jun_ago_pp",
      "jun_monto_mora","jul_monto_mora","ago_monto_mora",
      "jun_personas_mora","jul_personas_mora","ago_personas_mora","ago_monto_cartera"])
    filas=[]
    for c in sorted(cat):
        t=[];mm=[];pm=[]
        for m in MESES:
            d=M[m]["entidades"].get(c)
            t.append(p(d["f_mm"],d["f_mc"]) if d else ""); mm.append(round(d["f_mm"]) if d else "")
            pm.append(d["f_pm"] if d else "")
        dl=round(t[2]-t[0],2) if (t[0]!="" and t[2]!="") else ""
        d8=M[ULT]["entidades"].get(c)
        filas.append([c,maestro.get(c,f"[{c}]"),cat[c],regimen(c),*t,dl,*mm,*pm,
                      round(d8["f_mc"]) if d8 else ""])
    filas.sort(key=lambda r:-(r[10] if isinstance(r[10],int) else 0))
    w.writerows(filas)

# ---- 5. mes corriente: entidades, resumenes, excluidas, denominadores
A=M[ULT]
exc=[]; filas=[]
for c,d in A["entidades"].items():
    if d["f_mc"]<=0 and d["j_mc"]<=0:
        exc.append((c,maestro.get(c,f"[{c}]"))); continue
    filas.append([c,maestro.get(c,f"[{c}]"),cat[c],regimen(c),
      round(d["f_mm"]),round(d["f_mc"]),p(d["f_mm"],d["f_mc"]),d["f_pm"],d["f_pc"],
      p(d["f_pm"],d["f_pc"]),round(d["f_mm"]/d["f_pm"]) if d["f_pm"] else "",
      round(d["j_mm"]),round(d["j_mc"]),p(d["j_mm"],d["j_mc"]),d["j_pm"],d["j_pc"],
      round(d["f_mm"]+d["j_mm"]),p(d["f_mm"]+d["j_mm"],d["f_mc"]+d["j_mc"])])
filas.sort(key=lambda r:-r[16])
with open(f"{DEST}/entidades-202608.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["codigo_entidad","entidad","categoria_comercial","regimen_inscripcion",
      "ph_monto_mora","ph_monto_cartera","ph_tasa_mora_monto_pct","ph_personas_mora","ph_personas_cartera",
      "ph_tasa_mora_personas_pct","ph_credito_promedio_mora",
      "pj_monto_mora","pj_monto_cartera","pj_tasa_mora_monto_pct","pj_sociedades_mora","pj_sociedades_cartera",
      "total_monto_mora","total_tasa_mora_monto_pct"])
    w.writerows(filas)
with open(f"{DEST}/entidades-excluidas-202608.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["codigo_entidad","entidad","motivo"])
    for c,n in sorted(exc): w.writerow([c,n,"informa cartera y/o personas en cero"])

nent=defaultdict(int)
for c in A["entidades"]: nent[cat[c]]+=1
GA=G[ULT]; GJ=agrj(ULT,lambda c:cat.get(c)); F=A["fisicas"]
with open(f"{DEST}/resumen-por-categoria-202608.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["categoria","entidades","ph_monto_mora","ph_monto_cartera",
      "ph_tasa_mora_monto_pct","ph_personas_mora","ph_personas_cartera","ph_tasa_mora_personas_pct",
      "ph_credito_promedio_mora","pct_monto_sistema","pct_personas_sistema",
      "pj_monto_mora","pj_tasa_mora_monto_pct"])
    for c in ORDEN:
        a=GA.get(c)
        if not a: continue
        b=GJ.get(c,[0,0,0])
        w.writerow([c,nent[c],round(a[0]),round(a[1]),p(a[0],a[1]),a[2],a[3],p(a[2],a[3]),
          round(a[0]/a[2]) if a[2] else "",p(a[0],F["mm"]),p(a[2],F["pm"]),round(b[0]),p(b[0],b[1])])
    J=A["juridicas"]
    w.writerow(["TOTAL - personas humanas",len(A["entidades"]),round(F["mm"]),round(F["mc"]),
      p(F["mm"],F["mc"]),F["pm"],F["pu"],p(F["pm"],F["pu"]),round(F["mm"]/F["pm"]),100.0,100.0,"",""])
    w.writerow(["TOTAL - sociedades","",round(J["mm"]),round(J["mc"]),p(J["mm"],J["mc"]),
      J["pm"],J["pu"],p(J["pm"],J["pu"]),round(J["mm"]/J["pm"]),"","","",""])

with open(f"{DEST}/denominadores-202608.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["denominador","base","morosos","tasa_pct","fuente"])
    T=A["total"]
    w.writerow(["Registros deudor-entidad",A["registros"],A["registros_mora"],
                p(A["registros_mora"],A["registros"]),"Central de Deudores"])
    w.writerow(["CUIT unicos (humanas + sociedades)",T["pu"],T["pm"],p(T["pm"],T["pu"]),"Central de Deudores"])
    w.writerow(["Personas humanas registradas",F["pu"],F["pm"],p(F["pm"],F["pu"]),"Central de Deudores"])
    w.writerow(["Sociedades registradas",J["pu"],J["pm"],p(J["pm"],J["pu"]),"Central de Deudores"])
    w.writerow(["Poblacion adulta 18+",ADULTOS,F["pm"],p(F["pm"],ADULTOS),"INDEC - proyecciones Censo 2022"])
print("CSVs del repo generados")
