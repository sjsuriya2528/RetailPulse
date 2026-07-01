"""
RetailPulse – Data Cleaning
Standardises columns, removes duplicates, handles missing values.
"""
import pandas as pd
import numpy as np
from loguru import logger

def clean_order_items(df: pd.DataFrame, products: pd.DataFrame = None, orders: pd.DataFrame = None) -> pd.DataFrame:
    df = df.copy()
    if orders is not None and not orders.empty:
        order_dates = orders[["id", "createdAt"]].rename(columns={"id": "orderId", "createdAt": "orderCreatedAt"})
        df = df.merge(order_dates, on="orderId", how="left")
        df["createdAt"] = df["orderCreatedAt"].fillna(df["createdAt"])
        df.drop(columns=["orderCreatedAt"], inplace=True)
        
    df["createdAt"] = pd.to_datetime(df["createdAt"], errors="coerce")
    df = df.dropna(subset=["createdAt", "orderId", "productId"])
    
    if products is not None and not products.empty:
        valid_product_ids = products["id"].unique()
        df = df[df["productId"].isin(valid_product_ids)]
        # Use official product name from the catalog
        product_names = products[["id", "name"]].rename(columns={"id": "productId", "name": "officialName"})
        df = df.merge(product_names, on="productId", how="left")
        df["productName"] = df["officialName"].fillna(df["productName"]).str.strip().str.upper()
        df.drop(columns=["officialName"], inplace=True)
        
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

def clean_orders(df: pd.DataFrame, cancelled_orders: pd.DataFrame = None) -> pd.DataFrame:
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
    
    if cancelled_orders is not None and not cancelled_orders.empty:
        cancelled_ids = cancelled_orders["id"].unique()
        df.loc[df["id"].isin(cancelled_ids), "status"] = "Cancelled"
        
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

def clean_invoices(df: pd.DataFrame, payments: pd.DataFrame = None) -> pd.DataFrame:
    df = df.copy()
    df["invoiceDate"] = pd.to_datetime(df["invoiceDate"], errors="coerce")
    df["netTotal"] = pd.to_numeric(df["netTotal"], errors="coerce").fillna(0)
    
    if payments is not None and not payments.empty:
        payment_totals = payments.groupby("invoiceId")["amount"].sum().reset_index()
        df = df.merge(payment_totals, left_on="id", right_on="invoiceId", how="left")
        df["paidAmount"] = df["amount"].fillna(0)
        df["balanceAmount"] = df["netTotal"] - df["paidAmount"]
        df["paymentStatus"] = np.where(df["balanceAmount"] <= 0, "Paid", "Pending")
        df.drop(columns=["invoiceId", "amount"], inplace=True)
    else:
        df["paidAmount"] = pd.to_numeric(df["paidAmount"], errors="coerce").fillna(0)
        df["balanceAmount"] = pd.to_numeric(df["balanceAmount"], errors="coerce").fillna(0)
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
    products_clean = clean_products(data["products"])
    payments_clean = clean_payments(data["payments"])
    orders_clean = clean_orders(data["orders"], cancelled_orders=data["cancelled_orders"])
    
    return {
        "order_items": clean_order_items(data["order_items"], products=products_clean, orders=orders_clean),
        "orders": orders_clean,
        "retailers": clean_retailers(data["retailers"]),
        "products": products_clean,
        "invoices": clean_invoices(data["invoices"], payments=payments_clean),
        "payments": payments_clean,
        "cancelled_orders": data["cancelled_orders"],
        "cancelled_items": data["cancelled_items"],
    }
