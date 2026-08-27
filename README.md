# La mora argentina: análisis de microdatos de la Central de Deudores

**Lic. Pablo Santiago Martínez Soler** — Economista (UBA), Maestría en Economía Aplicada (UBA, en curso)

Procesamiento completo de la base de la Central de Deudores del Sistema Financiero
del BCRA correspondiente a **junio de 2026**: 40.837.262 registros individuales,
507 entidades acreedoras clasificadas.

El objetivo es responder con datos, y no con estimaciones agregadas, tres preguntas
que el debate público sobre el aumento de la morosidad mezcla permanentemente:
**cuántas personas están en mora, quién les prestó, y bajo qué régimen legal.**

---

## Hallazgo principal: no hay diez millones de morosos

La Central de Deudores no registra personas: registra **relaciones entre un deudor y
una entidad**. Una persona que debe en un banco, en una billetera y en una casa de
electrodomésticos aparece tres veces.

| | |
|---|---|
| Registros en situación irregular | 10.039.067 |
| CUIT únicos en mora | 5.918.384 |
| **Personas humanas en mora** | **5.875.113** |
| Sociedades en mora | 43.271 |
| Factor de sobreconteo | 1,70x |
| **Tasa sobre personas humanas registradas** | **28,1%** |
| **Tasa de mora sobre monto — hogares** | **15,6%** |
| Tasa de mora sobre monto — sociedades | 3,2% |
| Morosos sobre población adulta (18+) | 16,8% |
| Adultos sin ninguna financiación registrada | 40,1% (14,04 M) |

La cifra de "diez millones de morosos" que circuló en agosto de 2026 surge de sumar
registros sin deduplicar.

---

## Segundo hallazgo: el corte normativo separa dos sistemas

Agrupando por el régimen legal bajo el cual cada entidad reporta —que es objetivo,
porque surge del código de entidad y no del criterio del analista:

| Régimen | Códigos | Entidades | Tasa de mora s/ monto |
|---|---|---|---|
| Entidades financieras — bancos | `00xxx` | 60 | **12,4%** |
| Compañías financieras y cajas de crédito | `44/45/65xxx` | 13 | 9,9% |
| Proveedores no financieros de crédito | `55/70/71/72xxx` | 372 | **30,9%** |
| Fideicomisos financieros | `10xxx` | 11 | 100%* |
| SGR y fondos de garantía | `50/51xxx` | 51 | 78,3%* |

\* No comparables: los fideicomisos de recupero adquieren cartera que ya venía impaga
y las SGR informan garantías ya afrontadas. Ver [METODOLOGIA.md](docs/METODOLOGIA.md).

Medido sobre la misma cartera de hogares, el sistema con exigencia de capital y
previsionamiento prudencial tiene 12,4% de mora. El que solo debe registrarse e
informar, 30,9%.

**Validación:** restringido a bancos, este procesamiento da 12,4% en personas humanas
y 3,0% en sociedades. El *Informe sobre Bancos* del BCRA de junio 2026 reporta 12,8%
en familias y 3,5% en empresas.

---

## Tercer hallazgo: por tipo de prestamista

| Tipo de prestamista | Mora ($ bill.) | Personas únicas | Tasa s/ monto | Tasa s/ personas | Crédito prom. impago |
|---|---|---|---|---|---|
| Bancos privados | 7,38 | 1.781.347 | 7,5% | 17,7% | $3.394.973 |
| Bancos provinciales | 2,53 | 566.836 | 9,2% | 12,4% | $4.408.552 |
| Banco Nación | 2,05 | 380.597 | 6,0% | 15,8% | $5.374.932 |
| Crédito rápido de alto riesgo | 1,64 | 1.544.223 | 34,4% | 47,0% | $825.584 |
| Tarjetas de crédito no bancarias | 1,46 | 1.213.147 | 25,5% | 25,8% | $1.164.598 |
| Fintech y billeteras | 0,91 | 1.781.011 | 19,4% | 22,5% | $451.159 |
| **Electrodomésticos y retail** | 0,69 | 556.852 | **43,1%** | 33,1% | $1.164.432 |
| Financieras de marca / prendarias | 0,13 | 9.790 | 3,3% | 4,6% | $13.445.113 |
| Compra de carteras en mora\* | 0,66 | 912.228 | 100% | 100% | $671.297 |
| SGR y fondos de garantía\* | 0,16 | 58.824 | 81,2% | 95,5% | $2.671.292 |
| **Total sistema (deduplicado)** | **17,61** | **5.918.384** | **9,7%** | **27,9%** | $2.975.099 |

La suma de personas por categoría (8.804.855) excede el total del sistema porque una
misma persona puede estar en mora en más de un tipo de prestamista. El total está
deduplicado por CUIT.

---

## Validación externa

