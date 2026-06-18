# Verificacion de tablas y cromatogramas

Este documento describe el proyecto de verificacion de integridad de datos analiticos y el comportamiento actualizado del script `main_v1.py`.

## Contexto del proyecto

El proyecto permite auditar reportes analiticos generados en archivos `.docx`, comparando la informacion consolidada de una tabla de resultados contra el detalle individual de los cromatogramas. Esta verificacion aplica a secuencias analiticas de espectrometria de masas y busca detectar diferencias entre los datos reportados en ambos documentos.

## Objetivo

Validar automaticamente que los datos del **Archivo de Resultados Analiticos (Tabla/Resumen)** coincidan con los datos del **Archivo de Cromatogramas (Detalle)** para cada muestra procesada.

El flujo actualizado no utiliza LLM para decidir las coincidencias. La auditoria se realiza mediante reglas deterministicas en Python:

- Extrae datos estructurados de ambos archivos `.docx`.
- Compara campos clave muestra por muestra.
- Acepta coincidencias exactas de texto.
- Para valores numericos, tambien acepta equivalencias cercanas aunque esten expresadas en formatos distintos, por ejemplo `8.731e+05` y `873100`.
- Genera un reporte Markdown y, cuando es posible, una version PDF del mismo reporte.

## Script principal actualizado: `main_v1.py`

`main_v1.py` ejecuta una auditoria analitica en modo codigo puro.

### Entradas

El script recibe los siguientes argumentos:

| Argumento | Descripcion | Valor por defecto |
| :--- | :--- | :--- |
| `--tabla` | Ruta al archivo `.docx` con la tabla/resumen de resultados analiticos. | `datos/Tabla Secuencia 1-RE-EZPC.docx` |
| `--cromatograma` | Ruta al archivo `.docx` con el detalle de cromatogramas. | `datos/Cromatogramas Secuencia 1-RE-EZPC.docx` |
| `--output` | Ruta donde se guarda el reporte Markdown. Si se omite, se genera automaticamente en el mismo directorio del archivo de tabla. | Autogenerado |

Ejemplo de ejecucion:

```bash
python main_v1.py --tabla "datos/Tabla Secuencia 4-EZPC.docx" --cromatograma "datos/Cromatogramas Secuencia 4-EZPC.docx"
```

Si no se informa `--output`, el nombre del reporte se arma a partir del archivo de tabla y se guarda en el mismo directorio donde estan los DOCX. Por ejemplo:

```text
datos/reporte_auditoria_v1_Secuencia 4-EZPC.md
datos/reporte_auditoria_v1_Secuencia 4-EZPC.pdf
```

### Salidas

El script genera:

- Un reporte Markdown con el resumen de auditoria, la matriz de correspondencia y el detalle de inconsistencias.
- Un PDF equivalente usando `markdown_pdf`, salvo que ocurra un error durante la conversion. Las tablas del PDF usan CSS propio para evitar indentacion antes de la primera columna y mantener padding uniforme.
- Mensajes por consola indicando archivos procesados, estado de la auditoria y ubicacion del reporte final.

## Archivos de referencia

### 1. Archivo de Resultados Analiticos (Tabla/Resumen)

Documento tabular que consolida los datos de multiples muestras o inyecciones.

Contiene:

- **Informacion del analito**
  - Nombre del analito, por ejemplo `Analyte: X`.
  - Transiciones o masas, cuando estan presentes en el encabezado.
- **Metadatos globales del proceso**
  - `Data File`
  - `Result Table`
  - `Acquisition Date`
  - `Algorithm Used`
  - `Acquisition Method`
  - `Operator`
  - `Project`
  - `Instrument`
- **Tabla de muestras**
  - `Sample Name`
  - `Acquisition Date`
  - `Sample Type`
  - `Area (cps)`
  - `IS Area (cps)`
  - `RT (min)`
  - `Target Conc. (ng/mL)`
  - `Calculated Conc. (ng/mL)`

### 2. Archivo de Cromatogramas (Detalle)

Documento con informacion detallada por muestra. El extractor identifica cada muestra buscando tablas de metadatos que comienzan con `Sample Name` y luego toma la tabla de resultados inmediatamente posterior.

Contiene:

