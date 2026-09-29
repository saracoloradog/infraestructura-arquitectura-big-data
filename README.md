# Infraestructura y arquitectura para Big Data

Repositorio de evidencias del curso. El proyecto construye un flujo analítico con 194 productos: obtiene los datos desde una API, los almacena en SQLite, realiza su limpieza con Pandas y los enriquece con seis catálogos externos. GitHub Actions permite repetir y verificar cada etapa.

## Actividades y entregables

- [EA1 - Ingestión de datos desde una API](EA1_ingestion_api/): API DummyJSON, SQLite, Excel y auditoría.
- [EA2 - Preprocesamiento y limpieza](EA2_limpieza_datos/): revisión de calidad, tratamiento de nulos y variables derivadas.
- [EA3 - Enriquecimiento de datos](EA3_enriquecimiento_datos/): integración de fuentes JSON, XLSX, CSV, XML, HTML y TXT.
- [EA4 - Arquitectura y modelo de datos](docs/arquitectura_modelo.pdf): informe final de la arquitectura, flujo, modelo lógico, decisiones técnicas y recomendaciones.

## Cómo clonar el repositorio

```bash
git clone https://github.com/saracoloradog/infraestructura-arquitectura-big-data.git
cd infraestructura-arquitectura-big-data
```

Se requiere Python 3.10 o superior. Cada actividad tiene su propio archivo `requirements.txt` y un README con instrucciones específicas.

## Ejecución del proceso

Las etapas se pueden ejecutar de forma independiente:

```bash
# EA1: extracción desde la API y creación de SQLite
cd EA1_ingestion_api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/ingestion.py

# EA2: limpieza del dataset
cd ../EA2_limpieza_datos
pip install -r requirements.txt
python src/cleaning.py

# EA3: enriquecimiento con fuentes externas
cd ../EA3_enriquecimiento_datos
pip install -r requirements.txt
python src/enrichment.py
```

Los resultados principales son `ingestion.db`, `cleaned_data.xlsx`, `enriched_data.xlsx` y los reportes de auditoría de cada etapa.

## Automatización con GitHub Actions

Los archivos de `.github/workflows/` configuran las ejecuciones automáticas. Los workflows preparan Python, instalan las dependencias, ejecutan los scripts y publican las evidencias como artefactos descargables. También pueden iniciarse manualmente desde la pestaña **Actions** del repositorio.

## Cómo verificar las evidencias

1. En EA1, comprobar que SQLite contiene la tabla `products` con 194 registros y que se generaron el Excel y `ingestion.txt`.
2. En EA2, revisar `cleaned_data.xlsx` y `cleaning_report.txt`: deben conservarse 194 registros, quedar 0 nulos e identificarse 12 precios atípicos.
3. En EA3, revisar `enriched_data.xlsx` y `enrichment_report.txt`: cada fuente debe registrar 194 coincidencias y 0 registros sin relación.
4. En **Actions**, confirmar que las ejecuciones finalizan con marca verde y permiten descargar los artefactos.
5. Consultar el [informe de arquitectura y modelo de datos](docs/arquitectura_modelo.pdf), donde se explica cómo se conectan las cuatro evidencias.
