from copy import copy
from datetime import datetime
from pathlib import Path
import sqlite3

import pandas as pd
import requests
from openpyxl.styles import PatternFill


API_URL = "https://dummyjson.com/products?limit=0"
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "db" / "ingestion.db"
EXCEL_PATH = BASE_DIR / "xlsx" / "ingestion.xlsx"
AUDIT_PATH = BASE_DIR / "static" / "auditoria" / "ingestion.txt"

FIELDS = [
    "id",
    "title",
    "description",
    "category",
    "price",
    "discountPercentage",
    "rating",
    "stock",
    "brand",
    "sku",
    "weight",
    "availabilityStatus",
]


def extract_products() -> pd.DataFrame:
    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()
    products = response.json().get("products", [])
    if not products:
        raise ValueError("La API no devolvió productos")

    dataframe = pd.DataFrame(products).reindex(columns=FIELDS)
    dataframe = dataframe.rename(
        columns={
            "discountPercentage": "discount_percentage",
            "availabilityStatus": "availability_status",
        }
    )
    return dataframe


def save_to_sqlite(dataframe: pd.DataFrame) -> int:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("DROP TABLE IF EXISTS products")
        connection.execute(
            """
            CREATE TABLE products (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                discount_percentage REAL,
                rating REAL,
                stock INTEGER,
                brand TEXT,
                sku TEXT,
                weight REAL,
                availability_status TEXT
            )
            """
        )
        dataframe.to_sql("products", connection, if_exists="append", index=False)
        return connection.execute("SELECT COUNT(*) FROM products").fetchone()[0]


def generate_excel(dataframe: pd.DataFrame) -> None:
    EXCEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    sample_columns = [
        "id",
        "title",
        "category",
        "price",
        "discount_percentage",
        "rating",
        "stock",
        "brand",
        "sku",
        "availability_status",
    ]
    summary = (
        dataframe.groupby("category", as_index=False)
        .agg(
            products=("id", "count"),
            average_price=("price", "mean"),
            total_stock=("stock", "sum"),
            average_rating=("rating", "mean"),
        )
        .round(2)
        .sort_values("products", ascending=False)
    )

    with pd.ExcelWriter(EXCEL_PATH, engine="openpyxl") as writer:
        dataframe[sample_columns].head(25).to_excel(
            writer, sheet_name="Muestra", index=False
        )
        summary.to_excel(writer, sheet_name="Resumen categorias", index=False)

        for worksheet in writer.book.worksheets:
            worksheet.freeze_panes = "A2"
            worksheet.auto_filter.ref = worksheet.dimensions
            for cell in worksheet[1]:
                header_font = copy(cell.font)
                header_font.bold = True
                header_font.color = "FFFFFF"
                cell.font = header_font
                cell.fill = PatternFill(fill_type="solid", fgColor="4472C4")
            for column in worksheet.columns:
                width = min(max(len(str(cell.value or "")) for cell in column) + 2, 35)
                worksheet.column_dimensions[column[0].column_letter].width = width


def generate_audit(api_data: pd.DataFrame, database_count: int) -> bool:
    with sqlite3.connect(DB_PATH) as connection:
        stored_data = pd.read_sql_query("SELECT * FROM products ORDER BY id", connection)

    api_ids = set(api_data["id"].tolist())
    database_ids = set(stored_data["id"].tolist())
    duplicate_ids = int(api_data["id"].duplicated().sum())
    missing_required = int(
        api_data[["id", "title", "category", "price"]].isna().any(axis=1).sum()
    )
    missing_in_database = sorted(api_ids - database_ids)
    extra_in_database = sorted(database_ids - api_ids)

    successful = (
        len(api_data) == database_count
        and duplicate_ids == 0
        and missing_required == 0
        and not missing_in_database
        and not extra_in_database
    )

    lines = [
        "AUDITORIA DE INGESTION DE DATOS",
        f"Fecha: {datetime.now().isoformat(timespec='seconds')}",
        f"API: {API_URL}",
        f"Registros extraidos: {len(api_data)}",
        f"Registros almacenados: {database_count}",
        f"ID duplicados: {duplicate_ids}",
        f"Registros con campos obligatorios vacios: {missing_required}",
        f"ID faltantes en SQLite: {missing_in_database or 'Ninguno'}",
        f"ID adicionales en SQLite: {extra_in_database or 'Ninguno'}",
        f"Resultado: {'EXITOSO' if successful else 'CON DIFERENCIAS'}",
    ]
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return successful


def main() -> None:
    products = extract_products()
    stored_count = save_to_sqlite(products)
    generate_excel(products)
    if not generate_audit(products, stored_count):
        raise RuntimeError("La auditoría encontró diferencias en la ingesta")

    print(f"Ingestión finalizada: {stored_count} productos almacenados")
    print(f"Base de datos: {DB_PATH}")
    print(f"Excel: {EXCEL_PATH}")
    print(f"Auditoría: {AUDIT_PATH}")


if __name__ == "__main__":
    main()
