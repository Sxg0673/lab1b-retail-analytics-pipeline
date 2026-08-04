
# Retail Analytics ETL Pipeline

## Overview

This project implements an ETL (Extract, Transform and Load) pipeline for a retail analytics platform. The pipeline processes transactional and reference data from heterogeneous sources, including CSV, JSON, and XML files. Its purpose is to integrate, clean, transform, and validate retail data to generate a consolidated dataset that supports business intelligence and analytical dashboards.

The project follows a modular architecture, where each ETL stage is implemented independently to improve maintainability, scalability, and reproducibility.

---

## Objectives

The pipeline is designed to:

- Extract data from heterogeneous data sources.
- Profile datasets to assess data quality.
- Standardize and clean inconsistent records.
- Transform and integrate transactional and reference data.
- Validate the consistency of the integrated dataset.
- Load the processed data into a relational database for analytical purposes.

---

## Project Structure

```text
Retail-Analytics-Pipeline
│
├── data
│   ├── raw/                 # Raw input datasets
│   └── processed/           # Processed datasets
│
├── docs
│   └── eda_outputs/         # Profiling reports and EDA summaries
│
├── logs
    └── etl_run.log
├── src
│   ├── extract.py
│   ├── profile.py
│   ├── clean.py
│   ├── transform.py
│   ├── validate.py
│   ├── load.py
│   └── main.py
│
└── README.md
```

---

## Data Sources

The project processes two categories of datasets.

### Transactional Data

| File | Description |
|------|-------------|
| `sales_cali.csv` | Sales transactions from Cali |
| `sales_bogota.json` | Sales transactions from Bogotá |
| `sales_medellin.xml` | Sales transactions from Medellín |

### Reference Data

| File | Description |
|------|-------------|
| `products.csv` | Product catalog |
| `stores.csv` | Store information (city and region) |
| `promotions.csv` | Promotion campaigns and discounts |
| `monthly_targets.csv` | Monthly sales targets by store |

---

# ETL Pipeline

## 1. Data Extraction

The extraction module scans the `data/raw` directory recursively and loads every supported file into a pandas DataFrame.

Supported formats include:

- CSV
- JSON
- XML

Each dataset is stored independently and passed to the following ETL stages.

**Output**

- Dictionary of DataFrames.

---

## 2. Data Profiling

This stage evaluates the quality and structure of every dataset before any transformation is applied.

The profiling process includes:

- Number of rows and columns
- Data types
- Missing values
- Duplicate records
- Invalid dates
- Invalid quantities
- Invalid prices
- Cardinality of selected categorical attributes

For every dataset, three outputs are generated:

- Dataset summary
- Column profile
- Data quality report

Generated reports are stored under:

```text
docs/eda_outputs/
```

---

## 3. Data Cleaning

The cleaning stage standardizes the datasets and applies the business rules identified during the profiling stage.

Implemented rules include:

- Standardize column names.
- Standardize identifier names.
- Remove leading and trailing whitespace.
- Normalize text casing.
- Convert dates into a common format.
- Convert quantity and unit price to numeric data types.
- Remove duplicated sales records.
- Remove records with invalid dates.
- Remove records where quantity ≤ 0.
- Remove records where unit price ≤ 0.
- Standardize missing promotion codes.

**Output**

- Clean and standardized datasets.

---

## 4. Data Transformation

The transformation stage integrates the transactional datasets and enriches them with reference information.

Main operations include:

- Merge sales datasets.
- Join product information.
- Join store information.
- Join promotion information.
- Join monthly sales targets.
- Generate a unified analytical dataset.

**Output**

- Integrated analytical dataset.

---

## 5. Data Validation

The validation stage verifies that the transformed data satisfy the expected business rules before loading.

Validation checks include:

- Referential integrity.
- Record consistency.
- Schema validation.
- Unexpected missing values.
- Unexpected duplicate records.

**Output**

- Validated dataset.

---

## 6. Data Loading

The validated dataset is loaded into the target relational database.

The resulting tables become the data source for SQL queries and analytical dashboards.

**Output**

- Database populated with the transformed data.

---

## Pipeline Execution

Run the complete ETL pipeline from the project root.

```bash
python src/main.py
```

---

## Generated Outputs

### Data Profiles

The profiling stage generates detailed reports for every dataset.

```text
docs/eda_outputs/perfiles/
```

Outputs include:

- Dataset summary
- Column profile
- Data quality report

organized by source type:

```text
csv/
json/
xml/
```

### EDA Summary Tables

The project also generates summary tables describing the main quality findings.

```text
docs/eda_outputs/tablas/
```

Generated files:

- `01_resumen_eda_cali.csv`
- `02_resumen_eda_bogota.csv`
- `03_resumen_eda_medellin.csv`

---

## Data Quality Summary

The profiling stage identified several quality issues within the transactional datasets.

| Dataset | Main Findings |
|----------|---------------|
| **Sales Cali** | Missing promotion codes, duplicated records, invalid quantities |
| **Sales Bogotá** | Missing promotion codes, duplicated records, invalid quantities, invalid prices |
| **Sales Medellín** | Invalid dates, duplicated records, invalid prices |

The reference datasets (`products`, `stores`, `promotions`, and `monthly_targets`) did not present significant quality issues.

---

## Technologies

- Python
- Pandas
- CSV
- JSON
- XML
- SQL
- ETL
- Data Profiling

---

## Future Work

The current implementation provides the foundation for the analytical platform. Future developments include:

- Incremental data loading.
- Automated data quality validation.
- Data warehouse implementation.
- Dashboard development for retail analytics.
- Pipeline orchestration and scheduling.
