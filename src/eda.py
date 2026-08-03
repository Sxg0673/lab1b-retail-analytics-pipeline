import pandas as pd
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET

# ============================================================
# Cali CSV
# ============================================================
df_cali = pd.read_csv("data/raw/sales_cali.csv")

print("Forma del DataFrame (filas, columnas):")
print(df_cali.shape)

print("\nTipos de dato por columna:")
print(df_cali.dtypes)

print("\nValores nulos por columna:")
print(df_cali.isna().sum())

print("\nCantidad de valores invalidos en quantity (<= 0):")
print((df_cali["quantity"] <= 0).sum())
print("\nFilas con quantity invalida (<= 0):")
print(df_cali[df_cali["quantity"] <= 0])


print("\nCantidad de valores invalidos en unit_price (<= 0):") 
print((df_cali["unit_price"] <= 0).sum()) 
print("\nFilas con unit_price invalida (<= 0):") 
print(df_cali[df_cali["unit_price"] <= 0])

print("\nCantidad de sale_line_id duplicados:")
print(df_cali["sale_line_id"].duplicated().sum())

print("\nFilas duplicadas (todas las ocurrencias):")
print(df_cali[df_cali["sale_line_id"].duplicated(keep=False)])

print("\nValores distintos en payment_method:")
print(df_cali["payment_method"].unique())

print("\nConteo de cada valor en payment_method:")
print(df_cali["payment_method"].value_counts())

print("\nConversion de sale_date a formato fecha real:")
fechas_convertidas = pd.to_datetime(df_cali["sale_date"], format="%Y-%m-%d", errors="coerce")

print("\nCantidad de fechas invalidas:")
print(fechas_convertidas.isna().sum())

print("\nFilas con fecha invalida:")
print(df_cali[fechas_convertidas.isna()])




# ============================================================
# Bogota JSON
# ============================================================
df_bogota = pd.read_json("data/raw/sales_bogota.json")

print("\n" + "="*60)
print("BOGOTA")
print("="*60)

print("\nForma del DataFrame (filas, columnas):")
print(df_bogota.shape)

print("\nTipos de dato por columna:")
print(df_bogota.dtypes)

print("\nValores nulos por columna:")
print(df_bogota.isna().sum())

print("\nCantidad de valores invalidos en unidades (<= 0):")
print((df_bogota["unidades"] <= 0).sum())
print(df_bogota[df_bogota["unidades"] <= 0])

print("\nTipo de dato de la columna precio:")
print(df_bogota["precio"].apply(type).value_counts())

print("\nValores de precio que NO son numericos:")
print(df_bogota[df_bogota["precio"].apply(lambda x: isinstance(x, str))])

precio_numerico = pd.to_numeric(df_bogota["precio"], errors="coerce")

print("\nCantidad de valores invalidos en precio (<=0 o no numerico):")
print(((precio_numerico <= 0) | precio_numerico.isna()).sum())
print(df_bogota[(precio_numerico <= 0) | precio_numerico.isna()])

print("\nCantidad de id_linea duplicados:")
print(df_bogota["id_linea"].duplicated().sum())
print(df_bogota[df_bogota["id_linea"].duplicated(keep=False)])

print("\nValores distintos en medio_pago:")
print(df_bogota["medio_pago"].unique())
print(df_bogota["medio_pago"].value_counts())

print("\nFechas invalidas (formato esperado DD/MM/YYYY):")
fechas_bogota = pd.to_datetime(df_bogota["fecha"], format="%d/%m/%Y", errors="coerce")
print(fechas_bogota.isna().sum())
print(df_bogota[fechas_bogota.isna()])



# ============================================================
# Medellin XML
# ============================================================
tree = ET.parse("data/raw/sales_medellin.xml")
root = tree.getroot()

