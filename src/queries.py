import os
from pathlib import Path
import sqlite3

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

plt.style.use("seaborn-v0_8-whitegrid") # Establece un estilo de gráfico limpio y moderno
plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.edgecolor": "#4A5A66",
    "axes.labelcolor": "#2E3D46",
    "text.color": "#2E3D46",
    "xtick.color": "#2E3D46",
    "ytick.color": "#2E3D46",
})

COLOR_PRIMARIO = "#2C6E8F"
COLOR_SECUNDARIO = "#C1873B"
COLOR_ALERTA = "#B03A48"
COLOR_EXITO = "#3E7C55"

DB_PATH =  Path(__file__).resolve().parents[1] / "database" / "retail_analytics.db"
TABLE_NAME = "sales_analytics"
TABLAS_DIR = "docs/query_outputs/tablas"
GRAFICAS_DIR = "docs/query_outputs/graficas"


def _formato_miles(x, _pos=None): # Formato de número con separador de miles y sin decimales.
    return f"{x:,.0f}"


def _conectar(): # Establece una conexión a la base de datos SQLite.
    return sqlite3.connect(DB_PATH)


def _guardar_tabla(df, nombre_archivo): # Guarda un DataFrame como archivo CSV en la carpeta de salida de tablas.
    os.makedirs(TABLAS_DIR, exist_ok=True)
    ruta = os.path.join(TABLAS_DIR, nombre_archivo)
    df.to_csv(ruta, index=False)
    return ruta


def _guardar_grafica(fig, nombre_archivo): # Guarda una figura de Matplotlib como archivo PNG en la carpeta de salida de gráficas.
    os.makedirs(GRAFICAS_DIR, exist_ok=True)
    ruta = os.path.join(GRAFICAS_DIR, nombre_archivo)
    fig.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return ruta


def query_rf01_ventas_totales(conn):
    # RF01 - Ventas totales en el periodo, como indicador principal.
    explicacion = (
        "Responde la pregunta de negocio sobre cuales son las ventas totales "
        "en el periodo, como indicador principal antes de profundizar en el detalle."
    )
    sql = f"""
        SELECT
            COUNT(*) AS total_transacciones,
            SUM(gross_sales) AS ventas_brutas,
            SUM(discount_amount) AS total_descuentos,
            SUM(net_sales) AS ventas_netas
        FROM {TABLE_NAME}
    """
    df = pd.read_sql(sql, conn)
    _guardar_tabla(df, "rf01_ventas_totales.csv")
    return explicacion, df


def query_rf02_ventas_por_producto(conn):
    # RF02 - Ventas por producto, para identificar los productos con menor desempeño.
    explicacion = (
        "Responde la pregunta de negocio sobre que productos se estan vendiendo "
        "por debajo de lo esperado, ordenando de menor a mayor venta neta."
    )
    sql = f"""
        SELECT category, product_name,
               SUM(quantity) AS unidades_vendidas,
               SUM(net_sales) AS ventas_netas
        FROM {TABLE_NAME}
        GROUP BY category, product_name
        ORDER BY ventas_netas ASC
    """
    df = pd.read_sql(sql, conn)
    _guardar_tabla(df, "rf02_ventas_por_producto.csv")

    peores = df.head(5).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 4.8))
    barras = ax.barh(peores["product_name"], peores["ventas_netas"], color=COLOR_ALERTA, height=0.6)
    ax.set_xlabel("Ventas netas (COP)")
    ax.set_title("5 productos con menor venta neta", loc="left", pad=12)
    ax.set_xlim(0, peores["ventas_netas"].max() * 1.22)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(_formato_miles))
    ax.spines[["top", "right"]].set_visible(False)
    for barra, valor in zip(barras, peores["ventas_netas"]):
        ax.text(barra.get_width() * 1.02, barra.get_y() + barra.get_height() / 2,
                 f"${valor:,.0f}", va="center", fontsize=10, fontweight="bold", color=COLOR_ALERTA)
    plt.tight_layout()
    _guardar_grafica(fig, "rf02_productos_bajo_desempeno.png")

    return explicacion, df


