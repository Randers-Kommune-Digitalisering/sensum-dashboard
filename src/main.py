import streamlit as st

from utils.logo import get_logo
from page.ongoing_cases import get_ongoing_cases
from page.indsatser import get_indsatser
from page.indsats_supplier import get_indsatser_with_supplier
from page.ydelse import get_ydelse


st.set_page_config(
    page_title="Sensum Dashboard",
    page_icon="assets/favicon.ico",
)


PAGES = {
    "ongoing_cases": {
        "label": "Antal igangværende sager",
        "function": get_ongoing_cases,
    },
    "indsatser": {
        "label": "Indsatser",
        "function": get_indsatser,
    },
    "ydelse": {
        "label": "Ydelse fordelt på afdeling",
        "function": get_ydelse,
    },
    "supplier": {
        "label": (
            "Indsatser fordelt på afdeling, "
            "leverandørnavn og leverandørindsats"
        ),
        "function": get_indsatser_with_supplier,
    },
}


st.markdown(
    """
<style>
/* Entire sidebar */
[data-testid="stSidebar"] {
    background-color: #f0f0f0;
}

/* Sidebar content spacing */
[data-testid="stSidebarContent"] {
    padding-top: 1rem;
}

/* Sensum Dashboard heading */
.dashboard-heading {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    margin: 24px 12px 20px 12px;
    color: #4a4a4a;
}

/* Bootstrap clipboard icon in the heading */
.dashboard-heading-icon {
    width: 27px;
    height: 27px;
    margin-top: 5px;
    flex-shrink: 0;
}

/* Heading text */
.dashboard-heading-text {
    font-size: 26px;
    font-weight: 700;
    line-height: 1.45;
}

/* Divider underneath heading */
.dashboard-divider {
    border: none;
    border-top: 1px solid #bcbcbc;
    margin: 0 12px 14px 12px;
}

/* Remove space between menu choices */
[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 5px;
}

/* Each radio menu choice */
[data-testid="stSidebar"] div[role="radiogroup"] > label {
    display: flex;
    align-items: flex-start;
    width: 100%;
    min-height: 54px;
    padding: 13px 16px;
    margin: 0;
    border-radius: 9px;
    cursor: pointer;
}

/* Menu hover */
[data-testid="stSidebar"]
div[role="radiogroup"]
> label:hover {
    background-color: #e0e0e0;
}

/* Selected menu choice */
[data-testid="stSidebar"]
div[role="radiogroup"]
> label:has(input:checked) {
    background-color: #d0d0d0;
}

/* Hide normal radio circle */
[data-testid="stSidebar"]
div[role="radiogroup"]
input {
    display: none;
}

/* Hide Streamlit's radio-control container */
[data-testid="stSidebar"]
div[role="radiogroup"]
label > div:first-child {
    display: none;
}

/* Menu text */
[data-testid="stSidebar"]
div[role="radiogroup"]
label p {
    margin: 0;
    color: #303030;
    font-size: 17px;
    line-height: 1.45;
    white-space: normal;
    overflow-wrap: break-word;
}

/* Selected menu text */
[data-testid="stSidebar"]
div[role="radiogroup"]
> label:has(input:checked) p {
    color: #4a4a4a;
    font-weight: 700;
}

/* Shared Bootstrap icon area */
[data-testid="stSidebar"]
div[role="radiogroup"]
> label::before {
    content: "";
    display: block;
    width: 21px;
    height: 21px;
    flex: 0 0 21px;
    margin-top: 2px;
    margin-right: 12px;

    background-repeat: no-repeat;
    background-position: center;
    background-size: contain;
}

/* First menu choice: Bootstrap map icon */
[data-testid="stSidebar"]
div[role="radiogroup"]
> label:nth-of-type(1)::before {
    background-image: url(
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/icons/map.svg"
    );
}

/* Remaining choices: Bootstrap bar chart icon */
[data-testid="stSidebar"]
div[role="radiogroup"]
> label:nth-of-type(2)::before,
[data-testid="stSidebar"]
div[role="radiogroup"]
> label:nth-of-type(3)::before,
[data-testid="stSidebar"]
div[role="radiogroup"]
> label:nth-of-type(4)::before {
    background-image: url(
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/icons/bar-chart.svg"
    );
}
</style>
""",
    unsafe_allow_html=True,
)


with st.sidebar:
    st.markdown(
        get_logo(),
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="dashboard-heading">
    <img
        class="dashboard-heading-icon"
        src="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/icons/clipboard-data-fill.svg"
        alt=""
    >
    <div class="dashboard-heading-text">
        Sensum<br>
        Dashboard
    </div>
</div>
<hr class="dashboard-divider">
""",
        unsafe_allow_html=True,
    )

    selected_page = st.radio(
        "Navigation",
        options=list(PAGES.keys()),
        format_func=lambda page: PAGES[page]["label"],
        label_visibility="collapsed",
        key="sidebar_navigation",
    )


# Open the selected page.
PAGES[selected_page]["function"]()
