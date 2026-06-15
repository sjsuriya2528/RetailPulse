"""
RetailPulse – Data Ingestion & Loading
Loads all raw CSVs and returns clean DataFrames.
"""
import pandas as pd
from pathlib import Path
from loguru import logger

RAW = Path(__file__).parent.parent.parent / "data" / "raw"
PROCESSED = Path(__file__).parent.parent.parent / "data" / "processed"


def load_order_items() -> pd.DataFrame:
    df = pd.read_csv(RAW / "final_updated_orderitems_combined.csv", parse_dates=["createdAt", "updatedAt"])
    logger.info(f"Loaded order_items: {df.shape}")
    return df


def load_orders() -> pd.DataFrame:
    df = pd.read_csv(RAW / "updated_Orders.csv", parse_dates=["createdAt", "updatedAt"])
    logger.info(f"Loaded orders: {df.shape}")
    return df


def load_retailers() -> pd.DataFrame:
    df = pd.read_csv(RAW / "retailers.csv", parse_dates=["createdAt", "updatedAt"])
    logger.info(f"Loaded retailers: {df.shape}")
    return df


def load_products() -> pd.DataFrame:
    df = pd.read_csv(RAW / "Updated_Products.csv")
    logger.info(f"Loaded products: {df.shape}")
    return df


def load_invoices() -> pd.DataFrame:
    df = pd.read_csv(RAW / "Updated_Invoices.csv", parse_dates=["createdAt", "invoiceDate"])
    logger.info(f"Loaded invoices: {df.shape}")
    return df


def load_payments() -> pd.DataFrame:
    df = pd.read_csv(RAW / "Updated_Payements.csv", parse_dates=["paymentDate", "createdAt"])
    logger.info(f"Loaded payments: {df.shape}")
    return df


def load_cancelled_orders() -> pd.DataFrame:
    df = pd.read_csv(RAW / "CancelledOrders.csv", parse_dates=["cancelledAt", "createdAt"])
    logger.info(f"Loaded cancelled_orders: {df.shape}")
    return df


def load_cancelled_items() -> pd.DataFrame:
    df = pd.read_csv(RAW / "CancelledOrderItems.csv", parse_dates=["createdAt"])
    logger.info(f"Loaded cancelled_items: {df.shape}")
    return df


def load_all() -> dict:
    """Load all datasets and return as a dict."""
    return {
        "order_items": load_order_items(),
        "orders": load_orders(),
        "retailers": load_retailers(),
        "products": load_products(),
        "invoices": load_invoices(),
        "payments": load_payments(),
        "cancelled_orders": load_cancelled_orders(),
        "cancelled_items": load_cancelled_items(),
    }
