# Cómo obtener los microdatos

Los microdatos **no están incluidos en este repositorio** y no pueden estarlo.

## Por qué no están acá

El archivo contiene número de identificación fiscal y razón social de personas
humanas y jurídicas, con el detalle de sus deudas y su situación crediticia. Su
descarga exige firmar una **declaración jurada de no divulgación de información
personal**. Publicarlos infringiría esa declaración y la normativa de protección
de datos personales.

Por eso el `.gitignore` excluye explícitamente `*.7z`, `deudores.zip`,
`deudores.txt`, `Maeent.txt`, `Nomdeu.txt` y los `.pkl` intermedios.
**Verificá que esa exclusión siga vigente antes de cada commit.**

Lo que sí se publica son los **agregados por entidad**, que no permiten
identificar a ninguna persona.

## Pasos para descargarlos

1. Tramitar **Clave Fiscal nivel 3** si no se la tiene.
2. Acceder al sitio del BCRA y solicitar el alta para microdatos de la Central
   de Deudores del Sistema Financiero.
3. Firmar la declaración jurada de no divulgación de información personal.
4. Descargar el archivo del período de interés. Se publica mensualmente, con
   nomenclatura `AAAAMMDEUDORES.7Z`.

El procedimiento y la ubicación exacta del formulario cambian con el tiempo;
conviene verificarlos en el sitio del BCRA al momento de la descarga.

## Qué contiene la descarga

| Archivo | Contenido |
|---|---|
| `deudores.txt` | Base principal, ancho fijo. ~7 GB descomprimido |
| `Maeent.txt` | Maestro de entidades: código y razón social. **Codificado en latin-1** |
| `Nomdeu.txt` | Nomenclatura de deudores no empadronados |
| `LEAME DEUDORES.pdf` | Instructivo con el layout completo y las definiciones |
| `Fecha_Proceso_AAAAMMDD.txt` | Fecha de proceso |

El instructivo `LEAME DEUDORES.pdf` es la referencia autorizada para el layout
y para saber qué campos son *no aplicables* según el tipo de entidad informante.

## No hace falta descomprimirlo

Los scripts leen `deudores.txt` **en streaming desde el `.7z`** usando
`libarchive`, así que no es necesario escribir los 7 GB a disco:

```bash
python scripts/00_extraer_maestro.py /ruta/202608DEUDORES.7Z maestro.pkl
python scripts/01_procesar_mes.py    /ruta/202608DEUDORES.7Z d08.pkl
```

Si preferís descomprimirlo de todos modos:

```bash
sudo apt install p7zip-full
7z x 202608DEUDORES.7Z
```

## Agregar un mes nuevo a la serie

```bash
# 1. maestro actualizado (el padron cambia mes a mes)
python scripts/00_extraer_maestro.py /ruta/202609DEUDORES.7Z m09.pkl

# 2. procesar el mes
python scripts/01_procesar_mes.py /ruta/202609DEUDORES.7Z d09.pkl

# 3. reclasificar incluyendo el mes nuevo, en orden cronologico
python scripts/02_clasificar_entidades.py maestro.pkl d06.pkl d07.pkl d08.pkl d09.pkl

# 4. regenerar CSV y graficos
python scripts/03_generar_salidas.py
python scripts/04_generar_graficos.py
```

El paso 3 debe recibir los meses **en orden cronológico**: la categoría de cada
entidad se fija con el primero en que aparece.

## Verificación

Al procesar los meses de 2026 los scripts deberían reproducir estos totales:

```
                            junio         julio        agosto
Registros              40.848.459    41.055.292    41.518.574
Personas humanas       20.932.724    21.034.369    21.181.595
   en mora              5.875.113     5.940.912     5.967.952
   tasa                    28,07%        28,24%        28,18%
Mora s/ monto (hogares)   15,55%        15,78%        15,79%
Entidades                     540           526           519
```

Si los números no coinciden, revisar primero el encoding del maestro de
entidades (latin-1, no UTF-8) y las posiciones de los campos de ancho fijo.
