# Metodología

Lic. Pablo Santiago Martínez Soler — Economista (UBA)

## 1. Fuente y alcance

Bases completas de la Central de Deudores del Sistema Financiero del BCRA,
archivos `202606`, `202607` y `202608`.

| | junio | julio | agosto |
|---|---|---|---|
| Registros procesados | 40.848.459 | 41.055.292 | 41.518.574 |
| Personas humanas registradas | 20.932.724 | 21.034.369 | 21.181.595 |
| Sociedades registradas | 285.195 | 285.939 | 285.452 |
| Entidades acreedoras con registros | 540 | 526 | 519 |

Las cifras del artículo corresponden a **agosto de 2026**, el último dato
disponible, salvo donde se presenta la serie.

## 2. Layout del archivo

`deudores.txt` es un archivo de ancho fijo de aproximadamente 7 GB. Las
posiciones utilizadas (base 0) son:

| Campo | Posición | Contenido |
|---|---|---|
| Código de entidad | 0–5 | Identifica la entidad y su régimen |
| Identificación | 13–24 | CUIT / CUIL / CDI del deudor |
| Situación | 27–29 | 1 a 5, o 9 = no aplicable |
| Monto | 29–41 | En miles de pesos, coma decimal |

Dos detalles que hacen fallar el procesamiento si se pasan por alto:

- `Maeent.txt` (maestro de entidades) está codificado en **latin-1**, no en
  UTF-8. Leerlo como UTF-8 devuelve un maestro vacío o corrupto.
- El archivo viene en `.7z`. Los scripts lo leen **en streaming** con
  `libarchive`, sin descomprimir los 7 GB a disco.

## 3. Definición de mora

Se considera moroso a quien registra **situación 3, 4 o 5**:

| Situación | Denominación |
|---|---|
| 1 | Normal |
| 2 | Con seguimiento especial / riesgo bajo |
| **3** | **Con problemas / riesgo medio** |
| **4** | **Con alto riesgo de insolvencia** |
| **5** | **Irrecuperable** |
| 9 | No aplicable |

Corresponde aproximadamente a más de 90 días de atraso en cartera de consumo,
y es el mismo criterio de "cartera irregular" que usa el BCRA en sus informes
agregados, lo que permite la validación cruzada de la sección 9.

## 4. Deduplicación: el punto crítico

**La Central registra relaciones deudor-entidad, no personas.** Cada fila es la
situación de una persona *en una entidad*. Una persona con deudas en tres
entidades genera tres filas.

| | junio | julio | agosto |
|---|---|---|---|
| Registros en mora | 10.039.067 | 10.199.629 | 10.291.348 |
| CUIT únicos en mora | 5.918.384 | 5.984.634 | 6.013.788 |
| Personas humanas en mora | 5.875.113 | 5.940.912 | 5.967.952 |
| Factor de sobreconteo | 1,70x | 1,72x | 1,72x |

Consecuencias metodológicas:

- **El total del sistema debe deduplicarse por CUIT.** No son diez millones de
  morosos.
- **Los totales por categoría no pueden sumarse.** Una persona en mora en un
  banco y en una fintech pertenece legítimamente a ambas filas. Esto no es un
  error: es la naturaleza del dato, pero impide sumar.
- Las tasas por categoría son válidas dentro de cada categoría.

## 5. Denominadores

La tasa de mora admite cuatro denominadores distintos, que dan números muy
diferentes y sostienen afirmaciones diferentes (agosto de 2026):

| Denominador | Base | Morosos | Tasa |
|---|---|---|---|
| Registros deudor-entidad | 41.518.574 | 10.291.348 | 24,8% |
| CUIT únicos | 21.467.047 | 6.013.788 | 28,0% |
| Personas humanas registradas | 21.181.595 | 5.967.952 | **28,2%** |
| Población adulta 18+ | 34.970.989 | 5.967.952 | **17,1%** |

