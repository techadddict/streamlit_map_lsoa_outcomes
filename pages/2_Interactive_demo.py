"""
Streamlit app template.

Because a long app quickly gets out of hand,
try to keep this document to mostly direct calls to streamlit to write
or display stuff. Use functions in other files to create and
organise the stuff to be shown. In this example, most of the work is
done in functions stored in files named container_(something).py
"""
# ----- Imports -----
import streamlit as st
from streamlit_folium import folium_static

# Importing libraries
import folium
from folium import plugins
import pandas as pd
import json

# Custom functions:
from utilities_maps.fixed_params import page_setup


# ###########################
# ##### START OF SCRIPT #####
# ###########################
page_setup()

# Title:
st.markdown('# Folium map test')

## Load data files
# travel times
df_travel_times = pd.read_csv("./data_maps/clinic_travel_times.csv")

# clinic info
df_clinics = pd.read_csv("./data_maps/clinic_locations.csv")

# lsoa geojson
with open('./data_maps/cornwall.geojson') as f:
    geojson_cornwall = json.load(f)

## Copy the LSOA11CD code to features.id within geojson
for i in geojson_cornwall['features']:
    i['id'] = i['properties']['LSOA11CD']

# Create a map
clinic_map = folium.Map(location=[50.435, -5.09426],
                        zoom_start=9,
                        tiles='cartodbpositron')
# Add markers
for (index, row) in df_clinics.iterrows():
    pop_up_text = f"The postcode for {row.loc['Name']} " + \
                    f"({row.loc['Clinic']}) is {row.loc['postcode']}"
    folium.Marker(location=[row.loc['lat'], row.loc['long']], 
                  popup=pop_up_text, 
                  tooltip=row.loc['Name']).add_to(clinic_map)
    
# Add choropleth
folium.Choropleth(geo_data=geojson_cornwall,
                  name='choropleth',
                  data=df_travel_times,
                  columns=['LSOA11CD', 'travel_time_mins'],
                  key_on='feature.id',
                  fill_color='OrRd',
                  fill_opacity=0.5,
                  line_opacity=0.5,
                  legend_name='travel_time_mins',
                  highlight=True).add_to(clinic_map)

# Generate map
# clinic_map
folium_static(clinic_map)



# ----- The end! -----
