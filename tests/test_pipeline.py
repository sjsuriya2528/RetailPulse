import pandas as pd
from pathlib import Path

def test_processed_data_exists():
    """Test that the processed directory exists."""
    processed = Path("data/processed")
    assert processed.exists(), "Processed data directory is missing"

def test_orders_data_validity():
    """Test that the core orders dataset is valid."""
    orders_path = Path("data/processed/orders.parquet")
    if orders_path.exists():
        df = pd.read_parquet(orders_path)
        assert len(df) > 0, "Orders dataset is empty"
        assert "totalAmount" in df.columns, "Missing required revenue column"

def test_kpi_metrics():
    """Test that KPI summary metrics are generated correctly."""
    kpi_path = Path("data/processed/kpi.parquet")
    if kpi_path.exists():
        kpi = pd.read_parquet(kpi_path)
        assert len(kpi) == 1, "KPI dataset should have exactly 1 row"
        assert "total_revenue" in kpi.columns, "Missing revenue KPI"
        assert kpi["total_orders"].iloc[0] > 0, "Total orders must be > 0"
