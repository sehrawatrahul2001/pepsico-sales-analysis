from __future__ import annotations

from bootstrap_data import main as bootstrap_main
from pepsico_sales_performance_analysis import main as pipeline_main


def main() -> None:
    bootstrap_main()
    pipeline_main()


if __name__ == "__main__":
    main()
