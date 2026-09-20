from copy import copy
from datetime import datetime
from pathlib import Path

import pandas as pd
from openpyxl.styles import PatternFill


BASE_DIR = Path(__file__).resolve().parent
INPUT_PATH = BASE_DIR / "input" / "cleaned_data.xlsx"
SOURCES_DIR = BASE_DIR / "sources"
OUTPUT_PATH = BASE_DIR / "xlsx" / "enriched_data.xlsx"
REPORT_PATH = BASE_DIR / "static" / "auditoria" / "enrichment_report.txt"


def normalize_category(dataframe: pd.DataFrame) -> pd.DataFrame:
    normalized = dataframe.copy()
    normalized["category"] = (
        normalized["category"].astype("string").str.strip().str.lower()
    )
    return normalized


def load_sources() -> list[tuple[str, str, pd.DataFrame]]:
    return [
        (
            "JSON - segmentos",
            "category_segments.json",
            pd.read_json(SOURCES_DIR / "category_segments.json"),
        ),
        (
            "XLSX - proveedores",
            "category_suppliers.xlsx",
            pd.read_excel(SOURCES_DIR / "category_suppliers.xlsx"),
        ),
        (
            "CSV - impuestos",
            "category_tax.csv",
            pd.read_csv(SOURCES_DIR / "category_tax.csv"),
        ),
        (
            "XML - garantías",
            "category_warranty.xml",
            pd.read_xml(
                SOURCES_DIR / "category_warranty.xml",
                xpath="./category",
                parser="etree",
            ),
        ),
        (
            "HTML - envíos",
            "category_shipping.html",
            pd.read_html(SOURCES_DIR / "category_shipping.html")[0],
        ),
        (
            "TXT - manejo",
            "category_handling.txt",
            pd.read_csv(SOURCES_DIR / "category_handling.txt", sep="|"),
        ),
    ]


def enrich_data(base: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    enriched = normalize_category(base)
    audit = []

    for source_name, file_name, source in load_sources():
        source = normalize_category(source)
        duplicated_keys = int(source["category"].duplicated().sum())
        source = source.drop_duplicates(subset=["category"], keep="first")
        added_columns = [column for column in source.columns if column != "category"]

        enriched = enriched.merge(
            source,
            on="category",
            how="left",
            validate="many_to_one",
            indicator=True,
        )
        matches = int((enriched["_merge"] == "both").sum())
        unmatched = int((enriched["_merge"] == "left_only").sum())
        enriched = enriched.drop(columns="_merge")

        audit.append(
            {
                "source": source_name,
                "file": file_name,
                "source_rows": len(source),
                "matches": matches,
                "unmatched": unmatched,
                "duplicate_keys": duplicated_keys,
                "added_columns": ", ".join(added_columns),
            }
        )

    enriched["price_with_tax"] = (
        enriched["price_after_discount"] * (1 + enriched["tax_rate"])
    ).round(2)
    enriched["restock_priority"] = (
        (enriched["stock"] < 20) & (enriched["replenishment_days"] >= 15)
    )
    return enriched, audit


def export_excel(dataframe: pd.DataFrame) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(OUTPUT_PATH, engine="openpyxl") as writer:
        dataframe.to_excel(writer, sheet_name="Datos enriquecidos", index=False)
        worksheet = writer.book["Datos enriquecidos"]
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

        header_positions = {cell.value: cell.column_letter for cell in worksheet[1]}
        for name in ["price", "discount_percentage", "price_after_discount", "price_with_tax"]:
            for cell in worksheet[header_positions[name]][1:]:
                cell.number_format = "0.00"
        for cell in worksheet[header_positions["tax_rate"]][1:]:
            cell.number_format = "0.0%"


def write_report(base: pd.DataFrame, enriched: pd.DataFrame, audit: list[dict]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "REPORTE DE ENRIQUECIMIENTO DE DATOS",
        f"Fecha: {datetime.now().isoformat(timespec='seconds')}",
        f"Dataset base: {INPUT_PATH.name}",
        f"Registros base: {len(base)}",
        f"Registros enriquecidos: {len(enriched)}",
        f"Columnas iniciales: {len(base.columns)}",
        f"Columnas finales: {len(enriched.columns)}",
        "Clave de integración: category",
        "",
        "CRUCES REALIZADOS",
    ]

    for item in audit:
        lines.extend(
            [
                f"- {item['source']} ({item['file']})",
                f"  Registros de referencia: {item['source_rows']}",
                f"  Coincidencias: {item['matches']}",
                f"  Sin coincidencia: {item['unmatched']}",
                f"  Claves duplicadas descartadas: {item['duplicate_keys']}",
                f"  Columnas agregadas: {item['added_columns']}",
            ]
        )

    lines.extend(
        [
            "",
            "TRANSFORMACIONES ADICIONALES",
            "- Normalización de la categoría a minúsculas y sin espacios externos.",
            "- Cálculo de price_with_tax a partir del precio con descuento y la tasa.",
            "- Identificación de restock_priority para productos con poco stock y reposición lenta.",
            "",
            "RESULTADO",
            f"Valores nulos en las columnas agregadas: {int(enriched.iloc[:, len(base.columns):].isna().sum().sum())}",
            f"Productos con prioridad de reposición: {int(enriched['restock_priority'].sum())}",
            "Resultado: ENRIQUECIMIENTO EXITOSO",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"No se encontró el dataset de la EA2: {INPUT_PATH}")

    base = pd.read_excel(INPUT_PATH)
    enriched, audit = enrich_data(base)
    export_excel(enriched)
    write_report(base, enriched, audit)
    print(f"Enriquecimiento finalizado: {len(enriched)} registros")
    print(f"Excel: {OUTPUT_PATH}")
    print(f"Auditoría: {REPORT_PATH}")


if __name__ == "__main__":
    main()
