"""
RetailPulse – Customer Segmentation
K-Means clustering on RFM features + DBSCAN for outlier detection.
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from loguru import logger
import mlflow
import warnings
warnings.filterwarnings("ignore")


SEGMENT_LABELS = {
    0: "High-Value Champions",
    1: "Loyal Regulars",
    2: "Occasional Buyers",
    3: "At-Risk Customers",
    4: "Dormant Accounts",
    5: "New Customers",
}


def find_optimal_k(X_scaled: np.ndarray, k_range=range(3, 9)) -> int:
    """Find best K using silhouette score."""
    best_k, best_score = 3, -1
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X_scaled)
        score = silhouette_score(X_scaled, labels)
        logger.info(f"  k={k}: silhouette={score:.3f}")
        if score > best_score:
            best_score, best_k = score, k
    logger.info(f"Optimal k={best_k} (silhouette={best_score:.3f})")
    return best_k


def run_kmeans(rfm: pd.DataFrame, n_clusters: int = None) -> pd.DataFrame:
    """
    Run K-Means on RFM features and return rfm DataFrame with cluster labels.
    """
    features = ["recency_days", "frequency", "monetary"]
    X = rfm[features].copy()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    if n_clusters is None:
        n_clusters = find_optimal_k(X_scaled)

    with mlflow.start_run(run_name="kmeans_segmentation", nested=True):
        km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        rfm["cluster"] = km.fit_predict(X_scaled)
        mlflow.log_param("n_clusters", n_clusters)
        mlflow.log_metric("inertia", km.inertia_)
        sil = silhouette_score(X_scaled, rfm["cluster"])
        mlflow.log_metric("silhouette_score", sil)
        logger.info(f"K-Means done. Clusters: {n_clusters}, Silhouette: {sil:.3f}")

    # PCA for 2D visualization
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(X_scaled)
    rfm["pca_x"] = coords[:, 0]
    rfm["pca_y"] = coords[:, 1]

    # Label clusters by average RFM total (highest = Champions)
    cluster_rank = rfm.groupby("cluster")["RFM_Total"].mean().sort_values(ascending=False)
    rank_map = {old: new for new, old in enumerate(cluster_rank.index)}
    rfm["cluster_ranked"] = rfm["cluster"].map(rank_map)

    cluster_names = {
        0: "Champions",
        1: "Loyal Customers",
        2: "Potential Loyalists",
        3: "At Risk",
        4: "Needs Attention",
        5: "Dormant",
    }
    rfm["cluster_label"] = rfm["cluster_ranked"].map(
        lambda x: cluster_names.get(x, f"Cluster {x}")
    )
    return rfm


def run_dbscan(rfm: pd.DataFrame, eps: float = 0.8, min_samples: int = 3) -> pd.DataFrame:
    """Run DBSCAN for outlier/noise detection."""
    features = ["recency_days", "frequency", "monetary"]
    X = rfm[features].copy()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    db = DBSCAN(eps=eps, min_samples=min_samples)
    rfm["dbscan_label"] = db.fit_predict(X_scaled)
    rfm["is_outlier"] = rfm["dbscan_label"] == -1
    n_outliers = rfm["is_outlier"].sum()
    logger.info(f"DBSCAN: {n_outliers} outlier retailers detected")
    return rfm
