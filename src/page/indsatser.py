import altair as alt
import pandas as pd
import streamlit as st

from utils.database_connection import get_db_client


WEEKDAY = {
    "Monday": "Mandag",
    "Tuesday": "Tirsdag",
    "Wednesday": "Onsdag",
    "Thursday": "Torsdag",
    "Friday": "Fredag",
    "Saturday": "Lørdag",
    "Sunday": "Søndag",
}


def render_period_tabs() -> str:

    if "indsatser_period_tab" not in st.session_state:
        st.session_state.indsatser_period_tab = "Uge"

    selected_tab = st.session_state.indsatser_period_tab

    st.markdown(
        """
<style>
/* Full-width wrapper around both tabs */
.st-key-period_tabs {
    width: 100%;
    margin-bottom: 1.5rem;
}

/* Control the distance between Uge and Måned */
.st-key-period_tabs [data-testid="stHorizontalBlock"] {
    gap: 3rem;
}

/* Make each keyed tab container fill its column */
.st-key-period_week,
.st-key-period_month {
    width: 100%;
}

/* Remove spacing around Streamlit's button wrapper */
.st-key-period_week [data-testid="stButton"],
.st-key-period_month [data-testid="stButton"] {
    width: 100%;
    margin: 0;
}

/* Base appearance for both tabs */
.st-key-period_week button,
.st-key-period_month button {
    width: 100% !important;
    min-height: 86px;

    display: flex;
    align-items: center;
    justify-content: center;

    padding: 12px 10px;
    margin: 0;

    background-color: transparent !important;
    color: #34343c !important;

    border: none !important;
    border-bottom: 2px solid #dddddd !important;
    border-radius: 0 !important;

    box-shadow: none !important;
}

/* Remove Streamlit's default red border and focus effects */
.st-key-period_week button:focus,
.st-key-period_month button:focus,
.st-key-period_week button:active,
.st-key-period_month button:active {
    box-shadow: none !important;
    outline: none !important;
}

/* Light hover appearance */
.st-key-period_week button:hover,
.st-key-period_month button:hover {
    background-color: #fafafa !important;
    color: #34343c !important;
}

/* Text inside the tabs */
.st-key-period_week button p,
.st-key-period_month button p {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;

    margin: 0;

    color: #34343c !important;
    font-size: 22px;
    font-weight: 400;
    line-height: 1.3;
}

/* Shared grey pill appearance */
.st-key-period_week button p::after,
.st-key-period_month button p::after {
    display: inline-block;

    padding: 3px 10px;

    background-color: #f1f1f1;
    border: 1px solid #d1d1d1;
    border-radius: 999px;

    color: #55555d;
    font-size: 13px;
    font-weight: 400;
    line-height: 1.2;
}

/* Text inside the Uge pill */
.st-key-period_week button p::after {
    content: "Uge";
}

/* Text inside the Måned pill */
.st-key-period_month button p::after {
    content: "Måned";
}

/* Stack the tabs vertically on small screens */
@media (max-width: 700px) {
    .st-key-period_tabs [data-testid="stHorizontalBlock"] {
        gap: 0.5rem;
    }

    .st-key-period_week button,
    .st-key-period_month button {
        min-height: 60px;
    }
}
</style>
""",
        unsafe_allow_html=True,
    )

    # Add the dark underline to the currently selected tab.
    if selected_tab == "Uge":
        st.markdown(
            """
<style>
.st-key-period_week button {
    border-bottom-color: #2f2f2f !important;
}
</style>
""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
<style>
.st-key-period_month button {
    border-bottom-color: #2f2f2f !important;
}
</style>
""",
            unsafe_allow_html=True,
        )

    def select_period(period: str) -> None:
        st.session_state.indsatser_period_tab = period

    with st.container(key="period_tabs"):
        week_column, month_column = st.columns(
            2,
            gap="large",
        )

        with week_column:
            with st.container(key="period_week"):
                st.button(
                    "Uge",
                    key="period_week_button",
                    use_container_width=True,
                    on_click=select_period,
                    args=("Uge",),
                )

        with month_column:
            with st.container(key="period_month"):
                st.button(
                    "Måned",
                    key="period_month_button",
                    use_container_width=True,
                    on_click=select_period,
                    args=("Måned",),
                )

    return st.session_state.indsatser_period_tab

