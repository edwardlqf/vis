from collections import namedtuple
import altair as alt
import math
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
import calendar
import time

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


# #option for dropdown expander
# my_expander = st.beta_expander('Select Month and Sentiment Metric')
# with my_expander:
#     selected_month = st.slider("Month of the year", 1, 12, 1)
#     option = st.selectbox('Select Sentiment',
#                           ('valence_intensity','anger_intensity','fear_intensity','sadness_intensity','joy_intensity'))


c1, c2, c3 = st.beta_columns((3, 0.4, 3))

selected_month = c1.slider("Month of the year", 1, 12, 12, 1)

option = c3.selectbox('Select Sentiment',
                      ('Valence Intensity','Anger Intensity','Fear Intensity','Sadness Intensity','Joy Intensity'))


country_shapes = 'streamlit/world_countries.json'

#df = pd.read_csv ('clean-data/date_country_sentiment_cases_predictions.csv')
df = pd.read_csv ('clean-data/date_country_cases.csv')
df.dropna()
df['date'] = pd.to_datetime(df['date'])
filtered_df = df[df['date'].dt.month == selected_month]

filtered_df = (filtered_df.groupby('countries_and_territories', as_index=False)
       .agg({'cumulative_confirmed_cases_rate':'mean'}))


#data processing.
import json
json1_file = open(country_shapes)
json1_str = json1_file.read()
json1_data = json.loads(json1_str)

for i, name in enumerate(json1_data['features']):
    c = filtered_df.cumulative_confirmed_cases_rate[filtered_df['countries_and_territories'] == name['properties']['name']]
    if c.size != 0 :
        tooltip_text = name['properties']['name'] + ' ' + str(round(c.values[0],3))
        json1_data['features'][i]['properties']['tooltip1'] = tooltip_text


# with open('data.txt', 'w') as outfile:
#      json.dump(data, outfile)


c1.header('Cumulative cases rate for ' + calendar.month_name[selected_month] + ' 2020')
m = folium.Map(tiles='OpenStreetMap', min_zoom=1,  width='100%', height='80%', )
choropleth = folium.Choropleth(
            geo_data=json1_data,
            min_zoom=1,
            data=filtered_df,
            columns=['countries_and_territories','cumulative_confirmed_cases_rate'],
            key_on='feature.properties.name',
            fill_color='YlGn',
            nan_fill_color='grey',
            legend_name='Cumulative Confirmed Cases Rate',
            titles = 'map'
            ).add_to(m)

#tooptips

folium.LayerControl().add_to(m)
choropleth.geojson.add_child(
    folium.features.GeoJsonTooltip(['tooltip1'], labels=False)
)

with c1:
    folium_static(m)
c1.text('COVID data from: https://console.cloud.google.com/bigquery?project=covid-305420&supportedpurview=project&p=bigquery-public-data&page=table&d=covid19_ecdc&t=covid_19_geographic_distribution_worldwide')
c1.text('\n')




df = pd.read_csv ('clean-data/date_country_sentiment_cases_predictions.csv')
df.dropna()
df['date'] = pd.to_datetime(df['date'])
filtered_df = df[df['date'].dt.month == selected_month]

filtered_df2 = (filtered_df.groupby('country', as_index=False)
       .agg({option:'mean'}))

# for i, name in enumerate(json1_data['features']):
#     c = filtered_df2[option][filtered_df2['country'] == name['properties']['name']]
#     if c.size != 0 :
#         tooltip_text = name['properties']['name'] + ' ' + str(round(c.values[0],3))
#         json1_data['features'][i]['properties']['tooltip2'] = tooltip_text
#

c3.header(' '.join(option.split('_')) + ' for ' + calendar.month_name[selected_month] + ' 2020' )
m2 = folium.Map(tiles='OpenStreetMap', min_zoom=1,  width='100%', height='80%', )
choropleth2 = folium.Choropleth(
geo_data=json1_data,
min_zoom=1,
data=filtered_df2,
columns=['country', option],
key_on='feature.properties.name',
fill_color='BuPu',
nan_fill_color='grey',
legend_name=' '.join(option.split('_')),
titles = 'map'
).add_to(m2)

#tooptips

# folium.LayerControl().add_to(m2)
# choropleth2.geojson.add_child(
#     folium.features.GeoJsonTooltip(['tooltip2'], labels=False)
# )

with c3:
    folium_static(m2)

c3.text('Sentiment data from: https://www.openicpsr.org/openicpsr/project/120321/version/V6/view?path=/openicpsr/120321/fcr:versions/V6/Twitter-COVID-dataset---Jan-2021')
c3.text('\n')

daily_df = (filtered_df.groupby('date', as_index=False)
       .agg({'predicted_cumulative_confirmed_cases_rate':'mean',
             'upper_cumulative_confirmed_cases_rate':'mean',
             'lower_cumulative_confirmed_cases_rate':'mean',
             'cumulative_confirmed_cases_rate':'mean'})
       .rename(columns={'predicted_cumulative_confirmed_cases_rate':'Predicted',
                        'upper_cumulative_confirmed_cases_rate':'upper',
                        'lower_cumulative_confirmed_cases_rate':'lower',
                        'cumulative_confirmed_cases_rate':'Actual'}))

df_line = daily_df[['date','Predicted', 'Actual']].melt('date')
df_line.rename(columns={'variable': 'Line Chart'}, inplace=True)

st.header('Actual vs Predicted total COVID case rate for ' + calendar.month_name[selected_month] + ' 2020')

line = alt.Chart(df_line).mark_line().encode(
    x='date',
    y='value',
    color='Line Chart'
).properties(
    width=1000,
    height=300
)
band = alt.Chart(daily_df).mark_area(
    opacity=0.5
).encode(
    x='date',
    y=alt.Y('lower', title='Predicted rate with upper and lower CI'),
    y2='upper'
)

band + line