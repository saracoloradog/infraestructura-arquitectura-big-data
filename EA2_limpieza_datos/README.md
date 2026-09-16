# EA2. Preprocesamiento y limpieza de datos

Este proyecto toma la base SQLite generada en la EA1 y limpia la tabla de productos con Pandas.

La fuente contiene 194 productos. En la exploración se revisan duplicados, valores nulos, tipos de datos y precios atípicos. Se encontraron 92 marcas faltantes y no se encontraron IDs duplicados.

## Proceso

- Elimina registros duplicados por ID.
- Corrige tipos numéricos y estandariza textos.
- Completa las marcas faltantes con `Sin marca`.
- Valida rangos y señala precios atípicos por categoría.
- Calcula el precio después del descuento.

## Ejecución

```bash
git clone https://github.com/saracoloradog/infraestructura-arquitectura-big-data.git
cd infraestructura-arquitectura-big-data/EA2_limpieza_datos
pip install -r requirements.txt
python src/cleaning.py
```

## Archivos generados

- `src/xlsx/cleaned_data.xlsx`: conjunto de datos limpio.
- `src/static/auditoria/cleaning_report.txt`: comparación antes y después.

El workflow `.github/workflows/bigdata.yml` se activa con los cambios de la EA2. Instala las dependencias, ejecuta la limpieza y publica el Excel y el reporte como evidencias descargables.
