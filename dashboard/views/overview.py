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
        kpi = pd.read_parquet(PROCESSED / "kpi.parquet").iloc[0].to_dict()
        orders = pd.read_parquet(PROCESSED / "orders.parquet")
        order_items = pd.read_parquet(PROCESSED / "order_items.parquet")
        payments = pd.read_parquet(PROCESSED / "payments.parquet")
        invoices = pd.read_parquet(PROCESSED / "invoices.parquet")
        return kpi, orders, order_items, payments, invoices
    except FileNotFoundError:
        st.error("⚠️ Processed data not found. Please run `python pipeline.py` first.")
        st.stop()



def show():
    # ── CSS ──────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0a0e1a 0%, #0d1527 50%, #0a1628 100%); }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0d1b2a 0%, #112240 100%); border-right: 1px solid rgba(100,180,255,0.1); }
    [data-testid="metric-container"] { background: linear-gradient(135deg, rgba(255,255,255,0.05), rgba(100,180,255,0.08)); border: 1px solid rgba(100,180,255,0.2); border-radius: 16px; padding: 1rem; }
    [data-testid="metric-container"]:hover { transform: translateY(-2px); border-color: rgba(100,180,255,0.5); }
    h1, h2, h3 { color: #e8f4fd !important; }
    </style>
    """, unsafe_allow_html=True)
    kpi, orders, order_items, payments, invoices = load_data()


    # ── Header ───────────────────────────────────────────────────────
    st.markdown("""
    <div style='padding:1.5rem 0 1rem 0;'>
        <h1 style='font-size:2rem; font-weight:800;'>🏠 Business Overview</h1>
        <p style='color:#78909c;'>Real-time KPIs and performance metrics for your distribution network</p>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI Metrics Row ──────────────────────────────────────────────
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.metric("💰 Total Revenue", f"₹{kpi['total_revenue']:,.0f}")
    with c2:
        st.metric("📦 Total Orders", f"{kpi['total_orders']:,}")
    with c3:
        st.metric("🏪 Active Retailers", f"{kpi['active_retailers']:,}")
    with c4:
        st.metric("🛍️ Avg Order Value", f"₹{kpi['avg_order_value']:,.0f}")
    with c5:
        st.metric("⚠️ Churn Rate", f"{kpi['churn_rate']:.1%}")
    with c6:
        st.metric("🎯 High Risk", f"{kpi['high_risk_retailers']:,} retailers")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Revenue Over Time ─────────────────────────────────────────────
    st.markdown("### 📈 Revenue Trend")
    orders["createdAt"] = pd.to_datetime(orders["createdAt"])
    daily_rev = orders.groupby(orders["createdAt"].dt.date)["totalAmount"].sum().reset_index()
    daily_rev.columns = ["date", "revenue"]
    daily_rev["date"] = pd.to_datetime(daily_rev["date"])
    daily_rev["rolling_7"] = daily_rev["revenue"].rolling(7, min_periods=1).mean()

    fig_rev = go.Figure()
    fig_rev.add_trace(go.Scatter(
        x=daily_rev["date"], y=daily_rev["revenue"],
        mode="lines", name="Daily Revenue",
        line=dict(color="rgba(100,181,246,0.4)", width=1),
        fill="tozeroy", fillcolor="rgba(100,181,246,0.05)"
    ))
    fig_rev.add_trace(go.Scatter(
        x=daily_rev["date"], y=daily_rev["rolling_7"],
        mode="lines", name="7-Day Moving Avg",
        line=dict(color="#64b5f6", width=2.5)
    ))
    fig_rev.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=300, margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor="rgba(100,180,255,0.1)"),
        yaxis=dict(gridcolor="rgba(100,180,255,0.1)", tickprefix="₹"),
    )
    st.plotly_chart(fig_rev, use_container_width=True)

    # ── Row 2: Orders by Status + Payment Mode ────────────────────────
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 📋 Order Status")
        status_counts = orders["status"].value_counts().reset_index()
        status_counts.columns = ["status", "count"]
        fig_status = px.pie(
            status_counts, names="status", values="count",
            color_discrete_sequence=["#42a5f5", "#66bb6a", "#ef5350", "#ffa726"],
            hole=0.5
        )
        fig_status.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=280, margin=dict(l=0, r=0, t=0, b=0),
            showlegend=True, legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11))
        )
        st.plotly_chart(fig_status, use_container_width=True)

    with col2:
        st.markdown("### 💳 Payment Modes")
        pay_counts = orders["paymentMode"].value_counts().reset_index()
        pay_counts.columns = ["mode", "count"]
        fig_pay = px.bar(
            pay_counts, x="mode", y="count",
            color="count", color_continuous_scale="Blues",
            text="count"
        )
        fig_pay.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=280, margin=dict(l=0, r=0, t=0, b=0),
            coloraxis_showscale=False,
            xaxis_title="", yaxis_title="Orders",
            xaxis=dict(gridcolor="rgba(100,180,255,0.1)"),
            yaxis=dict(gridcolor="rgba(100,180,255,0.1)"),
        )
        fig_pay.update_traces(textposition="outside", textfont=dict(color="white"))
        st.plotly_chart(fig_pay, use_container_width=True)

    with col3:
        st.markdown("### 📅 Orders by Day of Week")
        orders["weekday"] = pd.to_datetime(orders["createdAt"]).dt.day_name()
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        dow = orders["weekday"].value_counts().reindex(day_order, fill_value=0).reset_index()
        dow.columns = ["day", "orders"]
        fig_dow = px.bar(
            dow, x="day", y="orders",
            color="orders", color_continuous_scale="Blues", text="orders"
        )
        fig_dow.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=280, margin=dict(l=0, r=0, t=0, b=0),
            coloraxis_showscale=False,
            xaxis_title="", yaxis_title="Orders",
            xaxis=dict(gridcolor="rgba(100,180,255,0.1)", tickangle=-30),
            yaxis=dict(gridcolor="rgba(100,180,255,0.1)"),
        )
        fig_dow.update_traces(textposition="outside", textfont=dict(color="white"))
        st.plotly_chart(fig_dow, use_container_width=True)

    # ── Top Products ──────────────────────────────────────────────────
    st.markdown("### 🏆 Top 10 Products by Revenue")
    top_prod = (
        order_items.groupby("productName")["totalPrice"]
        .sum().sort_values(ascending=False).head(10).reset_index()
    )
    top_prod.columns = ["product", "revenue"]
    top_prod["product_short"] = top_prod["product"].str[:35]

    fig_prod = px.bar(
        top_prod, x="revenue", y="product_short", orientation="h",
        color="revenue", color_continuous_scale="Blues",
        text=top_prod["revenue"].apply(lambda x: f"₹{x:,.0f}")
    )
    fig_prod.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=380, margin=dict(l=0, r=0, t=10, b=0),
        coloraxis_showscale=False,
        yaxis=dict(gridcolor="rgba(100,180,255,0.1)", autorange="reversed"),
        xaxis=dict(gridcolor="rgba(100,180,255,0.1)", tickprefix="₹"),
    )
    fig_prod.update_traces(textposition="outside", textfont=dict(color="white", size=11))
    st.plotly_chart(fig_prod, use_container_width=True)

    # ── Invoice Payment Status ────────────────────────────────────────
    st.markdown("### 🧾 Invoice Payment Status")
    col1, col2 = st.columns(2)
    with col1:
        pay_status = invoices["paymentStatus"].value_counts().reset_index()
        pay_status.columns = ["status", "count"]
        fig_inv = px.pie(
            pay_status, names="status", values="count",
            color_discrete_sequence=["#66bb6a", "#ef5350", "#ffa726"],
            hole=0.4
        )
        fig_inv.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            height=250, margin=dict(l=0, r=0, t=0, b=0),
            legend=dict(bgcolor="rgba(0,0,0,0)")
        )
        st.plotly_chart(fig_inv, use_container_width=True)

    with col2:
        paid = invoices[invoices["paymentStatus"] == "Paid"]["netTotal"].sum()
        pending = invoices[invoices["paymentStatus"] == "Pending"]["netTotal"].sum()
        partial = invoices[~invoices["paymentStatus"].isin(["Paid", "Pending"])]["netTotal"].sum()
        st.markdown(f"""
        <br>
        <div style='background:rgba(102,187,106,0.1); border:1px solid rgba(102,187,106,0.3); border-radius:12px; padding:1rem; margin-bottom:0.5rem;'>
            <div style='color:#66bb6a; font-weight:700;'>✅ Paid</div>
            <div style='font-size:1.5rem; font-weight:800; color:#e8f4fd;'>₹{paid:,.0f}</div>
        </div>
        <div style='background:rgba(239,83,80,0.1); border:1px solid rgba(239,83,80,0.3); border-radius:12px; padding:1rem; margin-bottom:0.5rem;'>
            <div style='color:#ef5350; font-weight:700;'>⏳ Pending</div>
            <div style='font-size:1.5rem; font-weight:800; color:#e8f4fd;'>₹{pending:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