rows = []
for sale in root.findall("sale"):
    rows.append({
        "line_id": sale.findtext("line_id"),
        "date": sale.findtext("date"),
        "branch_code": sale.findtext("branch_code"),
        "sku": sale.findtext("sku"),
        "units": sale.findtext("units"),
        "unit_value": sale.findtext("unit_value"),
        "promo_code": sale.findtext("promo_code"),
        "payment": sale.findtext("payment"),
    })

df_medellin = pd.DataFrame(rows)

print("\n" + "="*60)
print("MEDELLIN")
print("="*60)

print("\nForma del DataFrame (filas, columnas):")
print(df_medellin.shape)

print("\nTipos de dato por columna:")
print(df_medellin.dtypes)

print("\nValores nulos por columna:")
print(df_medellin.isna().sum())

print("\nCantidad de promo_code vacios (string vacio, no nulo):")
print((df_medellin["promo_code"] == "").sum())

units_numerico = pd.to_numeric(df_medellin["units"], errors="coerce")
print("\nCantidad de valores invalidos en units (<=0 o no numerico):")
print(((units_numerico <= 0) | units_numerico.isna()).sum())
print(df_medellin[(units_numerico <= 0) | units_numerico.isna()])

unit_value_numerico = pd.to_numeric(df_medellin["unit_value"], errors="coerce")
print("\nCantidad de valores invalidos en unit_value (<=0 o no numerico):")
print(((unit_value_numerico <= 0) | unit_value_numerico.isna()).sum())
print(df_medellin[(unit_value_numerico <= 0) | unit_value_numerico.isna()])

print("\nCantidad de line_id duplicados:")
print(df_medellin["line_id"].duplicated().sum())
print(df_medellin[df_medellin["line_id"].duplicated(keep=False)])

print("\nValores distintos en payment:")
print(df_medellin["payment"].unique())
print(df_medellin["payment"].value_counts())

print("\nFechas invalidas (formato esperado MM-DD-YYYY):")
fechas_medellin = pd.to_datetime(df_medellin["date"], format="%m-%d-%Y", errors="coerce")
print(fechas_medellin.isna().sum())
print(df_medellin[fechas_medellin.isna()])




# --- Tabla resumen de hallazgos EDA - Cali ---
resumen_cali = pd.DataFrame([
    {"hallazgo": "Filas totales", "valor": df_cali.shape[0]},
    {"hallazgo": "Columnas totales", "valor": df_cali.shape[1]},
    {"hallazgo": "Nulos en promotion_code", "valor": df_cali["promotion_code"].isna().sum()},
    {"hallazgo": "Quantity invalida (<=0)", "valor": (df_cali["quantity"] <= 0).sum()},
    {"hallazgo": "Unit_price invalido (<=0)", "valor": (df_cali["unit_price"] <= 0).sum()},
    {"hallazgo": "sale_line_id duplicados", "valor": df_cali["sale_line_id"].duplicated().sum()},
    {"hallazgo": "Valores distintos payment_method", "valor": df_cali["payment_method"].nunique()},
    {"hallazgo": "Fechas invalidas", "valor": fechas_convertidas.isna().sum()},
])

print("\nResumen de hallazgos - Cali:")
print(resumen_cali)

resumen_cali.to_csv("docs/eda_outputs/tablas/01_resumen_eda_cali.csv", index=False)
print("\nTabla guardada en docs/eda_outputs/tablas/01_resumen_eda_cali.csv")




# --- Tabla resumen de hallazgos EDA - Bogota ---
resumen_bogota = pd.DataFrame([
    {"hallazgo": "Filas totales", "valor": df_bogota.shape[0]},
    {"hallazgo": "Columnas totales", "valor": df_bogota.shape[1]},
    {"hallazgo": "Nulos en promocion", "valor": df_bogota["promocion"].isna().sum()},
    {"hallazgo": "Unidades invalida (<=0)", "valor": (df_bogota["unidades"] <= 0).sum()},
    {"hallazgo": "Precio invalido (<=0 o no numerico)", "valor": ((precio_numerico <= 0) | precio_numerico.isna()).sum()},
    {"hallazgo": "id_linea duplicados", "valor": df_bogota["id_linea"].duplicated().sum()},
    {"hallazgo": "Valores distintos medio_pago", "valor": df_bogota["medio_pago"].nunique()},
    {"hallazgo": "Fechas invalidas", "valor": fechas_bogota.isna().sum()},
])

