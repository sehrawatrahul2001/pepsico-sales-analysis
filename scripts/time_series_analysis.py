from __future__ import annotations

import numpy as np
import pandas as pd


def build_monthly_summary(dataframe: pd.DataFrame) -> pd.DataFrame:
    monthly = (
        dataframe.groupby("month", as_index=False)
        .agg(
            total_orders=("price_inr", "size"),
            total_revenue_inr=("price_inr", "sum"),
            average_order_value_inr=("price_inr", "mean"),
        )
        .sort_values("month")
    )
    monthly["rolling_3m_revenue_inr"] = monthly["total_revenue_inr"].rolling(3, min_periods=1).mean()
    revenue_mean = monthly["total_revenue_inr"].mean()
    revenue_std = monthly["total_revenue_inr"].std(ddof=0) or 1
    monthly["revenue_zscore"] = (monthly["total_revenue_inr"] - revenue_mean) / revenue_std
    monthly["anomaly_flag"] = monthly["revenue_zscore"].abs() >= 1.5
    return monthly


def build_revenue_forecast(monthly_summary: pd.DataFrame, forecast_periods: int = 3) -> pd.DataFrame:
    indexed = monthly_summary.copy().reset_index(drop=True)
    indexed["month_period"] = pd.PeriodIndex(indexed["month"], freq="M")

    x_values = np.arange(len(indexed))
    coefficients = np.polyfit(x_values, indexed["total_revenue_inr"], 1)
    future_x = np.arange(len(indexed), len(indexed) + forecast_periods)
    future_periods = [
        (indexed["month_period"].iloc[-1] + step).strftime("%Y-%m")
        for step in range(1, forecast_periods + 1)
    ]
    forecast_values = np.polyval(coefficients, future_x)

    return pd.DataFrame(
        {
            "forecast_month": future_periods,
            "forecast_revenue_inr": forecast_values.round(2),
            "forecast_method": "linear_trend_baseline",
        }
    )
