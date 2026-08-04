from pathlib import Path
import subprocess
import sys

import pandas as pd

# from eda import run_eda
from extract import extract_from_csv, extract_from_xml, extract_from_json
from profile import profile_datasets
from clean import clean_sales
from transform import transform_sales
from validate import validate_sales
from load import load_to_csv, load_to_db
from queries import ejecutar_todas_las_queries
from log import log_progress


def main():
    project_root = Path(__file__).resolve().parents[1]
    data_path = project_root / "data" / "raw"
    profile_output_dir = project_root / "docs" / "eda_outputs" / "perfiles"
    # eda_output_dir = project_root / "docs" / "eda_outputs" / "graficas"
    log_file = project_root / "logs" / "etl_run.log"

    
    log_file.parent.mkdir(parents=True, exist_ok=True)

    def log(message):
        log_progress(message, log_file)

    log(f"Iniciando pipeline con datos en: {data_path}")

    # Extract
    extracted_data_csv = extract_from_csv(data_path)
    extracted_data_xml = extract_from_xml(data_path)
    extracted_data_json = extract_from_json(data_path)

    log(f"Archivos CSV cargados: {len(extracted_data_csv)}")
    for name, frame in extracted_data_csv.items():
        log(f"CSV {name}: {frame.shape[0]} filas, {frame.shape[1]} columnas")

    log(f"Archivos XML cargados: {len(extracted_data_xml)}")
    for name, frame in extracted_data_xml.items():
        log(f"XML {name}: {frame.shape[0]} filas, {frame.shape[1]} columnas")

    log(f"Archivos JSON cargados: {len(extracted_data_json)}")
    for name, frame in extracted_data_json.items():
        log(f"JSON {name}: {frame.shape[0]} filas, {frame.shape[1]} columnas")


    # Profile
    log(f"Generando perfiles en: {profile_output_dir}")
    profile_results_csv = profile_datasets(extracted_data_csv, profile_output_dir / "csv")
    profile_results_xml = profile_datasets(extracted_data_xml, profile_output_dir / "xml")
    profile_results_json = profile_datasets(extracted_data_json, profile_output_dir / "json")

    for source_name, profiles in {
        "csv": profile_results_csv,
        "xml": profile_results_xml,
        "json": profile_results_json,
    }.items():
        for dataset_name, profile in profiles.items():
            log(f"[{source_name}] {dataset_name}: {profile['report_path']}")


  
    # Clean sales datasets
    sales_source_map = {
        "sales_cali.csv": "Cali",
        "sales_bogota.json": "Bogota",
        "sales_medellin.xml": "Medellin",
    }

    cleaned_sales_data = {}
    rejected_sales_data = {}

    for dataset_name, frame in [
        ("sales_cali.csv", extracted_data_csv.get("sales_cali.csv")),
        ("sales_bogota.json", extracted_data_json.get("sales_bogota.json")),
        ("sales_medellin.xml", extracted_data_xml.get("sales_medellin.xml")),
       
    ]:
        if frame is None:
            continue

        frame_to_clean = frame.copy()
        frame_to_clean["source_branch"] = sales_source_map[dataset_name]

        clean_df, rejected_df = clean_sales(frame_to_clean)
        cleaned_sales_data[dataset_name] = clean_df
        rejected_sales_data[dataset_name] = rejected_df

        log(
            f"{dataset_name} limpiado: {clean_df.shape[0]} filas válidas, "
            f"{rejected_df.shape[0]} filas rechazadas"
        )
    #En sale_cali rechaza porque en L00011 la cantidad es 0
    #En bogotá se rechaza por  L00261:"unidades": -1,
    #EN medellín se rechaza por L00521:<unit_value>-86000</unit_value>  y L00601 -> no encuentro razón
            
    #Tranform Datasets
    # Aquí se asume que los DataFrames de productos, tiendas, promociones y objetivos mensuales ya han sido extraídos y están disponibles.
    df_products = extracted_data_csv.get("products.csv")
    df_stores = extracted_data_csv.get("stores.csv")
    df_promotions = extracted_data_csv.get("promotions.csv")
    df_targets = extracted_data_csv.get("monthly_targets.csv")
    #Función de transformación que combina los DataFrames de ventas limpios con los DataFrames de productos, tiendas, promociones y objetivos mensuales.
    df_transformed = transform_sales(clean_df, df_products, df_stores, df_promotions, df_targets)
    
    #Validación
    is_valid, validation_results = validate_sales(df_transformed, df_products, df_stores)
    if is_valid:
        log("Validación exitosa: Todos los registros cumplen con las reglas de negocio.")
        print(validation_results)
    else:
        log("Validación fallida: Algunos registros no cumplen con las reglas de negocio.")
        print(validation_results)   

    #Carga
    db_path, table_name = load_to_db(df_transformed)
    log(f"Datos cargados en la base de datos SQLite: {db_path}, tabla: {table_name}")   

    #Querys
    ejecutar_todas_las_queries()

    # Launch dashboard
    log("Iniciando dashboard Streamlit")
    launch_dashboard(project_root)


def launch_dashboard(project_root: Path) -> None:
    app_path = project_root / "src" / "dashboard" / "app.py"
    try:
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", str(app_path)],
            check=True,
        )
    except FileNotFoundError:
        log_progress(
            "Streamlit no está instalado. Instale streamlit y vuelva a ejecutar el pipeline.",
            project_root / "logs" / "etl_run.log",
        )
    except subprocess.CalledProcessError:
        log_progress(
            "No se pudo iniciar el dashboard Streamlit.",
            project_root / "logs" / "etl_run.log",
        )


if __name__ == "__main__":
    main()
