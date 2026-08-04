import numpy as np
import pandas as pd


def transform_sales(df_ventas, df_products, df_stores, df_promotions, df_targets): # Realiza la transformación de los datos de ventas, enriqueciendo con información de productos, tiendas, promociones y objetivos de ventas mensuales.

    df = df_ventas.copy()

    # 1. product_name y category desde products.csv (cruce por product_id).
    df = df.merge(
        df_products[["product_id", "product_name", "category"]],
        on="product_id", how="left"
    )

    # 2. store_name, city y region desde stores.csv (cruce por store_id).
    df = df.merge(
        df_stores[["store_id", "store_name", "city", "region"]],
        on="store_id", how="left"
    )

    # 3. discount_pct y campaign_name desde promotions.csv (cruce por
    #    promotion_code). Las ventas sin promocion quedan con discount_pct
    #    en 0 y campaign_name vacio, ya que no aplica ningun descuento.
    #    Se incluyen tambien start_date y end_date de la promocion que no se usaran
    #    en esta seccion pero quedan disponibles para el bloque
    #    Validate, que verificara si la venta cayo dentro del periodo
    #    de vigencia de la promocion aplicada.
    df = df.merge( 
        df_promotions[["promotion_code", "discount_pct", "campaign_name", "start_date", "end_date"]], 
        on="promotion_code", how="left"
    )
    df["discount_pct"] = df["discount_pct"].fillna(0) # Ventas sin promocion quedan con discount_pct en 0

    # 4. Metricas de venta.
    df["gross_sales"] = df["quantity"] * df["unit_price"]
    df["discount_amount"] = df["gross_sales"] * df["discount_pct"]
    df["net_sales"] = df["gross_sales"] - df["discount_amount"]

    # 5. Dimensiones de tiempo derivadas de sale_date.
    df["month"] = df["sale_date"].dt.strftime("%Y-%m")
    df["week"] = df["sale_date"].dt.isocalendar().week
    df["day_name"] = df["sale_date"].dt.day_name()

    # 6. sales_target desde monthly_targets.csv (cruce por store_id + month).
    df = df.merge(
        df_targets[["store_id", "month", "sales_target"]],
        on=["store_id", "month"], how="left"
    )

    return df 