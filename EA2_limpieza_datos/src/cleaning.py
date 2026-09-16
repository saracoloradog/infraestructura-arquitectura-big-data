from copy import copy
from datetime import datetime
from pathlib import Path
import sqlite3

import pandas as pd
from openpyxl.styles import PatternFill


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "db" / "ingestion.db"
EXCEL_PATH = BASE_DIR / "xlsx" / "cleaned_data.xlsx"
REPORT_PATH = BASE_DIR / "static" / "auditoria" / "cleaning_report.txt"

TEXT_COLUMNS = [
    "title",
    "description",
    "category",
    "brand",
    "sku",
    "availability_status",
]
NUMERIC_COLUMNS = [
    "price",
    "discount_percentage",
    "rating",
    "stock",
    "weight",
]
REQUIRED_COLUMNS = ["id", "title", "category", "price"]


def load_data() -> pd.DataFrame:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"No se encontró la base de datos: {DB_PATH}")
    with sqlite3.connect(DB_PATH) as connection:
        return pd.read_sql_query("SELECT * FROM products", connection)


def count_nulls(dataframe: pd.DataFrame) -> int:
    return int(dataframe.isna().sum().sum())


def clean_data(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    clean = dataframe.copy()
    metrics = {
        "records_before": len(clean),
        "duplicates_before": int(clean.duplicated(subset=["id"]).sum()),
        "nulls_before": count_nulls(clean),
        "missing_brand_before": int(clean["brand"].isna().sum()),
        "price_min_before": float(clean["price"].min()),
        "price_max_before": float(clean["price"].max()),
        "price_mean_before": float(clean["price"].mean()),
        "stock_mean_before": float(clean["stock"].mean()),
        "rating_mean_before": float(clean["rating"].mean()),
    }

    clean = clean.drop_duplicates(subset=["id"], keep="first")

    clean["id"] = pd.to_numeric(clean["id"], errors="coerce")
    for column in NUMERIC_COLUMNS:
        clean[column] = pd.to_numeric(clean[column], errors="coerce")

    for column in TEXT_COLUMNS:
        clean[column] = clean[column].astype("string").str.strip()
        clean[column] = clean[column].replace("", pd.NA)

    clean = clean.dropna(subset=REQUIRED_COLUMNS)
    clean["id"] = clean["id"].astype("int64")
    clean["stock"] = clean["stock"].fillna(0).clip(lower=0).round().astype("int64")
    clean["price"] = clean["price"].clip(lower=0).round(2)
    clean["discount_percentage"] = (
        clean["discount_percentage"].fillna(0).clip(0, 100).round(2)
    )
    clean["rating"] = clean["rating"].fillna(clean["rating"].median()).clip(0, 5).round(2)
    clean["weight"] = clean["weight"].fillna(clean["weight"].median()).clip(lower=0)
    clean["brand"] = clean["brand"].fillna("Sin marca")
    clean["description"] = clean["description"].fillna("Sin descripción")
    clean["availability_status"] = clean["availability_status"].fillna("Sin estado")
    clean["category"] = clean["category"].str.lower()

    grouped_price = clean.groupby("category")["price"]
    q1 = grouped_price.transform(lambda values: values.quantile(0.25))
    q3 = grouped_price.transform(lambda values: values.quantile(0.75))
    iqr = q3 - q1
    clean["price_outlier"] = (clean["price"] < q1 - 1.5 * iqr) | (
        clean["price"] > q3 + 1.5 * iqr
    )
    clean["price_after_discount"] = (
        clean["price"] * (1 - clean["discount_percentage"] / 100)
    ).round(2)

    clean = clean.sort_values(["category", "id"]).reset_index(drop=True)
    metrics.update(
        {
            "records_after": len(clean),
            "duplicates_removed": metrics["duplicates_before"],
            "nulls_after": count_nulls(clean),
            "brands_imputed": metrics["missing_brand_before"],
            "outliers_flagged": int(clean["price_outlier"].sum()),
        }
    )
    return clean, metrics


def export_excel(dataframe: pd.DataFrame) -> None:
    EXCEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(EXCEL_PATH, engine="openpyxl") as writer:
        dataframe.to_excel(writer, sheet_name="Datos limpios", index=False)
        worksheet = writer.book["Datos limpios"]
        worksheet.freeze_panes = "A2"
        worksheet.auto_filter.ref = worksheet.dimensions

        for cell in worksheet[1]:
            font = copy(cell.font)
            font.bold = True
            font.color = "FFFFFF"
            cell.font = font
            cell.fill = PatternFill(fill_type="solid", fgColor="4472C4")

        for column in worksheet.columns:
            width = min(max(len(str(cell.value or "")) for cell in column) + 2, 32)
            worksheet.column_dimensions[column[0].column_letter].width = width

        for cell in worksheet["E"][1:]:
            cell.number_format = "0.00"
        for cell in worksheet["F"][1:]:
            cell.number_format = "0.00"


def write_report(metrics: dict) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "REPORTE DE LIMPIEZA DE DATOS",
        f"Fecha: {datetime.now().isoformat(timespec='seconds')}",
        f"Fuente: {DB_PATH.name}, tabla products",
        "",
        "ESTADO INICIAL",
        f"Registros: {metrics['records_before']}",
        f"Duplicados por ID: {metrics['duplicates_before']}",
        f"Valores nulos: {metrics['nulls_before']}",
        f"Marcas faltantes: {metrics['missing_brand_before']}",
        f"Precio mínimo: {metrics['price_min_before']:.2f}",
        f"Precio máximo: {metrics['price_max_before']:.2f}",
        f"Precio promedio: {metrics['price_mean_before']:.2f}",
        f"Stock promedio: {metrics['stock_mean_before']:.2f}",
        f"Calificación promedio: {metrics['rating_mean_before']:.2f}",
        "",
        "OPERACIONES REALIZADAS",
        f"Duplicados eliminados: {metrics['duplicates_removed']}",
        f"Marcas imputadas con 'Sin marca': {metrics['brands_imputed']}",
        "Conversión de ID y stock a enteros.",
        "Conversión de precio, descuento, calificación y peso a valores numéricos.",
        "Estandarización de textos y categorías en minúscula.",
        "Control de rangos para precio, descuento, calificación, stock y peso.",
        f"Precios atípicos identificados por categoría: {metrics['outliers_flagged']}",
        "Cálculo del precio después del descuento.",
        "",
        "ESTADO FINAL",
        f"Registros: {metrics['records_after']}",
        f"Valores nulos: {metrics['nulls_after']}",
        "Resultado: LIMPIEZA EXITOSA" if metrics["nulls_after"] == 0 else "Resultado: REVISAR DATOS",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    source = load_data()
    cleaned, metrics = clean_data(source)
    export_excel(cleaned)
    write_report(metrics)
    print(f"Limpieza finalizada: {metrics['records_after']} registros")
    print(f"Excel: {EXCEL_PATH}")
    print(f"Auditoría: {REPORT_PATH}")


if __name__ == "__main__":
    main()
