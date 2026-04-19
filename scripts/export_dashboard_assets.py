from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def main() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")

    monthly_df = pd.read_csv(PROCESSED_DIR / "pepsico_monthly_summary.csv")
    category_df = pd.read_csv(PROCESSED_DIR / "pepsico_category_summary.csv").head(5)

    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    axes[0].plot(monthly_df["month"], monthly_df["total_revenue_inr"] / 1_000_000, marker="o", color="#0f766e")
    axes[0].set_title("Monthly Revenue Trend")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("Revenue (INR Millions)")
    axes[0].tick_params(axis="x", rotation=45)

    axes[1].barh(
        category_df["beverage_category"],
        category_df["total_revenue_inr"] / 1_000_000,
        color="#1d4ed8",
    )
    axes[1].set_title("Top Categories by Revenue")
    axes[1].set_xlabel("Revenue (INR Millions)")
    axes[1].set_ylabel("")

    fig.suptitle("PepsiCo Sales Overview", fontsize=16, fontweight="bold")
    fig.tight_layout()
    output_path = ASSETS_DIR / "pepsico_sales_overview.png"
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved dashboard asset: {output_path}")


if __name__ == "__main__":
    main()
