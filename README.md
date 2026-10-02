# La mora argentina: análisis de microdatos de la Central de Deudores

**Lic. Pablo Santiago Martínez Soler** — Economista (UBA), Maestría en Economía Aplicada (UBA, en curso)

Procesamiento completo de la Central de Deudores del Sistema Financiero del BCRA
para **junio, julio y agosto de 2026**: hasta 41.518.574 registros individuales
por mes y 519 entidades acreedoras clasificadas.

El objetivo es responder con datos, y no con estimaciones agregadas, cuatro
preguntas que el debate público sobre el aumento de la morosidad mezcla
permanentemente: **cuántas personas están en mora, quién les prestó, bajo qué
régimen legal, y hacia dónde va la curva.**

---

## Cuatro hallazgos

### 1. No hay diez millones de morosos

La Central de Deudores no registra personas: registra **relaciones entre un
deudor y una entidad**. Una persona que debe en un banco, en una billetera y en
una casa de electrodomésticos aparece tres veces.

| | agosto 2026 |
|---|---|
| Registros en situación irregular | 10.291.348 |
| CUIT únicos en mora | 6.013.788 |
| **Personas humanas en mora** | **5.967.952** |
| Factor de sobreconteo | 1,72x |
| Tasa sobre personas humanas registradas | 28,2% |
| **Morosos sobre población adulta (18+)** | **17,1%** |

### 2. Cuatro de cada diez adultos no tienen crédito

Las personas humanas con alguna financiación registrada son el 60,6% de los
adultos. **13.789.394 adultos, el 39,4%, no tienen crédito de ningún tipo.** No
es que no lo paguen: no lo tienen. El problema argentino de fondo no es que
haya demasiado crédito, es que hay muy poco.

### 3. Hogares y empresas son dos universos distintos

| | Personas humanas | Sociedades |
|---|---|---|
| Registros | 41.028.548 | 490.026 |
| CUIT únicos | 21.181.595 | 285.452 |
| Cartera | $98,25 bill. | $90,36 bill. |
| **Tasa de mora sobre monto** | **15,8%** | **3,6%** |

Las sociedades son el 1,2% de los registros pero casi la mitad del dinero
prestado, y casi no entran en mora. Mezclarlas baja artificialmente la tasa del
sistema del 15,8% al 9,9%. **Salvo indicación expresa, todas las cifras de este
repositorio son de personas humanas.**

### 4. El corte normativo separa dos sistemas

Agrupando por el régimen legal bajo el cual cada entidad reporta —que es
objetivo, porque surge del código de entidad y no del criterio del analista:

| Régimen | Códigos | Entidades | Tasa de mora s/ monto |
|---|---|---|---|
| Entidades financieras — bancos | `00xxx` | 59 | **12,4%** |
| Compañías financieras y cajas de crédito | `44/45/65xxx` | 13 | 10,7% |
| Proveedores no financieros de crédito | `55/70/71/72xxx` | 383 | **31,4%** |
| Fideicomisos financieros | `10xxx` | 13 | 100%* |
| SGR y fondos de garantía | `50/51xxx` | 50 | 82,3%* |

\* No comparables: los fideicomisos de recupero adquieren cartera que ya venía
impaga y las SGR informan garantías ya ejecutadas. Ver
[METODOLOGIA.md](docs/METODOLOGIA.md).

Medido sobre la misma cartera de hogares, el sistema con exigencia de capital y
previsionamiento prudencial tiene 12,4% de mora. El que solo debe registrarse e
informar, 31,4%.

---

## La serie: qué cambió entre junio y agosto

| | junio | julio | agosto | Δ |
|---|---|---|---|---|
| Personas humanas en mora | 5.875.113 | 5.940.912 | 5.967.952 | +92.839 |
| Tasa sobre personas | 28,07% | 28,24% | 28,18% | +0,11 pp |
| Tasa sobre monto | 15,55% | 15,78% | 15,79% | +0,24 pp |
| Morosos / adultos | 16,80% | 16,99% | 17,07% | +0,27 pp |
| Adultos sin crédito | 40,14% | 39,85% | **39,43%** | **−0,71 pp** |

**Julio subió 0,23 puntos; agosto subió 0,01.** El deterioro prácticamente se
detuvo, y medido sobre personas la tasa incluso bajó levemente. Al mismo tiempo
entraron 249 mil personas nuevas al sistema de crédito.

