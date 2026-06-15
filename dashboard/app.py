"""
RetailPulse – Streamlit Dashboard Main Entry
"""
import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="RetailPulse | AI Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif !important;
}

/* Premium animated background */
.stApp {
    background: radial-gradient(circle at 15% 50%, rgba(20, 30, 48, 1), rgba(15, 23, 42, 1));
    background-size: 200% 200%;
    animation: bg-shift 20s ease infinite;
}

@keyframes bg-shift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.8) !important;
    backdrop-filter: blur(20px) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
}

[data-testid="stSidebar"] .stMarkdown h1, h2, h3 {
    color: #e2e8f0;
}

/* Glassmorphism Metric Cards */
[data-testid="metric-container"] {
    background: rgba(30, 41, 59, 0.5) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 20px !important;
    padding: 1.5rem !important;
    backdrop-filter: blur(16px) !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    overflow: hidden;
    position: relative;
}

[data-testid="metric-container"]::before {
    content: '';
    position: absolute;
    top: 0; left: -100%; width: 50%; height: 100%;
    background: linear-gradient(to right, transparent, rgba(255,255,255,0.05), transparent);
    transform: skewX(-20deg);
    transition: 0.5s;
}

[data-testid="metric-container"]:hover {
    transform: translateY(-5px) scale(1.02) !important;
    border-color: rgba(56, 189, 248, 0.5) !important;
    box-shadow: 0 15px 40px -5px rgba(56, 189, 248, 0.2) !important;
}

[data-testid="metric-container"]:hover::before {
    left: 200%;
}

/* Typography Enhancements */
h1, h2, h3 { color: #f8fafc !important; font-weight: 700 !important; letter-spacing: -0.02em !important; }

/* Custom Feature Cards */
.feature-card {
    background: linear-gradient(145deg, rgba(30, 41, 59, 0.6), rgba(15, 23, 42, 0.8));
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 24px;
    padding: 2rem;
    margin-bottom: 1.5rem;
    backdrop-filter: blur(20px);
    transition: all 0.4s ease;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    min-height: 180px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    position: relative;
    overflow: hidden;
}

.feature-card::after {
    content: '';
    position: absolute;
    top: -50%; left: -50%; width: 200%; height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.03) 0%, transparent 60%);
    opacity: 0;
    transition: opacity 0.5s;
}

.feature-card:hover::after {
    opacity: 1;
}

.feature-card:hover {
    transform: translateY(-8px);
    border-color: rgba(56, 189, 248, 0.4);
    box-shadow: 0 20px 40px rgba(0,0,0,0.4), inset 0 0 20px rgba(56, 189, 248, 0.1);
}

.icon-wrapper {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    display: inline-block;
    padding: 10px;
    border-radius: 16px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.05);
}

.feature-title {
    font-weight: 700;
    color: #f8fafc;
    font-size: 1.2rem;
    margin-bottom: 0.5rem;
    letter-spacing: -0.01em;
}

.feature-desc {
    color: #94a3b8;
    font-size: 0.9rem;
    line-height: 1.5;
    font-weight: 300;
}

