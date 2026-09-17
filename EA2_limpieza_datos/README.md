# EA2. Preprocesamiento y limpieza de datos

## Descripción de la solución

La solución carga con Pandas la tabla `products` de la base SQLite obtenida en la EA1. Después revisa duplicados, valores nulos, tipos de datos y precios atípicos. El proceso corrige los tipos numéricos, estandariza los textos, completa las marcas faltantes con `Sin marca`, valida los rangos y calcula el precio después del descuento.

La fuente contiene 194 productos. En la revisión inicial se encontraron 92 marcas faltantes y ningún ID duplicado. Como resultado se conservan los 194 registros, no quedan valores nulos y se identifican 12 precios atípicos, que se señalan sin eliminarlos.

## Estructura principal

- `src/db/ingestion.db`: base de datos recibida de la EA1.
- `src/cleaning.py`: script de exploración, limpieza y exportación.
- `src/xlsx/cleaned_data.xlsx`: datos limpios generados.
- `src/static/auditoria/cleaning_report.txt`: reporte del estado inicial y final.
- `.github/workflows/bigdata.yml`: automatización de la ejecución.

## Clonar, instalar y ejecutar

Se requiere Python 3.10 o superior. En la terminal se ejecutan los siguientes comandos:

```bash
git clone https://github.com/saracoloradog/infraestructura-arquitectura-big-data.git
cd infraestructura-arquitectura-big-data/EA2_limpieza_datos
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/cleaning.py
```

Al finalizar, la terminal debe mostrar `Limpieza finalizada: 194 registros` y las ubicaciones del Excel y del reporte.

## Automatización con GitHub Actions

El workflow `.github/workflows/bigdata.yml` se activa cuando se modifican los archivos de la EA2 y también puede ejecutarse manualmente. GitHub Actions descarga el repositorio, configura Python, instala las dependencias, ejecuta `src/cleaning.py` y publica el Excel y el reporte en un artefacto llamado `evidencias-ea2`.

## Verificación de las evidencias

Después de ejecutar el proyecto se comprueba lo siguiente:

1. La base de datos existe en `src/db/ingestion.db` y contiene la tabla `products` utilizada como fuente.
2. El archivo `src/xlsx/cleaned_data.xlsx` fue generado y contiene 194 registros limpios.
3. El archivo `src/static/auditoria/cleaning_report.txt` muestra 92 valores nulos inicialmente, 0 valores nulos al final y 12 precios atípicos identificados.
4. En la pestaña **Actions** del repositorio, la ejecución **EA2 - Limpieza de datos** debe aparecer con una marca verde.
5. Al abrir esa ejecución, en la sección **Artifacts** se puede descargar `evidencias-ea2`, que contiene el Excel y el reporte de auditoría.
