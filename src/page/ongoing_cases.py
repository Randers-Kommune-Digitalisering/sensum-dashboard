import streamlit as st
import streamlit_antd_components as sac
import pandas as pd
import altair as alt
from sensum.sensum import create_merge_lambda, process_sensum
from utils.api_requests import APIClient
from utils.config import CONFIG_LIBRARY_USER, CONFIG_LIBRARY_PASS, CONFIG_LIBRARY_URL

config_library_client = APIClient(base_url=CONFIG_LIBRARY_URL, username=CONFIG_LIBRARY_USER, password=CONFIG_LIBRARY_PASS)

sensum_jobs_config = [
    {
        "name": "SA_Tester.csv",
        "patterns": ["Sager_*.csv", "Afdeling_*.csv", "Medarbejder_*.csv"],
        "group_by": "SagId",
        "directories": ["sensum_randers"],
        "agg_columns": {
            "SagNavn": "first",
            "SagType": "first",
            "MedarbejderFornavn": "first",
            "MedarbejderEfternavn": "first",
            "AfdelingNavn": "first",
            "Status": "first"
        },
        "columns": [
            "SagNavn", "SagType",
            "MedarbejderFornavn", "MedarbejderEfternavn", "AfdelingNavn", "Status"
        ],
        "merge_func": "sager_afdeling_medarbejder_merge_df"
    }
]


def get_ongoing_cases():
    col_1 = st.columns([1])[0]

    with col_1:
        content_tabs = sac.tabs([
            sac.TabsItem('Antal igangværende sager', tag='Antal igangværende sager'),
        ], color='dark', size='md', position='top', align='start', use_container_width=True)

    if content_tabs == 'Antal igangværende sager':
        try:
            if 'cases_final_result' not in st.session_state:
                if sensum_jobs_config is None:
                    st.error("Failed to load configuration.")
                    return

                results = []
                with st.spinner('Loading data...'):
                    for config in sensum_jobs_config:
                        merge_lambda = create_merge_lambda(config)

                        result = process_sensum(
                            config['patterns'],
                            config['directories'],
                            merge_lambda,
                            config['name']
                        )
                        if result is not None:
                            results.append(result)
                        else:
                            st.error(f"Failed to process data for {config['name']}")
                            return

                if results:
                    st.success("Data processed successfully.")
                    st.session_state.cases_final_result = pd.concat(results, ignore_index=True)
                else:
                    st.error("No data to display.")
                    return

            final_result = st.session_state.cases_final_result

            sagstype_options = final_result['SagType'].unique()
            selected_sagstype = st.selectbox('Filter by Sagstype', sagstype_options)

            filtered_result = final_result[final_result['SagType'] == selected_sagstype]

            chart_data = filtered_result.groupby(['AfdelingNavn', 'MedarbejderFornavn', 'MedarbejderEfternavn']).size().reset_index(name='Antal igangværende sager')

            chart = alt.Chart(chart_data).mark_bar().encode(
                x=alt.X('AfdelingNavn', title='Afdeling Navn'),
                y=alt.Y('Antal igangværende sager', title='Antal igangværende sager'),
                color='MedarbejderFornavn',
                tooltip=['AfdelingNavn', 'MedarbejderFornavn', 'MedarbejderEfternavn', 'Antal igangværende sager']
            ).properties(
                width=600,
                height=400,
                title='Fordeling af igangværende sager på afdelinger og medarbejdere'
            )

            st.altair_chart(chart, use_container_width=True)
        except Exception as e:
            st.error(f'An error occurred: {e}')