def query_rf03_ventas_por_region(conn):
    # RF03 - Ventas por region o por tienda, para identificar las regiones o tiendas con menor desempeño.
    explicacion = (
        "Responde la pregunta de negocio sobre el desempeño al filtrar por "
        "region o por tienda especifica."
    )
    sql = f"""
        SELECT region, store_name,
               SUM(net_sales) AS ventas_netas
        FROM {TABLE_NAME}
        GROUP BY region, store_name
        ORDER BY ventas_netas DESC
    """
    df = pd.read_sql(sql, conn)
    _guardar_tabla(df, "rf03_ventas_por_region.csv")
    return explicacion, df


def query_rf04_ventas_por_periodo(conn):
    # RF04 - Ventas por periodo (mes y dia de la semana), para identificar los periodos con mayor volumen de ventas.
    explicacion = (
        "Responde la pregunta de negocio sobre en que dias o meses se "
        "concentra el mayor volumen de ventas."
    )
    sql_mes = f"""
        SELECT month, SUM(net_sales) AS ventas_netas
        FROM {TABLE_NAME}
        GROUP BY month
        ORDER BY month
    """
    df_mes = pd.read_sql(sql_mes, conn)
    _guardar_tabla(df_mes, "rf04_ventas_por_mes.csv")

    sql_dia = f"""
        SELECT day_name, SUM(net_sales) AS ventas_netas
        FROM {TABLE_NAME}
        GROUP BY day_name
        ORDER BY ventas_netas DESC
    """
    df_dia = pd.read_sql(sql_dia, conn)
    _guardar_tabla(df_dia, "rf04_ventas_por_dia_semana.csv")

    fig, ax = plt.subplots(figsize=(7, 4.5))
    barras = ax.bar(df_mes["month"], df_mes["ventas_netas"], color=COLOR_PRIMARIO, width=0.55)
    ax.set_title("Ventas netas por mes", loc="left", pad=12)
    ax.set_ylabel("Ventas netas (COP)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(_formato_miles))
    ax.set_ylim(0, df_mes["ventas_netas"].max() * 1.15)
    ax.spines[["top", "right"]].set_visible(False)
    for barra, valor in zip(barras, df_mes["ventas_netas"]):
        ax.text(barra.get_x() + barra.get_width() / 2, barra.get_height() * 1.02,
                 f"${valor:,.0f}", ha="center", fontsize=10, fontweight="bold", color=COLOR_PRIMARIO)
    plt.tight_layout()
    _guardar_grafica(fig, "rf04_ventas_por_mes.png")

    return explicacion, {"por_mes": df_mes, "por_dia_semana": df_dia}


def query_rf05_comparacion_mes_anterior(conn):
    # RF05 - Comparación de ventas frente al mes anterior, para identificar la tendencia de ventas.
    explicacion = (
        "Responde la pregunta de negocio sobre como han evolucionado las "
        "ventas frente al mes anterior."
    )
    sql = f"""
        SELECT month,
               SUM(net_sales) AS ventas_netas,
               SUM(net_sales) - LAG(SUM(net_sales)) OVER (ORDER BY month) AS variacion_vs_mes_anterior
        FROM {TABLE_NAME}
        GROUP BY month
        ORDER BY month
    """
    df = pd.read_sql(sql, conn)
    _guardar_tabla(df, "rf05_comparacion_mes_anterior.csv")

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(df["month"], df["ventas_netas"], marker="o", markersize=8,
            color=COLOR_EXITO, linewidth=2.5, markerfacecolor="white", markeredgewidth=2)
    ax.set_title("Tendencia de ventas netas mes a mes", loc="left", pad=12)
    ax.set_ylabel("Ventas netas (COP)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(_formato_miles))
    ax.set_ylim(df["ventas_netas"].min() * 0.88, df["ventas_netas"].max() * 1.18)
    ax.spines[["top", "right"]].set_visible(False)
    for x, y in zip(df["month"], df["ventas_netas"]):
        ax.annotate(f"${y:,.0f}", (x, y), textcoords="offset points", xytext=(0, 12),
                     ha="center", fontsize=10, fontweight="bold", color=COLOR_EXITO)
    plt.tight_layout()
    _guardar_grafica(fig, "rf05_tendencia_mensual.png")

    return explicacion, df


def query_rf06_cumplimiento_metas(conn):
    # RF06 - Cumplimiento de metas de ventas, para identificar que tiendas estan cumpliendo sus metas y cuales no.
    explicacion = (
        "Responde la pregunta de negocio sobre que tiendas estan cumpliendo "
        "sus metas de ventas y cuales no."
    )
    sql = f"""
        SELECT store_name, month,
               SUM(net_sales) AS ventas_reales,
               MAX(sales_target) AS meta,
               SUM(net_sales) - MAX(sales_target) AS diferencia,
               CASE WHEN SUM(net_sales) >= MAX(sales_target) THEN 'Cumplida' ELSE 'No cumplida' END AS estado
        FROM {TABLE_NAME}
        GROUP BY store_name, month
        ORDER BY store_name, month
    """
    df = pd.read_sql(sql, conn)
    _guardar_tabla(df, "rf06_cumplimiento_metas.csv")

    fig, ax = plt.subplots(figsize=(10, 5.5))
    x = range(len(df))
    ancho = 0.38
    barras_reales = ax.bar([i - ancho/2 for i in x], df["ventas_reales"], width=ancho,
                            label="Ventas reales", color=COLOR_PRIMARIO)
    ax.bar([i + ancho/2 for i in x], df["meta"], width=ancho,
           label="Meta", color=COLOR_SECUNDARIO, alpha=0.85)
    ax.set_xticks(list(x))
    ax.set_xticklabels(df["store_name"] + "\n" + df["month"], fontsize=9)
    ax.set_ylabel("Ventas (COP)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(_formato_miles))
    ax.set_title("Ventas reales vs. meta, por tienda y mes", loc="left", pad=12)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, loc="upper right")
    hay_cumplidas = (df["estado"] == "Cumplida").any()
    for i, cumplida in enumerate(df["estado"] == "Cumplida"):
        if cumplida:
            ax.scatter(i - ancho/2, df["ventas_reales"].iloc[i] * 1.05, marker="*",
                        s=220, color=COLOR_EXITO, zorder=5,
                        label="Meta cumplida" if i == df[df["estado"]=="Cumplida"].index[0] else None)
    if hay_cumplidas:
        ax.legend(frameon=False, loc="upper right")
    plt.tight_layout()
    _guardar_grafica(fig, "rf06_ventas_vs_meta.png")

    return explicacion, df


def ejecutar_todas_las_queries():
    # Ejecuta todas las queries de negocio y muestra los resultados en consola, además de guardar los resultados en archivos CSV y gráficas en PNG.
    conn = _conectar()
    try:
        queries = [
            ("RF01", query_rf01_ventas_totales),
            ("RF02", query_rf02_ventas_por_producto),
            ("RF03", query_rf03_ventas_por_region),
            ("RF04", query_rf04_ventas_por_periodo),
            ("RF05", query_rf05_comparacion_mes_anterior),
            ("RF06", query_rf06_cumplimiento_metas),
        ]
        for codigo, funcion in queries:
            print("=" * 70)
            print(codigo)
            explicacion, resultado = funcion(conn)
            print(explicacion)
            if isinstance(resultado, dict):
                for nombre, df in resultado.items():
                    print(f"\n-- {nombre} --")
                    print(df.to_string(index=False))
            else:
                print(resultado.to_string(index=False))
            print()
    finally:
        conn.close()


if __name__ == "__main__":
    ejecutar_todas_las_queries()