- **Metadatos de inyeccion**
  - `Sample Name`
  - `Batch Name`
  - `Acquisition Date`
  - `Acquisition Method`
  - `Project`
  - `Injection Volume`
  - `Sample Type`
  - `Dilution Factor`
  - `Vial`
  - `Instrument Name`
- **Resultados**
  - **Internal Standard**
    - `Name`
    - `Area (cps)`
    - `RT (min)`
    - `Calc. Conc. (ng/mL)`
    - `Calc. Conc.`
  - **Target Analyte**
    - `Name`
    - `Area (cps)`
    - `RT (min)`
    - `Calc. Conc. (ng/mL)`
    - `Accuracy (%)`

## Reglas de comparacion

La comparacion se realiza muestra por muestra, usando el orden extraido de ambos documentos. Cada muestra de la tabla se compara con la muestra correspondiente del archivo de cromatogramas.

El total de muestras auditadas se define como el menor valor entre:

- Cantidad de muestras extraidas de la tabla.
- Cantidad de muestras extraidas del cromatograma.

La funcion de comparacion aplica estas reglas:

1. Si ambos valores son identicos como texto, el campo se considera correcto.
2. Si no son identicos, intenta convertir ambos valores a numero.
3. Si ambos valores son numericos y son cercanos con una tolerancia relativa de `1e-4`, el campo se considera correcto.
4. Si ninguna regla coincide, se registra una inconsistencia.

## Matriz de correspondencia auditada

| Campo logico | Ubicacion en Tabla/Resumen | Ubicacion en Cromatograma/Detalle |
| :--- | :--- | :--- |
| `Sample Name` | Columna `Sample Name` | Metadatos de inyeccion: `Sample Name` |
| `Sample Type` | Columna `Sample Type` | Metadatos de inyeccion: `Sample Type` |
| `Acquisition Date` | Columna `Acquisition Date` | Metadatos de inyeccion: `Acquisition Date` |
| `Area (cps)` | Columna `Area (cps)` | `Target Analyte` -> `Area (cps)` |
| `IS Area (cps)` | Columna `IS Area (cps)` | `Internal Standard` -> `Area (cps)` |
| `RT (min)` | Columna `RT (min)` | `Target Analyte` -> `RT (min)` |
| `Calculated Conc. (ng/mL)` | Columna `Calculated Conc. (ng/mL)` | `Target Analyte` -> `Calc. Conc. (ng/mL)` |
| `Acquisition Method` | Metadatos globales: `Acquisition Method` | Metadatos de inyeccion: `Acquisition Method` |
| `Project` | Metadatos globales: `Project` | Metadatos de inyeccion: `Project` |
| `Instrument` | Metadatos globales: `Instrument` | Metadatos de inyeccion: `Instrument Name` |

## Reporte generado

El reporte producido por `main_v1.py` incluye:

- **Resumen de Auditoria**
  - Informacion del analito, si fue encontrada.
  - Cantidad total de muestras analizadas.
  - Cantidad de muestras sin errores.
  - Cantidad de muestras con errores.
- **Correspondencia de Variables**
  - Tabla con la ubicacion de cada campo en ambos documentos.
- **Detalle de Errores Encontrados**
  - Lista de inconsistencias indicando ID, nombre de muestra, campo observado, valor en tabla y valor en cromatograma.

Cuando no se detectan inconsistencias, el reporte informa que todos los datos comparados coinciden.

## Requerimientos funcionales

1. Extraer datos de archivos `.docx` de tabla y cromatogramas.
2. Verificar automaticamente la correspondencia de los campos definidos en la matriz de auditoria.
3. Detectar diferencias de texto, fecha, metadatos y resultados numericos.
4. Evitar falsos errores cuando los valores numericos equivalentes esten expresados con formatos distintos.
5. Guardar un reporte Markdown reproducible.
6. Generar un PDF del reporte cuando la dependencia `markdown_pdf` este disponible y funcione correctamente.
7. Informar errores claros si alguno de los archivos de entrada no existe o si ocurre un problema durante la extraccion.

## Alcance actual

La version `main_v1.py` audita los campos definidos en la matriz de correspondencia y no utiliza el flujo anterior basado en LangGraph/LLM. El script esta orientado a una verificacion reproducible, trazable y facil de revisar manualmente a partir del reporte final.
