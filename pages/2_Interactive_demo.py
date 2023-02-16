"""
Streamlit app template.

Because a long app quickly gets out of hand,
try to keep this document to mostly direct calls to streamlit to write
or display stuff. Use functions in other files to create and
organise the stuff to be shown. In this example, most of the work is
done in functions stored in files named container_(something).py

This folium code is directly copied from Elliot's HSMA exercise
https://github.com/hsma5/5b_geospatial_problems/blob/main/exercise/5B_Folium_map_Group-SOLUTION.ipynb
"""
# ----- Imports -----
import streamlit as st
from streamlit_folium import st_folium

# Importing libraries
import folium
from folium import plugins
import pandas as pd
import json
import numpy as np

# Custom functions:
from utilities_maps.fixed_params import page_setup


# ###########################
# ##### START OF SCRIPT #####
# ###########################
page_setup()

# Title:
st.markdown('# Folium map test')

try:
    last_object_clicked_tooltip = st.session_state['last_object_clicked_tooltip']
except KeyError:
    last_object_clicked_tooltip = ''


## Load data files
# Hospital info
df_hospitals = pd.read_csv("./data_maps/stroke_hospitals_2022.csv")

# Select a hospital of interest
hospital_input = st.selectbox(
    'Pick a hospital',
    df_hospitals['Stroke Team']
)
st.write(hospital_input)

# Find which region this hospital is in:
df_hospitals_regions = pd.read_csv("./data_maps/hospitals_and_lsoas.csv")
df_hospital_regions = df_hospitals_regions[df_hospitals_regions['Stroke Team'] == hospital_input]

long_hospital = df_hospital_regions['long'].iloc[0]
lat_hospital = df_hospital_regions['lat'].iloc[0]
region_hospital = df_hospital_regions['RGN11NM'].iloc[0]
if region_hospital == 'Wales':
    group_hospital = df_hospital_regions['LHB20NM'].iloc[0]
else:
    group_hospital = df_hospital_regions['STP19NM'].iloc[0]

# travel times
# df_travel_times = pd.read_csv("./data_maps/clinic_travel_times.csv")
df_travel_matrix = pd.read_csv('./data_maps/lsoa_travel_time_matrix_calibrated.csv')
LSOA_names = df_travel_matrix['LSOA']
placeholder = np.random.rand(len(LSOA_names))
table_placeholder = np.stack([LSOA_names, placeholder], axis=-1)
# st.write(table_placeholder)
df_placeholder = pd.DataFrame(
    data=table_placeholder,
    columns=['LSOA11NMW', 'Placeholder']
)

# Choose which geojson to open:
geojson_file = 'LSOA_' + group_hospital.replace(' ', '~') + '.geojson'

# lsoa geojson
with open('./data_maps/region_geojson/' + geojson_file) as f:
    geojson_ew = json.load(f)

## Copy the LSOA11CD code to features.id within geojson
for i in geojson_ew['features']:
    i['id'] = i['properties']['LSOA11NMW']

# st.write(geojson_ew['features'][0])

# st.stop()

# Find which LSOAs are within some travel time of this hospital
travel_time_max = 120
# Get the postcode of this hospital
postcode_for_hospital_input = df_hospitals['Postcode'][df_hospitals['Stroke Team'] == hospital_input].iloc[0]
# Import the travel time matrix:
# (above)
# Only pick out the LSOA names and travel times to chosen hospital:
df_travel_time_for_hospital_input = df_travel_matrix.filter(items=['LSOA', postcode_for_hospital_input])
# Only keep LSOAs with travel times below the max:
df_travel_time_for_hospital_input = df_travel_time_for_hospital_input[df_travel_time_for_hospital_input[postcode_for_hospital_input] <= travel_time_max]

# Now reduce the contents of the geojson to just these nearby LSOAs:

# Create a map
clinic_map = folium.Map(location=[lat_hospital, long_hospital],
                        zoom_start=9,
                        tiles='cartodbpositron',
                        # Override how much people can zoom in or out:
                        min_zoom=0,
                        max_zoom=18
                        )
# # Add markers
# for (index, row) in df_clinics.iterrows():
#     pop_up_text = f"The postcode for {row.loc['Name']} " + \
#                     f"({row.loc['Clinic']}) is {row.loc['postcode']}"
#     folium.Marker(location=[row.loc['lat'], row.loc['long']], 
#                   popup=pop_up_text, 
#                   tooltip=row.loc['Name']).add_to(clinic_map)
# folium.features.GeoJsonTooltip(['travel_time_mins'])
# Add choropleth
folium.Choropleth(geo_data=geojson_ew,
                  name='choropleth',
                  data=df_placeholder,
                  columns=['LSOA11NMW', 'Placeholder'],
                  key_on='feature.id',
                  fill_color='OrRd',
                  fill_opacity=0.5,
                  line_opacity=0.5,
                  legend_name='Placeholder',
                  highlight=True,
                #   tooltip='travel_time_mins',
                #   smooth_factor=1.0
                  ).add_to(clinic_map)

# fg = folium.FeatureGroup(name="test")

# Add markers
for (index, row) in df_hospitals.iterrows():
    pop_up_text = f'{row.loc["Stroke Team"]}'

    if last_object_clicked_tooltip == row.loc['Stroke Team']:
        icon = folium.Icon(
            # color='black',
            # icon_color='white',
            icon='star', #'fa-solid fa-hospital',#'info-sign',
            # angle=0,
            prefix='glyphicon')#, prefix='fa')
    else:
        icon = None

    folium.Marker(location=[row.loc['lat'], row.loc['long']], 
                  popup=pop_up_text, 
                  tooltip=row.loc['Stroke Team']).add_to(clinic_map)
    # folium.Circle(
    #     radius=100, # metres
    #     location=[row.loc['lat'], row.loc['long']],
    #     popup=pop_up_text,
    #     color='black',
    #     tooltip=row.loc['Stroke Team'],
    #     fill=False,
    #     weight=1
    # ).add_to(clinic_map)
    # fg.add_child(
    #     folium.Marker(location=[row.loc['lat'], row.loc['long']], 
    #               popup=pop_up_text, 
    #               tooltip=row.loc['Name'],
    #               icon=icon
    #               )
    # )

# # Add choropleth
# fg.add_child(
#     folium.Choropleth(geo_data=geojson_cornwall,
#                     name='choropleth',
#                     data=df_travel_times,
#                     columns=['LSOA11CD', 'travel_time_mins'],
#                     key_on='feature.id',
#                     fill_color='OrRd',
#                     fill_opacity=0.5,
#                     line_opacity=0.5,
#                     legend_name='travel_time_mins',
#                     highlight=True
#                     )
#                     )#.add_to(clinic_map)


# Generate map
# clinic_map
output = st_folium(
    clinic_map,
    # feature_group_to_add=fg,
    returned_objects=[]#"last_object_clicked_tooltip"]
    )

# st.session_state['last_object_clicked_tooltip'] = output['last_object_clicked_tooltip']

# {
# "last_clicked":NULL
# "last_object_clicked":NULL
# "last_object_clicked_tooltip":NULL
# "all_drawings":NULL
# "last_active_drawing":NULL
# "bounds":{
#     "_southWest":{
#     "lat":39.94384773921137
#     "lng":-75.15805006027223
#     }
# "_northEast":{
#     "lat":39.9553624980935
#     "lng":-75.14249324798585
#     }
#     }
# "zoom":16
# "last_circle_radius":NULL
# "last_circle_polygon":NULL
# "center":{
# "lat":39.94961
# "lng":-75.150282
# }
# }

st.write(output)


# ----- The end! -----
