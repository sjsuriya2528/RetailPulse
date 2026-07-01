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
        daily = pd.read_parquet(PROCESSED / "daily_sales.parquet")
        forecast = pd.read_parquet(PROCESSED / "forecast.parquet")
        product_daily = pd.read_parquet(PROCESSED / "product_daily.parquet")
        kpi = pd.read_parquet(PROCESSED / "kpi.parquet").iloc[0].to_dict()
        return daily, forecast, product_daily, kpi
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
    daily, forecast, product_daily, kpi = load_data()


    st.markdown("""
    <div style='padding:1.5rem 0 1rem 0;'>
        <h1 style='font-size:2rem; font-weight:800;'>📈 Demand Forecasting</h1>
        <p style='color:#78909c;'>30-day ahead predictions using ARIMA + ETS ensemble models</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Metrics ───────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("📊 Forecast MAPE", f"{kpi.get('forecast_mape', 0):.1f}%", help="Mean Absolute Percentage Error — lower is better")
    with c2:
        st.metric("📅 Forecast Horizon", "30 Days")
    with c3:
        st.metric("📦 Avg Forecasted Qty/Day", f"{forecast['forecast'].mean():.1f} units")
    with c4:
        st.metric("📈 Total Forecast (30d)", f"{forecast['forecast'].sum():.0f} units")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── What-If Slider ────────────────────────────────────────────────
    st.markdown("### 🎛️ What-If Analysis")
    col1, col2 = st.columns([2, 1])
    with col1:
        growth_pct = st.slider("📈 Apply growth/decline scenario (%)", -50, 100, 0, 5,
                                help="Simulate demand scenarios by adjusting the forecast up or down")
    with col2:
        horizon_days = st.slider("📅 Forecast horizon (days)", 7, 30, 30)

    adjusted_forecast = forecast.head(horizon_days).copy()
    adjusted_forecast["forecast_adjusted"] = adjusted_forecast["forecast"] * (1 + growth_pct / 100)
    adjusted_forecast["lower_adjusted"] = adjusted_forecast["lower"] * (1 + growth_pct / 100)
    adjusted_forecast["upper_adjusted"] = adjusted_forecast["upper"] * (1 + growth_pct / 100)

    # ── Main Forecast Chart ───────────────────────────────────────────
    fig = go.Figure()

    # Historical
    daily["date"] = pd.to_datetime(daily["date"])
    fig.add_trace(go.Scatter(
        x=daily["date"], y=daily["total_qty"],
        name="Historical Demand",
        line=dict(color="rgba(100,181,246,0.6)", width=1.5),
        fill="tozeroy", fillcolor="rgba(100,181,246,0.06)"
    ))

    # 7-day rolling avg on historical
    rolling = daily["total_qty"].rolling(7, min_periods=1).mean()
    fig.add_trace(go.Scatter(
        x=daily["date"], y=rolling,
        name="Historical (7d avg)",
        line=dict(color="#64b5f6", width=2)
    ))

    # Confidence band
    adjusted_forecast["ds"] = pd.to_datetime(adjusted_forecast["ds"])
    fig.add_trace(go.Scatter(
        x=pd.concat([adjusted_forecast["ds"], adjusted_forecast["ds"].iloc[::-1]]),
        y=pd.concat([adjusted_forecast["upper_adjusted"], adjusted_forecast["lower_adjusted"].iloc[::-1]]),
        fill="toself", fillcolor="rgba(255,167,38,0.12)",
        line=dict(color="rgba(255,255,255,0)"),
        name="80% Confidence Band", showlegend=True
    ))

    # Forecast line
    fig.add_trace(go.Scatter(
        x=adjusted_forecast["ds"], y=adjusted_forecast["forecast_adjusted"],
        name=f"Forecast{f' (+{growth_pct}%)' if growth_pct != 0 else ''}",
        line=dict(color="#ffa726", width=2.5, dash="dot"),
        mode="lines+markers", marker=dict(size=5)
    ))

    # Divider
    last_date = daily["date"].max().timestamp() * 1000
    fig.add_vline(x=last_date, line_dash="dash", line_color="rgba(100,181,246,0.4)",
                  annotation_text="Forecast Start", annotation_font_color="#64b5f6")

    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=400, margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", yanchor="bottom", y=1.02),
        xaxis=dict(gridcolor="rgba(100,180,255,0.1)"),
        yaxis=dict(gridcolor="rgba(100,180,255,0.1)", title="Units Demanded"),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Forecast Table ────────────────────────────────────────────────
    with st.expander("📋 View Forecast Table (Next 30 Days)"):
        display_fc = adjusted_forecast[["ds", "forecast_adjusted", "lower_adjusted", "upper_adjusted"]].copy()
        display_fc.columns = ["Date", "Forecasted Qty", "Lower Bound (80%)", "Upper Bound (80%)"]
        display_fc["Date"] = display_fc["Date"].dt.strftime("%Y-%m-%d")
        display_fc["Forecasted Qty"] = display_fc["Forecasted Qty"].round(1)
        display_fc["Lower Bound (80%)"] = display_fc["Lower Bound (80%)"].round(1)
        display_fc["Upper Bound (80%)"] = display_fc["Upper Bound (80%)"].round(1)
        st.dataframe(display_fc, use_container_width=True, hide_index=True)

    # ── Top Products Trend ────────────────────────────────────────────
    st.markdown("### 📦 Product-Level Demand Trends")
    products = product_daily["productName"].unique().tolist()
    selected_products = st.multiselect(
        "Select products to compare:",
        options=products,
        default=products[:5] if len(products) >= 5 else products,
        max_selections=8
    )

    if selected_products:
        filtered = product_daily[product_daily["productName"].isin(selected_products)]
        filtered["date"] = pd.to_datetime(filtered["date"])
        fig_prod = px.line(
            filtered, x="date", y="qty", color="productName",
            labels={"qty": "Quantity", "date": "Date", "productName": "Product"},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_prod.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=350, margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(bgcolor="rgba(0,0,0,0)"),
            xaxis=dict(gridcolor="rgba(100,180,255,0.1)"),
            yaxis=dict(gridcolor="rgba(100,180,255,0.1)"),
        )
        st.plotly_chart(fig_prod, use_container_width=True)

