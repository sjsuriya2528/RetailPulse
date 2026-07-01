import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import io

PROCESSED = Path(__file__).parent.parent.parent / "data" / "processed"

@st.cache_data
def load_data():
    try:
        churn = pd.read_parquet(PROCESSED / "churn_scored_named.parquet")
        feat_imp = pd.read_parquet(PROCESSED / "feature_importance.parquet")
        kpi = pd.read_parquet(PROCESSED / "kpi.parquet").iloc[0].to_dict()
        return churn, feat_imp, kpi
    except FileNotFoundError:
        st.error("⚠️ Please run `python pipeline.py` first.")
        st.stop()



def show():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0a0e1a 0%, #0d1527 50%, #0a1628 100%); }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0d1b2a 0%, #112240 100%); }
    [data-testid="metric-container"] { background: linear-gradient(135deg, rgba(255,255,255,0.05), rgba(100,180,255,0.08)); border: 1px solid rgba(100,180,255,0.2); border-radius: 16px; }
    h1, h2, h3 { color: #e8f4fd !important; }
    </style>
    """, unsafe_allow_html=True)
    churn, feat_imp, kpi = load_data()


    st.markdown("""
    <div style='padding:1.5rem 0 1rem 0;'>
        <h1 style='font-size:2rem; font-weight:800;'>⚠️ Churn Analysis</h1>
        <p style='color:#78909c;'>Identify at-risk retailers before they stop ordering — powered by XGBoost + SHAP</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Metrics ───────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    high_risk = churn[churn["churn_risk"] == "High Risk"]
    med_risk = churn[churn["churn_risk"] == "Medium Risk"]
    low_risk = churn[churn["churn_risk"] == "Low Risk"]
    with c1:
        st.metric("🎯 AUC-ROC", f"{kpi.get('churn_auc', 0):.3f}", help="Model performance — higher is better (target: ≥ 0.88)")
    with c2:
        st.metric("🔴 High Risk", f"{len(high_risk)}", delta=f"{len(high_risk)/len(churn):.1%} of retailers", delta_color="inverse")
    with c3:
        st.metric("🟡 Medium Risk", f"{len(med_risk)}")
    with c4:
        st.metric("🟢 Low Risk", f"{len(low_risk)}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Churn Risk Distribution ───────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🍩 Risk Distribution")
        risk_counts = churn["churn_risk"].value_counts().reset_index()
        risk_counts.columns = ["risk", "count"]
        fig_risk = px.pie(
            risk_counts, names="risk", values="count",
            color="risk",
            color_discrete_map={"High Risk": "#ef5350", "Medium Risk": "#ffa726", "Low Risk": "#66bb6a"},
            hole=0.5
        )
        fig_risk.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            height=300, margin=dict(l=0, r=0, t=0, b=0),
            legend=dict(bgcolor="rgba(0,0,0,0)")
        )
        st.plotly_chart(fig_risk, use_container_width=True)

    with col2:
        st.markdown("### 📊 Churn Probability Distribution")
        fig_hist = px.histogram(
            churn, x="churn_prob", nbins=30,
            color_discrete_sequence=["#42a5f5"],
            labels={"churn_prob": "Churn Probability", "count": "Retailers"},
        )
        fig_hist.add_vline(x=0.3, line_dash="dash", line_color="#66bb6a", annotation_text="Low/Med boundary")
        fig_hist.add_vline(x=0.6, line_dash="dash", line_color="#ef5350", annotation_text="Med/High boundary")
        fig_hist.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=300, margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(gridcolor="rgba(100,180,255,0.1)"),
            yaxis=dict(gridcolor="rgba(100,180,255,0.1)"),
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    # ── Feature Importance ────────────────────────────────────────────
    st.markdown("### 🔬 What Drives Churn? (Feature Importance)")
    fig_fi = px.bar(
        feat_imp.head(10), x="importance", y="feature", orientation="h",
        color="importance", color_continuous_scale="Reds",
        text=feat_imp.head(10)["importance"].apply(lambda x: f"{x:.3f}")
    )
    fig_fi.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=320, margin=dict(l=0, r=0, t=10, b=0),
        coloraxis_showscale=False,
        yaxis=dict(gridcolor="rgba(100,180,255,0.1)", autorange="reversed"),
        xaxis=dict(gridcolor="rgba(100,180,255,0.1)"),
    )
    fig_fi.update_traces(textposition="outside", textfont=dict(color="white"))
    st.plotly_chart(fig_fi, use_container_width=True)

    # ── Scatter: Recency vs Frequency colored by churn risk ──────────
    st.markdown("### 🔵 Retailer Risk Map")
    fig_scatter = px.scatter(
        churn, x="recency_days", y="frequency",
        color="churn_risk",
        size="monetary", size_max=20,
        color_discrete_map={"High Risk": "#ef5350", "Medium Risk": "#ffa726", "Low Risk": "#66bb6a"},
        hover_data={"shopName": True, "churn_prob": ":.2f", "monetary": ":.0f"},
        labels={"recency_days": "Days Since Last Order", "frequency": "Order Count"}
    )
    fig_scatter.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=380, margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor="rgba(100,180,255,0.1)"),
        yaxis=dict(gridcolor="rgba(100,180,255,0.1)"),
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # ── High Risk Table ───────────────────────────────────────────────
    st.markdown("### 🔴 High Risk Retailers — Action Required")
    st.markdown("> These retailers have a >60% probability of churning. Prioritize outreach!")

    high_risk_display = high_risk[[
        "shopName", "churn_prob", "recency_days", "frequency", "monetary", "cancel_rate", "credit_rate"
    ]].rename(columns={
        "shopName": "Shop Name",
        "churn_prob": "Churn Prob",
        "recency_days": "Days Inactive",
        "frequency": "Total Orders",
        "monetary": "Revenue (₹)",
        "cancel_rate": "Cancel Rate",
        "credit_rate": "Credit Rate",
    }).copy()

    high_risk_display["Churn Prob"] = high_risk_display["Churn Prob"].apply(lambda x: f"{x:.1%}")
    high_risk_display["Revenue (₹)"] = high_risk_display["Revenue (₹)"].apply(lambda x: f"₹{x:,.0f}")
    high_risk_display["Cancel Rate"] = high_risk_display["Cancel Rate"].apply(lambda x: f"{x:.1%}")
    high_risk_display["Credit Rate"] = high_risk_display["Credit Rate"].apply(lambda x: f"{x:.1%}")

    st.dataframe(high_risk_display.head(30), use_container_width=True, hide_index=True)

