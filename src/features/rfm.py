"""
RetailPulse – RFM Feature Engineering
Computes Recency, Frequency, Monetary scores per retailer.
"""
import pandas as pd
import numpy as np
from datetime import datetime
from loguru import logger


def compute_rfm(orders: pd.DataFrame, snapshot_date: datetime = None) -> pd.DataFrame:
    """
    Compute RFM scores for each retailer.
    
    Parameters
    ----------
    orders : cleaned orders DataFrame
    snapshot_date : reference date for recency (defaults to max date + 1 day)
    
    Returns
    -------
    DataFrame with columns: retailerId, recency_days, frequency, monetary,
                             R, F, M, RFM_Score, RFM_Segment
    """
    orders = orders[orders["status"] == "Delivered"].copy()
    orders["createdAt"] = pd.to_datetime(orders["createdAt"])

    if snapshot_date is None:
        snapshot_date = orders["createdAt"].max() + pd.Timedelta(days=1)

    rfm = orders.groupby("retailerId").agg(
        recency_days=("createdAt", lambda x: (snapshot_date - x.max()).days),
        frequency=("id", "count"),
        monetary=("totalAmount", "sum"),
        last_order=("createdAt", "max"),
        first_order=("createdAt", "min"),
    ).reset_index()

    # Score 1–4 using quartiles (4 = best)
    rfm["R"] = pd.qcut(rfm["recency_days"], q=4, labels=[4, 3, 2, 1]).astype(int)
    rfm["F"] = pd.qcut(rfm["frequency"].rank(method="first"), q=4, labels=[1, 2, 3, 4]).astype(int)
    rfm["M"] = pd.qcut(rfm["monetary"].rank(method="first"), q=4, labels=[1, 2, 3, 4]).astype(int)

    rfm["RFM_Score"] = rfm["R"].astype(str) + rfm["F"].astype(str) + rfm["M"].astype(str)
    rfm["RFM_Total"] = rfm["R"] + rfm["F"] + rfm["M"]

    # Map to business segments
    def segment(row):
        r, f, m = row["R"], row["F"], row["M"]
        if r >= 4 and f >= 4 and m >= 4:
            return "Champions"
        elif r >= 3 and f >= 3:
            return "Loyal Customers"
        elif r >= 4 and f <= 2:
            return "Recent Customers"
        elif r >= 3 and f <= 2 and m >= 3:
            return "Potential Loyalists"
        elif r == 2 and f >= 3:
            return "At Risk"
        elif r <= 2 and f <= 2 and m >= 3:
            return "Can't Lose Them"
        elif r == 1 and f == 1:
            return "Lost"
        else:
            return "Needs Attention"

    rfm["RFM_Segment"] = rfm.apply(segment, axis=1)
    logger.info(f"RFM computed for {len(rfm)} retailers. Segments: {rfm['RFM_Segment'].value_counts().to_dict()}")
    return rfm


def compute_order_features(orders: pd.DataFrame, order_items: pd.DataFrame) -> pd.DataFrame:
    """Build enriched order-level feature set."""
    # Items per order
    items_agg = order_items.groupby("orderId").agg(
        num_products=("productId", "nunique"),
        total_qty=("quantity", "sum"),
        avg_item_price=("pricePerUnit", "mean"),
    ).reset_index()

    enriched = orders.merge(items_agg, left_on="id", right_on="orderId", how="left")
    enriched["num_products"] = enriched["num_products"].fillna(0)
    enriched["total_qty"] = enriched["total_qty"].fillna(0)
    enriched["hour"] = pd.to_datetime(enriched["createdAt"]).dt.hour
    enriched["weekday"] = pd.to_datetime(enriched["createdAt"]).dt.dayofweek
    enriched["is_weekend"] = enriched["weekday"].isin([5, 6]).astype(int)
    return enriched
