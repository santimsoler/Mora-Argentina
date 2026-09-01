# Metodología

Lic. Pablo Santiago Martínez Soler — Economista (UBA)

## 1. Fuente y alcance

Base completa de la Central de Deudores del Sistema Financiero del BCRA,
archivo `202606` (junio de 2026).

| | |
|---|---|
| Registros procesados | 40.837.262 |
| Personas únicas (CUIT/CUIL/CDI) | 21.217.101 |
| Entidades acreedoras clasificadas | 507 |
| Entidades excluidas | 34 |

## 2. Layout del archivo

`deudores.txt` es un archivo de ancho fijo. Las posiciones utilizadas
(base 0) son:

| Campo | Posición | Contenido |
|---|---|---|
| Código de entidad | 0–5 | Identifica la entidad y su régimen |
| Identificación | 13–24 | CUIT / CUIL / CDI del deudor |
| Situación | 27–29 | 1 a 5, o 9 = no aplicable |
| Monto | 29–41 | En miles de pesos, coma decimal |

El archivo `Maeent.txt` (maestro de entidades) está codificado en **latin-1**,
no en UTF-8. Leerlo como UTF-8 produce un maestro vacío o corrupto.

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

Corresponde aproximadamente a más de 90 días de atraso en cartera de consumo.
Es el mismo criterio de "cartera irregular" que usa el BCRA en sus informes
agregados, lo que permite la validación cruzada.

## 4. Deduplicación: el punto crítico

**La Central registra relaciones deudor-entidad, no personas.** Cada fila es la
situación de una persona *en una entidad*. Una persona con deudas en tres
entidades genera tres filas.

| | |
|---|---|
| Registros en mora | 10.039.067 |
| Personas únicas en mora | 5.918.384 |
| Factor de sobreconteo | 1,70x |
| Relaciones por persona (promedio) | 1,93 |

Consecuencias metodológicas:

- **El total del sistema debe deduplicarse por CUIT.** 5.918.384 personas, no
  10 millones.
- **Los totales por categoría no pueden sumarse.** La suma de personas únicas
  de las diez categorías da 8.804.855, un 49% más que el total real, porque una
  persona en mora en un banco y en una fintech pertenece legítimamente a ambas
  filas. Esto no es un error: es la naturaleza del dato. Pero impide sumar.
- Las tasas por categoría son válidas dentro de cada categoría.

## 4.bis Denominadores poblacionales

La tasa de mora admite tres denominadores distintos y conviene no confundirlos,
porque dan números muy diferentes y sostienen afirmaciones diferentes:

| Denominador | Base | Morosos | Tasa |
|---|---|---|---|
| Registros en la Central | 40.837.262 | 10.039.067 | 24,6% |
| Personas registradas en la Central | 21.217.101 | 5.918.384 | **27,9%** |
| Población adulta (18+) | 34.970.989 | 5.918.384 | **16,9%** |

El primero es incorrecto para hablar de personas. El segundo es el que usan los
informes del BCRA y el que corresponde para medir la salud de la cartera. El
tercero es el que corresponde cuando se afirma algo sobre "los argentinos".

Del tercer denominador surge además que las personas con alguna financiación
registrada son el 60,7% de los adultos: **13.753.888 adultos, el 39,3%, no tienen
crédito registrado de ningún tipo.**

La población adulta proviene de las proyecciones por edad simple del INDEC sobre
el Censo 2022 (población total 2026: 46.466.688), no de la Central de Deudores.

## 5. Las dos taxonomías

### 5.1 Régimen de inscripción (objetivo)

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

### 5.2 Categoría comercial (analítica)

Construcción del autor según modelo de negocio. Reglas en orden de prioridad:

1. SGR o fondo de garantía → por razón social
2. Retail identificado → por listado explícito
3. Fideicomiso con mora ≥ 95% → compra de carteras
4. Mora 100% en monto **y** en personas → compra de carteras
5. Fintech verificable (app, billetera, servicios financieros más allá del crédito) → listado
6. Emisor verificable de plástico → listado
7. Resto → crédito rápido de alto riesgo

La regla 7 es deliberada. Ante la duda sobre el modelo de negocio, la entidad va
a crédito rápido, para no inflar las categorías de fintech y tarjetas con
entidades que solo comparten el nombre comercial. Los listados están en
`scripts/02_clasificar_entidades.py`, uno por código.

## 6. Categorías que no son comparables

Dos categorías tienen tasas de mora que **no miden desempeño crediticio**:

**Compra de carteras en mora (100%).** Son fideicomisos y vehículos de recupero
que adquieren cartera que ya estaba impaga. Su tasa del 100% refleja su objeto
social. Sumarlos al problema como si hubieran originado mal el crédito es contar
dos veces el mismo default.

**SGR y fondos de garantía (81,2%).** Informan *garantías afrontadas*: el monto
aparece cuando la sociedad ya pagó por el socio incumplidor. Los avales vigentes
y sanos no están en el denominador. Son garantes, no prestamistas, y su
exposición no debe sumarse como crédito otorgado.

En los cuadros del artículo estas dos filas aparecen atenuadas por ese motivo.

## 7. Exclusiones

34 entidades informan cartera y/o cantidad de deudores en cero pese a figurar
como acreedores. No son clasificables por métricas ni computables en las tasas.
Se listan en `datos/entidades-excluidas.csv`.

## 8. Limitaciones

**No es un análisis causal.** Un solo corte temporal, sin variación exógena.
Muestra heterogeneidad entre segmentos; no aísla la contribución de cada factor.
La brecha entre 7,4% bancario y 29,1% no bancario admite varias explicaciones
simultáneas: población de distinto riesgo, productos distintos, tasas distintas,
expansión más agresiva, criterios de clasificación no sujetos a igual supervisión.

**Campos no aplicables.** Refinanciaciones, situación jurídica e irrecuperabilidad
son *no aplicables* para proveedores no financieros, SGR y plataformas P2P. El
análisis de refinanciaciones solo puede hacerse sobre entidades financieras —
precisamente el segmento donde el problema es menos agudo.

**Calidad de la información.** Los prestamistas más chicos informan de manera
irregular, tardía o incompleta. Algunos informan solo el saldo caído sin la
cartera total, lo que infla artificialmente su tasa. Toda lectura de entidades no
bancarias pequeñas debe hacerse con esa advertencia.

**Securitización.** Si una entidad originante cede cartera a un fideicomiso y
ambas la informan, el mismo crédito se cuenta dos veces. No se testeó el
solapamiento de CUIT entre fideicomisos y originantes. Es la verificación
pendiente más relevante.

**Sin apertura por producto.** La base no distingue tipo de línea. No permite
comparar, por ejemplo, la mora de un préstamo personal bancario contra la de un
adelanto de una billetera.
