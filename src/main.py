import streamlit as st
from streamlit_option_menu import option_menu
from utils.logo import get_logo
from page.ongoing_cases import get_ongoing_cases
from page.indsatser import get_indsatser

st.set_page_config(page_title="Sensum Dashboard", page_icon="assets/favicon.ico")

with st.sidebar:
    st.sidebar.markdown(get_logo(), unsafe_allow_html=True)
    selected = option_menu(
        "Sensum Dashboard",
        ["Antal igangværende sager", "Indsatser", "Ydelse fordelt på afdeling"],
        default_index=0,
        icons=['map', 'bi-bar-chart', 'bi-bar-chart'],
        menu_icon="bi-clipboard-data-fill",
        styles={
            "container": {"padding": "5px", "background-color": "#f0f0f0"},
            "icon": {"color": "#4a4a4a", "font-size": "18px"},
            "nav-link": {"font-size": "18px", "text-align": "left", "margin": "0px", "--hover-color": "#e0e0e0"},
            "nav-link-selected": {"background-color": "#d0d0d0", "color": "#4a4a4a"},
            "menu-title": {"font-size": "20px", "font-weight": "bold", "color": "#4a4a4a", "margin-bottom": "10px"},
        }
    )

if selected == "Antal igangværende sager":
    get_ongoing_cases()
elif selected == "Indsatser":
    get_indsatser()
elif selected == "Ydelse fordelt på afdeling":
    st.write("Ydelse fordelt på afdeling")
