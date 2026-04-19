from __future__ import annotations

import argparse
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

import pandas as pd

from data_access import PROCESSED_DATA_PATH, resolve_source_path
from kpi_metrics import add_order_value_band, build_kpis, build_summary_tables
from time_series_analysis import build_monthly_summary, build_revenue_forecast


PROJECT_ROOT = Path(__file__).resolve().parent.parent
XML_NS = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def excel_column_index(cell_reference: str) -> int:
    column = "".join(character for character in cell_reference if character.isalpha())
    index = 0
    for character in column:
        index = index * 26 + (ord(character.upper()) - 64)
    return index - 1


def load_shared_strings(workbook: ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in workbook.namelist():
        return []

    root = ET.fromstring(workbook.read("xl/sharedStrings.xml"))
    strings: list[str] = []
    for item in root.findall("a:si", XML_NS):
        text_parts = [node.text or "" for node in item.findall(".//a:t", XML_NS)]
        strings.append("".join(text_parts))
    return strings


def parse_excel_date(value: str) -> pd.Timestamp:
    if value in {"", None}:
        return pd.NaT
    if "/" in value:
        return pd.to_datetime(value, dayfirst=True, errors="coerce")
    return pd.to_datetime(float(value), unit="D", origin="1899-12-30", errors="coerce")


def load_sales_data_from_xlsx_xml(path: Path) -> pd.DataFrame:
    with ZipFile(path) as workbook:
        shared_strings = load_shared_strings(workbook)
        rows: list[list[str]] = []
        max_columns = 0

        with workbook.open("xl/worksheets/sheet1.xml") as worksheet:
            current_row: list[str] = []

            for _, element in ET.iterparse(worksheet, events=("end",)):
                tag = element.tag.rsplit("}", 1)[-1]
                if tag == "c":
                    cell_reference = element.attrib.get("r", "")
                    column_index = excel_column_index(cell_reference)
                    while len(current_row) <= column_index:
                        current_row.append("")
                    value_node = element.find("a:v", XML_NS)
                    value = value_node.text if value_node is not None else ""
                    if element.attrib.get("t") == "s" and value:
                        value = shared_strings[int(value)]
                    current_row[column_index] = value
                    max_columns = max(max_columns, len(current_row))
                    element.clear()
                elif tag == "row":
                    if current_row:
                        while len(current_row) < max_columns:
                            current_row.append("")
                        rows.append(current_row)
                    current_row = []
                    element.clear()

        header = rows[0]
        records = [row[: len(header)] for row in rows[1:]]
        dataframe = pd.DataFrame(records, columns=header)
        dataframe["Order Date"] = dataframe["Order Date"].map(parse_excel_date)
        for column in ["Price (INR)", "Rating", "Rating Count"]:
            dataframe[column] = pd.to_numeric(dataframe[column], errors="coerce")
        return dataframe


def load_sales_data(path: Path | str | None = None, prefer_sample: bool = False) -> pd.DataFrame:
    file_path = Path(path) if path else resolve_source_path(prefer_sample=prefer_sample)
    if file_path.suffix.lower() == ".csv":
        dataframe = pd.read_csv(file_path)
    else:
        try:
            dataframe = pd.read_excel(file_path)
        except ImportError:
            dataframe = load_sales_data_from_xlsx_xml(file_path)
    dataframe.columns = (
        dataframe.columns.str.strip().str.lower().str.replace(" ", "_").str.replace(r"[^a-z0-9_]", "", regex=True)
    )
    dataframe["order_date"] = pd.to_datetime(dataframe["order_date"], dayfirst=True, format="mixed")
    dataframe["month"] = dataframe["order_date"].dt.to_period("M").astype(str)
    dataframe["quarter"] = dataframe["order_date"].dt.to_period("Q").astype(str)
    dataframe["day_name"] = dataframe["order_date"].dt.day_name()
    return dataframe


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze PepsiCo sales performance using raw or sample data.")
    parser.add_argument("--source", default="", help="Optional explicit dataset path.")
    parser.add_argument("--use-sample", action="store_true", help="Use the GitHub-safe sample dataset.")
    parser.add_argument("--skip-export", action="store_true", help="Skip writing processed outputs.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dataframe = load_sales_data(args.source or None, prefer_sample=args.use_sample)
    dataframe = add_order_value_band(dataframe)
    kpis = build_kpis(dataframe)
    monthly_summary = build_monthly_summary(dataframe)
    forecast_summary = build_revenue_forecast(monthly_summary)
    summary_tables = build_summary_tables(dataframe)

    if not args.skip_export:
        PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        dataframe.to_csv(PROCESSED_DATA_PATH, index=False)
        monthly_summary.to_csv(PROCESSED_DATA_PATH.parent / "pepsico_monthly_summary.csv", index=False)
        forecast_summary.to_csv(PROCESSED_DATA_PATH.parent / "pepsico_revenue_forecast.csv", index=False)
        for output_name, output_df in summary_tables.items():
            output_df.to_csv(PROCESSED_DATA_PATH.parent / f"{output_name}.csv", index=False)

    print("PepsiCo Sales Performance & Business Insights Summary")
    for key, value in kpis.items():
        print(f"- {key}: {value}")
    print(f"- forecast_output: {PROCESSED_DATA_PATH.parent / 'pepsico_revenue_forecast.csv'}")


if __name__ == "__main__":
    main()
