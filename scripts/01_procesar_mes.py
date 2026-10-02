#!/usr/bin/env python3
"""
Procesa un mes de la Central de Deudores del BCRA.

Lee `deudores.txt` directamente desde el .7z en streaming, sin descomprimir
los ~7 GB a disco, y guarda los agregados por entidad y los totales del
sistema deduplicados por CUIT.

La distincion clave: la Central registra RELACIONES deudor-entidad, no
personas. Sumar registros sobreestima la cantidad de deudores en un 72%.
Este script cuenta las dos cosas por separado.

Tambien separa personas humanas (prefijo de CUIT 20/23/24/27) de sociedades
(30/33/34): son universos con tasas de mora muy distintas y mezclarlos
distorsiona el agregado.

Uso:
    python scripts/01_procesar_mes.py /ruta/202608DEUDORES.7Z d08.pkl

Requisitos: numpy y libarchive (preinstalada en la mayoria de las distros).
Tiempo: unos 2 minutos y ~1,5 GB de RAM para 41 millones de registros.
"""
import ctypes, sys, time, pickle
import numpy as np

RUTA, SALIDA = sys.argv[1], sys.argv[2]

lib = ctypes.CDLL("libarchive.so.13")
lib.archive_read_new.restype = ctypes.c_void_p
lib.archive_read_support_filter_all.argtypes=[ctypes.c_void_p]
lib.archive_read_support_format_all.argtypes=[ctypes.c_void_p]
lib.archive_read_open_filename.argtypes=[ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t]
lib.archive_read_next_header.argtypes=[ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
lib.archive_entry_pathname.argtypes=[ctypes.c_void_p]; lib.archive_entry_pathname.restype=ctypes.c_char_p
lib.archive_read_data.argtypes=[ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]
lib.archive_read_data.restype=ctypes.c_ssize_t

a = lib.archive_read_new()
lib.archive_read_support_filter_all(a); lib.archive_read_support_format_all(a)
lib.archive_read_open_filename(a, RUTA.encode(), 1024*1024)
ent = ctypes.c_void_p()
while lib.archive_read_next_header(a, ctypes.byref(ent)) == 0:
    if lib.archive_entry_pathname(ent).decode('latin-1').endswith('deudores.txt'): break

N = 46_000_000
cu = np.zeros(N, dtype=np.int64)     # CUIT
en = np.zeros(N, dtype=np.int32)     # indice de entidad
mo = np.zeros(N, dtype=bool)         # situacion >= 3
mt = np.zeros(N, dtype=np.float64)   # monto en pesos
pf = np.zeros(N, dtype=np.int8)      # prefijo del CUIT

cix, codes = {}, []
buf = ctypes.create_string_buffer(16*1024*1024)
resto = b''; i = 0; t0 = time.time()
while True:
    n = lib.archive_read_data(a, buf, len(buf))
    if n <= 0: break
    data = resto + buf.raw[:n]
    lineas = data.split(b'\n'); resto = lineas.pop()
    for l in lineas:
        if len(l) < 41: continue
        c = l[0:5].decode('latin-1').strip()
        k = l[13:24].decode('latin-1').strip()
        if not k.isdigit() or len(k) != 11: continue
        s = l[27:29].decode('latin-1').strip()
        try: v = float(l[29:41].decode('latin-1').strip().replace(',', '.')) * 1000
        except ValueError: v = 0.0
        j = cix.get(c)
        if j is None: j = cix[c] = len(codes); codes.append(c)
        en[i] = j; cu[i] = int(k); mt[i] = v; pf[i] = int(k[:2])
        mo[i] = s.isdigit() and int(s) >= 3
        i += 1
print(f"  leidos {i:,} registros en {time.time()-t0:.0f}s, {len(codes)} entidades", flush=True)

cu = cu[:i]; en = en[:i]; mo = mo[:i]; mt = mt[:i]; pf = pf[:i]
FIS = np.isin(pf, [20, 23, 24, 25, 26, 27])
JUR = np.isin(pf, [30, 33, 34])
NE = len(codes)

def unicos_por_entidad(mask):
    """Cantidad de CUIT unicos por entidad, vectorizado."""
    e = en[mask].astype(np.int64); c = cu[mask]
    if e.size == 0: return np.zeros(NE, dtype=np.int64)
    key = e * 100_000_000_000 + c
    key = np.unique(key)
    ee = (key // 100_000_000_000).astype(np.int64)
    return np.bincount(ee, minlength=NE)

res = {}
for etq, M in (('f', FIS), ('j', JUR)):
    res[etq+'_mm'] = np.bincount(en[M & mo], weights=mt[M & mo], minlength=NE)
    res[etq+'_mc'] = np.bincount(en[M], weights=mt[M], minlength=NE)
    res[etq+'_pm'] = unicos_por_entidad(M & mo)
    res[etq+'_pc'] = unicos_por_entidad(M)

ent_out = {}
for c, j in cix.items():
    ent_out[c] = {k: (float(v[j]) if k.endswith('m m') or k[-2:] in ('mm','mc') else int(v[j]))
                  for k, v in res.items()}

def tot(M):
    return dict(pu=int(len(np.unique(cu[M]))), pm=int(len(np.unique(cu[M & mo]))),
                mm=float(mt[M & mo].sum()), mc=float(mt[M].sum()))

salida = dict(entidades=ent_out,
              fisicas=tot(FIS), juridicas=tot(JUR), total=tot(FIS | JUR),
              registros=int(i), registros_mora=int(mo.sum()), n_entidades=NE,
              registros_fisicas=int(FIS.sum()), registros_juridicas=int(JUR.sum()),
              registros_mora_fisicas=int((FIS & mo).sum()),
              registros_mora_juridicas=int((JUR & mo).sum()))
pickle.dump(salida, open(SALIDA, 'wb'))
F = salida['fisicas']
print(f"  personas humanas: {F['pu']:,} | en mora {F['pm']:,} ({F['pm']/F['pu']*100:.1f}%) "
      f"| mora s/monto {F['mm']/F['mc']*100:.1f}%", flush=True)
