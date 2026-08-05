from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[2]
TABLES_DIR = ROOT_DIR / "docs" / "query_outputs" / "tablas"
GRAPHS_DIR = ROOT_DIR / "docs" / "query_outputs" / "graficas"

PAGE_SIZE_DEFAULT = 10

SECTION_OPTIONS = [
    "Resumen ejecutivo",
    "Desempeño por categoría",
    "Comparación por región",
    "Tendencias por periodo",
    "Cumplimiento de metas",
    "Reportes de marketing",
]

SECTION_DESCRIPTIONS = {
    "Resumen ejecutivo": "Visión general corporativa del rendimiento de ventas, métricas clave y tendencias estratégicas.",
    "Desempeño por categoría": "Analiza qué categorías mueven más volumen y cuáles necesitan atención en el portafolio.",
    "Comparación por región": "Compara ventas netas entre regiones y tiendas para detectar oportunidades de expansión.",
    "Tendencias por periodo": "Visualiza la evolución diaria y mensual para anticipar demanda y turnos de campaña.",
    "Cumplimiento de metas": "Monitorea qué tiendas cumplen sus objetivos comerciales y dónde hay brechas en desempeño.",
    "Reportes de marketing": "Genera reportes descargables listos para campañas, promociones y análisis de marketing.",
}


@st.cache_data
def load_dataframe(file_name: str) -> pd.DataFrame:
    path = TABLES_DIR / file_name
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def read_image(image_name: str):
    path = GRAPHS_DIR / image_name
    return path if path.exists() else None


def format_currency(value) -> str:
    if pd.isna(value) or value == "":
        return "-"
    return f"${value:,.0f}"


