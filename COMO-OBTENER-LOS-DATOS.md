# Cómo obtener los microdatos

Los microdatos **no están incluidos en este repositorio** y no pueden estarlo.

## Por qué no están acá

El archivo contiene número de identificación fiscal y razón social de personas
humanas y jurídicas, con el detalle de sus deudas y su situación crediticia. Su
descarga exige firmar una **declaración jurada de no divulgación de información
personal**. Publicarlos infringiría esa declaración y la normativa de protección
de datos personales.

Por eso el `.gitignore` excluye explícitamente `deudores.zip`, `deudores.txt`,
`Maeent.txt`, `Nomdeu.txt` y los archivos `.7z` originales. **Verificá que esa
exclusión siga vigente antes de cada commit.**

Lo que sí se publica son los **agregados por entidad**, que no permiten
identificar a ninguna persona.

## Pasos para descargarlos

1. Tramitar **Clave Fiscal nivel 3** si no se la tiene.
2. Acceder al sitio del BCRA y solicitar el alta para microdatos de la Central
   de Deudores del Sistema Financiero.
3. Firmar la declaración jurada de no divulgación de información personal.
4. Descargar el archivo correspondiente al período de interés. Se publica
   mensualmente, con nomenclatura `AAAAMM` — para este trabajo, `202606`.

El procedimiento y la ubicación exacta del formulario cambian con el tiempo;
conviene verificarlos en el sitio del BCRA al momento de la descarga.

## Qué contiene la descarga

| Archivo | Contenido |
|---|---|
| `deudores.txt` | Base principal, ancho fijo. ~7 GB descomprimido |
| `Maeent.txt` | Maestro de entidades: código y razón social. **Codificado en latin-1** |
| `Nomdeu.txt` | Nomenclatura |
| `LEAME DEUDORES.pdf` | Instructivo con el layout completo y las definiciones |
| `Fecha_Proceso_AAAAMMDD.txt` | Fecha de proceso |

El instructivo `LEAME DEUDORES.pdf` es la referencia autorizada para el layout
y para saber qué campos son *no aplicables* según el tipo de entidad informante.

## Descompresión

El archivo original viene en formato `.7z`. En Linux:

```bash
sudo apt install p7zip-full
7z x 202606DEUDORES.7Z
```

Los scripts de este repositorio leen directamente desde un `.zip` sin
descomprimir, para evitar escribir 7 GB en disco.

## Verificación

Al procesar `202606` los scripts deberían reproducir estos totales:

```
Registros procesados        40.837.262
Personas únicas             21.217.101
Registros en mora           10.039.067
Personas únicas en mora      5.918.384
Factor de sobreconteo             1,70x
Tasa de mora s/ personas         27,9%
Tasa de mora s/ monto             9,7%
Entidades                           541
```

Si los números no coinciden, revisar primero el encoding del maestro de
entidades (latin-1, no UTF-8) y las posiciones de los campos de ancho fijo.
