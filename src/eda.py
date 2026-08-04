from pathlib import Path
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import re


matplotlib.use("Agg")

def _sanitize_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")


def _plot_missing_values(df: pd.DataFrame, output_path: Path):
    missing = df.isna().sum().sort_values(ascending=False)
    if missing.empty:
        return

    fig, ax = plt.subplots(figsize=(8, 4.5))
    missing.head(10).plot(kind="bar", color="#4C78A8", ax=ax)
    ax.set_title("Valores faltantes por columna")
    ax.set_ylabel("Cantidad")
    ax.set_xlabel("Columna")
    ax.tick_params(axis="x", rotation=45)
    plt.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def _plot_categorical_distribution(df: pd.DataFrame, output_path: Path):
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    if not categorical_cols:
        return

    target_col = next((col for col in categorical_cols if df[col].nunique(dropna=True) <= 10), categorical_cols[0])
    counts = df[target_col].fillna("<NA>").value_counts().head(10)
    if counts.empty:
        return

    fig, ax = plt.subplots(figsize=(7, 4.5))
    counts.plot(kind="bar", color="#F58518", ax=ax)
    ax.set_title(f"Distribución de {target_col}")
    ax.set_ylabel("Frecuencia")
    ax.set_xlabel(target_col)
    ax.tick_params(axis="x", rotation=45)
    plt.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def _plot_numeric_distributions(df: pd.DataFrame, output_path: Path):
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if not numeric_cols:
        return

    n_cols = min(2, len(numeric_cols))
    fig, axes = plt.subplots(1, n_cols, figsize=(8 * n_cols, 4.5))
    if n_cols == 1:
        axes = [axes]

    for ax, column in zip(axes, numeric_cols[:n_cols]):
        values = pd.to_numeric(df[column], errors="coerce").dropna()
        if values.empty:
            continue
        values.plot(kind="hist", bins=12, ax=ax, color="#54A24B", edgecolor="black")
        ax.set_title(f"Distribución de {column}")
        ax.set_xlabel(column)
        ax.set_ylabel("Frecuencia")

    plt.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def _summarize_sales_quality(extracted_data_csv, extracted_data_json, extracted_data_xml):
    rows = []

    datasets = (
        list(extracted_data_csv.items()) +
        list(extracted_data_json.items()) +
        list(extracted_data_xml.items())
    )

    for dataset_name, frame in datasets:

        quantity_numeric = pd.to_numeric(frame["quantity"], errors="coerce")
        price_numeric = pd.to_numeric(frame["unit_price"], errors="coerce")

        # Deja que pandas detecte automáticamente el formato de la fecha
        dates = pd.to_datetime(frame["sale_date"], errors="coerce")

        rows.append({
            "dataset": dataset_name,
            "filas": int(frame.shape[0]),
            "invalid_quantity": int(((quantity_numeric <= 0) | quantity_numeric.isna()).sum()),
            "invalid_price": int(((price_numeric <= 0) | price_numeric.isna()).sum()),
            "duplicados": int(frame.duplicated().sum()),
            "promocion_vacia": int(frame["promotion_code"].fillna("").astype(str).eq("").sum()),
            "fechas_invalidas": int(dates.isna().sum()),
            "payment_values": int(frame["payment_method"].nunique(dropna=True)),
        })

    return pd.DataFrame(rows)

def _plot_sales_quality(summary_df: pd.DataFrame, output_path: Path):
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    axes = axes.flatten()

    metrics = ["invalid_quantity", "invalid_price", "duplicados", "fechas_invalidas"]
    for ax, metric in zip(axes, metrics):
        summary_df.plot(kind="bar", x="dataset", y=metric, ax=ax, color="#4E79A7")
        ax.set_title(metric.replace("_", " ").title())
        ax.set_ylabel("Cantidad")
        ax.tick_params(axis="x", rotation=45)

    plt.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def _plot_revenue_comparison(extracted_data_csv,
                             extracted_data_json,
                             extracted_data_xml,
                             output_path: Path):

    rows = []

    datasets = (
        list(extracted_data_csv.items()) +
        list(extracted_data_json.items()) +
        list(extracted_data_xml.items())
    )

    for dataset_name, frame in datasets:

        quantity_numeric = pd.to_numeric(frame["quantity"], errors="coerce")
        price_numeric = pd.to_numeric(frame["unit_price"], errors="coerce")

        revenue = (quantity_numeric * price_numeric).fillna(0).sum()

        rows.append({
            "dataset": dataset_name,
            "revenue": float(revenue)
        })

    if not rows:
        return

    revenue_df = pd.DataFrame(rows)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    revenue_df.plot(kind="bar", x="dataset", y="revenue", ax=ax, color="#B07AA1")
    ax.set_title("Ingresos estimados por fuente")
    ax.set_ylabel("Valor estimado")
    ax.tick_params(axis="x", rotation=45)

    plt.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


# def run_eda(extracted_data_csv, extracted_data_json, extracted_data_xml, output_dir=None):
    output_dir = Path(output_dir) if output_dir is not None else Path("docs/eda_outputs/graficas")
    output_dir.mkdir(parents=True, exist_ok=True)

    summary_df = _summarize_sales_quality(extracted_data_csv, extracted_data_json, extracted_data_xml)
    if not summary_df.empty:
        summary_df.to_csv(output_dir / "01_quality_summary.csv", index=False)
        _plot_sales_quality(summary_df, output_dir / "01_quality_summary.png")
        _plot_revenue_comparison(extracted_data_csv, extracted_data_json, extracted_data_xml, output_dir / "02_revenue_comparison.png")

    for source_name, frames in [("csv", extracted_data_csv), ("json", extracted_data_json), ("xml", extracted_data_xml)]:
        for dataset_name, frame in frames.items():
            base_name = _sanitize_name(dataset_name)
            _plot_missing_values(frame, output_dir / f"{source_name}_{base_name}_missing.png")
            _plot_categorical_distribution(frame, output_dir / f"{source_name}_{base_name}_categorical.png")
            _plot_numeric_distributions(frame, output_dir / f"{source_name}_{base_name}_numeric.png")

    return output_dir
