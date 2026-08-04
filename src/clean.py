import numpy as np
import pandas as pd

# Diccionario que mapea cada fuente de datos a su formato de fecha correspondiente.
FORMATOS_FECHA_POR_FUENTE = {
    "Cali": "%Y-%m-%d",
    "Bogota": "%d/%m/%Y",
    "Medellin": "%m-%d-%Y",
}


def clean_sales(df): # Limpia y normaliza los datos de ventas, devolviendo un DataFrame limpio y otro con registros rechazados.
  
    df = df.copy()

    # 1. Normalizar texto en store_id y product_id: quitar espacios y unificar formato de texto.
    df["store_id"] = df["store_id"].astype(str).str.strip().str.upper()
    df["product_id"] = df["product_id"].astype(str).str.strip().str.upper()

    # 2. Normalizar texto en payment_method: quitar espacios y unificar formato de texto.
    df["payment_method"] = df["payment_method"].astype(str).str.strip().str.capitalize()

    # 3. Normalizar promotion_code: quitar espacios y reemplazar vacios por NaN.
    df["promotion_code"] = df["promotion_code"].replace("", np.nan)
    df["promotion_code"] = df["promotion_code"].where(df["promotion_code"].isna(),
                                                        df["promotion_code"].astype(str).str.strip()) # Si no es NaN, quitar espacios.

    # 4. Convertir quantity a numerico.
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce") # errors="coerce" convierte valores no numericos a NaN

    # 5. Convertir unit_price a numerico, eliminando cualquier caracter no numerico (excepto el punto decimal y el signo negativo).
    unit_price_texto = df["unit_price"].astype(str).str.replace(r"[^0-9.\-]", "", regex=True)
    df["unit_price"] = pd.to_numeric(unit_price_texto, errors="coerce") 

    # 6. Convertir sale_date a datetime, usando el formato correspondiente a cada fuente de datos.
    fechas_parseadas = pd.Series(pd.NaT, index=df.index) # Inicializar con NaT (Not a Time) para fechas no convertibles
    for fuente, formato in FORMATOS_FECHA_POR_FUENTE.items(): # Iterar sobre cada fuente y su formato de fecha
        mask = df["source_branch"] == fuente # Crear una mascara booleana para filtrar las filas de la fuente actual
        fechas_parseadas.loc[mask] = pd.to_datetime(df.loc[mask, "sale_date"], format=formato, errors="coerce") # Convertir las fechas de la fuente actual usando el formato especificado, convirtiendo a NaT las fechas no convertibles
    df["sale_date"] = fechas_parseadas # Asignar las fechas parseadas al DataFrame original

    # 7. Identificar filas con valores invalidos en sale_date, quantity o unit_price, y separarlas en un DataFrame de rechazados.
    es_invalido = (
        df["sale_date"].isna()
        | df["quantity"].isna() | (df["quantity"] <= 0)
        | df["unit_price"].isna() | (df["unit_price"] <= 0)
    )
    df_rechazados = df[es_invalido].copy()
    df = df[~es_invalido].copy() # Mantener solo las filas validas en el DataFrame principal

    # 8. Eliminar sale_line_id duplicados, quedandose con la primera ocurrencia.
    df = df.drop_duplicates(subset="sale_line_id", keep="first")

    return df.reset_index(drop=True), df_rechazados.reset_index(drop=True) # Devolver ambos DataFrames con indices reiniciados