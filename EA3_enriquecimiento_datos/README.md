# EA3. Enriquecimiento de datos

## Descripción de la solución

El proyecto toma los 194 productos limpios de la EA2 y complementa su información mediante seis catálogos en formatos JSON, XLSX, CSV, XML, HTML y TXT. Los cruces se realizan por la columna `category` con Pandas.

El dataset final agrega el segmento comercial, región del proveedor, días de reposición, tasa de impuesto, meses de garantía, clase de envío y recomendación de manejo. También calcula el precio con impuesto e identifica productos con prioridad de reposición.

## Fuentes utilizadas

- JSON: segmento comercial.
- XLSX: región del proveedor y días de reposición.
- CSV: tasa de impuesto.
- XML: meses de garantía.
- HTML: clase de envío.
- TXT: recomendación de manejo.

Los archivos se encuentran en `src/sources/` y contienen una fila de referencia para cada categoría del dataset.

## Clonar, instalar y ejecutar

```bash
git clone https://github.com/saracoloradog/infraestructura-arquitectura-big-data.git
cd infraestructura-arquitectura-big-data/EA3_enriquecimiento_datos
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/enrichment.py
```

Al finalizar, la terminal debe mostrar `Enriquecimiento finalizado: 194 registros`.

## Archivos generados

- `src/xlsx/enriched_data.xlsx`: dataset enriquecido.
- `src/static/auditoria/enrichment_report.txt`: detalle de las fuentes, coincidencias y transformaciones.

## Automatización con GitHub Actions

El workflow `.github/workflows/bigdata.yml` se activa con los cambios de la EA3 o manualmente. Instala las dependencias, ejecuta el enriquecimiento y publica el Excel y el reporte en el artefacto `evidencias-ea3`.

## Verificación de las evidencias

1. Verificar que `src/input/cleaned_data.xlsx` contiene el dataset limpio de la EA2.
2. Ejecutar `python src/enrichment.py` y comprobar el mensaje de 194 registros.
3. Abrir `src/xlsx/enriched_data.xlsx` y revisar las columnas adicionales.
4. Abrir `src/static/auditoria/enrichment_report.txt` y confirmar 194 coincidencias para cada fuente y 0 registros sin coincidencia.
5. En la pestaña **Actions** de GitHub, comprobar que **EA3 - Enriquecimiento de datos** aparece con marca verde y permite descargar `evidencias-ea3`.
