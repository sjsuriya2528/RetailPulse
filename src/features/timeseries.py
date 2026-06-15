"""
RetailPulse – Time-Series Feature Engineering
Prepares daily/weekly demand series for forecasting.
"""
import pandas as pd
import numpy as np
from loguru import logger


def build_daily_sales(order_items: pd.DataFrame) -> pd.DataFrame:
    """Aggregate order items to daily total sales (qty + revenue).
    
    Automatically trims future-dated outlier records by detecting gaps > 30 days
    and keeping only the contiguous active data period.
    """
    order_items["date"] = pd.to_datetime(order_items["createdAt"]).dt.date
    daily = order_items.groupby("date").agg(
        total_qty=("quantity", "sum"),
        total_revenue=("totalPrice", "sum"),
        num_orders=("orderId", "nunique"),
        num_products=("productId", "nunique"),
    ).reset_index()
    daily["date"] = pd.to_datetime(daily["date"])
    daily = daily.sort_values("date").reset_index(drop=True)

    # Detect and remove future-dated outliers: find first gap > 30 days
    daily["gap"] = daily["date"].diff().dt.days.fillna(0)
    gap_idx = daily[daily["gap"] > 30].index
    if len(gap_idx) > 0:
        cutoff = daily.loc[gap_idx[0] - 1, "date"]
        n_removed = len(daily) - gap_idx[0]
        logger.warning(f"Gap detected after {cutoff.date()} — trimming {n_removed} future-dated date groups")
        daily = daily.iloc[:gap_idx[0]].copy()
    daily = daily.drop(columns=["gap"])

    # Fill missing dates within the active period
    full_range = pd.date_range(daily["date"].min(), daily["date"].max(), freq="D")
    daily = daily.set_index("date").reindex(full_range, fill_value=0).reset_index()
    daily.rename(columns={"index": "date"}, inplace=True)
    logger.info(f"Daily sales series: {len(daily)} days from {daily['date'].min().date()} to {daily['date'].max().date()}")
    return daily


def build_product_daily(order_items: pd.DataFrame, min_orders: int = 5) -> pd.DataFrame:
    """Build per-product daily demand series."""
    order_items["date"] = pd.to_datetime(order_items["createdAt"]).dt.date
    prod_daily = order_items.groupby(["productName", "date"]).agg(
        qty=("quantity", "sum"),
        revenue=("totalPrice", "sum"),
    ).reset_index()
    prod_daily["date"] = pd.to_datetime(prod_daily["date"])

    # Only keep products with enough history
    counts = prod_daily.groupby("productName")["date"].count()
    valid = counts[counts >= min_orders].index
    prod_daily = prod_daily[prod_daily["productName"].isin(valid)]
    logger.info(f"Product daily series: {prod_daily['productName'].nunique()} products")
    return prod_daily


def add_time_features(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    """Add calendar + lag + rolling features to a daily DataFrame."""
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df["dayofweek"] = df[date_col].dt.dayofweek
    df["dayofmonth"] = df[date_col].dt.day
    df["month"] = df[date_col].dt.month
    df["week"] = df[date_col].dt.isocalendar().week.astype(int)
    df["is_weekend"] = df["dayofweek"].isin([5, 6]).astype(int)
    df["is_monthend"] = (df[date_col].dt.is_month_end).astype(int)

    target_col = "total_qty"
    if target_col in df.columns:
        df["lag_1"] = df[target_col].shift(1)
        df["lag_7"] = df[target_col].shift(7)
        df["lag_14"] = df[target_col].shift(14)
        df["roll_7_mean"] = df[target_col].rolling(7, min_periods=1).mean()
        df["roll_7_std"] = df[target_col].rolling(7, min_periods=1).std().fillna(0)
        df["roll_14_mean"] = df[target_col].rolling(14, min_periods=1).mean()

    return df
