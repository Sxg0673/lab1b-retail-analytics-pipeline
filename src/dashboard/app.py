from pathlib import Path

import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[2]
TABLES_DIR = ROOT_DIR / "docs" / "query_outputs" / "tablas"
GRAPHS_DIR = ROOT_DIR / "docs" / "query_outputs" / "graficas"

SECTION_OPTIONS = [
    "Resumen ejecutivo",
    "Ventas por producto",
    "Ventas por región",
    "Ventas por periodo",
    "Cumplimiento de metas",
]


def load_dataframe(file_name: str) -> pd.DataFrame:
    path = TABLES_DIR / file_name
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def read_image(image_name: str):
    path = GRAPHS_DIR / image_name
    return path if path.exists() else None


def paginate_dataframe(df: pd.DataFrame, page_size: int, page_number: int) -> tuple[pd.DataFrame, int]:
    total_rows = len(df)
    total_pages = max(1, (total_rows + page_size - 1) // page_size)
    page_number = min(max(1, page_number), total_pages)
    start = (page_number - 1) * page_size
    end = start + page_size
    return df.iloc[start:end], total_pages


def format_currency(value) -> str:
    if pd.isna(value):
        return "-"
    return f"${value:,.0f}"


def render_header() -> None:
    st.markdown(
        """
        <style>
            .dashboard-title {
                background: linear-gradient(135deg, #1f4f7a 0%, #4f96c1 100%);
                border-radius: 24px;
                padding: 24px;
                color: white;
                margin-bottom: 24px;
            }
            .dashboard-subtitle {
                color: #dbe9ff;
                font-size: 1rem;
                margin-top: 0.5rem;
            }
            .stMetric {
                border-radius: 18px;
                padding: 18px;
            }
        </style>
        <div class="dashboard-title">
            <h1 style="margin: 0; font-size: 2.6rem;">Retail Analytics Dashboard</h1>
            <p class="dashboard-subtitle">Panel ejecutivo para visualizar ventas, desempeño de producto y cumplimiento de metas.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_kpis(kpi_df: pd.DataFrame) -> None:
    if kpi_df.empty:
        st.warning("No se encontraron los indicadores generales. Verifique los archivos en docs/query_outputs/tablas.")
        return

    row = kpi_df.iloc[0]
    ventas_brutas = row.get("ventas_brutas", 0)
    ventas_netas = row.get("ventas_netas", 0)
    descuentos = row.get("total_descuentos", 0)
    transacciones = row.get("total_transacciones", 0)

    col1, col2, col3, col4 = st.columns(4, gap="large")
    col1.metric("Transacciones", f"{int(transacciones):,}")
    col2.metric("Ventas brutas", format_currency(ventas_brutas))
    col3.metric("Ventas netas", format_currency(ventas_netas))
    col4.metric("Total descuentos", format_currency(descuentos))

    st.markdown(
        "---"
    )


def show_dataframe_section(title: str, df: pd.DataFrame, page_size: int) -> None:
    if df.empty:
        st.warning("No hay datos para mostrar en esta sección.")
        return

    page_number = st.number_input(
        "Página",
        min_value=1,
        max_value=max(1, (len(df) + page_size - 1) // page_size),
        value=1,
        step=1,
        format="%d",
    )
    paged_df, total_pages = paginate_dataframe(df, page_size, page_number)
    st.write(f"Mostrando página {page_number} de {total_pages} — {len(df):,} registros totales")
    st.dataframe(paged_df.reset_index(drop=True), use_container_width=True)


def render_overview_section(page_size: int) -> None:
    kpi_df = load_dataframe("rf01_ventas_totales.csv")
    ventas_mes = load_dataframe("rf04_ventas_por_mes.csv")
    ventas_dia = load_dataframe("rf04_ventas_por_dia_semana.csv")
    comparacion_df = load_dataframe("rf05_comparacion_mes_anterior.csv")

    show_kpis(kpi_df)

    st.markdown("### Gráficas clave")
    cols = st.columns(2)
    with cols[0]:
        if not ventas_mes.empty:
            st.bar_chart(ventas_mes.set_index("month")["ventas_netas"], use_container_width=True)
            st.caption("Ventas netas por mes")
        else:
            st.warning("No hay información mensual disponible.")
    with cols[1]:
        if not ventas_dia.empty:
            st.bar_chart(ventas_dia.set_index("day_name")["ventas_netas"], use_container_width=True)
            st.caption("Ventas netas por día de la semana")
        else:
            st.warning("No hay información por día disponible.")

    chart_files = [
        "rf02_productos_bajo_desempeno.png",
        "rf04_ventas_por_mes.png",
        "rf05_tendencia_mensual.png",
        "rf06_ventas_vs_meta.png",
    ]

    st.markdown("### Gráficas generadas por el pipeline")
    row_images = st.columns(len(chart_files))
    for column, image_name in zip(row_images, chart_files):
        image_path = read_image(image_name)
        if image_path:
            column.image(image_path, caption=image_name.replace("_", " ").replace(".png", ""), use_container_width=True)
        else:
            column.write("Sin imagen")

    st.markdown("---")
    st.markdown("#### Comparación de ventas mes a mes")
    if not comparacion_df.empty:
        comparacion_df["variacion_vs_mes_anterior"] = comparacion_df["variacion_vs_mes_anterior"].fillna(0)
        st.line_chart(comparacion_df.set_index("month")["ventas_netas"], use_container_width=True)
        st.dataframe(comparacion_df, use_container_width=True)
    else:
        st.warning("La comparación mensual no está disponible.")


def render_product_section(page_size: int) -> None:
    df = load_dataframe("rf02_ventas_por_producto.csv")
    if df.empty:
        st.warning("No se encontró el archivo rf02_ventas_por_producto.csv.")
        return

    st.markdown("### Productos de mayor y menor desempeño")
    sort_option = st.radio("Ordenar por", ["Menos ventas netas", "Más ventas netas"], horizontal=True)
    ascending = sort_option == "Menos ventas netas"
    df = df.sort_values("ventas_netas", ascending=ascending)

    if st.checkbox("Mostrar sólo los 20 productos principales", value=True):
        df = df.head(20)

    st.write(df.rename(columns={
        "product_name": "Producto",
        "category": "Categoría",
        "unidades_vendidas": "Unidades vendidas",
        "ventas_netas": "Ventas netas",
    }))
    st.markdown("---")
    show_dataframe_section("Tabla de ventas por producto", df, page_size)


def render_region_section(page_size: int) -> None:
    df = load_dataframe("rf03_ventas_por_region.csv")
    if df.empty:
        st.warning("No se encontró el archivo rf03_ventas_por_region.csv.")
        return

    st.markdown("### Desempeño por región y tienda")
    st.write(df.rename(columns={
        "region": "Región",
        "store_name": "Tienda",
        "ventas_netas": "Ventas netas",
    }))

    st.markdown("---")
    show_dataframe_section("Tabla de ventas por región", df, page_size)


def render_period_section(page_size: int) -> None:
    ventas_mes = load_dataframe("rf04_ventas_por_mes.csv")
    ventas_dia = load_dataframe("rf04_ventas_por_dia_semana.csv")

    st.markdown("### Ventas por periodo")
    if not ventas_mes.empty and not ventas_dia.empty:
        cols = st.columns(2)
        with cols[0]:
            st.subheader("Mensual")
            st.bar_chart(ventas_mes.set_index("month")["ventas_netas"], use_container_width=True)
            st.dataframe(ventas_mes, use_container_width=True)
        with cols[1]:
            st.subheader("Por día de la semana")
            st.bar_chart(ventas_dia.set_index("day_name")["ventas_netas"], use_container_width=True)
            st.dataframe(ventas_dia, use_container_width=True)
    else:
        st.warning("No hay datos suficientes para mostrar las ventas por periodo.")

    st.markdown("---")
    st.markdown("#### Detalle de ventas por periodo")
    if not ventas_mes.empty:
        show_dataframe_section("Ventas por mes", ventas_mes, page_size)
    if not ventas_dia.empty:
        show_dataframe_section("Ventas por día", ventas_dia, page_size)


def render_targets_section(page_size: int) -> None:
    df = load_dataframe("rf06_cumplimiento_metas.csv")
    if df.empty:
        st.warning("No se encontró el archivo rf06_cumplimiento_metas.csv.")
        return

    st.markdown("### Cumplimiento de metas de ventas")
    df = df.rename(columns={
        "store_name": "Tienda",
        "month": "Mes",
        "ventas_reales": "Ventas reales",
        "meta": "Meta",
        "diferencia": "Diferencia",
        "estado": "Estado",
    })

    st.write(df)
    st.markdown("---")
    st.markdown("#### Barras de ventas reales vs meta")
    if not df.empty:
        df_chart = df.set_index("Tienda")[ ["Ventas reales", "Meta"] ]
        st.bar_chart(df_chart, use_container_width=True)

    st.markdown("---")
    show_dataframe_section("Tabla de cumplimiento de metas", df, page_size)


def main() -> None:
    st.set_page_config(
        page_title="Retail Analytics Dashboard",
        page_icon="🛍️",
        layout="wide",
    )

    render_header()

    st.sidebar.markdown("## Controles del dashboard")
    section = st.sidebar.radio("Selecciona una sección", SECTION_OPTIONS)
    page_size = st.sidebar.select_slider("Filas por página", [5, 10, 15, 20, 25], value=10)
    show_advanced = st.sidebar.checkbox("Mostrar gráficas generadas por el pipeline", value=True)

    if show_advanced:
        st.sidebar.markdown(
            "El dashboard usa los resultados de consultas ya generados en `docs/query_outputs`.")

    if section == "Resumen ejecutivo":
        render_overview_section(page_size)
    elif section == "Ventas por producto":
        render_product_section(page_size)
    elif section == "Ventas por región":
        render_region_section(page_size)
    elif section == "Ventas por periodo":
        render_period_section(page_size)
    elif section == "Cumplimiento de metas":
        render_targets_section(page_size)

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "### Cómo usarlo\n" 
        "1. Genera el pipeline de ETL y las consultas.\n"
        "2. Ejecuta este dashboard con Streamlit.\n"
        "3. Cambia la sección para ver métricas, tablas y tendencias."
    )


if __name__ == "__main__":
    main()