| Categoría | junio | julio | agosto | Δ |
|---|---|---|---|---|
| Banco Nación | 8,0% | 8,1% | 8,4% | +0,4 |
| Bancos provinciales | 12,2% | 12,5% | 13,0% | +0,8 |
| **Bancos privados** | 14,4% | 14,7% | **14,3%** | **−0,2** |
| Fintech y billeteras | 20,2% | 20,9% | 20,6% | +0,4 |
| Tarjetas no bancarias | 25,5% | 26,2% | 26,5% | +1,0 |
| Crédito rápido | 39,8% | 40,7% | 40,6% | +0,8 |
| **Electrodomésticos y retail** | 43,1% | 43,4% | **44,0%** | +0,9 |

La mejora llegó donde hay refinanciación activa y no llegó donde no la hay.

**El mecanismo importa:** en los bancos privados, el monto en mora bajó mientras
la cantidad de clientes en mora subía. Más gente en mora, menos plata en mora.
Los saldos grandes están saliendo por refinanciación o pase a pérdida mientras
siguen entrando deudores nuevos de monto chico.

**Advertencia:** no toda baja de tasa es una mejora. Ualá pasó de 22,5% a 12,6%
de mora en monto, pero con la cartera constante y los deudores en mora en
aumento (61.463 → 63.443). Eso es castigo o venta de cartera, no mejor
originación. Conviene mirar siempre las dos tasas antes de leer una baja como
mejora.

---

## Validación externa

Restringido a bancos, este procesamiento reproduce los agregados que el BCRA
publica por otra vía:

| | este trabajo (familias) | este trabajo (empresas) |
|---|---|---|
| junio | 12,4% | 3,0% |
| julio | 12,5% | 3,1% |
| agosto | 12,4% | 3,4% |

El *Informe sobre Bancos* del BCRA de junio 2026 reporta 12,8% en familias y
3,5% en empresas.

---

## Cuadro general por tipo de prestamista — agosto 2026

| Tipo de prestamista | Mora ($ bill.) | Personas | Tasa s/ monto | Tasa s/ personas | Créd. prom. impago |
|---|---|---|---|---|---|
| Bancos privados | 5,79 | 2.226.972 | 14,3% | 17,7% | $2.598.707 |
| Bancos provinciales | 2,26 | 609.362 | 13,0% | 13,3% | $3.715.354 |
| Banco Nación | 1,74 | 400.032 | 8,4% | 16,7% | $4.352.975 |
| Crédito rápido de alto riesgo | 1,61 | 2.006.795 | 40,6% | 47,3% | $800.836 |
| Tarjetas de crédito no bancarias | 1,54 | 1.283.674 | 26,5% | 26,6% | $1.200.920 |
| Fintech y billeteras | 0,97 | 2.158.086 | 20,6% | 22,6% | $450.381 |
| **Electrodomésticos y retail** | 0,69 | 574.288 | **44,0%** | 33,8% | $1.198.347 |
| Financieras de marca / prendarias | 0,11 | 10.342 | 4,1% | 4,7% | $10.433.378 |
| Compra de carteras en mora\* | 0,74 | 914.815 | 100% | 100% | $803.636 |
| SGR y fondos de garantía\* | 0,07 | 39.168 | 82,3% | 96,1% | $1.665.550 |
| **Total — personas humanas** | **15,51** | **5.967.952** | **15,8%** | **28,2%** | $2.598.840 |

La suma de personas por categoría excede el total porque una misma persona puede
estar en mora en más de un tipo de prestamista. El total está deduplicado por CUIT.

---

## Estructura del repositorio

```
├── articulo/
│   ├── articulo-mora-argentina.html    Artículo completo con gráficos
│   └── articulo-mora-argentina.pdf     Versión imprimible
├── datos/
│   ├── serie-sistema.csv               Los tres meses, totales del sistema
│   ├── serie-por-categoria.csv         Los tres meses, por tipo de prestamista
│   ├── serie-por-regimen.csv           Los tres meses, por régimen legal
│   ├── serie-por-entidad.csv           Las 549 entidades, tres meses y delta
│   ├── entidades-202608.csv            Detalle completo del último mes
│   ├── resumen-por-categoria-202608.csv
│   ├── denominadores-202608.csv
│   └── entidades-fuera-del-analisis-202608.csv
├── graficos/
│   ├── index.html                      Todos los gráficos en una página
│   └── *.svg                           Siete gráficos, vectoriales y autocontenidos
├── placas-reel/                        Placas 1080×1920 para redes
├── scripts/
│   ├── 00_extraer_maestro.py           Maestro de entidades desde el .7z
│   ├── 01_procesar_mes.py              Procesamiento en streaming de un mes
│   ├── 02_clasificar_entidades.py      Clasificación en ambas taxonomías
│   ├── 03_generar_salidas.py           CSV de series y del mes corriente
│   ├── 04_generar_graficos.py          Gráficos SVG desde los CSV
│   └── 05_generar_placas_reel.py       Placas verticales para redes
└── docs/
    ├── METODOLOGIA.md                  Criterios, layout, limitaciones
    ├── COMO-OBTENER-LOS-DATOS.md       Acceso a la fuente primaria
    └── GUION-REEL.md                   Guion del video de divulgación
```

