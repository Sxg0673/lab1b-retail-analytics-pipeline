from pathlib import Path
import subprocess
import sys

import pandas as pd

from extract import extract_from_csv, extract_from_xml, extract_from_json
from profile import profile_datasets, profile_sales
from clean import clean_sales
from transform import transform_sales
from validate import validate_sales
from load import load_to_csv, load_to_db
from queries import ejecutar_todas_las_queries
from log import log_progress
from dashboard.launcher import launch_dashboard

# Mapeo de cada archivo de transacciones a la sucursal que representa.
SALES_SOURCE_MAP = {
    "sales_cali.csv": "Cali",
    "sales_bogota.json": "Bogota",
    "sales_medellin.xml": "Medellin",
}


def main():
    project_root = Path(__file__).resolve().parents[1]
    data_path = project_root / "data" / "raw"
    profile_output_dir = project_root / "docs" / "eda_outputs" / "perfiles"
    log_file = project_root / "logs" / "etl_run.log"

    log_file.parent.mkdir(parents=True, exist_ok=True)

    def log(message):
        log_progress(message, log_file)
        print(message)

    log("=== Pipeline iniciado ===")
    log(f"Datos de entrada: {data_path}")

    # ------------------------------------------------------------------
    # Extract
    # ------------------------------------------------------------------
    log("Extract iniciado")
    extracted_data_csv = extract_from_csv(data_path)
    extracted_data_xml = extract_from_xml(data_path)
    extracted_data_json = extract_from_json(data_path)

    for etiqueta, datos in [("CSV", extracted_data_csv),
                            ("XML", extracted_data_xml),
                            ("JSON", extracted_data_json)]:
        log(f"Archivos {etiqueta} cargados: {len(datos)}")
        for name, frame in datos.items():
            log(f"  {name}: {frame.shape[0]} filas, {frame.shape[1]} columnas")
    log("Extract finalizado")

    # ------------------------------------------------------------------
    # Profile
    # ------------------------------------------------------------------
    log("Profile iniciado")
    for etiqueta, datos in [("csv", extracted_data_csv),
                            ("xml", extracted_data_xml),
                            ("json", extracted_data_json)]:
        perfiles = profile_datasets(datos, profile_output_dir / etiqueta)
        for dataset_name, perfil in perfiles.items():
            log(f"  [{etiqueta}] {dataset_name}: {perfil['report_path']}")
    log("Profile finalizado")

    # ------------------------------------------------------------------
    # Clean
    # ------------------------------------------------------------------
    log("Clean iniciado")
    fuentes_de_ventas = [
        ("sales_cali.csv", extracted_data_csv.get("sales_cali.csv")),
        ("sales_bogota.json", extracted_data_json.get("sales_bogota.json")),
        ("sales_medellin.xml", extracted_data_xml.get("sales_medellin.xml")),
    ]

    ventas_limpias = []
    ventas_rechazadas = []

    for dataset_name, frame in fuentes_de_ventas:
        if frame is None:
            log(f"  ADVERTENCIA: no se encontro {dataset_name}, se omite")
            continue

        frame_a_limpiar = frame.copy()
        frame_a_limpiar["source_branch"] = SALES_SOURCE_MAP[dataset_name]

        df_limpio, df_rechazado = clean_sales(frame_a_limpiar)
        ventas_limpias.append(df_limpio)
        ventas_rechazadas.append(df_rechazado)

        log(f"  {dataset_name}: {df_limpio.shape[0]} filas validas, "
            f"{df_rechazado.shape[0]} rechazadas")

    if not ventas_limpias:
        log("ERROR: no se pudo limpiar ninguna fuente de ventas. Pipeline detenido.")
        return

    # Las tres fuentes limpias se combinan en un unico conjunto antes de
    # transformar, para que el resto del pipeline trabaje con todas las
    # sucursales y no solo con la ultima procesada.
    df_ventas_limpias = pd.concat(ventas_limpias, ignore_index=True)
    df_ventas_rechazadas = pd.concat(ventas_rechazadas, ignore_index=True)
    log(f"Clean finalizado: {df_ventas_limpias.shape[0]} filas limpias en total, "
        f"{df_ventas_rechazadas.shape[0]} rechazadas en total")

    # ------------------------------------------------------------------
    # Transform
    # ------------------------------------------------------------------
    log("Transform iniciado")
    df_products = extracted_data_csv.get("products.csv")
    df_stores = extracted_data_csv.get("stores.csv")
    df_promotions = extracted_data_csv.get("promotions.csv")
    df_targets = extracted_data_csv.get("monthly_targets.csv")

    df_transformado = transform_sales(
        df_ventas_limpias, df_products, df_stores, df_promotions, df_targets
    )
    log(f"Transform finalizado: {df_transformado.shape[0]} filas, "
        f"{df_transformado.shape[1]} columnas")

    # ------------------------------------------------------------------
    # Validate
    # ------------------------------------------------------------------
    log("Validate iniciado")
    es_valido, resultados_validacion = validate_sales(df_transformado, df_products, df_stores)

    for _, fila in resultados_validacion.iterrows():
        log(f"  {fila['validacion']}: {fila['fallas']} fallas")

    if not es_valido:
        log("Validacion fallida. El pipeline se detiene antes de cargar los datos.")
        return

    log("Validate finalizado: todas las reglas pasaron")

    # ------------------------------------------------------------------
    # Load
    # ------------------------------------------------------------------
    log("Load iniciado")
    csv_path = load_to_csv(df_transformado)
    log(f"  CSV generado: {csv_path}")

    db_path, table_name = load_to_db(df_transformado)
    log(f"  Base de datos cargada: {db_path}, tabla: {table_name}")
    log("Load finalizado")

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------
    log("Query iniciado")
    ejecutar_todas_las_queries()
    log("Query finalizado")

    log("=== Pipeline finalizado correctamente ===")

    log("Iniciando dashboard Streamlit")
    launch_dashboard(project_root, log_file)


if __name__ == "__main__":
    main()