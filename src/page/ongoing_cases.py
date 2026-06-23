import altair as alt
import pandas as pd
import streamlit as st

from utils.database_connection import get_db_client


def render_cases_header() -> None:

    st.markdown(
        """
<style>
.ongoing-cases-header {
    width: 100%;
    margin: 0 0 1.5rem 0;
}

.ongoing-cases-title-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;

    min-height: 80px;
    padding: 10px;
}

.ongoing-cases-title {
    color: #34343c;
    font-size: 22px;
    font-weight: 400;
    line-height: 1.3;
}

.ongoing-cases-pill {
    display: inline-block;
    padding: 3px 10px;

    background-color: #f1f1f1;
    border: 1px solid #d1d1d1;
    border-radius: 999px;

    color: #55555d;
    font-size: 13px;
    font-weight: 400;
    line-height: 1.2;
    white-space: nowrap;
}

.ongoing-cases-line {
    width: 100%;
    height: 2px;
    background-color: #2f2f2f;
}
</style>
""",
        unsafe_allow_html=True,
    )

    # Keep this HTML on one line so Streamlit does not render it as code.
    st.markdown(
        '<div class="ongoing-cases-header">'
        '<div class="ongoing-cases-title-row">'
        '<span class="ongoing-cases-title">'
        'Antal igangværende sager'
        '</span>'
        '<span class="ongoing-cases-pill">'
        'Antal igangværende sager'
        '</span>'
        '</div>'
        '<div class="ongoing-cases-line"></div>'
        '</div>',
        unsafe_allow_html=True,
    )


def load_cases_data():
    """Load case data and close the connection safely."""

    db_client = get_db_client()

    try:
        query = """
        SELECT
            "SagNavn",
            "SagType",
            "MedarbejderFornavn",
            "MedarbejderEfternavn",
            "AfdelingNavn",
            "Status"
        FROM aktive_sager
        """

        return db_client.execute_sql(query)

    finally:
        db_client.close_connection()


def get_ongoing_cases():
    render_cases_header()

    try:
        if "cases_final_result" not in st.session_state:
            with st.spinner("Loading data..."):
                result = load_cases_data()

            if result is None:
                st.error("Failed to fetch data from the database.")
                return

            st.session_state.cases_final_result = pd.DataFrame(
                result,
                columns=[
                    "SagNavn",
                    "SagType",
                    "MedarbejderFornavn",
                    "MedarbejderEfternavn",
                    "AfdelingNavn",
                    "Status",
                ],
            )

        final_result = st.session_state.cases_final_result.copy()

        sagstype_options = (
            final_result["SagType"]
            .dropna()
            .sort_values()
            .unique()
        )

        if len(sagstype_options) == 0:
            st.warning("Der blev ikke fundet nogen sagstyper.")
            return

        selected_sagstype = st.selectbox(
            "Vælg Sagstype",
            options=sagstype_options,
            key="ongoing_cases_sagstype",
            help="Vælg den type sag, du vil se data for.",
        )

        filtered_result = final_result.loc[
            final_result["SagType"] == selected_sagstype
        ].copy()

        afdeling_options = (
            filtered_result
            .dropna(subset=["AfdelingNavn"])
            ["AfdelingNavn"]
            .sort_values()
            .unique()
        )

        if len(afdeling_options) == 0:
            st.warning(
                "Der blev ikke fundet nogen afdelinger "
                "for den valgte sagstype."
            )
            return

        selected_afdeling = st.selectbox(
            "Vælg Afdeling",
            options=afdeling_options,
            key="ongoing_cases_afdeling",
            help="Vælg den afdeling, du vil se data for.",
        )

        filtered_result = filtered_result.loc[
            filtered_result["AfdelingNavn"]
            == selected_afdeling
        ].copy()

        filtered_result["MedarbejderNavn"] = (
            filtered_result["MedarbejderFornavn"].fillna("")
            + " "
            + filtered_result["MedarbejderEfternavn"].fillna("")
        ).str.strip()

        medarbejder_options = (
            filtered_result.loc[
                filtered_result["MedarbejderNavn"] != "",
                "MedarbejderNavn",
            ]
            .sort_values()
            .unique()
        )

        if len(medarbejder_options) > 0:
            selected_medarbejder = st.selectbox(
                "Vælg Medarbejder",
                options=medarbejder_options,
                key="ongoing_cases_medarbejder",
                help=(
                    "Vælg den medarbejder, "
                    "du vil se data for."
                ),
            )

            filtered_result = filtered_result.loc[
                filtered_result["MedarbejderNavn"]
                == selected_medarbejder
            ].copy()

        num_ongoing_cases = len(filtered_result)

        st.metric(
            label="Antal igangværende sager",
            value=num_ongoing_cases,
        )

        chart_data = (
            filtered_result
            .groupby(
                [
                    "AfdelingNavn",
                    "MedarbejderFornavn",
                    "MedarbejderEfternavn",
                ],
                dropna=False,
            )
            .size()
            .reset_index(
                name="Antal igangværende sager"
            )
        )

        chart = (
            alt.Chart(chart_data)
            .mark_bar()
            .encode(
                x=alt.X(
                    "AfdelingNavn:N",
                    title="Afdeling Navn",
                ),
                y=alt.Y(
                    "Antal igangværende sager:Q",
                    title="Antal igangværende sager",
                ),
                color=alt.Color(
                    "MedarbejderFornavn:N",
                    title="Medarbejder",
                ),
                tooltip=[
                    alt.Tooltip(
                        "AfdelingNavn:N",
                        title="Afdeling",
                    ),
                    alt.Tooltip(
                        "MedarbejderFornavn:N",
                        title="Fornavn",
                    ),
                    alt.Tooltip(
                        "MedarbejderEfternavn:N",
                        title="Efternavn",
                    ),
                    alt.Tooltip(
                        "Antal igangværende sager:Q",
                        title="Antal",
                    ),
                ],
            )
            .properties(
                width=600,
                height=400,
                title=(
                    "Fordeling af igangværende sager "
                    "på afdelinger og medarbejdere"
                ),
            )
        )

        st.altair_chart(
            chart,
            use_container_width=True,
        )

    except Exception as error:
        st.error(f"An error occurred: {error}")