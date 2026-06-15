import pandas as pd
import numpy as np
from src.features.timeseries import add_time_features

def test_add_time_features():
    """Test that time features are correctly added to daily data."""
    df = pd.DataFrame({
        "date": pd.date_range("2023-01-01", periods=10),
        "total_qty": np.random.randint(1, 10, 10)
    })
    result = add_time_features(df)
    
    assert "dayofweek" in result.columns
    assert "is_weekend" in result.columns
    assert "lag_1" in result.columns
    assert "roll_7_mean" in result.columns
    assert len(result) == 10

def test_pipeline_import():
    """Test that the main pipeline module imports successfully."""
    import pipeline
    assert pipeline.PROCESSED.name == "processed"
