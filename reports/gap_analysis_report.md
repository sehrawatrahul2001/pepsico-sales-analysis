# Gap Analysis Report

## Audit Summary

The PepsiCo project already had a strong commercial narrative, but the repository still lacked several signals that hiring managers expect from an industry-grade analytics case: flexible dataset ingestion, reusable summary exports, forecast-ready outputs, and visible recruiter-facing assets.

## Missing vs Full Project Before Upgrade

### Missing Files

- no project-local `requirements.txt`
- no example source configuration for automated download
- no generated dashboard image in `assets/`
- no forecast export file
- no reusable category, state, or value-band summary exports

### Missing Datasets In GitHub

- full `pepsico_sales_dataset.xlsx` workbook

This workbook remains local-only by design because it is intentionally excluded from GitHub.

### Missing Preprocessing / Analytics Steps

- no reusable order-value band field in the processed dataset
- no standalone forecast output for planning conversations
- no exported category/state/value-band summary tables

### Missing Automation / Operational Layer

- no configurable Google Drive or Kaggle bootstrap pattern
- no one-command chart export for the README

### Missing Dashboards / Reports

- dashboard brief existed, but the repo lacked a current PNG screenshot generated from processed outputs

### Missing Documentation

- README did not fully explain how a reviewer could run the project without the raw workbook
- the business output layer was stronger in narrative than in exported files

## Upgrades Implemented

- added project-local `requirements.txt`
- added `data/data_sources.example.json` and multi-path bootstrap support
- added `order_value_band` to the processed dataset
- added forecast, category, state, and value-band CSV outputs
- generated `assets/pepsico_sales_overview.png`
- rewrote the README to be recruiter-friendly and execution-ready

## Remaining Local-Only Elements

- full workbook remains intentionally excluded from GitHub
- any Power BI or other heavy dashboard authoring file should remain local unless a smaller shareable version is prepared
