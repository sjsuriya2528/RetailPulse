"""
RetailPulse – Master Pipeline
Run this once to generate all processed data and pre-trained model outputs.
Saves everything to data/processed/ for the dashboard to load instantly.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import pickle
import mlflow
from loguru import logger

from src.data.ingest import load_all
from src.data.clean import clean_all
from src.features.rfm import compute_rfm, compute_order_features
from src.features.timeseries import build_daily_sales, build_product_daily, add_time_features
from src.models.segmentation import run_kmeans, run_dbscan
from src.models.forecasting import run_forecast
from src.models.churn import build_churn_dataset, train_churn_model, predict_churn
from src.optimization.inventory import build_inventory_recommendations

PROCESSED = Path("data/processed")
PROCESSED.mkdir(parents=True, exist_ok=True)

mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("RetailPulse")


def run():
    logger.info("=" * 60)
    logger.info("RetailPulse Pipeline Starting...")
    logger.info("=" * 60)

    # ── 1. Load & Clean ─────────────────────────────────────────
    logger.info("Step 1: Loading & Cleaning Data")
    raw = load_all()
    data = clean_all(raw)

    order_items = data["order_items"]
    orders = data["orders"]
    retailers = data["retailers"]
    products = data["products"]
    invoices = data["invoices"]
    payments = data["payments"]
    cancelled_orders = data["cancelled_orders"]

    # Save cleaned data
    orders.to_parquet(PROCESSED / "orders.parquet", index=False)
    order_items.to_parquet(PROCESSED / "order_items.parquet", index=False)
    retailers.to_parquet(PROCESSED / "retailers.parquet", index=False)
    products.to_parquet(PROCESSED / "products.parquet", index=False)
    invoices.to_parquet(PROCESSED / "invoices.parquet", index=False)
    payments.to_parquet(PROCESSED / "payments.parquet", index=False)
    logger.info("✅ Step 1 Complete")

    # ── 2. RFM Features ─────────────────────────────────────────
    logger.info("Step 2: Computing RFM Scores")
    rfm = compute_rfm(orders)
    rfm.to_parquet(PROCESSED / "rfm.parquet", index=False)
    logger.info("✅ Step 2 Complete")

    # ── 3. Customer Segmentation ────────────────────────────────
    logger.info("Step 3: Customer Segmentation (K-Means)")
    with mlflow.start_run(run_name="segmentation_pipeline"):
        rfm_clustered = run_kmeans(rfm, n_clusters=5)
        rfm_clustered = run_dbscan(rfm_clustered)
    rfm_clustered.to_parquet(PROCESSED / "rfm_clustered.parquet", index=False)
    logger.info("✅ Step 3 Complete")

    # ── 4. Daily Sales + Forecasting ────────────────────────────
    logger.info("Step 4: Demand Forecasting")
    daily_sales = build_daily_sales(order_items)
    daily_sales = add_time_features(daily_sales)
    daily_sales.to_parquet(PROCESSED / "daily_sales.parquet", index=False)

    product_daily = build_product_daily(order_items)
    product_daily.to_parquet(PROCESSED / "product_daily.parquet", index=False)

    forecast = run_forecast(daily_sales, horizon=30)
    forecast.to_parquet(PROCESSED / "forecast.parquet", index=False)
    logger.info("✅ Step 4 Complete")

    # ── 5. Churn Prediction ─────────────────────────────────────
    logger.info("Step 5: Churn Prediction")
    churn_df = build_churn_dataset(rfm_clustered, orders, cancelled_orders)
    churn_model, metrics, feat_imp = train_churn_model(churn_df)
    scored = predict_churn(churn_model, churn_df)
    scored.to_parquet(PROCESSED / "churn_scored.parquet", index=False)
    feat_imp.to_parquet(PROCESSED / "feature_importance.parquet", index=False)

    # Merge retailer names
    retailer_names = retailers[["id", "shopName"]].rename(columns={"id": "retailerId"})
    scored_named = scored.merge(retailer_names, on="retailerId", how="left")
    scored_named["shopName"] = scored_named["shopName"].fillna("Unknown Shop")
    scored_named.to_parquet(PROCESSED / "churn_scored_named.parquet", index=False)

    with open(PROCESSED / "churn_model.pkl", "wb") as f:
        pickle.dump(churn_model, f)
    logger.info(f"✅ Step 5 Complete — AUC-ROC: {metrics['auc_roc']:.3f}")

    # ── 6. Inventory Optimization ───────────────────────────────
    logger.info("Step 6: Inventory Optimization")
    inventory_recs = build_inventory_recommendations(products, order_items, forecast)
    inventory_recs.to_parquet(PROCESSED / "inventory_recs.parquet", index=False)
    logger.info("✅ Step 6 Complete")

    # ── 7. KPI Summary ──────────────────────────────────────────
    logger.info("Step 7: Computing KPI Summary")
    kpi = {
        "total_orders": len(orders),
        "total_revenue": orders["totalAmount"].sum(),
        "total_retailers": retailers["id"].nunique(),
        "active_retailers": int(orders["retailerId"].nunique()),
        "total_products": products["id"].nunique(),
        "avg_order_value": orders["totalAmount"].mean(),
        "cancellation_rate": len(cancelled_orders) / max(len(orders), 1),
        "paid_invoices": (invoices["paymentStatus"] == "Paid").sum(),
        "pending_invoices": (invoices["paymentStatus"] == "Pending").sum(),
        "total_payments": payments["amount"].sum(),
        "churn_rate": churn_df["churned"].mean(),
        "forecast_mape": forecast.attrs.get("mape", 0),
        "churn_auc": metrics["auc_roc"],
        "high_risk_retailers": int((scored["churn_risk"] == "High Risk").sum()),
    }
    pd.DataFrame([kpi]).to_parquet(PROCESSED / "kpi.parquet", index=False)
    logger.info("✅ Step 7 Complete")

    logger.info("=" * 60)
    logger.info("🎉 Pipeline Complete! All outputs saved to data/processed/")
    logger.info("=" * 60)
    for k, v in kpi.items():
        if isinstance(v, float):
            logger.info(f"  {k}: {v:.2f}")
        else:
            logger.info(f"  {k}: {v}")


if __name__ == "__main__":
    run()
