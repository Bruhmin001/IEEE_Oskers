import streamlit as st
import pandas as pd

df = pd.read_csv('Main.csv')
st.title('EarthWorm')

st.write("Select the changing conditions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    high_temp = st.checkbox('Change in Temperature')
    if high_temp:
        df['apparent_temperature_mean'] = df['apparent_temperature_mean'] + st.slider("Temp Change", min_value=-10, max_value=10, step=1)

with col2:
    low_rainfall = st.checkbox('Change in Rainfall')
    if low_rainfall:
        df['precipitation_sum'] = df['precipitation_sum'] + st.slider("Rainfall Change", min_value=-10, max_value=10, step=1)

with col3:
    high_wind = st.checkbox('Change in Wind Speed')
    if high_wind:
        df['wind_speed_10m_max'] = df['wind_speed_10m_max'] + st.slider("Wind Speed Change", min_value=-10, max_value=10, step=1)

with col4:
    low_soil_moisture = st.checkbox('Change in Soil Moisture')
    if low_soil_moisture:
        df['RICE IRRIGATED AREA (1000 ha)'] = df['RICE IRRIGATED AREA (1000 ha)'] + st.slider("Soil Moisture Change", min_value=-10, max_value=10, step=1)


st.write(df[['apparent_temperature_mean', 'precipitation_sum', 'wind_speed_10m_max', 'RICE IRRIGATED AREA (1000 ha)']])


