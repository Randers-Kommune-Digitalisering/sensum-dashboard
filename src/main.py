import streamlit as st
from streamlit_option_menu import option_menu
from utils.logo import get_logo
from page.ongoing_cases import get_ongoing_cases

st.set_page_config(page_title="Sensum Dashboard", page_icon="assets/favicon.ico")

with st.sidebar:
    st.sidebar.markdown(get_logo(), unsafe_allow_html=True)
    selected = option_menu(
        "Sensum data",
        ["Antal igangværende sager", "Indsatser", "Ydelse fordelt på afdeling"],
        icons=['house'],
        default_index=0
    )

if selected == "Antal igangværende sager":
    get_ongoing_cases()
elif selected == "Indsatser":
    st.write("Indsatser")
elif selected == "Ydelse fordelt på afdeling":
    st.write("Ydelse fordelt på afdeling")
