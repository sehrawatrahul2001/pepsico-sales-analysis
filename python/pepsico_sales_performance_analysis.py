from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "pepsico_sales_dataset.xlsx"
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
            current_row_number: str | None = None

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
                    current_row_number = "".join(character for character in cell_reference if character.isdigit())
                    max_columns = max(max_columns, len(current_row))
                    element.clear()

                elif tag == "row":
                    if current_row:
                        while len(current_row) < max_columns:
                            current_row.append("")
                        rows.append(current_row)
                    current_row = []
                    current_row_number = None
                    element.clear()

        header = rows[0]
        records = [row[: len(header)] for row in rows[1:]]
        dataframe = pd.DataFrame(records, columns=header)
        dataframe["Order Date"] = dataframe["Order Date"].map(parse_excel_date)
        for column in ["Price (INR)", "Rating", "Rating Count"]:
            dataframe[column] = pd.to_numeric(dataframe[column], errors="coerce")
        return dataframe


def load_sales_data(path: Path | str = DATA_PATH) -> pd.DataFrame:
    file_path = Path(path)
    try:
        dataframe = pd.read_excel(file_path)
    except ImportError:
        dataframe = load_sales_data_from_xlsx_xml(file_path)
    dataframe.columns = (
        dataframe.columns.str.strip().str.lower().str.replace(" ", "_").str.replace(r"[^a-z0-9_]", "", regex=True)
    )
    dataframe["order_date"] = pd.to_datetime(dataframe["order_date"])
    dataframe["month"] = dataframe["order_date"].dt.to_period("M").astype(str)
    dataframe["quarter"] = dataframe["order_date"].dt.to_period("Q").astype(str)
    dataframe["day_name"] = dataframe["order_date"].dt.day_name()
    return dataframe


def build_kpis(dataframe: pd.DataFrame) -> dict[str, object]:
    top_category = dataframe.groupby("beverage_category")["price_inr"].sum().sort_values(ascending=False).index[0]
    top_product = dataframe.groupby("beverage_name")["price_inr"].sum().sort_values(ascending=False).index[0]
    top_state = dataframe.groupby("state")["price_inr"].sum().sort_values(ascending=False).index[0]

    monthly_revenue = dataframe.groupby("month")["price_inr"].sum().sort_values(ascending=False)
    return {
        "total_orders": int(len(dataframe)),
        "total_revenue_inr": round(float(dataframe["price_inr"].sum()), 2),
        "average_order_value_inr": round(float(dataframe["price_inr"].mean()), 2),
        "average_rating": round(float(dataframe["rating"].mean()), 2),
        "top_category": top_category,
        "top_product": top_product,
        "top_state": top_state,
        "peak_month": monthly_revenue.index[0],
    }


def main() -> None:
    dataframe = load_sales_data()
    kpis = build_kpis(dataframe)

    print("PepsiCo Sales Performance & Business Insights Summary")
    for key, value in kpis.items():
        print(f"- {key}: {value}")


if __name__ == "__main__":
    main()
