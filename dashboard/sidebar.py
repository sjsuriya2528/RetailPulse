import streamlit as st
from streamlit_option_menu import option_menu

def render_sidebar(default_index=0):
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center; padding: 0.2rem 0 0.2rem 0;'>
            <div style='font-size:2.2rem; margin-bottom: 0px; animation: pulse 2s infinite;'>⚡</div>
            <div style='font-size:1.4rem; font-weight:800; background: linear-gradient(to right, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>RetailPulse</div>
            <div style='font-size:0.7rem; color:#94a3b8; margin-top:0px; font-weight: 300; letter-spacing: 1px; text-transform: uppercase;'>Analytics Engine</div>
        </div>
        <hr style='border-color:rgba(255,255,255,0.05); margin: 5px 0;'>
        """, unsafe_allow_html=True)
        
        # Hide the default Streamlit sidebar
        st.markdown("""
        <style>
            [data-testid="stSidebarNav"] { display: none !important; }
            [data-testid="stSidebar"] { padding-top: 0rem !important; overflow: hidden !important; scrollbar-width: none; }
            [data-testid="stSidebar"]::-webkit-scrollbar { display: none; }
            [data-testid="stSidebar"] .block-container { padding-top: 0.5rem !important; padding-bottom: 0.5rem !important; overflow: hidden !important;}
            section[data-testid="stSidebar"] > div { padding-top: 0rem !important; overflow-y: hidden !important; }
            section[data-testid="stSidebar"] > div::-webkit-scrollbar { display: none; }
        </style>
        """, unsafe_allow_html=True)

        selected = option_menu(
            menu_title="Explore App",
            options=["Home", "Overview", "Forecasting", "Segmentation", "Churn Analysis", "Inventory", "Export"],
            icons=["house", "layout-text-sidebar-reverse", "graph-up-arrow", "people", "exclamation-triangle", "box", "cloud-download"],
            menu_icon="compass",
            default_index=default_index,
            styles={
                "container": {"padding": "0!important", "margin": "0!important", "background-color": "transparent"},
                "icon": {"color": "#64748b", "font-size": "1rem"}, 
                "nav-link": {"font-size": "0.9rem", "text-align": "left", "margin":"0px", "padding": "8px 10px", "border-radius": "10px", "--hover-color": "rgba(56, 189, 248, 0.1)"},
                "nav-link-selected": {"background-color": "rgba(56, 189, 248, 0.15)", "color": "#f8fafc", "font-weight": "600", "border-left": "4px solid #38bdf8"},
                "menu-title": {"color": "#64748b", "font-size": "0.75rem", "text-transform": "uppercase", "letter-spacing": "1px", "padding-left": "10px", "margin-top": "0px", "margin-bottom": "2px"}
            }
        )

        st.markdown("<hr style='border-color:rgba(255,255,255,0.05); margin: 10px 0 5px 0;'>", unsafe_allow_html=True)
        st.markdown("""
        <div style='font-size:0.65rem; color:#475569; text-align:center; font-weight: 300;'>
            Powered by Zidio Development<br>
            Data Science & Analytics · 2026
        </div>
        """, unsafe_allow_html=True)
        
        return selected


