# EA1. Ingestión de datos desde un API

Proyecto que extrae productos desde la API pública DummyJSON, los almacena en SQLite y genera un archivo Excel y un reporte de auditoría.

## Ejecución

```bash
pip install -r requirements.txt
python src/ingestion.py
```

## Resultados

- `src/db/ingestion.db`: base de datos SQLite.
- `src/xlsx/ingestion.xlsx`: muestra de productos y resumen por categoría.
- `src/static/auditoria/ingestion.txt`: comparación entre la API y SQLite.

## Automatización

El workflow `ea1_ingestion.yml` ejecuta el proceso automáticamente en GitHub Actions y publica los tres archivos generados como artefactos.

**Fuente:** [DummyJSON Products](https://dummyjson.com/docs/products)

