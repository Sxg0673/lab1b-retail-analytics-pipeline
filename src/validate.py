import numpy as np
import pandas as pd


def validate_sales(df, df_products, df_stores): # valida las reglas de negocio sobre el DataFrame de ventas, devolviendo un DataFrame con los resultados de cada validación y un booleano indicando si todas las validaciones pasaron.

    resultados = []

    # 1. sale_line_id debe ser unico.
    duplicados = df["sale_line_id"].duplicated().sum()
    resultados.append({"validacion": "sale_line_id unico", "fallas": int(duplicados)})

    # 2. Identificadores y fecha requeridos no deben ser nulos.
    campos_requeridos = ["sale_line_id", "sale_date", "store_id", "product_id"]
    nulos_requeridos = df[campos_requeridos].isna().any(axis=1).sum()
    resultados.append({"validacion": "identificadores y fecha no nulos", "fallas": int(nulos_requeridos)})

    # 3. quantity, unit_price, gross_sales y net_sales deben ser positivos.
    no_positivos = (
        (df["quantity"] <= 0) | (df["unit_price"] <= 0)
        | (df["gross_sales"] <= 0) | (df["net_sales"] <= 0)
    ).sum()
    resultados.append({"validacion": "quantity/unit_price/gross_sales/net_sales positivos", "fallas": int(no_positivos)})

    # 4. Cada product_id debe existir en el maestro de productos.
    productos_invalidos = (~df["product_id"].isin(df_products["product_id"])).sum()
    resultados.append({"validacion": "product_id existe en el maestro de productos", "fallas": int(productos_invalidos)})

    # 5. Cada store_id debe existir en el maestro de tiendas.
    tiendas_invalidas = (~df["store_id"].isin(df_stores["store_id"])).sum()
    resultados.append({"validacion": "store_id existe en el maestro de tiendas", "fallas": int(tiendas_invalidas)})

    # 6. net_sales debe ser igual a gross_sales - discount_amount.
    coincide = np.isclose(df["net_sales"], df["gross_sales"] - df["discount_amount"]) # np.isclose para comparar flotantes con tolerancia
    resultados.append({"validacion": "net_sales = gross_sales - discount_amount", "fallas": int((~coincide).sum())})

    # 7. Si hay promotion_code, sale_date debe estar dentro de start_date y end_date.
    con_promo = df["promotion_code"].notna()
    fuera_de_rango = con_promo & ( 
        (df["sale_date"] < df["start_date"]) | (df["sale_date"] > df["end_date"])
    )
    resultados.append({"validacion": "fecha de venta dentro de vigencia de la promocion", "fallas": int(fuera_de_rango.sum())}) 

    tabla_resultados = pd.DataFrame(resultados) # Crear un DataFrame con los resultados de las validaciones
    es_valido = bool((tabla_resultados["fallas"] == 0).all()) # Si todas las validaciones pasaron (fallas = 0), entonces es_valido es True, de lo contrario False

    return es_valido, tabla_resultados