El primero es incorrecto para hablar de personas. El tercero es el que
corresponde para medir la salud de la cartera. El cuarto es el que corresponde
cuando se afirma algo sobre "los argentinos".

Del cuarto surge además que las personas humanas con alguna financiación
registrada son el 60,6% de los adultos: **13.789.394 adultos, el 39,4%, no
tienen crédito registrado de ningún tipo.**

La población adulta proviene de las proyecciones por edad simple del INDEC
sobre el Censo 2022 (población total 2026: 46.466.688), no de la Central de
Deudores.

## 6. Separación entre personas humanas y sociedades

El prefijo del CUIT distingue ambos universos sin residuo:

- **Personas humanas:** 20, 23, 24, 27 (y marginalmente 25 y 26)
- **Sociedades:** 30, 33, 34

La separación es indispensable. Las sociedades son el 1,3% de los registros
pero casi la mitad del dinero prestado, y su tasa de mora es cinco veces menor
que la de los hogares. Mezclarlas reduce artificialmente la tasa del sistema
del 15,8% al 9,9%.

Salvo indicación expresa, todas las cifras del análisis corresponden a
**personas humanas**.

## 7. Las dos taxonomías

### 7.1 Régimen de inscripción (objetivo)

Se deduce del prefijo del código de entidad:

| Prefijo | Régimen | Marco |
|---|---|---|
| `00xxx` | Entidades financieras — bancos | Ley 21.526 |
| `44xxx`, `45xxx`, `65xxx` | Compañías financieras y cajas de crédito | Ley 21.526, objeto limitado |
| `10xxx` | Fideicomisos financieros | Informa el fiduciario |
| `50xxx` | Sociedades de garantía recíproca | Ley 24.467 |
| `51xxx` | Fondos de garantía de carácter público | Ley 24.467 |
| `40xxx` | Plataformas de crédito entre particulares | Registro BCRA |
| `55xxx`, `70–72xxx` | Proveedores no financieros de crédito | Registro BCRA |

Diferencia sustantiva: las entidades financieras tienen capitales mínimos,
efectivo mínimo, previsionamiento obligatorio por situación de deudor y
supervisión in situ, y pueden captar depósitos del público. Los proveedores no
financieros solo deben registrarse, informar deudores y cumplir normas de
transparencia y protección al usuario; **no tienen exigencia de capital ni de
previsionamiento prudencial** y no captan depósitos.

### 7.2 Categoría comercial (analítica)

Construcción del autor según modelo de negocio. Reglas en orden de prioridad:

1. Banco Nación (código `00011`)
2. Bancos provinciales (listado explícito)
3. Financieras de marca automotriz o agrícola (listado explícito)
4. SGR o fondo de garantía → por razón social
5. Retail identificado → listado explícito
6. Fideicomiso con mora ≥ 95% → compra de carteras
7. Mora 100% en monto **y** en personas → compra de carteras
8. Fintech verificable (app, billetera, servicios más allá del crédito) → listado
9. Emisor verificable de plástico → listado
10. Código `00xxx` restante → bancos privados
11. Resto → crédito rápido de alto riesgo

La regla 11 es deliberada: ante la duda sobre el modelo de negocio, la entidad
va a crédito rápido, para no inflar las categorías de fintech y tarjetas con
entidades que solo comparten el nombre comercial. Los listados están en
`scripts/02_clasificar_entidades.py`, uno por código, para que puedan
auditarse y corregirse.

**La categoría se fija con el primer mes en que aparece la entidad** y se
mantiene en los meses siguientes. Evaluarla mes a mes haría que una entidad
saltara de categoría al cruzar el umbral de mora de las reglas 6 y 7, lo que
rompería la comparabilidad de la serie.

## 8. Categorías que no son comparables

Dos categorías tienen tasas de mora que **no miden desempeño crediticio**:

