"""
RetailPulse – Churn Prediction
XGBoost classifier with SHAP explainability.
A retailer is "churned" if they haven't ordered in the last 30 days
relative to the snapshot date.
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import roc_auc_score, classification_report, precision_score
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import mlflow
import mlflow.xgboost
from loguru import logger
import warnings
warnings.filterwarnings("ignore")


def build_churn_dataset(
    rfm: pd.DataFrame,
    orders: pd.DataFrame,
    cancelled_orders: pd.DataFrame,
    snapshot_date=None,
    churn_threshold_days: int = 30,
) -> pd.DataFrame:
    """
    Build supervised churn dataset from RFM + order features.
    Label: 1 if retailer hasn't ordered in churn_threshold_days.
    """
    if snapshot_date is None:
        snapshot_date = pd.to_datetime(orders["createdAt"]).max() + pd.Timedelta(days=1)

    # Cancellation rate per retailer
    cancel_counts = (
        cancelled_orders.groupby("retailerId").size().reset_index(name="cancel_count")
        if "retailerId" in cancelled_orders.columns else pd.DataFrame(columns=["retailerId", "cancel_count"])
    )
    total_counts = orders.groupby("retailerId").size().reset_index(name="total_orders")

    cancel_rate = total_counts.merge(cancel_counts, on="retailerId", how="left")
    cancel_rate["cancel_count"] = cancel_rate["cancel_count"].fillna(0)
    cancel_rate["cancel_rate"] = cancel_rate["cancel_count"] / cancel_rate["total_orders"]

    # Payment mode distribution
    pay_mode = orders.groupby("retailerId")["paymentMode"].agg(
        lambda x: (x == "Credit").mean()
    ).reset_index(name="credit_rate")

    # Avg order value
    avg_order = orders.groupby("retailerId")["totalAmount"].agg(["mean", "std"]).reset_index()
    avg_order.columns = ["retailerId", "avg_order_value", "std_order_value"]
    avg_order["std_order_value"] = avg_order["std_order_value"].fillna(0)

    # Merge all
    df = rfm.merge(cancel_rate[["retailerId", "cancel_rate"]], on="retailerId", how="left")
    df = df.merge(pay_mode, on="retailerId", how="left")
    df = df.merge(avg_order, on="retailerId", how="left")
    df["cancel_rate"] = df["cancel_rate"].fillna(0)
    df["credit_rate"] = df["credit_rate"].fillna(0)
    df["avg_order_value"] = df["avg_order_value"].fillna(df["monetary"] / df["frequency"].clip(lower=1))
    df["std_order_value"] = df["std_order_value"].fillna(0)

    # Churn label
    df["churned"] = (df["recency_days"] >= churn_threshold_days).astype(int)
    churn_rate = df["churned"].mean()
    logger.info(f"Churn dataset: {len(df)} retailers, churn rate={churn_rate:.1%}")
    return df


FEATURE_COLS = [
    "frequency", "monetary",
    "R", "F", "M", "RFM_Total",
    "cancel_rate", "credit_rate",
    "avg_order_value", "std_order_value",
]


def train_churn_model(churn_df: pd.DataFrame):
    """Train XGBoost churn classifier with stratified split.
    
    Note: recency_days is excluded from features (see FEATURE_COLS) to prevent
    direct leakage, since churn label is derived from recency threshold.
    Stratified split ensures balanced churn representation in train/test.
    """
    X = churn_df[FEATURE_COLS].fillna(0)
    y = churn_df["churned"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    params = {
        "n_estimators": 200,
        "max_depth": 4,
        "learning_rate": 0.05,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "scale_pos_weight": (y == 0).sum() / (y == 1).sum(),
        "random_state": 42,
        "eval_metric": "auc",
    }

    with mlflow.start_run(run_name="churn_xgboost"):
        model = xgb.XGBClassifier(**params)
        model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

        y_proba = model.predict_proba(X_test)[:, 1]
        y_pred = (y_proba >= 0.5).astype(int)

        auc = roc_auc_score(y_test, y_proba)
        # Precision at top 20%
        top20_idx = np.argsort(y_proba)[::-1][: max(1, len(y_proba) // 5)]
        p_top20 = y_test.iloc[top20_idx].mean()

        mlflow.log_params(params)
        mlflow.log_metric("auc_roc", auc)
        mlflow.log_metric("precision_top20", p_top20)
        mlflow.xgboost.log_model(model, "churn_model")

        metrics = {"auc_roc": auc, "precision_top20": p_top20}
        logger.info(f"Churn model: AUC-ROC={auc:.3f}, Precision@Top20%={p_top20:.3f}")

    feat_imp = pd.DataFrame({
        "feature": FEATURE_COLS,
        "importance": model.feature_importances_,
    }).sort_values("importance", ascending=False)

    return model, metrics, feat_imp


def predict_churn(model, churn_df: pd.DataFrame) -> pd.DataFrame:
    """Score all retailers with churn probability."""
    X = churn_df[FEATURE_COLS].fillna(0)
    churn_df = churn_df.copy()
    churn_df["churn_prob"] = model.predict_proba(X)[:, 1]
    churn_df["churn_risk"] = pd.cut(
        churn_df["churn_prob"],
        bins=[0, 0.3, 0.6, 1.0],
        labels=["Low Risk", "Medium Risk", "High Risk"],
    )
    return churn_df.sort_values("churn_prob", ascending=False)


def get_shap_values(model, churn_df: pd.DataFrame):
    """Return SHAP values for explainability."""
    try:
        import shap
        X = churn_df[FEATURE_COLS].fillna(0)
        explainer = shap.TreeExplainer(model)
        shap_vals = explainer.shap_values(X)
        return shap_vals, X
    except Exception as e:
        logger.warning(f"SHAP failed: {e}")
        return None, None
