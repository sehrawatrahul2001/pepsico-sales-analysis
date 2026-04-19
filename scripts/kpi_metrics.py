from __future__ import annotations

import pandas as pd


VALUE_BAND_BINS = [0, 100, 250, 500, float("inf")]
VALUE_BAND_LABELS = ["Budget", "Core", "Premium", "Enterprise"]


def add_order_value_band(dataframe: pd.DataFrame) -> pd.DataFrame:
    banded = dataframe.copy()
    banded["order_value_band"] = pd.cut(
        banded["price_inr"],
        bins=VALUE_BAND_BINS,
        labels=VALUE_BAND_LABELS,
        include_lowest=True,
    )
    return banded


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


def build_summary_tables(dataframe: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {
        "pepsico_category_summary": dataframe.groupby("beverage_category", as_index=False)
        .agg(
            total_orders=("price_inr", "size"),
            total_revenue_inr=("price_inr", "sum"),
            average_order_value_inr=("price_inr", "mean"),
        )
        .sort_values("total_revenue_inr", ascending=False),
        "pepsico_state_summary": dataframe.groupby("state", as_index=False)
        .agg(
            total_orders=("price_inr", "size"),
            total_revenue_inr=("price_inr", "sum"),
            average_order_value_inr=("price_inr", "mean"),
        )
        .sort_values("total_revenue_inr", ascending=False),
        "pepsico_value_band_summary": dataframe.groupby("order_value_band", as_index=False, observed=False)
        .agg(
            total_orders=("price_inr", "size"),
            total_revenue_inr=("price_inr", "sum"),
            average_rating=("rating", "mean"),
        )
        .sort_values("total_revenue_inr", ascending=False),
    }
