import pandas as pd
import xml.etree.ElementTree as ET

# Esquema comun de columnas para las fuentes de transacciones de ventas de Cali, Bogota y Medellin.
COMMON_COLUMNS = [
    "sale_line_id", "sale_date", "store_id", "product_id",
    "quantity", "unit_price", "promotion_code", "payment_method",
]


def extract_from_csv(file_path):

    return pd.read_csv(file_path, encoding="utf-8-sig")


def extract_from_json(file_path): 

    df = pd.read_json(file_path)
    df = df.rename(columns={
        "id_linea": "sale_line_id",
        "fecha": "sale_date",
        "sucursal": "store_id",
        "codigo_producto": "product_id",
        "unidades": "quantity",
        "precio": "unit_price",
        "promocion": "promotion_code",
        "medio_pago": "payment_method",
    })
    return df[COMMON_COLUMNS]


def extract_from_xml(file_path):
 
    tree = ET.parse(file_path)
    root = tree.getroot()

    rows = []
    for sale in root.findall("sale"):
        rows.append({
            "sale_line_id": sale.findtext("line_id"),
            "sale_date": sale.findtext("date"),
            "store_id": sale.findtext("branch_code"),
            "product_id": sale.findtext("sku"),
            "quantity": sale.findtext("units"),
            "unit_price": sale.findtext("unit_value"),
            "promotion_code": sale.findtext("promo_code"),
            "payment_method": sale.findtext("payment"),
        })

    return pd.DataFrame(rows, columns=COMMON_COLUMNS)