import altair as alt
import pandas as pd
import streamlit as st

from utils.database_connection import get_db_client


def render_period_header() -> None:

    st.markdown(
        """
<style>
.ydelse-period-header {
    width: 100%;
    margin: 0 0 1.5rem 0;
}

.ydelse-period-title-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;

    min-height: 80px;
    padding: 10px;
}

.ydelse-period-title {
    color: #34343c;
    font-size: 22px;
    font-weight: 400;
    line-height: 1.3;
}

.ydelse-period-pill {
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

.ydelse-period-line {
    width: 100%;
    height: 2px;
    background-color: #2f2f2f;
}
</style>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="ydelse-period-header">'
        '<div class="ydelse-period-title-row">'
        '<span class="ydelse-period-title">Periode</span>'
        '<span class="ydelse-period-pill">Periode</span>'
        '</div>'
        '<div class="ydelse-period-line"></div>'
        '</div>',
        unsafe_allow_html=True,
    )


def load_ydelse_data():
    """Load ydelse data and close the database connection safely."""

    db_client = get_db_client()

    try:
        query = """
        SELECT
            "YdelseNavn",
            "AfdelingNavn",
            "StartDato",
            "SlutDato"
        FROM ydelse
        """

        return db_client.execute_sql(query)

    finally:
        db_client.close_connection()


def get_ydelse():
    render_period_header()

    try:
        if "ydelse_final_result" not in st.session_state:
            with st.spinner("Loading data..."):
                result = load_ydelse_data()

            if result is None:
                st.error("Failed to fetch data from the database.")
                return

            st.session_state.ydelse_final_result = pd.DataFrame(
                result,
                columns=[
                    "YdelseNavn",
                    "AfdelingNavn",
                    "StartDato",
                    "SlutDato",
                ],
            )

        # Work on a copy so the stored data is not modified on every rerun.
        final_result = st.session_state.ydelse_final_result.copy()

        date_format = "%d-%m-%Y %H-%M"

        final_result["StartDato"] = pd.to_datetime(
            final_result["StartDato"],
            format=date_format,
            errors="coerce",
        )

        final_result["SlutDato"] = pd.to_datetime(
            final_result["SlutDato"],
            format=date_format,
            errors="coerce",
        )

        # Rows without a valid start date cannot be grouped by year/month.
        final_result = final_result.dropna(
            subset=["StartDato"]
        ).copy()

        if final_result.empty:
            st.warning("Der blev ikke fundet nogen gyldige data.")
            return

        final_result["Year"] = (
            final_result["StartDato"]
            .dt.year
            .astype(int)
        )

        final_result["Month"] = (
            final_result["StartDato"]
            .dt.month
            .astype(int)
        )

        unique_years = sorted(
            final_result["Year"].unique(),
            reverse=True,
        )

        if not unique_years:
            st.warning("Der blev ikke fundet nogen gyldige årstal.")
            return

        year_column, month_column = st.columns(2)

        with year_column:
            selected_year = st.selectbox(
                "Vælg et år",
                options=unique_years,
                key="ydelse_selected_year",
                help=(
                    "Vælg det år, for hvilket du vil se "
                    "dataene."
                ),
            )

        filtered_result_year = final_result.loc[
            final_result["Year"] == selected_year
        ].copy()

        unique_months = sorted(
            filtered_result_year["Month"].unique()
        )

        if not unique_months:
            st.warning(
                "Der blev ikke fundet nogen måneder "
                "for det valgte år."
            )
            return

        with month_column:
            selected_month = st.selectbox(
                "Vælg en måned",
                options=unique_months,
                key="ydelse_selected_month",
                help=(
                    "Vælg den måned, for hvilken du vil "
                    "se dataene."
                ),
            )

        month_data = (
            filtered_result_year.loc[
                filtered_result_year["Month"]
                == selected_month
            ]
            .groupby(
                [
                    "Month",
                    "YdelseNavn",
                    "AfdelingNavn",
                ],
                dropna=False,
            )
            .size()
            .reset_index(name="Antal ydelse")
        )

        total_ydelse_month = int(
            month_data["Antal ydelse"].sum()
        )

        st.metric(
            label="Samlet antal ydelse (Måned)",
            value=total_ydelse_month,
        )

        st.write(
            "## Antal af Ydelse "
            f"(Måned) - {selected_year}, "
            f"Måned {selected_month}"
        )

        month_chart = (
            alt.Chart(month_data)
            .mark_bar()
            .encode(
                x=alt.X(
                    "Antal ydelse:Q",
                    title="Antal ydelse",
                ),
                y=alt.Y(
                    "YdelseNavn:N",
                    title="YdelseNavn",
                ),
                color=alt.Color(
                    "AfdelingNavn:N",
                    title="Afdeling",
                ),
                tooltip=[
                    alt.Tooltip(
                        "YdelseNavn:N",
                        title="Ydelse",
                    ),
                    alt.Tooltip(
                        "Antal ydelse:Q",
                        title="Antal ydelse",
                    ),
                    alt.Tooltip(
                        "AfdelingNavn:N",
                        title="Afdeling",
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

    except Exception as error:
        st.error(f"An error occurred: {error}")