def load_indsatser_data():
    """Load the indsats data and close the database connection safely."""

    db_client = get_db_client()

    try:
        query = """
        SELECT
            "IndsatsStartDato",
            "IndsatsStatus",
            "IndsatsSlutDato"
        FROM aktive_indsatser
        """

        return db_client.execute_sql(query)

    finally:
        db_client.close_connection()


def get_indsatser():
    content_tabs = render_period_tabs()

    try:
        if "indsatser_final_result" not in st.session_state:
            with st.spinner("Loading data..."):
                result = load_indsatser_data()

            if result is None:
                st.error("Failed to fetch data from the database.")
                return

            st.session_state.indsatser_final_result = pd.DataFrame(
                result,
                columns=[
                    "IndsatsStartDato",
                    "IndsatsStatus",
                    "IndsatsSlutDato",
                ],
            )

        # Copy the data before adding calculated columns.
        final_result = (
            st.session_state.indsatser_final_result.copy()
        )

        final_result["IndsatsStartDato"] = pd.to_datetime(
            final_result["IndsatsStartDato"],
            dayfirst=True,
            errors="coerce",
        )

        final_result["IndsatsSlutDato"] = pd.to_datetime(
            final_result["IndsatsSlutDato"],
            dayfirst=True,
            errors="coerce",
        )

        current_time = pd.Timestamp.now()

        filtered_result = final_result.loc[
            (final_result["IndsatsStatus"] == "Godkendt")
            & (
                final_result["IndsatsSlutDato"].isna()
                | (
                    final_result["IndsatsSlutDato"]
                    >= current_time
                )
            )
        ].copy()

        if filtered_result.empty:
            st.warning("Der blev ikke fundet nogen aktive indsatser.")
            return

        total_active_indsatser = len(filtered_result)

        st.metric(
            label="Samlet antal aktive indsatser (Alle)",
            value=total_active_indsatser,
        )

        filtered_result["Year"] = (
            filtered_result["IndsatsStartDato"].dt.year
        )

        unique_years = sorted(
            filtered_result["Year"]
            .dropna()
            .astype(int)
            .unique(),
            reverse=True,
        )

        if not unique_years:
            st.warning(
                "Der blev ikke fundet nogen gyldige årstal."
            )
            return

        if content_tabs == "Uge":
            show_week_view(
                filtered_result=filtered_result,
                unique_years=unique_years,
            )

        elif content_tabs == "Måned":
            show_month_view(
                filtered_result=filtered_result,
                unique_years=unique_years,
            )

    except Exception as error:
        st.error(f"An error occurred: {error}")


