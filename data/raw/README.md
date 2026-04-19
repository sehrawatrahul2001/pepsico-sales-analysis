# Raw Data

The full PepsiCo sales workbook is stored locally in this folder and is intentionally excluded from GitHub.

Supported bootstrap paths:

- Local-first: keep the workbook locally and set `PEPSICO_DATA_PATH`, or copy `data/data_sources.example.json` to `data/data_sources.json` and list your preferred workbook path there.
- Google Drive: add the file ID to `data/data_sources.json` and run `python3 scripts/bootstrap_data.py`.
- Kaggle: add the dataset slug to `data/data_sources.json` and run `python3 scripts/bootstrap_data.py`.
- Sample fallback: if the workbook is unavailable, the project can still run from `data/sample/pepsico_sales_sample.csv`.
