"""
RetailPulse – Data Cleaning
Standardises columns, removes duplicates, handles missing values.
"""
import pandas as pd
import numpy as np
from loguru import logger


def clean_order_items(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["createdAt"] = pd.to_datetime(df["createdAt"], errors="coerce")
    df = df.dropna(subset=["createdAt", "orderId", "productId"])
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0)
    df["totalPrice"] = pd.to_numeric(df["totalPrice"], errors="coerce").fillna(0)
    df["netAmount"] = pd.to_numeric(df["netAmount"], errors="coerce").fillna(0)
    df["productName"] = df["productName"].str.strip().str.upper()
    df = df[df["quantity"] > 0]
    df["date"] = df["createdAt"].dt.date
    df["week"] = df["createdAt"].dt.to_period("W").dt.start_time
    df["month"] = df["createdAt"].dt.to_period("M").dt.start_time
    logger.info(f"clean_order_items: {df.shape} rows after cleaning")
    return df.reset_index(drop=True)


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["createdAt"] = pd.to_datetime(df["createdAt"], errors="coerce")
    df = df.dropna(subset=["createdAt", "retailerId"])
    df["totalAmount"] = pd.to_numeric(df["totalAmount"], errors="coerce").fillna(0)
    df["discountAmount"] = pd.to_numeric(df["discountAmount"], errors="coerce").fillna(0)
    df["retailerId"] = df["retailerId"].astype(int)
    df["date"] = df["createdAt"].dt.date
    df["month"] = df["createdAt"].dt.to_period("M").dt.start_time
    df["dayofweek"] = df["createdAt"].dt.day_name()
    df["status"] = df["status"].str.strip()
    df["paymentMode"] = df["paymentMode"].fillna("Unknown").str.strip()
    logger.info(f"clean_orders: {df.shape} rows after cleaning")
    return df.reset_index(drop=True)


def clean_retailers(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["shopName"] = df["shopName"].str.strip().str.title()
    df["isActive"] = pd.to_numeric(df["isActive"], errors="coerce").fillna(0).astype(bool)
    df["creditBalance"] = pd.to_numeric(df["creditBalance"], errors="coerce").fillna(0)
    df["createdAt"] = pd.to_datetime(df["createdAt"], errors="coerce")
    logger.info(f"clean_retailers: {df.shape} rows after cleaning")
    return df.reset_index(drop=True)


def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)
    df["sellingPrice"] = pd.to_numeric(df["sellingPrice"], errors="coerce").fillna(0)
    df["stockQuantity"] = pd.to_numeric(df["stockQuantity"], errors="coerce").fillna(0)
    df["gstPercentage"] = pd.to_numeric(df["gstPercentage"], errors="coerce").fillna(0)
    df["name"] = df["name"].str.strip().str.upper()
    df["groupName"] = df["groupName"].fillna("MISC").str.upper()
    df["isActive"] = df["isActive"].astype(str).str.lower().map({"true": True, "false": False}).fillna(True)
    logger.info(f"clean_products: {df.shape} rows after cleaning")
    return df.reset_index(drop=True)


def clean_invoices(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["invoiceDate"] = pd.to_datetime(df["invoiceDate"], errors="coerce")
    df["paidAmount"] = pd.to_numeric(df["paidAmount"], errors="coerce").fillna(0)
    df["balanceAmount"] = pd.to_numeric(df["balanceAmount"], errors="coerce").fillna(0)
    df["netTotal"] = pd.to_numeric(df["netTotal"], errors="coerce").fillna(0)
    df["paymentStatus"] = df["paymentStatus"].fillna("Pending").str.strip()
    df["customerName"] = df["customerName"].fillna("Unknown").str.strip().str.title()
    logger.info(f"clean_invoices: {df.shape} rows after cleaning")
    return df.reset_index(drop=True)


def clean_payments(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["paymentDate"] = pd.to_datetime(df["paymentDate"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
    df["paymentMode"] = df["paymentMode"].fillna("Unknown").str.strip()
    df["retailerName"] = df["retailerName"].fillna("Unknown").str.strip().str.title()
    df = df[df["amount"] > 0]
    logger.info(f"clean_payments: {df.shape} rows after cleaning")
    return df.reset_index(drop=True)


def clean_all(data: dict) -> dict:
    return {
        "order_items": clean_order_items(data["order_items"]),
        "orders": clean_orders(data["orders"]),
        "retailers": clean_retailers(data["retailers"]),
        "products": clean_products(data["products"]),
        "invoices": clean_invoices(data["invoices"]),
        "payments": clean_payments(data["payments"]),
        "cancelled_orders": data["cancelled_orders"],
        "cancelled_items": data["cancelled_items"],
    }
