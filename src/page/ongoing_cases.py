import streamlit as st
import streamlit_antd_components as sac
import pandas as pd
import altair as alt
from utils.database_connection import get_db_client

db_client = get_db_client()


def get_ongoing_cases():
    col_1 = st.columns([1])[0]

    with col_1:
        content_tabs = sac.tabs([
            sac.TabsItem('Antal igangværende sager', tag='Antal igangværende sager'),
        ], color='dark', size='md', position='top', align='start', use_container_width=True)

    if content_tabs == 'Antal igangværende sager':
        try:
            if 'cases_final_result' not in st.session_state:
                results = []
                with st.spinner('Loading data...'):
                    query = """
                    SELECT SagNavn, SagType, MedarbejderFornavn, MedarbejderEfternavn, AfdelingNavn, Status
                    FROM SA_Tester
                    """
                    result = db_client.execute_sql(query)
                    if result is not None:
                        results.append(pd.DataFrame(result, columns=['SagNavn', 'SagType', 'MedarbejderFornavn', 'MedarbejderEfternavn', 'AfdelingNavn', 'Status']))
                    else:
                        st.error("Failed to fetch data from the database.")
                        return

                if results:
                    st.success("Data fetched successfully.")
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
