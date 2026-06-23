import streamlit as st
import pandas as pd
import altair as alt

from utils.database_connection import get_db_client


db_client = get_db_client()


def render_supplier_tabs() -> str:

    st.markdown(
        """
<style>

[data-testid="stMain"] [data-testid="stRadio"] {
    width: 100%;
}

[data-testid="stMain"] [data-testid="stRadio"] > div {
    width: 100%;
}

[data-testid="stMain"]
[data-testid="stRadio"]
div[role="radiogroup"] {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    width: 100%;
    gap: 2.5rem;
    border-bottom: 1px solid #dddddd;
}

[data-testid="stMain"]
[data-testid="stRadio"]
div[role="radiogroup"]
> label {
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 0;
    min-height: 68px;
    padding: 12px 8px;
    margin: 0 0 -1px 0;
    border-bottom: 2px solid transparent;
    cursor: pointer;
}

[data-testid="stMain"]
[data-testid="stRadio"]
div[role="radiogroup"]
> label:hover {
    background-color: #f7f7f7;
}

[data-testid="stMain"]
[data-testid="stRadio"]
div[role="radiogroup"]
> label:has(input:checked) {
    border-bottom-color: #2f2f2f;
}

[data-testid="stMain"]
[data-testid="stRadio"]
div[role="radiogroup"]
> label
> div:first-child {
    display: none;
}

[data-testid="stMain"]
[data-testid="stRadio"]
div[role="radiogroup"]
label p {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-wrap: wrap;
    gap: 7px;
    width: 100%;
    min-width: 0;
    margin: 0;

    color: #34343c;
    font-size: 18px;
    font-weight: 400;
    line-height: 1.3;
    text-align: center;
    white-space: normal;
    overflow-wrap: break-word;
}

[data-testid="stMain"]
[data-testid="stRadio"]
div[role="radiogroup"]
> label:has(input:checked)
p {
    color: #242429;
}

[data-testid="stMain"]
[data-testid="stRadio"]
div[role="radiogroup"]
> label
p::after {
    display: inline-block;
    padding: 2px 8px;

    border: 1px solid #d1d1d1;
    border-radius: 999px;
    background-color: #f1f1f1;

    color: #55555d;
    font-size: 12px;
    font-weight: 400;
    line-height: 1.2;
    white-space: nowrap;
}

[data-testid="stMain"]
[data-testid="stRadio"]
div[role="radiogroup"]
> label:nth-child(1)
p::after {
    content: "Afdeling";
}

[data-testid="stMain"]
[data-testid="stRadio"]
div[role="radiogroup"]
> label:nth-child(2)
p::after {
    content: "Leverandørnavn";
}

[data-testid="stMain"]
[data-testid="stRadio"]
div[role="radiogroup"]
> label:nth-child(3)
p::after {
    content: "LeverandørIndsats";
}

@media (max-width: 800px) {
    [data-testid="stMain"]
    [data-testid="stRadio"]
    div[role="radiogroup"] {
        grid-template-columns: 1fr;
        gap: 0;
    }

    [data-testid="stMain"]
    [data-testid="stRadio"]
    div[role="radiogroup"]
    > label {
        min-height: 54px;
    }
}
</style>
""",
        unsafe_allow_html=True,
    )

    return st.radio(
        "Vælg visning",
        options=[
            "Afdeling",
            "Leverandørnavn",
            "LeverandørIndsats",
        ],
        horizontal=True,
        label_visibility="collapsed",
        key="supplier_content_tabs",
    )