/* Cool neon text for hero */
.hero-title {
    font-size: 4.5rem;
    font-weight: 800;
    background: linear-gradient(to right, #38bdf8, #818cf8, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    line-height: 1.1;
    letter-spacing: -0.03em;
}

.hero-subtitle {
    color: #94a3b8;
    font-size: 1.4rem;
    margin-top: 1rem;
    font-weight: 300;
    max-width: 800px;
    margin-left: auto;
    margin-right: auto;
}

/* Dataset badge */
.dataset-badge {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(56, 189, 248, 0.2);
    border-radius: 20px;
    padding: 1.5rem 3rem;
    margin-top: 3rem;
    backdrop-filter: blur(10px);
    display: inline-block;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    transition: all 0.3s;
}

.dataset-badge:hover {
    border-color: rgba(56, 189, 248, 0.5);
    transform: translateY(-3px);
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 2rem 0 1rem 0;'>
        <div style='font-size:3.5rem; margin-bottom: 10px; animation: pulse 2s infinite;'>⚡</div>
        <div style='font-size:1.8rem; font-weight:800; background: linear-gradient(to right, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>RetailPulse</div>
        <div style='font-size:0.85rem; color:#94a3b8; margin-top:5px; font-weight: 300; letter-spacing: 2px; text-transform: uppercase;'>Analytics Engine</div>
    </div>
    <hr style='border-color:rgba(255,255,255,0.05); margin: 20px 0;'>
    """, unsafe_allow_html=True)

    st.markdown("### 🧭 Navigation")
    st.markdown("""
    <div style='padding-left: 10px; line-height: 2;'>
        <span style='color:#64748b; font-size:0.8rem; text-transform:uppercase; letter-spacing:1px;'>Explore App</span><br>
        <span style='font-size:1.1rem;'>🏠</span> <b style='color:#e2e8f0;'>Overview</b><br>
        <span style='font-size:1.1rem;'>📈</span> <b style='color:#e2e8f0;'>Forecasting</b><br>
        <span style='font-size:1.1rem;'>👥</span> <b style='color:#e2e8f0;'>Segmentation</b><br>
        <span style='font-size:1.1rem;'>⚠️</span> <b style='color:#e2e8f0;'>Churn Analysis</b><br>
        <span style='font-size:1.1rem;'>📦</span> <b style='color:#e2e8f0;'>Inventory</b><br>
        <span style='font-size:1.1rem;'>📤</span> <b style='color:#e2e8f0;'>Export</b>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(255,255,255,0.05); margin: 30px 0 20px 0;'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:0.75rem; color:#475569; text-align:center; font-weight: 300;'>
        Powered by Zidio Development<br>
        Data Science & Analytics · 2026
    </div>
    """, unsafe_allow_html=True)

# ── Home Page ─────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding: 4rem 0 3rem 0;'>
    <div style='font-size:4.5rem; margin-bottom:1rem;'>🌌</div>
    <h1 class='hero-title'>Intelligence Meets Retail</h1>
    <p class='hero-subtitle'>
        Uncover hidden patterns, predict future demand, and optimize your inventory with state-of-the-art AI.
    </p>
</div>
""", unsafe_allow_html=True)

# Feature cards
col1, col2, col3, col4 = st.columns(4)

features = [
    ("📈", "Demand Forecasting", "30-day ahead predictions using sophisticated ensemble models.", "#38bdf8"),
    ("👥", "Customer Segments", "RFM-based K-Means clustering identifying 5 core personas.", "#34d399"),
    ("⚠️", "Churn Detection", "XGBoost classifier with SHAP explainability matrices.", "#f87171"),
    ("📦", "Inventory AI", "Automated EOQ & safety stock optimization workflows.", "#fbbf24"),
]

for col, (icon, title, desc, color) in zip([col1, col2, col3, col4], features):
    with col:
        st.markdown(f"""
        <div class='feature-card'>
            <div class='icon-wrapper' style='color: {color}; box-shadow: inset 0 0 20px {color}20;'>{icon}</div>
            <div class='feature-title'>{title}</div>
            <div class='feature-desc'>{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center;'>
    <div class='dataset-badge'>
        <div style='color:#38bdf8; font-weight:700; margin-bottom:0.5rem; letter-spacing: 1px; text-transform: uppercase;'>
            <span style='margin-right: 5px; font-size:1.2rem;'>📊</span> Live Dataset Active
        </div>
        <div style='color:#e2e8f0; font-size:1rem; font-weight: 400; margin-top:10px;'>
            <strong>Campa Cola Network</strong> · 806 Retailers · 2,033 Orders · 43 Products<br>
            <span style='font-size: 0.85rem; color: #64748b; margin-top: 8px; display: inline-block;'>Dec 2025 – Feb 2026 | South India</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
