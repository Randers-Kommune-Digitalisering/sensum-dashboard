import streamlit as st
import streamlit_antd_components as sac
import pandas as pd
import altair as alt
from utils.database_connection import get_db_client

db_client = get_db_client()


def get_ydelse():
    col_1 = st.columns([1])[0]

    with col_1:
        content_tabs = sac.tabs([
            sac.TabsItem('Periode', tag='Periode'),
        ], color='dark', size='md', position='top', align='start', use_container_width=True)

    try:
        if 'ydelse_final_result' not in st.session_state:
            results = []
            with st.spinner('Loading data...'):
                query = """
                SELECT "YdelseNavn", "AfdelingNavn", "StartDato", "SlutDato"
                FROM "Ydelse"
                """
                result = db_client.execute_sql(query)
                if result is not None:
                    results.append(pd.DataFrame(result, columns=['YdelseNavn', 'AfdelingNavn', 'StartDato', 'SlutDato']))
                else:
                    st.error("Failed to fetch data from the database.")
                    return

            if results:
                st.success("Data fetched successfully.")
                st.session_state.ydelse_final_result = pd.concat(results, ignore_index=True)
            else:
                st.error("No data to display.")
                return

        final_result = st.session_state.ydelse_final_result

        date_format = "%d-%m-%Y %H-%M"
        final_result['StartDato'] = pd.to_datetime(final_result['StartDato'], format=date_format)
        final_result['SlutDato'] = pd.to_datetime(final_result['SlutDato'], format=date_format)

        final_result['Year'] = final_result['StartDato'].dt.year
        final_result['Month'] = final_result['StartDato'].dt.month

        unique_years = final_result['Year'].unique()
        unique_years = unique_years[unique_years >= 2024]

        if content_tabs == 'Periode':
            col1, col2 = st.columns(2)
            with col1:
                selected_year_month = st.selectbox(
                    "Vælg et år",
                    unique_years,
                    format_func=lambda x: f'{x}',
                    index=unique_years.tolist().index(st.session_state['selected_year_month']) if 'selected_year_month' in st.session_state and st.session_state['selected_year_month'] is not None else 0,
                    key='year_select_month',
                    help="Vælg det år, for hvilket du vil se dataene."
                )
            with col2:
                filtered_result_year = final_result[final_result['Year'] == selected_year_month]
                unique_months = filtered_result_year['Month'].sort_values().unique()
                selected_month = st.selectbox('Vælg en måned', unique_months, help="Vælg den måned, for hvilken du vil se dataene.")

            month_data = filtered_result_year[filtered_result_year['Month'] == selected_month].groupby(['Month', 'YdelseNavn', 'AfdelingNavn']).size().reset_index(name='Antal ydelse')

            total_ydelse_month = month_data['Antal ydelse'].sum()
            st.metric(label="Samlet antal ydelse (Måned)", value=total_ydelse_month)

            st.write(f"## Antal af Ydelse (Måned) - {selected_year_month}, Måned {selected_month}")
            month_chart = alt.Chart(month_data).mark_bar().encode(
                x=alt.X('Antal ydelse', title='Antal ydelse'),
                y=alt.Y('YdelseNavn', title='YdelseNavn'),
                color='AfdelingNavn',
                tooltip=['YdelseNavn', 'Antal ydelse', 'AfdelingNavn']
            ).properties(
                width=600,
                height=400
            )

            st.altair_chart(month_chart, use_container_width=True)

    except Exception as e:
        st.error(f"An error occurred: {e}")
    finally:
        db_client.close_connection()
