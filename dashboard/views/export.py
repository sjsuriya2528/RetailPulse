import streamlit as st
import pandas as pd
import io
from pathlib import Path

PROCESSED = Path(__file__).parent.parent.parent / "data" / "processed"

def show():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0a0e1a 0%, #0d1527 50%, #0a1628 100%); }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0d1b2a 0%, #112240 100%); }
    .stButton button { background: linear-gradient(135deg, #1565c0, #1976d2) !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; }
    h1, h2, h3 { color: #e8f4fd !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='padding:1.5rem 0 1rem 0;'>
        <h1 style='font-size:2rem; font-weight:800;'>📤 Export Reports</h1>
        <p style='color:#78909c;'>Download all analytics as CSV or Excel for offline use</p>
    </div>
    """, unsafe_allow_html=True)

    def load_parquet(fname):
        try:
            return pd.read_parquet(PROCESSED / fname)
        except Exception:
            return None

    def to_csv(df):
        return df.to_csv(index=False).encode("utf-8")

    def to_excel(dfs: dict) -> bytes:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            for sheet_name, df in dfs.items():
                df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
        return buf.getvalue()

    exports = {
        "📦 Inventory Recommendations": ("inventory_recs.parquet", "inventory_recommendations.csv"),
        "⚠️ Churn Risk Scores": ("churn_scored_named.parquet", "churn_risk_scores.csv"),
        "👥 Customer Segments (RFM)": ("rfm_clustered.parquet", "customer_segments_rfm.csv"),
        "📈 Demand Forecast (30 Days)": ("forecast.parquet", "demand_forecast_30d.csv"),
        "📊 Daily Sales History": ("daily_sales.parquet", "daily_sales_history.csv"),
        "🧾 Orders": ("orders.parquet", "orders.csv"),
        "🔬 Feature Importance (Churn)": ("feature_importance.parquet", "churn_feature_importance.csv"),
    }

    st.markdown("### 📁 Individual Report Downloads")
    for label, (parquet_file, csv_name) in exports.items():
        df = load_parquet(parquet_file)
        if df is not None:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"""
                <div style='background:rgba(255,255,255,0.03); border:1px solid rgba(100,180,255,0.15);
                            border-radius:10px; padding:0.75rem 1rem; margin-bottom:0.3rem;'>
                    <b style='color:#e8f4fd;'>{label}</b>
                    <span style='color:#546e7a; font-size:0.8rem; margin-left:1rem;'>{len(df):,} rows · {df.shape[1]} columns</span>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.download_button(
                    label="⬇️ CSV",
                    data=to_csv(df),
                    file_name=csv_name,
                    mime="text/csv",
                    key=f"csv_{csv_name}"
                )
            with col3:
                st.download_button(
                    label="📊 Excel",
                    data=to_excel({label[:31]: df}),
                    file_name=csv_name.replace(".csv", ".xlsx"),
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"excel_{csv_name}"
                )
        else:
            st.warning(f"⚠️ {label} — data not found. Run the pipeline first.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📦 Full Analytics Bundle (Excel)")
    st.markdown("Download all reports combined into a single Excel workbook with multiple sheets.")

    if st.button("📥 Generate Full Report Bundle"):
        all_dfs = {}
        for label, (parquet_file, _) in exports.items():
            df = load_parquet(parquet_file)
            if df is not None:
                all_dfs[label[:31]] = df
        if all_dfs:
            excel_data = to_excel(all_dfs)
            st.download_button(
                label="⬇️ Download RetailPulse_Full_Report.xlsx",
                data=excel_data,
                file_name="RetailPulse_Full_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="full_report"
            )
            st.success(f"✅ Bundle ready with {len(all_dfs)} sheets!")