---

## Reproducir el análisis

Los microdatos **no están en este repositorio** y no pueden estarlo: contienen
CUIT y razón social de personas humanas, y su descarga exige firmar una
declaración jurada de no divulgación. Ver
[COMO-OBTENER-LOS-DATOS.md](docs/COMO-OBTENER-LOS-DATOS.md).

```bash
pip install -r requirements.txt

# un mes
python scripts/00_extraer_maestro.py /ruta/202608DEUDORES.7Z maestro.pkl
python scripts/01_procesar_mes.py    /ruta/202608DEUDORES.7Z d08.pkl

# clasificar con todos los meses, en orden cronologico
python scripts/02_clasificar_entidades.py maestro.pkl d06.pkl d07.pkl d08.pkl

# salidas
python scripts/03_generar_salidas.py
python scripts/04_generar_graficos.py
```

Los scripts leen `deudores.txt` **directamente desde el `.7z`**, sin
descomprimir los 7 GB a disco. Cada mes tarda unos dos minutos y necesita
aproximadamente 1,5 GB de memoria.

Los gráficos se generan desde los CSV de `datos/`, así que ese último paso corre
sin necesidad de tener los microdatos.

---

## Sobre la clasificación

El repositorio contiene **dos taxonomías paralelas** y la distinción importa:

- El **régimen de inscripción** es objetivo. Surge del código de entidad que
  asigna el BCRA según la ley bajo la cual la entidad reporta. No admite
  discrecionalidad.

- La **categoría comercial** es una construcción del autor según el modelo de
  negocio real. Cruza regímenes: "Fintech" incluye entidades inscriptas como
  banco (Ualá), como compañía financiera (Naranja X) y como proveedor no
  financiero (Mercado Pago).

La segunda es el punto más discutible del trabajo y por eso los listados están
explícitos en `scripts/02_clasificar_entidades.py`, uno por código de entidad,
para que puedan auditarse y corregirse. El criterio ante la duda fue asignar a
*crédito rápido*, de modo de no inflar las categorías de fintech y tarjetas con
entidades que solo comparten el nombre.

La categoría de cada entidad **se fija con el primer mes en que aparece** y se
mantiene después, para que la serie sea comparable.

Las conclusiones sobre el corte normativo no dependen de esta clasificación.

---

## Limitaciones

1. **No es un análisis causal.** Tres cortes mensuales consecutivos, sin
   variación exógena. La serie muestra la dirección del movimiento; no aísla la
   contribución de cada factor.

2. **Las bajas pueden ser saneamiento, no mejora.** Una caída de la mora en
   monto con la cartera constante y los deudores en mora en aumento indica
   castigo o venta de cartera. Mirar siempre las dos tasas.

3. **Campos no aplicables.** Refinanciaciones, situación jurídica e
   irrecuperabilidad son *no aplicables* para proveedores no financieros, SGR y
   plataformas P2P. El análisis de refinanciaciones solo puede hacerse sobre
   entidades financieras.

4. **Calidad de la información.** Los prestamistas más chicos informan de manera
   irregular, tardía o incompleta. El padrón de informantes pasó de 540 a 519
   entidades entre junio y agosto.

5. **Posible doble conteo por securitización.** Si una entidad originante cede
   cartera a un fideicomiso y ambas la informan, el mismo crédito aparece dos
   veces. No se testeó el solapamiento.

---

## Fuentes

- Banco Central de la República Argentina — Central de Deudores del Sistema
  Financiero. Archivos `202606`, `202607` y `202608`.
- INDEC — Proyecciones de población por edad simple sobre el Censo 2022.
  Población total 2026: 46.466.688; población de 18 años o más: 34.970.989.

## Licencia

El código y los datos derivados se publican para su auditoría y reutilización.
Los microdatos originales pertenecen al BCRA y están sujetos a las condiciones
de la declaración jurada firmada al descargarlos.
