from pathlib import Path

from eda import run_eda
from extract import extract_from_csv, extract_from_xml, extract_from_json
from log import log_progress
from profile import profile_datasets


def main():
    project_root = Path(__file__).resolve().parents[1]
    data_path = project_root / "data" / "raw"
    profile_output_dir = project_root / "docs" / "eda_outputs" / "perfiles"
    eda_output_dir = project_root / "docs" / "eda_outputs" / "graficas"
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

    # EDA
    log(f"Generando gráficos EDA en: {eda_output_dir}")
    run_eda(extracted_data_csv, extracted_data_json, extracted_data_xml, eda_output_dir)

    log("Pipeline finalizada correctamente")

    # Limpieza de datos
    # transformed_data = transform(extracted_data_csv, extracted_data_xml, extracted_data_json)

    # Load
    # sql_connection = sqlite3.connect(project_root / "etl_database.db")
    # load_to_csv(transformed_data, target_file)
    # load_to_db(transformed_data, sql_connection, 'vehicles')


if __name__ == "__main__":
    main()
