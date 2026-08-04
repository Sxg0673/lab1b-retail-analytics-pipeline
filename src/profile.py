import json
import re
from pathlib import Path

import pandas as pd


def _sanitize_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")


def _serialize_values(values) -> str:
    return json.dumps(values, ensure_ascii=False, indent=2)


def profile_dataframe(df: pd.DataFrame, dataset_name: str, output_dir: str | Path | None = None):
    """Genera un perfil detallado de un DataFrame y guarda reportes en disco."""
    output_dir = Path(output_dir) if output_dir is not None else Path("docs/eda_outputs/perfiles")
    output_dir.mkdir(parents=True, exist_ok=True)

    safe_name = _sanitize_name(dataset_name)
    summary = {
        "dataset_name": dataset_name,
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "memory_mb": round(df.memory_usage(deep=True).sum() / 1024**2, 2),
        "duplicate_rows": int(df.duplicated().sum()),
        "complete_rows": int(df.dropna().shape[0]),
        "missing_cells": int(df.isna().sum().sum()),
    }

    column_profiles = []
    for column in df.columns:
        series = df[column]
        missing_count = int(series.isna().sum())
        missing_pct = round((missing_count / len(series)) * 100, 2) if len(series) else 0.0
        non_missing = series.dropna()

        if pd.api.types.is_numeric_dtype(series):
            numeric_series = pd.to_numeric(series, errors="coerce")
            numeric_non_missing = numeric_series.dropna()
            profile = {
                "dataset_name": dataset_name,
                "column": column,
                "dtype": str(series.dtype),
                "missing_count": missing_count,
                "missing_pct": missing_pct,
                "unique_count": int(series.nunique(dropna=True)),
                "min": float(numeric_non_missing.min()) if not numeric_non_missing.empty else None,
                "max": float(numeric_non_missing.max()) if not numeric_non_missing.empty else None,
                "mean": float(numeric_non_missing.mean()) if not numeric_non_missing.empty else None,
                "median": float(numeric_non_missing.median()) if not numeric_non_missing.empty else None,
                "std": float(numeric_non_missing.std()) if not numeric_non_missing.empty else None,
                "invalid_numeric_values": int(numeric_series.isna().sum() - series.isna().sum()),
                "top_values": _serialize_values(series.value_counts(dropna=False).head(5).to_dict()),
            }
        elif pd.api.types.is_datetime64_any_dtype(series):
            profile = {
                "dataset_name": dataset_name,
                "column": column,
                "dtype": str(series.dtype),
                "missing_count": missing_count,
                "missing_pct": missing_pct,
                "unique_count": int(series.nunique(dropna=True)),
                "min": series.min().to_pydatetime().isoformat() if not series.dropna().empty else None,
                "max": series.max().to_pydatetime().isoformat() if not series.dropna().empty else None,
                "mean": None,
                "median": None,
                "std": None,
                "invalid_numeric_values": 0,
                "top_values": _serialize_values(series.value_counts(dropna=False).head(5).to_dict()),
            }
        else:
            string_series = non_missing.astype(str)
            lengths = string_series.str.len()
            profile = {
                "dataset_name": dataset_name,
                "column": column,
                "dtype": str(series.dtype),
                "missing_count": missing_count,
                "missing_pct": missing_pct,
                "unique_count": int(series.nunique(dropna=True)),
                "min": None,
                "max": None,
                "mean": None,
                "median": None,
                "std": None,
                "invalid_numeric_values": 0,
                "top_values": _serialize_values(series.value_counts(dropna=False).head(5).to_dict()),
                "mode": str(series.mode(dropna=True).iloc[0]) if not series.mode(dropna=True).empty else None,
                "min_length": int(lengths.min()) if not lengths.empty else None,
                "max_length": int(lengths.max()) if not lengths.empty else None,
            }

        column_profiles.append(profile)

    overview_df = pd.DataFrame([summary])
    columns_df = pd.DataFrame(column_profiles)

    overview_df.to_csv(output_dir / f"{safe_name}_overview.csv", index=False)
    columns_df.to_csv(output_dir / f"{safe_name}_columns.csv", index=False)

    report_lines = [
        f"Perfil de datos: {dataset_name}",
        f"Filas: {summary['rows']}",
        f"Columnas: {summary['columns']}",
        f"Celdas vacías: {summary['missing_cells']}",
        f"Filas duplicadas: {summary['duplicate_rows']}",
        "",
        "Resumen por columna:",
    ]

    for row in column_profiles:
        report_lines.append(
            f"- {row['column']} | dtype={row['dtype']} | nulos={row['missing_count']} | únicos={row['unique_count']}"
        )

    report_path = output_dir / f"{safe_name}_profile.txt"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    return {
        "dataset_name": dataset_name,
        "overview": overview_df,
        "columns": columns_df,
        "report_path": report_path,
    }

