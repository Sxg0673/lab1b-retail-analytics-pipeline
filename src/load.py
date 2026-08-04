import sqlite3

CSV_OUTPUT_PATH = "data/processed/integrated_sales.csv"
DB_PATH = "database/retail_analytics.db"
TABLE_NAME = "sales_analytics"


def load_to_csv(df, output_path=CSV_OUTPUT_PATH): # Guarda el DataFrame transformado en un archivo CSV.
    df.to_csv(output_path, index=False)
    return output_path


def load_to_db(df, db_path=DB_PATH, table_name=TABLE_NAME): # Carga el DataFrame transformado a una base de datos SQLite.

    connection = sqlite3.connect(db_path)
    try:
        df.to_sql(table_name, connection, if_exists="replace", index=False) # si la tabla ya existe, reemplazarla
    finally:
        connection.close() 
    return db_path, table_name 