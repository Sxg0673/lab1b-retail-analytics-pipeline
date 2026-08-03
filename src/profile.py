import pandas as pd


def combine_sales_sources(df_cali, df_bogota, df_medellin): # Combina los DataFrames de ventas de Cali, Bogota y Medellin en un solo DataFrame.

    df_cali = df_cali.copy()
    df_bogota = df_bogota.copy()
    df_medellin = df_medellin.copy()

    df_cali["source_branch"] = "Cali"
    df_bogota["source_branch"] = "Bogota"
    df_medellin["source_branch"] = "Medellin"

    return pd.concat([df_cali, df_bogota, df_medellin], ignore_index=True) 


def profile_sales(df): # Realiza un perfilado exploratorio de los datos de ventas combinados y devuelve un DataFrame con los hallazgos.
  
    hallazgos = []

    # 1. Forma general
    hallazgos.append({"hallazgo": "Filas totales", "valor": df.shape[0]})
    hallazgos.append({"hallazgo": "Columnas totales", "valor": df.shape[1]})

    # 2. Ventas sin promotion_code (NaN + vacio)
    faltantes_promo = df["promotion_code"].isna().sum() + (df["promotion_code"] == "").sum()
    hallazgos.append({"hallazgo": "Ventas sin promotion_code (NaN + vacio)", "valor": int(faltantes_promo)})

    # 3. Cantidad invalida (no numerica o <= 0)
    quantity_numerico = pd.to_numeric(df["quantity"], errors="coerce")
    invalid_quantity = ((quantity_numerico <= 0) | quantity_numerico.isna()).sum()
    hallazgos.append({"hallazgo": "quantity invalida (<=0 o no numerica)", "valor": int(invalid_quantity)})

    # 4. Precio invalido (no numerico o <= 0)
    unit_price_numerico = pd.to_numeric(df["unit_price"], errors="coerce")
    invalid_price = ((unit_price_numerico <= 0) | unit_price_numerico.isna()).sum()
    hallazgos.append({"hallazgo": "unit_price invalido (<=0 o no numerico)", "valor": int(invalid_price)})

    # 5. Duplicados en sale_line_id
    duplicados = df["sale_line_id"].duplicated().sum()
    hallazgos.append({"hallazgo": "sale_line_id duplicados", "valor": int(duplicados)})

    # 6. Valores distintos en payment_method (sin limpiar)
    valores_pago = df["payment_method"].nunique()
    hallazgos.append({"hallazgo": "Valores distintos en payment_method", "valor": int(valores_pago)})

    # 7. Fechas invalidas (no convertibles a datetime)
    formatos_por_fuente = {"Cali": "%Y-%m-%d", "Bogota": "%d/%m/%Y", "Medellin": "%m-%d-%Y"}
    fechas_parseadas = pd.Series(pd.NaT, index=df.index)
    for fuente, formato in formatos_por_fuente.items():
        mask = df["source_branch"] == fuente
        fechas_parseadas.loc[mask] = pd.to_datetime(df.loc[mask, "sale_date"], format=formato, errors="coerce")
    fechas_invalidas = fechas_parseadas.isna().sum()
    hallazgos.append({"hallazgo": "Fechas invalidas", "valor": int(fechas_invalidas)})

    return pd.DataFrame(hallazgos)