def show_dataframe_section(title: str, df: pd.DataFrame, page_size: int) -> None:
    if df.empty:
        st.warning("No hay datos para mostrar en esta sección.")
        return

    total_rows = len(df)
    total_pages = max(1, (total_rows + page_size - 1) // page_size)
    page_number = st.number_input(
        "Página",
        min_value=1,
        max_value=total_pages,
        value=1,
        step=1,
        format="%d",
    )

    page_number = min(max(1, page_number), total_pages)
    start = (page_number - 1) * page_size
    end = start + page_size
    paged_df = df.iloc[start:end]

    st.write(f"Mostrando página {page_number} de {total_pages} — {total_rows:,} registros totales")
    st.dataframe(paged_df.reset_index(drop=True), use_container_width=True)


def render_header() -> None:
    st.markdown(
        """
        <style>
            .dashboard-title {
                background: linear-gradient(135deg, #1f4f7a 0%, #4f96c1 100%);
                border-radius: 24px;
                padding: 28px;
                color: white;
                margin-bottom: 28px;
            }
            .dashboard-subtitle {
                color: #deebff;
                font-size: 1.05rem;
                margin-top: 0.4rem;
            }
            .dashboard-card {
                background: #ffffff;
                border-radius: 18px;
                padding: 20px;
                box-shadow: 0 12px 30px rgba(31, 79, 122, 0.08);
                margin-bottom: 20px;
            }
            .dashboard-small {
                color: #6b7a91;
            }
            .stDownloadButton>button {
                background-color: #1f4f7a;
                color: white;
            }
            .css-1d391kg .sidebar .block-container, .sidebar .block-container {
                background: linear-gradient(180deg, #f5f8fc 0%, #edf5fc 100%);
                border-radius: 24px;
                border: 1px solid #d3e3f2;
                box-shadow: 0 14px 35px rgba(38, 84, 135, 0.12);
            }
            .sidebar .stRadio, .sidebar .stSelectbox, .sidebar .stSlider, .sidebar .stButton {
                background: rgba(255, 255, 255, 0.98);
                border-radius: 16px;
                padding: 12px;
                border: 1px solid #c8d7ea;
            }
            .sidebar .stMarkdown h2, .sidebar .stMarkdown h3, .sidebar .stMarkdown p, .sidebar .stMarkdown li {
                color: #0e3256;
            }
            .sidebar .stMarkdown a {
                color: #0066cc;
            }
            .sidebar .stRadio>div, .sidebar .stSelectbox>div {
                color: #0e3256;
            }
            .sidebar .stTextInput>div>input, .sidebar .stSelectbox>div>div>div>span {
                color: #0e3256;
            }
            .sidebar .stRadio>div>div:nth-child(2), .sidebar .stSelectbox>div>div {
                color: #0e3256;
            }

        </style>
        <div class="dashboard-title">
            <h1 style="margin: 0; font-size: 2.8rem;">Retail Analytics Dashboard</h1>
            <p class="dashboard-subtitle">Un panel visual para monitorear ventas totales, desempeño de categorías, regiones y cumplimiento de metas.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_summary_panel(kpi_df: pd.DataFrame, product_df: pd.DataFrame, region_df: pd.DataFrame, day_df: pd.DataFrame) -> None:
    if kpi_df.empty:
        st.warning("No hay indicadores generales para mostrar.")
        return

    row = kpi_df.iloc[0]
    ventas_brutas = row.get("ventas_brutas", 0)
    ventas_netas = row.get("ventas_netas", 0)
    descuentos = row.get("total_descuentos", 0)
    transacciones = row.get("total_transacciones", 0)
    promedio_ticket = ventas_netas / transacciones if transacciones else 0

    top_categoria = "N/A"
    if not product_df.empty:
        categoria_total = product_df.groupby("category", as_index=False)["ventas_netas"].sum()
        top_categoria = categoria_total.sort_values("ventas_netas", ascending=False).iloc[0]["category"]

    mejor_dia = "N/A"
    if not day_df.empty:
        mejor_dia = day_df.loc[day_df["ventas_netas"].idxmax(), "day_name"]

    mejor_region = "N/A"
    if not region_df.empty:
        mejor_region = region_df.loc[region_df["ventas_netas"].idxmax(), "region"]

    col1, col2, col3, col4 = st.columns(4, gap="large")
    col1.metric("Ventas netas", format_currency(ventas_netas), help="Suma de ventas netas en el período calculado.")
    col2.metric("Transacciones", f"{int(transacciones):,}", help="Número total de transacciones procesadas.")
    col3.metric("Promedio por transacción", format_currency(promedio_ticket), help="Promedio de ventas netas por transacción.")
    col4.metric("Descuentos totales", format_currency(descuentos), help="Total de descuentos aplicados en el periodo.")

    st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3, gap="large")
    col1.metric("Categoría top", top_categoria)
    col2.metric("Mejor día", mejor_dia)
    col3.metric("Región líder", mejor_region)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")


def create_download_bytes(df: pd.DataFrame) -> bytes:
    buffer = BytesIO()
    df.to_csv(buffer, index=False, encoding="utf-8")
    return buffer.getvalue()


def render_marketing_reports(data: dict[str, pd.DataFrame]) -> None:
    st.markdown("### Reportes descargables para marketing")
    st.markdown("Usa estos reportes para acciones comerciales, campañas por región y análisis de categorías.")

    products = data["product"]
    region = data["region"]
    targets = data["targets"]

    if products.empty or region.empty or targets.empty:
        st.warning("No hay datos suficientes para generar reportes marketing.")
        return

    sales_by_category = (
        products.groupby("category", as_index=False)[["ventas_netas"]].sum().sort_values("ventas_netas", ascending=False)
    )
    top_products = products.sort_values("ventas_netas", ascending=False).head(40)
    region_overview = region.sort_values("ventas_netas", ascending=False)
    targets_summary = (
        targets.groupby("store_name", as_index=False)
        .agg(
            ventas_reales=pd.NamedAgg(column="ventas_reales", aggfunc="sum"),
            meta=pd.NamedAgg(column="meta", aggfunc="sum"),
            cumplidas=pd.NamedAgg(column="estado", aggfunc=lambda s: (s == "Cumplida").sum()),
            total_meses=pd.NamedAgg(column="month", aggfunc="count"),
        )
    )

    cols = st.columns([1, 1, 1])
    with cols[0]:
        st.download_button(
            "Descargar top productos",
            data=create_download_bytes(top_products),
            file_name="marketing_top_productos.csv",
            mime="text/csv",
        )
    with cols[1]:
        st.download_button(
            "Descargar desempeño por categoría",
            data=create_download_bytes(sales_by_category),
            file_name="marketing_desempeno_categorias.csv",
            mime="text/csv",
        )
    with cols[2]:
        st.download_button(
            "Descargar desempeño por región",
            data=create_download_bytes(region_overview),
            file_name="marketing_desempeno_region.csv",
            mime="text/csv",
        )

    st.download_button(
        "Descargar resumen de cumplimiento de metas",
        data=create_download_bytes(targets_summary),
        file_name="marketing_cumplimiento_metas.csv",
        mime="text/csv",
    )

    st.markdown("---")
    st.markdown("#### Resumen rápido para marketing")
    left, right = st.columns(2)
    left.metric("Categoría con más ventas", sales_by_category.iloc[0]["category"], format_currency(sales_by_category.iloc[0]["ventas_netas"]))
    right.metric("Región con más ventas", region_overview.iloc[0]["region"], format_currency(region_overview.iloc[0]["ventas_netas"]))
    st.dataframe(sales_by_category, use_container_width=True)


def render_overview_section(page_size: int) -> None:
    data = {
        "kpi": load_dataframe("rf01_ventas_totales.csv"),
        "product": load_dataframe("rf02_ventas_por_producto.csv"),
        "region": load_dataframe("rf03_ventas_por_region.csv"),
        "day": load_dataframe("rf04_ventas_por_dia_semana.csv"),
        "month": load_dataframe("rf04_ventas_por_mes.csv"),
        "compare": load_dataframe("rf05_comparacion_mes_anterior.csv"),
    }

    render_summary_panel(data["kpi"], data["product"], data["region"], data["day"])

    st.markdown("### Tendencias y comportamiento")
    chart_cols = st.columns(2, gap="large")
    with chart_cols[0]:
        if not data["month"].empty:
            st.subheader("Ventas netas por mes")
            st.markdown("Comparativa mensual para evaluar estacionalidad, temporadas altas y planes de demanda.")
            st.bar_chart(data["month"].set_index("month")["ventas_netas"])
        else:
            st.warning("No hay datos mensuales.")
    with chart_cols[1]:
        if not data["day"].empty:
            st.subheader("Ventas netas por día de la semana")
            st.markdown("Demanda semanal por día para optimizar inventario, personal y ofertas comerciales.")
            st.bar_chart(data["day"].set_index("day_name")["ventas_netas"])
        else:
            st.warning("No hay datos diarios.")

    if not data["compare"].empty:
        st.markdown("---")
        st.subheader("Comparación mes a mes")
        st.markdown("Visualiza la variación del desempeño de ventas frente al mes anterior para detectar tendencias de crecimiento o declive.")
        comparison = data["compare"].copy()
        comparison["variacion_vs_mes_anterior"] = comparison["variacion_vs_mes_anterior"].fillna(0)
        st.line_chart(comparison.set_index("month")["ventas_netas"])
        st.dataframe(comparison, use_container_width=True)

    if any(read_image(img) for img in ["rf02_productos_bajo_desempeno.png", "rf04_ventas_por_mes.png", "rf05_tendencia_mensual.png", "rf06_ventas_vs_meta.png"]):
        st.markdown("---")
        st.subheader("Gráficas generadas por el pipeline")
        img_cols = st.columns(4)
        for column, image_name in zip(img_cols, ["rf02_productos_bajo_desempeno.png", "rf04_ventas_por_mes.png", "rf05_tendencia_mensual.png", "rf06_ventas_vs_meta.png"]):
            image_path = read_image(image_name)
            if image_path:
                column.image(image_path, caption=image_name.replace("_", " ").replace(".png", ""), use_container_width=True)
            else:
                column.write("Sin imagen")


def render_category_section(page_size: int) -> None:
    df = load_dataframe("rf02_ventas_por_producto.csv")
    if df.empty:
        st.warning("No se encontró el archivo rf02_ventas_por_producto.csv.")
        return

    st.markdown("### Análisis de categorías de productos")
    category_perf = df.groupby("category", as_index=False)[["ventas_netas", "unidades_vendidas"]].sum()
    category_perf = category_perf.sort_values("ventas_netas", ascending=False)

    st.markdown("El gráfico muestra el aporte de cada categoría a las ventas netas totales. Útil para priorizar surtido y promociones.")
    st.bar_chart(category_perf.set_index("category")["ventas_netas"], use_container_width=True)
    st.dataframe(category_perf.rename(columns={"ventas_netas": "Ventas netas", "unidades_vendidas": "Unidades vendidas"}), use_container_width=True)

    st.markdown("---")
    st.subheader("Productos destacados por categoría")
    category_filter = st.selectbox("Selecciona una categoría", options=category_perf["category"].tolist())
    filtered = df[df["category"] == category_filter].sort_values("ventas_netas", ascending=False)
    show_dataframe_section(f"Productos de {category_filter}", filtered, page_size)


def render_region_section(page_size: int) -> None:
    df = load_dataframe("rf03_ventas_por_region.csv")
    if df.empty:
        st.warning("No se encontró el archivo rf03_ventas_por_region.csv.")
        return

    st.markdown("### Comparación por región y tienda")
    st.markdown("Esta sección muestra a dónde están llegando las ventas más fuertes y cuáles tiendas lideran el desempeño en cada región.")
    df_display = df.rename(columns={"region": "Región", "store_name": "Tienda", "ventas_netas": "Ventas netas"})
    st.dataframe(df_display, use_container_width=True)

    st.markdown("---")
    st.subheader("Rendimiento regional")
    st.markdown("Ventas netas por región para identificar los mercados más fuertes y las zonas con mayor potencial.")
    st.bar_chart(df.set_index("region")["ventas_netas"], use_container_width=True)

    st.markdown("---")
    st.subheader("Rendimiento por tienda")
    st.markdown("Comparación de tiendas para entender qué puntos de venta lideran la operación en cada región.")
    st.bar_chart(df.set_index("store_name")["ventas_netas"], use_container_width=True)

    show_dataframe_section("Tabla de ventas por región y tienda", df, page_size)


def render_period_section(page_size: int) -> None:
    ventas_mes = load_dataframe("rf04_ventas_por_mes.csv")
    ventas_dia = load_dataframe("rf04_ventas_por_dia_semana.csv")
    comparacion = load_dataframe("rf05_comparacion_mes_anterior.csv")

    st.markdown("### Análisis de tendencias diarias y mensuales")
    if not ventas_mes.empty:
        st.subheader("Tendencia mensual")
        st.markdown("Evolución de las ventas mes a mes para el análisis de ciclos de venta y planes de abastecimiento.")
        st.line_chart(ventas_mes.set_index("month")["ventas_netas"], use_container_width=True)
        st.dataframe(ventas_mes.rename(columns={"ventas_netas": "Ventas netas"}), use_container_width=True)

    if not ventas_dia.empty:
        st.subheader("Tendencia semanal")
        st.markdown("Desempeño por día de la semana para detectar días pico y optimizar personal y promociones.")
        st.bar_chart(ventas_dia.set_index("day_name")["ventas_netas"], use_container_width=True)
        st.dataframe(ventas_dia.rename(columns={"ventas_netas": "Ventas netas"}), use_container_width=True)

    if not comparacion.empty:
        st.markdown("---")
        st.subheader("Comparación mes a mes")
        comparacion["variacion_vs_mes_anterior"] = comparacion["variacion_vs_mes_anterior"].fillna(0)
        st.line_chart(comparacion.set_index("month")["ventas_netas"], use_container_width=True)
        st.dataframe(comparacion, use_container_width=True)

    st.markdown("---")
    if not ventas_mes.empty:
        show_dataframe_section("Ventas por mes", ventas_mes, page_size)
    if not ventas_dia.empty:
        show_dataframe_section("Ventas por día", ventas_dia, page_size)


def render_targets_section(page_size: int) -> None:
    df = load_dataframe("rf06_cumplimiento_metas.csv")
    if df.empty:
        st.warning("No se encontró el archivo rf06_cumplimiento_metas.csv.")
        return

    df = df.rename(columns={
        "store_name": "Tienda",
        "month": "Mes",
        "ventas_reales": "Ventas reales",
        "meta": "Meta",
        "diferencia": "Diferencia",
        "estado": "Estado",
    })

    st.markdown("### Identificación de cumplimiento de metas")
    st.markdown("Evalúa el desempeño de las sucursales frente a sus objetivos de venta mensuales para priorizar acciones comerciales.")
    df["Cumplió"] = df["Estado"] == "Cumplida"
    total_records = len(df)
    cumplidas = df["Cumplió"].sum()
    no_cumplidas = total_records - cumplidas

    cols = st.columns(3, gap="large")
    cols[0].metric("Meses analizados", f"{total_records}")
    cols[1].metric("Metas cumplidas", f"{cumplidas}")
    cols[2].metric("Metas no cumplidas", f"{no_cumplidas}")

    st.markdown("---")
    st.subheader("Tienda con mejor cumplimiento")
    top_store = (
        df[df["Cumplió"]]
        .groupby("Tienda", as_index=False)["Cumplió"].sum()
        .sort_values("Cumplió", ascending=False)
    )
    if not top_store.empty:
        st.write(top_store.head(10))

    st.markdown("---")
    st.subheader("Detalle del cumplimiento")
    st.dataframe(df.drop(columns=["Cumplió"]), use_container_width=True)
    st.markdown("---")
    show_dataframe_section("Tabla de cumplimiento de metas", df.drop(columns=["Cumplió"]), page_size)


def main() -> None:
    st.set_page_config(
        page_title="Retail Analytics Dashboard",
        layout="wide",
    )

    render_header()
    st.sidebar.markdown("# Dashboard de Analítica Retail")
    st.sidebar.markdown("_Insights comerciales y métricas retail integradas para la operación y el área comercial._")
    section = st.sidebar.radio("Selecciona un módulo", SECTION_OPTIONS)
    page_size = PAGE_SIZE_DEFAULT
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Descripción:** {SECTION_DESCRIPTIONS.get(section, '')}")
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "### Acciones rápidas"
        "\n- Revisa métricas de ventas totales."
        "\n- Analiza desempeño por categoría."
        "\n- Compara regiones y tiendas."
        "\n- Genera reportes para marketing."
    )

    if section == "Resumen ejecutivo":
        render_overview_section(page_size)
    elif section == "Desempeño por categoría":
        render_category_section(page_size)
    elif section == "Comparación por región":
        render_region_section(page_size)
    elif section == "Tendencias por periodo":
        render_period_section(page_size)
    elif section == "Cumplimiento de metas":
        render_targets_section(page_size)
    elif section == "Reportes de marketing":
        data = {
            "product": load_dataframe("rf02_ventas_por_producto.csv"),
            "region": load_dataframe("rf03_ventas_por_region.csv"),
            "targets": load_dataframe("rf06_cumplimiento_metas.csv"),
        }
        render_marketing_reports(data)

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "### ¿Cómo usar este dashboard?"
        "1. Selecciona la sección desde la barra lateral."
        "2. Revisa las métricas y gráficos clave."
        "3. Descarga los reportes de marketing cuando lo necesites."
    )


if __name__ == "__main__":
    main()