Los resultados de este procesamiento son consistentes con los informes agregados
publicados por el propio BCRA, que se construyen por otra vía:

| Indicador | Informe BCRA | Este trabajo |
|---|---|---|
| Mora en venta de electrodomésticos | 44,3% (feb-2026) | 43,1% (jun-2026) |
| Mora en proveedores no financieros | 26,9% (feb-2026) | 29,1% (jun-2026) |

---

## Estructura del repositorio

```
├── articulo/
│   └── articulo-mora-argentina.html    Artículo completo con gráficos
├── datos/
│   ├── entidades-clasificadas.csv      Las 507 entidades, una por fila
│   ├── entidades-excluidas.csv         34 entidades que informan en cero
│   ├── resumen-por-categoria-comercial.csv
│   ├── resumen-por-regimen-inscripcion.csv
│   ├── mora-por-categoria-comercial.xlsx
│   └── mora-por-regimen-inscripcion.xlsx
├── graficos/
│   ├── index.html                      Todos los gráficos en una página
│   └── *.svg                           Seis gráficos, vectoriales y autocontenidos
├── scripts/
│   ├── 01_procesar_base.py             Lectura y agregación de los microdatos
│   ├── 02_clasificar_entidades.py      Clasificación en ambas taxonomías
│   └── 03_generar_graficos.py          Gráficos SVG a partir de los CSV
└── docs/
    ├── METODOLOGIA.md                  Criterios, layout, limitaciones
    └── COMO-OBTENER-LOS-DATOS.md       Acceso a la fuente primaria
```

---

## Reproducir el análisis

Los microdatos **no están en este repositorio** y no pueden estarlo: contienen CUIT y
razón social de personas humanas, y su descarga exige firmar una declaración jurada de
no divulgación. Ver [COMO-OBTENER-LOS-DATOS.md](docs/COMO-OBTENER-LOS-DATOS.md).

```bash
pip install -r requirements.txt
python scripts/01_procesar_base.py --zip /ruta/a/deudores.zip
python scripts/02_clasificar_entidades.py --zip /ruta/a/deudores.zip
python scripts/03_generar_graficos.py
```

Los gráficos se generan desde los CSV de `datos/`, así que ese último paso corre
sin necesidad de tener los microdatos.

El primer paso tarda entre tres y cinco minutos y requiere aproximadamente 1 GB de
memoria para la deduplicación por CUIT.

---

## Sobre la clasificación

El repositorio contiene **dos taxonomías paralelas** y la distinción importa:

- El **régimen de inscripción** es objetivo. Surge del código de entidad que asigna
  el BCRA según la ley bajo la cual la entidad reporta. No admite discrecionalidad.

- La **categoría comercial** es una construcción del autor según el modelo de negocio
  real. Cruza regímenes: "Fintech" incluye entidades inscriptas como banco (Ualá),
  como compañía financiera (Naranja X) y como proveedor no financiero (Mercado Pago).

La segunda es el punto más discutible del trabajo y por eso los listados están
explícitos en `scripts/02_clasificar_entidades.py`, uno por código de entidad, para
que puedan auditarse y corregirse. El criterio ante la duda fue asignar a *crédito
rápido*, de modo de no inflar las categorías de fintech y tarjetas con entidades que
solo comparten el nombre.

Las conclusiones sobre el corte normativo no dependen de esta clasificación.

---

## Limitaciones

1. **No es un análisis causal.** Los datos son descriptivos y de un solo corte
   temporal. Permiten mostrar heterogeneidad entre segmentos, no aislar la
   contribución de cada factor al deterioro.

2. **Campos no aplicables.** El régimen informativo del BCRA establece que
   refinanciaciones, situación jurídica e irrecuperabilidad son *no aplicables*
   para proveedores no financieros, SGR y plataformas P2P. El análisis de
   refinanciaciones solo puede hacerse sobre entidades financieras.

3. **Calidad de la información.** Los prestamistas más chicos informan de manera
   irregular, tardía o incompleta. Algunos informan el saldo caído sin la cartera
   total, lo que infla artificialmente su tasa de mora.

4. **Posible doble conteo por securitización.** Si una entidad originante cede
   cartera a un fideicomiso y ambas la informan, el mismo crédito aparece dos veces.
   No se testeó el solapamiento entre fideicomisos y originantes.

---

## Fuentes

- Banco Central de la República Argentina — Central de Deudores del Sistema
  Financiero. Fecha de información: **junio de 2026** (archivo `202606`).
- INDEC — Proyecciones de población por edad simple sobre el Censo 2022.
  Población total 2026: 46.466.688; población de 18 años o más: 34.970.989.

## Licencia

El código y los datos derivados se publican para su auditoría y reutilización.
Los microdatos originales pertenecen al BCRA y están sujetos a las condiciones de
la declaración jurada firmada al descargarlos.
