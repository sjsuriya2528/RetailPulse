"""
RetailPulse – Streamlit Dashboard Main Entry
"""
import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="RetailPulse | AI Analytics Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Dark gradient background */
.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1527 50%, #0a1628 100%);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1b2a 0%, #112240 100%);
    border-right: 1px solid rgba(100,180,255,0.1);
}

[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #64b5f6;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(100,180,255,0.08) 100%);
    border: 1px solid rgba(100,180,255,0.2);
    border-radius: 16px;
    padding: 1rem;
    backdrop-filter: blur(10px);
    transition: transform 0.2s ease, border-color 0.2s ease;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-2px);
    border-color: rgba(100,180,255,0.5);
}

/* Headers */
h1, h2, h3 { color: #e8f4fd !important; }

/* Tabs */
[data-testid="stTab"] { color: #90caf9; }

/* Plotly charts background */
.js-plotly-plot { border-radius: 12px; }

/* Cards */
.metric-card {
    background: linear-gradient(135deg, rgba(13,27,42,0.9), rgba(17,34,64,0.9));
    border: 1px solid rgba(100,180,255,0.2);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(10px);
}

.kpi-number {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #64b5f6, #42a5f5);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.badge-green { background: rgba(72,199,142,0.2); color: #48c78e; border-radius: 20px; padding: 2px 12px; font-size: 0.8rem; font-weight: 600; }
.badge-red   { background: rgba(255,99,99,0.2);  color: #ff6363; border-radius: 20px; padding: 2px 12px; font-size: 0.8rem; font-weight: 600; }
.badge-yellow{ background: rgba(255,189,46,0.2); color: #ffbd2e; border-radius: 20px; padding: 2px 12px; font-size: 0.8rem; font-weight: 600; }

.stButton button {
    background: linear-gradient(135deg, #1565c0, #1976d2) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}
.stButton button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(21,101,192,0.4) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0;'>
        <div style='font-size:2.5rem;'>⚡</div>
        <div style='font-size:1.4rem; font-weight:800; color:#64b5f6;'>RetailPulse</div>
        <div style='font-size:0.75rem; color:#90caf9; margin-top:4px;'>AI-Powered Analytics</div>
    </div>
    <hr style='border-color:rgba(100,180,255,0.2);'>
    """, unsafe_allow_html=True)

    st.markdown("### 📊 Navigation")
    st.markdown("""
    Use the **pages** in the sidebar to explore:
    - 🏠 **Overview** — KPI Summary
    - 📈 **Forecasting** — Demand Predictions
    - 👥 **Segmentation** — Customer Clusters
    - ⚠️ **Churn Analysis** — At-Risk Retailers
    - 📦 **Inventory** — Reorder Recommendations
    - 📤 **Export** — Download Reports
    """)

    st.markdown("<hr style='border-color:rgba(100,180,255,0.2);'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:0.75rem; color:#546e7a; text-align:center;'>
        Powered by Zidio Development<br>
        Data Science & Analytics · 2026
    </div>
    """, unsafe_allow_html=True)

# ── Home Page ─────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding: 3rem 0 2rem 0;'>
    <div style='font-size:3.5rem; margin-bottom:0.5rem;'>⚡</div>
    <h1 style='font-size:3rem; font-weight:800; background:linear-gradient(135deg,#64b5f6,#42a5f5,#90caf9);
               -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin:0;'>
        RetailPulse
    </h1>
    <p style='color:#90caf9; font-size:1.2rem; margin-top:0.5rem; font-weight:300;'>
        AI-Powered Customer Analytics & Demand Forecasting Platform
    </p>
    <p style='color:#546e7a; font-size:0.9rem; margin-top:0.3rem;'>
        Predictive Demand • Customer Segmentation • Churn Analysis • Inventory Optimization
    </p>
</div>
""", unsafe_allow_html=True)

# Feature cards
col1, col2, col3, col4 = st.columns(4)

features = [
    ("📈", "Demand Forecasting", "30-day ahead predictions using ARIMA + ETS ensemble models", "#1565c0"),
    ("👥", "Customer Segments", "RFM-based K-Means clustering identifying 5 distinct retailer personas", "#1b5e20"),
    ("⚠️", "Churn Detection", "XGBoost classifier with SHAP explainability for at-risk retailers", "#b71c1c"),
    ("📦", "Inventory AI", "EOQ + safety stock optimization to eliminate stockouts", "#e65100"),
]

for col, (icon, title, desc, color) in zip([col1, col2, col3, col4], features):
    with col:
        st.markdown(f"""
        <div class='metric-card' style='border-left: 3px solid {color}40; min-height:160px;'>
            <div style='font-size:2rem; margin-bottom:0.5rem;'>{icon}</div>
            <div style='font-weight:700; color:#e8f4fd; font-size:1rem; margin-bottom:0.5rem;'>{title}</div>
            <div style='color:#78909c; font-size:0.82rem; line-height:1.4;'>{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 👈 Select a page from the sidebar to explore the platform")

st.markdown("""
<div style='background:linear-gradient(135deg,rgba(21,101,192,0.15),rgba(13,71,161,0.1));
            border:1px solid rgba(100,180,255,0.2); border-radius:16px; padding:1.5rem; margin-top:1rem;'>
    <div style='color:#64b5f6; font-weight:700; margin-bottom:0.5rem;'>📊 Dataset: Campa Cola Distribution Network</div>
    <div style='color:#78909c; font-size:0.9rem;'>
        Real-world transactional data · 806 Retailers · 2,033 Orders · 43 Products · 8,803 Order Line Items
        <br>Data Period: Dec 2025 – Feb 2026 | South India Distribution Network
    </div>
</div>
""", unsafe_allow_html=True)