def profile_datasets(datasets: dict[str, pd.DataFrame], output_dir: str | Path | None = None):
    """Genera perfiles para todos los DataFrames contenidos en un diccionario."""
    output_dir = Path(output_dir) if output_dir is not None else Path("docs/eda_outputs/perfiles")
    output_dir.mkdir(parents=True, exist_ok=True)

    results = {}
    for name, df in datasets.items():
        results[name] = profile_dataframe(df, name, output_dir)

    return results


def combine_sales_sources(df_cali, df_bogota, df_medellin):
    df_cali = df_cali.copy()
    df_bogota = df_bogota.copy()
    df_medellin = df_medellin.copy()

    df_cali["source_branch"] = "Cali"
    df_bogota["source_branch"] = "Bogota"
    df_medellin["source_branch"] = "Medellin"

    return pd.concat([df_cali, df_bogota, df_medellin], ignore_index=True)

def profile_sales(df): # Realiza un perfilado exploratorio de los datos de ventas combinados y devuelve un DataFrame con los hallazgos.
  
    hallazgos = []

    # 1. Forma general
    hallazgos.append({"hallazgo": "Filas totales", "valor": df.shape[0]})
    hallazgos.append({"hallazgo": "Columnas totales", "valor": df.shape[1]})

    # 2. Ventas sin promotion_code (NaN + vacio)
    faltantes_promo = df["promotion_code"].isna().sum() + (df["promotion_code"] == "").sum()
    hallazgos.append({"hallazgo": "Ventas sin promotion_code (NaN + vacio)", "valor": int(faltantes_promo)})

    # 3. Cantidad invalida (no numerica o <= 0)
    quantity_numerico = pd.to_numeric(df["quantity"], errors="coerce")
    invalid_quantity = ((quantity_numerico <= 0) | quantity_numerico.isna()).sum()
    hallazgos.append({"hallazgo": "quantity invalida (<=0 o no numerica)", "valor": int(invalid_quantity)})

    # 4. Precio invalido (no numerico o <= 0)
    unit_price_numerico = pd.to_numeric(df["unit_price"], errors="coerce")
    invalid_price = ((unit_price_numerico <= 0) | unit_price_numerico.isna()).sum()
    hallazgos.append({"hallazgo": "unit_price invalido (<=0 o no numerico)", "valor": int(invalid_price)})

    # 5. Duplicados en sale_line_id
    duplicados = df["sale_line_id"].duplicated().sum()
    hallazgos.append({"hallazgo": "sale_line_id duplicados", "valor": int(duplicados)})

    # 6. Valores distintos en payment_method (sin limpiar)
    valores_pago = df["payment_method"].nunique()
    hallazgos.append({"hallazgo": "Valores distintos en payment_method", "valor": int(valores_pago)})

    # 7. Fechas invalidas (no convertibles a datetime)
    formatos_por_fuente = {"Cali": "%Y-%m-%d", "Bogota": "%d/%m/%Y", "Medellin": "%m-%d-%Y"}
    fechas_parseadas = pd.Series(pd.NaT, index=df.index)
    for fuente, formato in formatos_por_fuente.items():
        mask = df["source_branch"] == fuente
        fechas_parseadas.loc[mask] = pd.to_datetime(df.loc[mask, "sale_date"], format=formato, errors="coerce")
    fechas_invalidas = fechas_parseadas.isna().sum()
    hallazgos.append({"hallazgo": "Fechas invalidas", "valor": int(fechas_invalidas)})

    return pd.DataFrame(hallazgos)

