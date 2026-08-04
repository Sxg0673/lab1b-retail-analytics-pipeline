from pathlib import Path
import pandas as pd
import xml.etree.ElementTree as ET


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
                "line_id": sale.findtext("line_id"),
                "date": sale.findtext("date"),
                "branch_code": sale.findtext("branch_code"),
                "sku": sale.findtext("sku"),
                "units": sale.findtext("units"),
                "unit_value": sale.findtext("unit_value"),
                "promo_code": sale.findtext("promo_code"),
                "payment": sale.findtext("payment"),
            })

        dataframes[file.name] = pd.DataFrame(rows)

    return dataframes