import streamlit as st
import streamlit_antd_components as sac
import pandas as pd
import altair as alt
from utils.database_connection import get_db_client

db_client = get_db_client()


def get_indsatser_with_supplier():
    col_1 = st.columns([1])[0]

    with col_1:
        content_tabs = sac.tabs([
            sac.TabsItem('Afdeling', tag='Afdeling'),
            sac.TabsItem('Leverandørnavn', tag='Leverandørnavn'),
            sac.TabsItem('LeverandørIndsats', tag='LeverandørIndsats'),
        ], color='dark', size='md', position='top', align='start', use_container_width=True)

    try:
        if 'indsats_final_result' not in st.session_state:
            results = []
            with st.spinner('Loading data...'):
                query = '''
                SELECT "IndsatsStatus", "Indsats", "AfdelingNavn", "IndsatsStartDato", "IndsatsSlutDato", "LeverandørIndsats", "LeverandørNavn"
                FROM "Indsats_Fordeling"
                '''
                result = db_client.execute_sql(query)
                if result is not None:
                    results.append(pd.DataFrame(result, columns=['IndsatsStatus', 'Indsats', 'AfdelingNavn', 'IndsatsStartDato', 'IndsatsSlutDato', 'LeverandørIndsats', 'LeverandørNavn']))
                else:
                    st.error("Failed to fetch data from the database.")
                    return

            if results:
                st.success("Data fetched successfully.")
                st.session_state.indsats_final_result = pd.concat(results, ignore_index=True)
            else:
                st.error("No data to display.")
                return

        final_result = st.session_state.indsats_final_result

        final_result['IndsatsStartDato'] = pd.to_datetime(final_result['IndsatsStartDato'], dayfirst=True)
        final_result['IndsatsSlutDato'] = pd.to_datetime(final_result['IndsatsSlutDato'], dayfirst=True, errors='coerce')

        filtered_result = final_result[
            (final_result['IndsatsStatus'] == 'Godkendt') &
            (final_result['IndsatsSlutDato'].isna())
        ]

        if content_tabs == 'Afdeling':
            afdeling_filter = st.selectbox('Vælg Afdeling', options=filtered_result['AfdelingNavn'].unique(), help="Vælg den afdeling, du vil se data for.")
            afdeling_data = filtered_result[filtered_result['AfdelingNavn'] == afdeling_filter].groupby('AfdelingNavn').size().reset_index(name='Antal aktive indsatser')
            st.metric(label=f"Antal aktive indsatser for {afdeling_filter}", value=afdeling_data['Antal aktive indsatser'].sum())

            st.write("## Antal af Aktive Indsatser pr. Afdeling")
            afdeling_chart = alt.Chart(filtered_result.groupby('AfdelingNavn').size().reset_index(name='Antal aktive indsatser')).mark_bar().encode(
                x=alt.X('AfdelingNavn', title='Afdeling'),
                y=alt.Y('Antal aktive indsatser', title='Antal aktive indsatser'),
                tooltip=[alt.Tooltip('AfdelingNavn', title='Afdeling'), 'Antal aktive indsatser']
            ).properties(
                width=600,
                height=400
            )

            st.altair_chart(afdeling_chart, use_container_width=True)

        elif content_tabs == 'Leverandørnavn':
            leverandørnavn_filter = st.selectbox('Vælg Leverandørnavn', options=filtered_result['LeverandørNavn'].unique(), help="Vælg den leverandør, du vil se data for.")
            leverandørnavn_data = filtered_result[filtered_result['LeverandørNavn'] == leverandørnavn_filter].groupby('LeverandørNavn').size().reset_index(name='Antal aktive indsatser')

            st.metric(label=f"Antal aktive indsatser for {leverandørnavn_filter}", value=leverandørnavn_data['Antal aktive indsatser'].sum())

            st.write("## Antal af Aktive Indsatser pr. Leverandørnavn")
            leverandørnavn_chart = alt.Chart(filtered_result.groupby('LeverandørNavn').size().reset_index(name='Antal aktive indsatser')).mark_bar().encode(
                x=alt.X('LeverandørNavn', title='Leverandørnavn'),
                y=alt.Y('Antal aktive indsatser', title='Antal aktive indsatser'),
                tooltip=[alt.Tooltip('LeverandørNavn', title='Leverandørnavn'), 'Antal aktive indsatser']
            ).properties(
                width=600,
                height=400
            )

            st.altair_chart(leverandørnavn_chart, use_container_width=True)

        elif content_tabs == 'LeverandørIndsats':
            leverandørindsats_filter = st.selectbox('Vælg LeverandørIndsats', options=filtered_result['LeverandørIndsats'].unique(), help="Vælg den leverandørindsats, du vil se data for.")
            leverandørindsats_data = filtered_result[filtered_result['LeverandørIndsats'] == leverandørindsats_filter].groupby('LeverandørIndsats').size().reset_index(name='Antal aktive indsatser')

            st.metric(label=f"Antal aktive indsatser for {leverandørindsats_filter}", value=leverandørindsats_data['Antal aktive indsatser'].sum())

            st.write("## Antal af Aktive Indsatser pr. LeverandørIndsats")
            leverandørindsats_chart = alt.Chart(filtered_result.groupby('LeverandørIndsats').size().reset_index(name='Antal aktive indsatser')).mark_bar().encode(
                x=alt.X('LeverandørIndsats', title='LeverandørIndsats'),
                y=alt.Y('Antal aktive indsatser', title='Antal aktive indsatser'),
                tooltip=[alt.Tooltip('LeverandørIndsats', title='LeverandørIndsats'), 'Antal aktive indsatser']
            ).properties(
                width=600,
                height=400
            )

            st.altair_chart(leverandørindsats_chart, use_container_width=True)

    except Exception as e:
        st.error(f'An error occurred: {e}')
    finally:
        db_client.close_connection()
