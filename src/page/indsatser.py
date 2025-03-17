import streamlit as st
import streamlit_antd_components as sac
import pandas as pd
import altair as alt
from utils.database_connection import get_db_client

db_client = get_db_client()

weekday = {
    'Monday': 'Mandag',
    'Tuesday': 'Tirsdag',
    'Wednesday': 'Onsdag',
    'Thursday': 'Torsdag',
    'Friday': 'Fredag',
    'Saturday': 'Lørdag',
    'Sunday': 'Søndag'
}


def get_indsatser():
    col_1 = st.columns([1])[0]

    with col_1:
        content_tabs = sac.tabs([
            sac.TabsItem('Uge', tag='Uge'),
            sac.TabsItem('Måned', tag='Måned'),
        ], color='dark', size='md', position='top', align='start', use_container_width=True)

    try:
        if 'indsatser_final_result' not in st.session_state:
            results = []
            with st.spinner('Loading data...'):
                query = """
                SELECT "IndsatsStartDato", "IndsatsStatus", "IndsatsSlutDato"
                FROM "Aktive_Indsatser"
                """
                result = db_client.execute_sql(query)
                if result is not None:
                    results.append(pd.DataFrame(result, columns=['IndsatsStartDato', 'IndsatsStatus', 'IndsatsSlutDato']))
                else:
                    st.error("Failed to fetch data from the database.")
                    return

            if results:
                st.success("Data fetched successfully.")
                st.session_state.indsatser_final_result = pd.concat(results, ignore_index=True)
            else:
                st.error("No data to display.")
                return

        final_result = st.session_state.indsatser_final_result

        final_result['IndsatsStartDato'] = pd.to_datetime(final_result['IndsatsStartDato'], dayfirst=True)
        final_result['IndsatsSlutDato'] = pd.to_datetime(final_result['IndsatsSlutDato'], dayfirst=True, errors='coerce')

        filtered_result = final_result[
            (final_result['IndsatsStatus'] == 'Godkendt') &
            ((final_result['IndsatsSlutDato'].isna()) | (final_result['IndsatsSlutDato'] >= pd.Timestamp.now()))
        ]

        total_active_indsatser = filtered_result.shape[0]
        st.metric(label="Samlet antal aktive indsatser (Alle)", value=total_active_indsatser)

        filtered_result['Year'] = filtered_result['IndsatsStartDato'].dt.year

        unique_years = sorted(filtered_result['Year'].unique(), reverse=True)

        if content_tabs == 'Uge':
            filtered_result['Week'] = filtered_result['IndsatsStartDato'].dt.isocalendar().week
            filtered_result['Weekday'] = filtered_result['IndsatsStartDato'].dt.day_name().map(weekday)

            col1, col2 = st.columns(2)
            with col1:
                selected_year_week = st.selectbox(
                    "Vælg et år",
                    unique_years,
                    format_func=lambda x: f'{x}',
                    index=unique_years.tolist().index(st.session_state['selected_year_week']) if 'selected_year_week' in st.session_state and st.session_state['selected_year_week'] is not None else 0,
                    key='year_select_week'
                )
            with col2:
                filtered_result_year = filtered_result[filtered_result['Year'] == selected_year_week]
                unique_weeks = filtered_result_year['Week'].sort_values().unique()
                selected_week = st.selectbox('Vælg en uge', unique_weeks)

            week_data = filtered_result_year[filtered_result_year['Week'] == selected_week].groupby(['Week', 'Weekday']).size().reset_index(name='Antal aktive indsatser')

            total_active_indsatser_week = week_data['Antal aktive indsatser'].sum()
            st.metric(label="Samlet antal aktive indsatser (Uge)", value=total_active_indsatser_week)

            st.write(f"## Antal af Aktive Indsatser (Uge) - {selected_year_week}, Uge {selected_week}")
            week_chart = alt.Chart(week_data).mark_bar().encode(
                x=alt.X('Weekday', title='Ugedag', sort=['Mandag', 'Tirsdag', 'Onsdag', 'Torsdag', 'Fredag', 'Lørdag', 'Søndag']),
                y=alt.Y('Antal aktive indsatser', title='Antal aktive indsatser'),
                tooltip=[alt.Tooltip('Weekday', title='Ugedag'), 'Antal aktive indsatser']
            ).properties(
                width=600,
                height=400
            )

            st.altair_chart(week_chart, use_container_width=True)

        elif content_tabs == 'Måned':
            filtered_result['Month'] = filtered_result['IndsatsStartDato'].dt.month
            filtered_result['Månedsdag'] = filtered_result['IndsatsStartDato'].dt.day.astype(int)

            col1, col2 = st.columns(2)
            with col1:
                selected_year_month = st.selectbox(
                    "Vælg et år",
                    unique_years,
                    format_func=lambda x: f'{x}',
                    index=unique_years.tolist().index(st.session_state['selected_year_month']) if 'selected_year_month' in st.session_state and st.session_state['selected_year_month'] is not None else 0,
                    key='year_select_month'
                )
            with col2:
                filtered_result_year = filtered_result[filtered_result['Year'] == selected_year_month]
                unique_months = filtered_result_year['Month'].sort_values().unique()
                selected_month = st.selectbox('Vælg en måned', unique_months)

            month_data = filtered_result_year[filtered_result_year['Month'] == selected_month].groupby(['Month', 'Månedsdag']).size().reset_index(name='Antal aktive indsatser')

            total_active_indsatser_month = month_data['Antal aktive indsatser'].sum()
            st.metric(label="Samlet antal aktive indsatser (Måned)", value=total_active_indsatser_month)

            st.write(f"## Antal af Aktive Indsatser (Måned) - {selected_year_month}, Måned {selected_month}")
            month_chart = alt.Chart(month_data).mark_bar().encode(
                x=alt.X('Månedsdag:O', title='Månedsdag', axis=alt.Axis(format='d')),
                y=alt.Y('Antal aktive indsatser:Q', title='Antal aktive indsatser'),
                tooltip=[alt.Tooltip('Månedsdag:O', title='Månedsdag'), alt.Tooltip('Antal aktive indsatser:Q', title='Antal aktive indsatser')]
            ).properties(
                width=600,
                height=400
            )

            st.altair_chart(month_chart, use_container_width=True)

    except Exception as e:
        st.error(f'An error occurred: {e}')
    finally:
        db_client.close_connection()
