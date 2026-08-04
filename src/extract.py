from pathlib import Path
import pandas as pd
import xml.etree.ElementTree as ET

# Esquema comun de columnas para las fuentes de transacciones de ventas de Cali, Bogota y Medellin.
COMMON_COLUMNS = [
    "sale_line_id", "sale_date", "store_id", "product_id",
    "quantity", "unit_price", "promotion_code", "payment_method",
]


def _resolve_input_files(input_path, valid_extensions):
    path = Path(input_path)

    if not path.exists():
        raise FileNotFoundError(f"No se encontró la ruta: {path}")

    if path.is_file():
        if path.suffix.lower() not in valid_extensions:
            raise ValueError(
                f"El archivo {path} no tiene una extensión soportada: {sorted(valid_extensions)}"
            )
        return [path]

    if path.is_dir():
        files = [p for p in path.rglob("*") if p.is_file() and p.suffix.lower() in valid_extensions]
        files.sort()
        if not files:
            raise FileNotFoundError(
                f"No se encontraron archivos con extensión {sorted(valid_extensions)} en {path}"
            )
        return files

    raise FileNotFoundError(f"No se pudo resolver la ruta: {path}")


def extract_from_csv(file_path):
    """Lee todos los archivos CSV encontrados de forma recursiva."""
    files = _resolve_input_files(file_path, {".csv"})
    dataframes = {}

    for file in files:
        dataframes[file.name] = pd.read_csv(file, encoding="utf-8-sig")

    return dataframes


def extract_from_json(file_path):
    """Lee todos los archivos JSON encontrados de forma recursiva."""
    files = _resolve_input_files(file_path, {".json"})
    dataframes = {}

    for file in files:
        dataframes[file.name] = pd.read_json(file)
        dataframes[file.name]= dataframes[file.name].rename(columns={
        "id_linea": "sale_line_id",
        "fecha": "sale_date",
        "sucursal": "store_id",
        "codigo_producto": "product_id",
        "unidades": "quantity",
        "precio": "unit_price",
        "promocion": "promotion_code",
        "medio_pago": "payment_method",
    })
    dataframes[file.name] = dataframes[file.name][COMMON_COLUMNS]

    return dataframes


def extract_from_xml(file_path):
    """Lee todos los archivos XML encontrados de forma recursiva."""
    files = _resolve_input_files(file_path, {".xml"})
    dataframes = {}

    for file in files:
        tree = ET.parse(file)
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
           dataframes[file.name] = pd.DataFrame(rows, columns=COMMON_COLUMNS)
    return dataframes