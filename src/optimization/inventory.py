"""
RetailPulse – Inventory Optimization
EOQ + Safety Stock + Reorder Point logic based on forecasted demand.
"""
import pandas as pd
import numpy as np
from loguru import logger


def compute_eoq(
    annual_demand: float,
    ordering_cost: float = 500.0,
    holding_cost_pct: float = 0.20,
    unit_cost: float = 100.0,
) -> float:
    """
    Economic Order Quantity (EOQ) formula.
    EOQ = sqrt(2 * D * S / H)
    """
    H = holding_cost_pct * unit_cost
    if H <= 0 or annual_demand <= 0:
        return 0.0
    return np.sqrt(2 * annual_demand * ordering_cost / H)


def compute_safety_stock(
    daily_demand_std: float,
    lead_time_days: float = 3.0,
    service_level_z: float = 1.645,  # 95% service level
) -> float:
    """Safety stock = Z * std_demand * sqrt(lead_time)."""
    return service_level_z * daily_demand_std * np.sqrt(lead_time_days)


def compute_reorder_point(
    avg_daily_demand: float,
    lead_time_days: float = 3.0,
    safety_stock: float = 0.0,
) -> float:
    """ROP = avg_daily_demand * lead_time + safety_stock."""
    return avg_daily_demand * lead_time_days + safety_stock


def build_inventory_recommendations(
    products: pd.DataFrame,
    order_items: pd.DataFrame,
    forecast: pd.DataFrame,
    lead_time_days: float = 3.0,
) -> pd.DataFrame:
    """
    Build per-product inventory recommendation table.
    
    Returns
    -------
    DataFrame with columns:
        productName, current_stock, avg_daily_demand, forecast_30d,
        safety_stock, reorder_point, eoq, recommended_order_qty,
        stock_status, days_of_stock_left
    """
    # Aggregate historical daily demand per product
    order_items["date"] = pd.to_datetime(order_items["createdAt"]).dt.date
    n_days = order_items["date"].nunique()

    prod_agg = order_items.groupby("productName").agg(
        total_qty=("quantity", "sum"),
        total_revenue=("totalPrice", "sum"),
    ).reset_index()
    prod_agg["avg_daily_demand"] = prod_agg["total_qty"] / max(n_days, 1)

    # Demand std (use daily variation)
    daily_prod = order_items.groupby(["productName", "date"])["quantity"].sum().reset_index()
    std_df = daily_prod.groupby("productName")["quantity"].std().reset_index()
    std_df.columns = ["productName", "daily_demand_std"]
    prod_agg = prod_agg.merge(std_df, on="productName", how="left")
    prod_agg["daily_demand_std"] = prod_agg["daily_demand_std"].fillna(
        prod_agg["avg_daily_demand"] * 0.3
    )

    # Merge with product master
    products["productName_key"] = products["name"].str.strip().str.upper()
    prod_agg["productName_key"] = prod_agg["productName"].str.strip().str.upper()
    merged = prod_agg.merge(
        products[["productName_key", "stockQuantity", "sellingPrice", "groupName"]],
        on="productName_key", how="left"
    )
    merged["stockQuantity"] = merged["stockQuantity"].fillna(0)
    merged["sellingPrice"] = merged["sellingPrice"].fillna(100)

    # Total forecasted demand in next 30 days
    forecast_total = forecast["forecast"].sum() if len(forecast) > 0 else 0
    # Scale product forecast proportionally
    total_hist_qty = prod_agg["total_qty"].sum()
    merged["forecast_30d"] = (
        merged["total_qty"] / max(total_hist_qty, 1) * forecast_total
    ).round(1)

    # Compute EOQ, safety stock, ROP
    merged["safety_stock"] = merged.apply(
        lambda r: compute_safety_stock(r["daily_demand_std"], lead_time_days), axis=1
    ).round(1)

    merged["reorder_point"] = merged.apply(
        lambda r: compute_reorder_point(r["avg_daily_demand"], lead_time_days, r["safety_stock"]),
        axis=1
    ).round(1)

    merged["eoq"] = merged.apply(
        lambda r: compute_eoq(
            annual_demand=r["avg_daily_demand"] * 365,
            unit_cost=max(r["sellingPrice"], 1),
        ), axis=1
    ).round(1)

    merged["days_of_stock_left"] = (
        merged["stockQuantity"] / merged["avg_daily_demand"].clip(lower=0.01)
    ).round(1)

    # Recommended order quantity
    merged["recommended_order_qty"] = np.where(
        merged["stockQuantity"] <= merged["reorder_point"],
        merged["eoq"],
        0.0,
    ).round(1)

    # Stock status
    def status(row):
        if row["stockQuantity"] <= 0:
            return "🔴 Out of Stock"
        elif row["stockQuantity"] <= row["reorder_point"]:
            return "🟡 Reorder Now"
        elif row["days_of_stock_left"] > 60:
            return "🔵 Overstocked"
        else:
            return "🟢 Healthy"

    merged["stock_status"] = merged.apply(status, axis=1)

    result = merged[[
        "productName", "groupName", "stockQuantity", "avg_daily_demand",
        "daily_demand_std", "forecast_30d", "safety_stock", "reorder_point",
        "eoq", "recommended_order_qty", "stock_status", "days_of_stock_left",
    ]].rename(columns={
        "productName": "Product",
        "groupName": "Category",
        "stockQuantity": "Current Stock",
        "avg_daily_demand": "Avg Daily Demand",
        "daily_demand_std": "Demand Std",
        "forecast_30d": "30-Day Forecast",
        "safety_stock": "Safety Stock",
        "reorder_point": "Reorder Point",
        "eoq": "EOQ",
        "recommended_order_qty": "Order Qty",
        "stock_status": "Status",
        "days_of_stock_left": "Days of Stock",
    })

    result = result.sort_values("Status").reset_index(drop=True)
    logger.info(f"Inventory recommendations: {len(result)} products")
    return result
