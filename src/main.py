import streamlit as st
from streamlit_option_menu import option_menu
from utils.logo import get_logo

st.set_page_config(page_title="Sensum Dashboard", page_icon="assets/favicon.ico")

with st.sidebar:
    st.sidebar.markdown(get_logo(), unsafe_allow_html=True)
    selected = option_menu(
        "Sensum data",
        ["Antal igangværende sager", "Godkendte Indsatser", "Ydelse fordelt på afdeling"],
        icons=['house'],
        default_index=0
    )

if selected == "Antal igangværende sager":
    st.write("Antal igangværende sager")
elif selected == "Godkendte Indsatser":
    st.write("Godkendte Indsatser")
elif selected == "Ydelse fordelt på afdeling":
    st.write("Ydelse fordelt på afdeling")
