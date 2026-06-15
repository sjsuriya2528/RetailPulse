"""
RetailPulse – Page 3: Customer Segmentation
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="Segmentation | RetailPulse", page_icon="👥", layout="wide")

PROCESSED = Path(__file__).parent.parent.parent / "data" / "processed"

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


@st.cache_data
def load_data():
    try:
        rfm = pd.read_parquet(PROCESSED / "rfm_clustered.parquet")
        retailers = pd.read_parquet(PROCESSED / "retailers.parquet")
        return rfm, retailers
    except FileNotFoundError:
        st.error("⚠️ Please run `python pipeline.py` first.")
        st.stop()


rfm, retailers = load_data()

# Merge shop names
retailer_names = retailers[["id", "shopName"]].rename(columns={"id": "retailerId"})
rfm = rfm.merge(retailer_names, on="retailerId", how="left")
rfm["shopName"] = rfm["shopName"].fillna("Unknown Shop")

st.markdown("""
<div style='padding:1.5rem 0 1rem 0;'>
    <h1 style='font-size:2rem; font-weight:800;'>👥 Customer Segmentation</h1>
    <p style='color:#78909c;'>RFM-based K-Means clustering — identifying distinct retailer personas</p>
</div>
""", unsafe_allow_html=True)

# ── Metrics ───────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("🏪 Total Retailers", f"{len(rfm):,}")
with c2:
    st.metric("🎯 Segments", f"{rfm['cluster_label'].nunique()}")
with c3:
    champions = (rfm["cluster_label"] == "Champions").sum()
    st.metric("🏆 Champions", f"{champions}")
with c4:
    at_risk = (rfm["RFM_Segment"].isin(["At Risk", "Can't Lose Them"])).sum()
    st.metric("⚠️ At Risk", f"{at_risk}")

st.markdown("<br>", unsafe_allow_html=True)

# ── Segment Overview ──────────────────────────────────────────────
col1, col2 = st.columns(2)

COLORS = ["#42a5f5", "#66bb6a", "#ffa726", "#ef5350", "#ab47bc", "#26c6da"]

with col1:
    st.markdown("### 🍩 Segment Distribution")
    seg_counts = rfm["cluster_label"].value_counts().reset_index()
    seg_counts.columns = ["segment", "count"]
    fig_pie = px.pie(
        seg_counts, names="segment", values="count",
        color_discrete_sequence=COLORS, hole=0.5
    )
    fig_pie.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        height=320, margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(bgcolor="rgba(0,0,0,0)")
    )
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.markdown("### 💰 Revenue by Segment")
    seg_rev = rfm.groupby("cluster_label")["monetary"].agg(["sum", "mean", "count"]).reset_index()
    seg_rev.columns = ["segment", "total_revenue", "avg_revenue", "count"]
    fig_rev = px.bar(
        seg_rev.sort_values("total_revenue", ascending=True),
        x="total_revenue", y="segment", orientation="h",
        color="total_revenue", color_continuous_scale="Blues",
        text=seg_rev.sort_values("total_revenue", ascending=True)["total_revenue"].apply(lambda x: f"₹{x:,.0f}")
    )
    fig_rev.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=320, margin=dict(l=0, r=0, t=0, b=0),
        coloraxis_showscale=False,
        xaxis=dict(gridcolor="rgba(100,180,255,0.1)", tickprefix="₹"),
        yaxis=dict(gridcolor="rgba(100,180,255,0.1)"),
    )
    fig_rev.update_traces(textposition="outside", textfont=dict(color="white", size=10))
    st.plotly_chart(fig_rev, use_container_width=True)

# ── 2D Cluster Scatter (PCA) ──────────────────────────────────────
st.markdown("### 🔵 Cluster Visualization (PCA 2D)")
fig_scatter = px.scatter(
    rfm, x="pca_x", y="pca_y",
    color="cluster_label",
    hover_data={"shopName": True, "recency_days": True, "frequency": True, "monetary": ":.0f"},
    color_discrete_sequence=COLORS,
    size="monetary", size_max=25,
    labels={"pca_x": "Principal Component 1", "pca_y": "Principal Component 2"}
)
fig_scatter.update_layout(
    template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    height=400, margin=dict(l=0, r=0, t=10, b=0),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
    xaxis=dict(gridcolor="rgba(100,180,255,0.1)"),
    yaxis=dict(gridcolor="rgba(100,180,255,0.1)"),
)
st.plotly_chart(fig_scatter, use_container_width=True)

# ── RFM Heatmap ───────────────────────────────────────────────────
st.markdown("### 🗺️ RFM Score Heatmap")
rfm_heat = rfm.groupby(["R", "F"])["monetary"].mean().reset_index()
rfm_pivot = rfm_heat.pivot(index="R", columns="F", values="monetary")

fig_heat = px.imshow(
    rfm_pivot,
    color_continuous_scale="Blues",
    labels=dict(x="Frequency Score", y="Recency Score", color="Avg Revenue (₹)"),
    text_auto=".0f"
)
fig_heat.update_layout(
    template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    height=320, margin=dict(l=0, r=0, t=10, b=0),
)
st.plotly_chart(fig_heat, use_container_width=True)

# ── Segment Deep-Dive ─────────────────────────────────────────────
st.markdown("### 🔍 Segment Deep-Dive")
selected_seg = st.selectbox("Select a segment:", rfm["cluster_label"].unique())
seg_data = rfm[rfm["cluster_label"] == selected_seg]

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Retailers in Segment", len(seg_data))
with col2:
    st.metric("Avg Recency (days)", f"{seg_data['recency_days'].mean():.0f}")
with col3:
    st.metric("Avg Revenue", f"₹{seg_data['monetary'].mean():,.0f}")

st.dataframe(
    seg_data[["shopName", "recency_days", "frequency", "monetary", "RFM_Segment", "is_outlier"]]
    .rename(columns={
        "shopName": "Shop", "recency_days": "Recency (days)",
        "frequency": "Orders", "monetary": "Revenue (₹)",
        "RFM_Segment": "RFM Segment", "is_outlier": "Outlier"
    })
    .sort_values("Revenue (₹)", ascending=False)
    .head(20),
    use_container_width=True, hide_index=True
)