def get_indsatser_with_supplier():
    content_tabs = render_supplier_tabs()

    try:
        if "indsats_final_result" not in st.session_state:
            results = []

            with st.spinner("Loading data..."):
                query = """
                SELECT
                    "IndsatsStatus",
                    "Indsats",
                    "AfdelingNavn",
                    "IndsatsStartDato",
                    "IndsatsSlutDato",
                    "LeverandørIndsats",
                    "LeverandørNavn",
                    "IndsatsParagraf"
                FROM indsats_fordeling
                """

                result = db_client.execute_sql(query)

                if result is not None:
                    results.append(
                        pd.DataFrame(
                            result,
                            columns=[
                                "IndsatsStatus",
                                "Indsats",
                                "AfdelingNavn",
                                "IndsatsStartDato",
                                "IndsatsSlutDato",
                                "LeverandørIndsats",
                                "LeverandørNavn",
                                "IndsatsParagraf",
                            ],
                        )
                    )
                else:
                    st.error(
                        "Failed to fetch data from the database."
                    )
                    return

            if results:
                st.success("Data fetched successfully.")

                st.session_state.indsats_final_result = pd.concat(
                    results,
                    ignore_index=True,
                )
            else:
                st.error("No data to display.")
                return

        final_result = st.session_state.indsats_final_result.copy()

        final_result["IndsatsStartDato"] = pd.to_datetime(
            final_result["IndsatsStartDato"],
            dayfirst=True,
        )

        final_result["IndsatsSlutDato"] = pd.to_datetime(
            final_result["IndsatsSlutDato"],
            dayfirst=True,
            errors="coerce",
        )

        filtered_result = final_result[
            (final_result["IndsatsStatus"] == "Godkendt")
            & final_result["IndsatsSlutDato"].isna()
        ]

        if content_tabs == "Afdeling":
            afdeling_filter = st.selectbox(
                "Vælg Afdeling",
                options=filtered_result["AfdelingNavn"].unique(),
                help=(
                    "Vælg den afdeling, du vil se data for."
                ),
            )

            afdeling_data = (
                filtered_result[
                    filtered_result["AfdelingNavn"]
                    == afdeling_filter
                ]
                .groupby("AfdelingNavn")
                .size()
                .reset_index(
                    name="Antal aktive indsatser"
                )
            )

            st.metric(
                label=(
                    "Antal aktive indsatser for "
                    f"{afdeling_filter}"
                ),
                value=afdeling_data[
                    "Antal aktive indsatser"
                ].sum(),
            )

            st.write(
                "## Antal af Aktive Indsatser pr. Afdeling"
            )

            afdeling_chart_data = (
                filtered_result
                .groupby("AfdelingNavn")
                .size()
                .reset_index(
                    name="Antal aktive indsatser"
                )
            )

            afdeling_chart = (
                alt.Chart(afdeling_chart_data)
                .mark_bar()
                .encode(
                    x=alt.X(
                        "Antal aktive indsatser",
                        title="Antal aktive indsatser",
                    ),
                    y=alt.Y(
                        "AfdelingNavn",
                        title="Afdeling",
                    ),
                    tooltip=[
                        alt.Tooltip(
                            "AfdelingNavn",
                            title="Afdeling",
                        ),
                        "Antal aktive indsatser",
                    ],
                )
                .properties(
                    width=600,
                    height=400,
                )
            )

            st.altair_chart(
                afdeling_chart,
                use_container_width=True,
            )

        elif content_tabs == "Leverandørnavn":
            leverandørnavn_filter = st.selectbox(
                "Vælg Leverandørnavn",
                options=filtered_result[
                    "LeverandørNavn"
                ].unique(),
                help=(
                    "Vælg den leverandør, du vil se data for."
                ),
            )

            leverandørnavn_data = (
                filtered_result[
                    filtered_result["LeverandørNavn"]
                    == leverandørnavn_filter
                ]
                .groupby(
                    [
                        "LeverandørNavn",
                        "IndsatsParagraf",
                    ]
                )
                .size()
                .reset_index(
                    name="Antal aktive indsatser"
                )
            )

            st.metric(
                label=(
                    "Antal aktive indsatser for "
                    f"{leverandørnavn_filter}"
                ),
                value=leverandørnavn_data[
                    "Antal aktive indsatser"
                ].sum(),
            )

            st.write(
                "## Antal af Aktive Indsatser pr. "
                f"Paragraf for {leverandørnavn_filter}"
            )

            leverandørnavn_chart = (
                alt.Chart(leverandørnavn_data)
                .mark_bar()
                .encode(
                    x=alt.X(
                        "Antal aktive indsatser",
                        title="Antal aktive indsatser",
                    ),
                    y=alt.Y(
                        "IndsatsParagraf",
                        title="IndsatsParagraf",
                    ),
                    tooltip=[
                        "IndsatsParagraf",
                        "Antal aktive indsatser",
                    ],
                )
                .properties(
                    width=600,
                    height=400,
                )
            )

            st.altair_chart(
                leverandørnavn_chart,
                use_container_width=True,
            )

        elif content_tabs == "LeverandørIndsats":
            filtered_result = filtered_result[
                filtered_result["LeverandørIndsats"]
                != "Auto-oprettet"
            ]

            leverandørindsats_filter = st.selectbox(
                "Vælg LeverandørIndsats",
                options=filtered_result[
                    "LeverandørIndsats"
                ].unique(),
                help=(
                    "Vælg den leverandørindsats, "
                    "du vil se data for."
                ),
            )

            leverandørindsats_data = (
                filtered_result[
                    filtered_result["LeverandørIndsats"]
                    == leverandørindsats_filter
                ]
                .groupby("LeverandørIndsats")
                .size()
                .reset_index(
                    name="Antal aktive indsatser"
                )
            )

            st.metric(
                label=(
                    "Antal aktive indsatser for "
                    f"{leverandørindsats_filter}"
                ),
                value=leverandørindsats_data[
                    "Antal aktive indsatser"
                ].sum(),
            )

            st.write(
                "## Antal af Aktive Indsatser pr. "
                "LeverandørIndsats"
            )

            leverandørindsats_chart_data = (
                filtered_result
                .groupby("LeverandørIndsats")
                .size()
                .reset_index(
                    name="Antal aktive indsatser"
                )
            )

            leverandørindsats_chart = (
                alt.Chart(leverandørindsats_chart_data)
                .mark_bar()
                .encode(
                    x=alt.X(
                        "Antal aktive indsatser",
                        title="Antal aktive indsatser",
                    ),
                    y=alt.Y(
                        "LeverandørIndsats",
                        title="LeverandørIndsats",
                    ),
                    tooltip=[
                        alt.Tooltip(
                            "LeverandørIndsats",
                            title="LeverandørIndsats",
                        ),
                        "Antal aktive indsatser",
                    ],
                )
                .properties(
                    width=600,
                    height=400,
                )
            )

            st.altair_chart(
                leverandørindsats_chart,
                use_container_width=True,
            )

    except Exception as error:
        st.error(f"An error occurred: {error}")

    finally:
        db_client.close_connection()