**Compra de carteras en mora (100%).** Fideicomisos y vehículos de recupero que
adquieren cartera que ya estaba impaga. Su tasa del 100% refleja su objeto
social. Sumarlos al problema como si hubieran originado mal el crédito es
contar dos veces el mismo default.

**SGR y fondos de garantía (82,3% en agosto).** Informan *garantías afrontadas*:
el monto aparece cuando la sociedad ya pagó por el socio incumplidor. Los
avales vigentes y sanos no están en el denominador. Son garantes, no
prestamistas, y su exposición no debe sumarse como crédito otorgado.

En los cuadros del artículo estas dos filas aparecen atenuadas por ese motivo,
y los gráficos las excluyen.

## 9. Validación externa

Restringido a bancos, este procesamiento reproduce los agregados que el BCRA
publica por otra vía:

| | este trabajo (familias) | este trabajo (empresas) |
|---|---|---|
| junio | 12,4% | 3,0% |
| julio | 12,5% | 3,1% |
| agosto | 12,4% | 3,4% |

El *Informe sobre Bancos* del BCRA para junio de 2026 reporta 12,8% en familias
y 3,5% en empresas. Dos metodologías independientes —la del BCRA sobre balances
agregados, esta sobre los microdatos deudor por deudor— llegan prácticamente al
mismo número.

## 10. Entidades fuera del análisis de hogares

23 entidades de agosto no tienen cartera de personas humanas. La mayoría son
bancos mayoristas que operan solo con empresas (Citibank, JPMorgan, BNP
Paribas) y SGR que avalan exclusivamente a sociedades. Quedan fuera del
análisis de hogares por construcción, no por un problema de calidad del dato.
Se listan en `datos/entidades-fuera-del-analisis-202608.csv`.

## 11. Limitaciones

**No es un análisis causal.** Tres cortes mensuales consecutivos, sin variación
exógena. La serie muestra la dirección del movimiento; no aísla la contribución
de cada factor. La brecha entre 12,4% bancario y 31,4% no bancario admite
varias explicaciones simultáneas: población de distinto riesgo, productos
distintos, tasas distintas, expansión más agresiva, criterios de clasificación
no sujetos a igual supervisión.

**Las bajas de tasa pueden ser saneamiento, no mejora.** Una caída de la mora
en monto con la cartera constante y los deudores en mora en aumento indica
castigo o venta de cartera pesada, no mejor comportamiento de pago. Es lo que
ocurre con Ualá entre junio y agosto (22,5% → 12,6% en monto, con los deudores
en mora subiendo de 61.463 a 63.443). Conviene mirar siempre las dos tasas
—monto y personas— antes de leer una baja como mejora.

**Campos no aplicables.** Refinanciaciones, situación jurídica e
irrecuperabilidad son *no aplicables* para proveedores no financieros, SGR y
plataformas P2P. El análisis de refinanciaciones solo puede hacerse sobre
entidades financieras, precisamente el segmento donde el problema es menos
agudo.

**Calidad de la información.** Los prestamistas más chicos informan de manera
irregular, tardía o incompleta. Algunos informan solo el saldo caído sin la
cartera total, lo que infla artificialmente su tasa.

**Securitización.** Si una entidad originante cede cartera a un fideicomiso y
ambas la informan, el mismo crédito se cuenta dos veces. No se testeó el
solapamiento de CUIT entre fideicomisos y originantes. Es la verificación
pendiente más relevante.

**Sin apertura por producto.** La base no distingue tipo de línea. No permite
comparar, por ejemplo, la mora de un préstamo personal bancario contra la de un
adelanto de una billetera.

**Altas y bajas de entidades.** El padrón cambia mes a mes. Entre junio y
agosto dejaron de informar algunas entidades y aparecieron otras, lo que afecta
marginalmente los agregados por categoría. Los movimientos están en
`datos/serie-por-entidad.csv`, donde las celdas vacías indican que la entidad
no informó ese mes.