print("\nResumen de hallazgos - Bogota:")
print(resumen_bogota)

resumen_bogota.to_csv("docs/eda_outputs/tablas/02_resumen_eda_bogota.csv", index=False)
print("\nTabla guardada en docs/eda_outputs/tablas/02_resumen_eda_bogota.csv")




# --- Tabla resumen de hallazgos EDA - Medellin ---
resumen_medellin = pd.DataFrame([
    {"hallazgo": "Filas totales", "valor": df_medellin.shape[0]},
    {"hallazgo": "Columnas totales", "valor": df_medellin.shape[1]},
    {"hallazgo": "promo_code vacio (string vacio)", "valor": (df_medellin["promo_code"] == "").sum()},
    {"hallazgo": "Units invalida (<=0 o no numerico)", "valor": ((units_numerico <= 0) | units_numerico.isna()).sum()},
    {"hallazgo": "Unit_value invalido (<=0 o no numerico)", "valor": ((unit_value_numerico <= 0) | unit_value_numerico.isna()).sum()},
    {"hallazgo": "line_id duplicados", "valor": df_medellin["line_id"].duplicated().sum()},
    {"hallazgo": "Valores distintos payment", "valor": df_medellin["payment"].nunique()},
    {"hallazgo": "Fechas invalidas", "valor": fechas_medellin.isna().sum()},
])

print("\nResumen de hallazgos - Medellin:")
print(resumen_medellin)

resumen_medellin.to_csv("docs/eda_outputs/tablas/03_resumen_eda_medellin.csv", index=False)
print("\nTabla guardada en docs/eda_outputs/tablas/03_resumen_eda_medellin.csv")





## --- Grafica: problemas de calidad agregados ---
total_por_categoria = {
    "Cantidad invalida": resumen_cali.iloc[3]["valor"] + resumen_bogota.iloc[3]["valor"] + resumen_medellin.iloc[3]["valor"],
    "Precio invalido": resumen_cali.iloc[4]["valor"] + resumen_bogota.iloc[4]["valor"] + resumen_medellin.iloc[4]["valor"],
    "Duplicados": resumen_cali.iloc[5]["valor"] + resumen_bogota.iloc[5]["valor"] + resumen_medellin.iloc[5]["valor"],
    "Inconsistencia categorica": max(0, resumen_cali.iloc[6]["valor"]-3) + max(0, resumen_bogota.iloc[6]["valor"]-3) + max(0, resumen_medellin.iloc[6]["valor"]-3),
    "Fechas invalidas": resumen_cali.iloc[7]["valor"] + resumen_bogota.iloc[7]["valor"] + resumen_medellin.iloc[7]["valor"],
}

fig, ax = plt.subplots(figsize=(7, 4.5))
etiquetas = list(total_por_categoria.keys())
valores = list(total_por_categoria.values())
colores = ["#C1873B", "#B03A48", "#6A4C93", "#2C6E8F", "#3E7C55"]

barras = ax.barh(etiquetas, valores, color=colores)
ax.set_xlabel("Cantidad de registros afectados (combinando las 3 fuentes)")
ax.set_title("Problemas de calidad encontrados en el EDA")
ax.set_xlim(0, max(valores) + 1)

for barra, valor in zip(barras, valores):
    ax.text(barra.get_width() + 0.05, barra.get_y() + barra.get_height()/2,
            str(valor), va="center", fontweight="bold")

plt.tight_layout()
fig.savefig("docs/eda_outputs/graficas/01_problemas_calidad_agregados.png", dpi=150)
print("\nGrafica agregada guardada.")