from collections import namedtuple
import altair as alt
import math
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
import calendar

st.set_page_config(layout = 'wide')

"""
# Welcome to Covid-19 dashboard!

"""



# #option for side bar in stead of drop down
# st.sidebar.markdown("## Select Month and Sentiment Metric")
#
# selected_month = st.sidebar.slider("Month of the year", 1, 12, 1)
# option = st.sidebar.selectbox('Select Sentiment',
#                       ('valence_intensity','anger_intensity','fear_intensity','sadness_intensity','joy_intensity'))
#


my_expander = st.beta_expander('Select Month and Sentiment Metric')
with my_expander:
    selected_month = st.slider("Month of the year", 1, 12, 1)
    option = st.selectbox('Select Sentiment',
                          ('valence_intensity','anger_intensity','fear_intensity','sadness_intensity','joy_intensity'))






c1, c2, c3 = st.beta_columns((3, 0.5, 3))


country_shapes = 'streamlit/world_countries.json'

df = pd.read_csv ('clean-data/date_country_sentiment_cases_predictions.csv')
df.dropna()
#st.dataframe(df)
df['date'] = pd.to_datetime(df['date'])

filtered_df = df[df['date'].dt.month == selected_month]
#st.dataframe(filtered_df)


c1.header('COVID-19 cumulative confirmed cases rate for ' + calendar.month_name[selected_month] + ' 2020')
m = folium.Map(tiles='OpenStreetMap', min_zoom=1.5,  width='80%', height='80%', )
folium.Choropleth(
geo_data=country_shapes,
min_zoom=1,
data=filtered_df,
columns=['country','cumulative_confirmed_cases_rate'],
key_on='feature.properties.name',
fill_color='YlOrRd',
nan_fill_color='grey',
legend_name='cumulative_confirmed_cases_rate',
titles = 'map'
).add_to(m)
with c1:
    folium_static(m)


c3.header(' '.join(option.split('_')) + ' for ' + calendar.month_name[selected_month] + ' 2020' )
m2 = folium.Map(tiles='OpenStreetMap', min_zoom=1.5,  width='80%', height='80%', )
folium.Choropleth(
geo_data=country_shapes,
min_zoom=1,
data=filtered_df,
columns=['country',option],
key_on='feature.properties.name',
fill_color='YlOrRd',
nan_fill_color='grey',
legend_name=' '.join(option.split('_')),
titles = 'map'
).add_to(m2)
with c3:
    folium_static(m2)

daily_df = (filtered_df.groupby('date', as_index=False)
       .agg({'predicted_cumulative_confirmed_cases_rate':'mean',
             'upper_cumulative_confirmed_cases_rate':'mean',
             'lower_cumulative_confirmed_cases_rate':'mean'})
       .rename(columns={'predicted_cumulative_confirmed_cases_rate':'predicted',
                        'upper_cumulative_confirmed_cases_rate':'upper',
                        'lower_cumulative_confirmed_cases_rate':'lower'}))

st.header('Predicted total COVID case rate for ' + calendar.month_name[selected_month] + ' 2020')
#line chart
line = alt.Chart(daily_df).mark_line().encode(
    x='date',
    y='predicted'
).properties(
    width=1000,
    height=300
)

band = alt.Chart(daily_df).mark_area(
    opacity=0.5
).encode(
    x='date',
    y='lower',
    y2='upper'
)

band + line