import pandas as pd
import xml.etree.ElementTree as ET


def extract_from_csv(file_path): # Lee un archivo CSV y devuelve un DataFrame de pandas
    
    return pd.read_csv(file_path, encoding="utf-8-sig") # Se utiliza utf-8-sig para manejar correctamente los archivos CSV que contienen caracteres especiales, como acentos o eñes, y evitar problemas de codificación al leer el archivo.


def extract_from_json(file_path): # Lee un archivo JSON y devuelve un DataFrame de pandas

    return pd.read_json(file_path)


def extract_from_xml(file_path): # Lee un archivo XML y devuelve un DataFrame de pandas

    tree = ET.parse(file_path) 
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

    return pd.DataFrame(rows)