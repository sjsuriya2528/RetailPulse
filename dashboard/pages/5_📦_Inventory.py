"""
RetailPulse – Page 5: Inventory Optimization
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="Inventory | RetailPulse", page_icon="📦", layout="wide")

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
        inv = pd.read_parquet(PROCESSED / "inventory_recs.parquet")
        products = pd.read_parquet(PROCESSED / "products.parquet")
        return inv, products
    except FileNotFoundError:
        st.error("⚠️ Please run `python pipeline.py` first.")
        st.stop()


inv, products = load_data()

st.markdown("""
<div style='padding:1.5rem 0 1rem 0;'>
    <h1 style='font-size:2rem; font-weight:800;'>📦 Inventory Optimization</h1>
    <p style='color:#78909c;'>EOQ + Safety Stock recommendations to eliminate stockouts and reduce overstock</p>
</div>
""", unsafe_allow_html=True)

# ── Metrics ───────────────────────────────────────────────────────
out_of_stock = (inv["Status"] == "🔴 Out of Stock").sum()
reorder_now  = (inv["Status"] == "🟡 Reorder Now").sum()
healthy      = (inv["Status"] == "🟢 Healthy").sum()
overstocked  = (inv["Status"] == "🔵 Overstocked").sum()

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("🔴 Out of Stock", f"{out_of_stock} products", delta="Urgent" if out_of_stock > 0 else "None", delta_color="inverse")
with c2:
    st.metric("🟡 Reorder Now", f"{reorder_now} products")
with c3:
    st.metric("🟢 Healthy Stock", f"{healthy} products")
with c4:
    st.metric("🔵 Overstocked", f"{overstocked} products")

st.markdown("<br>", unsafe_allow_html=True)

# ── Filters ───────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    status_filter = st.multiselect(
        "Filter by Stock Status:",
        options=inv["Status"].unique().tolist(),
        default=inv["Status"].unique().tolist()
    )
with col2:
    categories = inv["Category"].dropna().unique().tolist()
    cat_filter = st.multiselect("Filter by Category:", options=categories, default=categories)

filtered = inv[inv["Status"].isin(status_filter) & inv["Category"].isin(cat_filter)]

# ── Stock Status Chart ────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Stock Status Overview")
    status_counts = inv["Status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]
    color_map = {
        "🔴 Out of Stock": "#ef5350",
        "🟡 Reorder Now": "#ffa726",
        "🟢 Healthy": "#66bb6a",
        "🔵 Overstocked": "#42a5f5",
    }
    fig_status = px.bar(
        status_counts, x="status", y="count",
        color="status", color_discrete_map=color_map,
        text="count"
    )
    fig_status.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=300, margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        xaxis=dict(gridcolor="rgba(100,180,255,0.1)", title=""),
        yaxis=dict(gridcolor="rgba(100,180,255,0.1)", title="Products"),
    )
    fig_status.update_traces(textposition="outside", textfont=dict(color="white"))
    st.plotly_chart(fig_status, use_container_width=True)

with col2:
    st.markdown("### 📅 Days of Stock Left")
    inv_sorted = filtered.sort_values("Days of Stock").head(20)
    fig_days = px.bar(
        inv_sorted, x="Days of Stock", y="Product", orientation="h",
        color="Days of Stock", color_continuous_scale="RdYlGn",
        text=inv_sorted["Days of Stock"].round(0)
    )
    fig_days.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=300, margin=dict(l=0, r=0, t=0, b=0),
        coloraxis_showscale=False,
        yaxis=dict(gridcolor="rgba(100,180,255,0.1)", autorange="reversed"),
        xaxis=dict(gridcolor="rgba(100,180,255,0.1)"),
    )
    fig_days.update_traces(textposition="outside", textfont=dict(color="white", size=10))
    st.plotly_chart(fig_days, use_container_width=True)

# ── Current Stock vs Reorder Point ───────────────────────────────
st.markdown("### ⚖️ Current Stock vs Reorder Point")
top20 = filtered.head(20).copy()
fig_comp = go.Figure()
fig_comp.add_trace(go.Bar(
    name="Current Stock",
    x=top20["Product"].str[:25],
    y=top20["Current Stock"],
    marker_color="#42a5f5",
    text=top20["Current Stock"].round(0),
    textposition="outside"
))
fig_comp.add_trace(go.Bar(
    name="Reorder Point",
    x=top20["Product"].str[:25],
    y=top20["Reorder Point"],
    marker_color="rgba(239,83,80,0.6)",
    text=top20["Reorder Point"].round(0),
    textposition="outside"
))
fig_comp.update_layout(
    barmode="group",
    template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    height=380, margin=dict(l=0, r=0, t=10, b=0),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
    xaxis=dict(gridcolor="rgba(100,180,255,0.1)", tickangle=-35),
    yaxis=dict(gridcolor="rgba(100,180,255,0.1)", title="Units"),
)
st.plotly_chart(fig_comp, use_container_width=True)

# ── Recommendations Table ─────────────────────────────────────────
st.markdown("### 📋 Full Inventory Recommendations")

# Highlight rows
def highlight_status(val):
    if "Out of Stock" in str(val):
        return "background-color: rgba(239,83,80,0.2); color: #ef5350;"
    elif "Reorder" in str(val):
        return "background-color: rgba(255,167,38,0.2); color: #ffa726;"
    elif "Healthy" in str(val):
        return "background-color: rgba(102,187,106,0.1); color: #66bb6a;"
    elif "Overstock" in str(val):
        return "background-color: rgba(66,165,245,0.1); color: #42a5f5;"
    return ""

display_cols = ["Product", "Category", "Status", "Current Stock", "Reorder Point", "EOQ", "Order Qty", "30-Day Forecast", "Days of Stock"]
st.dataframe(
    filtered[display_cols].style.map(highlight_status, subset=["Status"]),
    use_container_width=True, hide_index=True
)

# ── What-If: Lead Time Sensitivity ───────────────────────────────
st.markdown("### 🎛️ Lead Time Sensitivity Analysis")
lead_time = st.slider("Supplier Lead Time (days):", 1, 14, 3)
filtered_copy = filtered.copy()
filtered_copy["Adjusted Reorder Pt"] = (
    filtered_copy["Avg Daily Demand"] * lead_time + filtered_copy["Safety Stock"]
).round(1)
filtered_copy["Alert"] = filtered_copy["Current Stock"] <= filtered_copy["Adjusted Reorder Pt"]
needs_reorder = filtered_copy["Alert"].sum()
st.info(f"📦 With **{lead_time}-day** lead time: **{needs_reorder}** products need reordering")