def show_week_view(
    filtered_result: pd.DataFrame,
    unique_years: list,
):
    """Show active interventions grouped by week."""

    week_result = filtered_result.copy()

    week_result["Week"] = (
        week_result["IndsatsStartDato"]
        .dt.isocalendar()
        .week
        .astype(int)
    )

    week_result["Weekday"] = (
        week_result["IndsatsStartDato"]
        .dt.day_name()
        .map(WEEKDAY)
    )

    col1, col2 = st.columns(2)

    with col1:
        selected_year_week = st.selectbox(
            "Vælg et år",
            options=unique_years,
            key="selected_year_week",
            help=(
                "Vælg det år, for hvilket du vil se "
                "dataene."
            ),
        )

    filtered_result_year = week_result.loc[
        week_result["Year"] == selected_year_week
    ].copy()

    unique_weeks = sorted(
        filtered_result_year["Week"].dropna().unique()
    )

    if not unique_weeks:
        st.warning(
            "Der blev ikke fundet nogen uger for det valgte år."
        )
        return

    with col2:
        selected_week = st.selectbox(
            "Vælg en uge",
            options=unique_weeks,
            key="selected_week",
            help=(
                "Vælg den uge, for hvilken du vil se "
                "dataene."
            ),
        )

    week_data = (
        filtered_result_year.loc[
            filtered_result_year["Week"] == selected_week
        ]
        .groupby(
            ["Week", "Weekday"],
            dropna=False,
        )
        .size()
        .reset_index(
            name="Antal aktive indsatser"
        )
    )

    total_active_indsatser_week = int(
        week_data["Antal aktive indsatser"].sum()
    )

    st.metric(
        label="Samlet antal aktive indsatser (Uge)",
        value=total_active_indsatser_week,
    )

    st.write(
        "## Antal af Aktive Indsatser "
        f"(Uge) - {selected_year_week}, Uge {selected_week}"
    )

    week_chart = (
        alt.Chart(week_data)
        .mark_bar()
        .encode(
            x=alt.X(
                "Weekday:N",
                title="Ugedag",
                sort=[
                    "Mandag",
                    "Tirsdag",
                    "Onsdag",
                    "Torsdag",
                    "Fredag",
                    "Lørdag",
                    "Søndag",
                ],
            ),
            y=alt.Y(
                "Antal aktive indsatser:Q",
                title="Antal aktive indsatser",
            ),
            tooltip=[
                alt.Tooltip(
                    "Weekday:N",
                    title="Ugedag",
                ),
                alt.Tooltip(
                    "Antal aktive indsatser:Q",
                    title="Antal aktive indsatser",
                ),
            ],
        )
        .properties(
            width=600,
            height=400,
        )
    )

    st.altair_chart(
        week_chart,
        width=True,
    )


def show_month_view(
    filtered_result: pd.DataFrame,
    unique_years: list,
):
    """Show active interventions grouped by month."""

    month_result = filtered_result.copy()

    month_result["Month"] = (
        month_result["IndsatsStartDato"].dt.month
    )

    month_result["Månedsdag"] = (
        month_result["IndsatsStartDato"]
        .dt.day
        .astype(int)
    )

    col1, col2 = st.columns(2)

    with col1:
        selected_year_month = st.selectbox(
            "Vælg et år",
            options=unique_years,
            key="selected_year_month",
            help=(
                "Vælg det år, for hvilket du vil se "
                "dataene."
            ),
        )

    filtered_result_year = month_result.loc[
        month_result["Year"] == selected_year_month
    ].copy()

    unique_months = sorted(
        filtered_result_year["Month"]
        .dropna()
        .astype(int)
        .unique()
    )

    if not unique_months:
        st.warning(
            "Der blev ikke fundet nogen måneder "
            "for det valgte år."
        )
        return

    with col2:
        selected_month = st.selectbox(
            "Vælg en måned",
            options=unique_months,
            key="selected_month",
            help=(
                "Vælg den måned, for hvilken du vil se "
                "dataene."
            ),
        )

    month_data = (
        filtered_result_year.loc[
            filtered_result_year["Month"]
            == selected_month
        ]
        .groupby(
            ["Month", "Månedsdag"],
            dropna=False,
        )
        .size()
        .reset_index(
            name="Antal aktive indsatser"
        )
    )

    total_active_indsatser_month = int(
        month_data["Antal aktive indsatser"].sum()
    )

    st.metric(
        label="Samlet antal aktive indsatser (Måned)",
        value=total_active_indsatser_month,
    )

    st.write(
        "## Antal af Aktive Indsatser "
        f"(Måned) - {selected_year_month}, "
        f"Måned {selected_month}"
    )

    month_chart = (
        alt.Chart(month_data)
        .mark_bar()
        .encode(
            x=alt.X(
                "Månedsdag:O",
                title="Månedsdag",
                axis=alt.Axis(format="d"),
            ),
            y=alt.Y(
                "Antal aktive indsatser:Q",
                title="Antal aktive indsatser",
            ),
            tooltip=[
                alt.Tooltip(
                    "Månedsdag:O",
                    title="Månedsdag",
                ),
                alt.Tooltip(
                    "Antal aktive indsatser:Q",
                    title="Antal aktive indsatser",
                ),
            ],
        )
        .properties(
            width=600,
            height=400,
        )
    )

    st.altair_chart(
        month_chart,
        width=True,
    )
    