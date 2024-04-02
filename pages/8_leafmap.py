import streamlit as st
from datetime import datetime
import numpy as np
import pandas as pd

import leafmap.foliumap as leafmap
# For the colour bar:
import branca
# Importing libraries
import folium
from folium.features import GeoJsonTooltip


from utilities_maps.fixed_params import page_setup


def draw_map_leafmap(
        lat_hospital, long_hospital, geojson_list,
        # region_list,
        df_placeholder, df_hospitals,
        # nearest_hospital_geojson_list, nearest_mt_hospital_geojson_list,
        choro_bins=6
        ):
    # Create a map
    clinic_map = leafmap.Map(
        location=[lat_hospital, long_hospital],
        zoom_start=9,
        tiles='cartodbpositron',
        # prefer_canvas=True,
        # Override how much people can zoom in or out:
        min_zoom=0,
        max_zoom=18,
        width=1200,
        height=600
        )

    outcome_min = 0
    outcome_max = 1
    choro_bins = np.linspace(outcome_min, outcome_max, 7)

    # Make a new discrete colour map:
    # (colour names have to be #000000 strings or names)
    colormap = branca.colormap.StepColormap(
        vmin=outcome_min,
        vmax=outcome_max,
        colors=["red", "orange", "LimeGreen", "green", "darkgreen", 'blue'],
        caption='Placeholder',
        index=choro_bins
    )
    colormap.add_to(clinic_map)
    # clinic_map.add_colormap(colormap)

    # Add choropleth
    for g, geojson_ew in enumerate(geojson_list):

        # style = {#lambda y:{
        #         # "fillColor": colormap(y["properties"]["Estimate_UN"]),
        #         # "fillColor": colormap(df_placeholder[df_placeholder['LSOA11NMW'] == y['properties']['LSOA11NMW']]['Placeholder'].iloc[0]),
        #         # "fillColor": colormap(df_placeholder[df_placeholder['LSOA11NMW'] == y['geometries']['properties']['LSOA11NMW']]['Placeholder'].iloc[0]),
        #         'fillColor': 'red',
        #         'stroke':'false',
        #         'fillOpacity': 0.5,
        #         'color':'black',  # line colour
        #         'weight':0.5,
        #         # 'dashArray': '5, 5'
        #     }

        # st.write(geojson_ew)

        # def style(y):
        #     # st.write(y)
        #     style_list=[]
        #     for x in y['features']:
        #         style_dict = {#lambda y:{
        #             # "fillColor": colormap(y["properties"]["Estimate_UN"]),
        #             "fillColor": colormap(
        #                 df_placeholder[
        #                     df_placeholder['LSOA11NMW'] == x['properties']['LSOA11NMW']
        #                     ]['Placeholder'].iloc[0]
        #                 ),
        #             # "fillColor": colormap(df_placeholder[df_placeholder['LSOA11NMW'] == y['geometries']['properties']['LSOA11NMW']]['Placeholder'].iloc[0]),
        #             # 'fillColor': 'red',
        #             'stroke':'false',
        #             'fillOpacity': 0.5,
        #             'color':'black',  # line colour
        #             'weight':0.5,
        #             # 'dashArray': '5, 5'
        #         }
        #         style_list.append(style_dict)
        #     # st.write(style_list)
        #     return style_list

        # st.write(geojson_ew)
        # colour_list = [
        #     colormap(
        #                 df_placeholder[
        #                     df_placeholder['LSOA11NMW'] == x['properties']['LSOA11NMW']
        #                     ]['Placeholder'].iloc[0]
        #                 )
        #     for x in geojson_ew['features']
        #     ]

        # ValueError: highlight_function should be a function that accepts items from data['features'] and returns a dictionary.

        # # fg.add_child(
        # clinic_map.add_geojson(
        folium.GeoJson(
            # in_geojson=geojson_ew,
            data=geojson_ew,
            tooltip=GeoJsonTooltip(
                fields=['LSOA11CD'],
                aliases=[''],
                localize=True
                ),
            # # lambda x:f"{x['properties']['LSOA11NMW']}",
            # # popup=popup,
            # name=region_list[g],
            # style=style(geojson_ew),
            style_function=lambda y: {  # style / style_function
                    # "fillColor": colormap(y["properties"]["Estimate_UN"]),
                    "fillColor": colormap(
                        df_placeholder[
                            df_placeholder['LSOA11CD'] == y['properties']['LSOA11CD']
                            ]['Placeholder'].iloc[0]
                        ),
                    # "fillColor": colormap(df_placeholder[df_placeholder['LSOA11NMW'] == y['geometries']['properties']['LSOA11NMW']]['Placeholder'].iloc[0]),
                    # 'fillColor': 'red',
                    # 'fillColor': colour_list,
                    # 'stroke':'false',
                    # 'fillOpacity': 0.5,
                    # 'color':'black',  # line colour
                    'weight': 0.1,
                    # 'dashArray': '5, 5'
                },
            highlight_function=lambda y: {'weight': 2.0},  # highlight_function / hover_dict
            # smooth_factor=1.5,  # 2.0 is about the upper limit here
            # show=False if g > 0 else True
            ).add_to(clinic_map)
        # ))
        # )

    # for g, geojson_ew in enumerate(geojson_list):
    #     clinic_map.add_data(
    #         data=geojson_ew
    #     )



    fg = folium.FeatureGroup(name='hospital_markers')
    # Add markers
    for (index, row) in df_hospitals.iterrows():
        # pop_up_text = f'{row.loc["Stroke Team"]}'

        # if last_object_clicked_tooltip == row.loc['Stroke Team']:
        #     icon = folium.Icon(
        #         # color='black',
        #         # icon_color='white',
        #         icon='star', #'fa-solid fa-hospital',#'info-sign',
        #         # angle=0,
        #         prefix='glyphicon')#, prefix='fa')
        # else:
        #     icon = None


        fg.add_child(
            folium.Marker(
            # clinic_map.add_marker(
                location=[row.loc['lat'], row.loc['long']],
                        # popup=pop_up_text,
                        tooltip=row.loc['Stroke Team']
            ))
                    # )#.add_to(clinic_map)

    fg.add_to(clinic_map)

    # folium.map.LayerControl().add_to(clinic_map)
    clinic_map.add_layer_control()
    # fg.add_child(folium.map.LayerControl())

    # Generate map
    hello = clinic_map.to_streamlit()
    # hello = clinic_map.show_in_browser()

    # with open('pickle_test.p', 'wb') as pickle_file:
    #     pickle.dump(hello, pickle_file)

    # st.write(type(hello))
    # st.write(hello)
    # clinic_map
    # output = st_folium(
    #     clinic_map,
    #     # feature_group_to_add=fg,
    #     returned_objects=[
    #         # 'bounds',
    #         # 'center',
    #         # "last_object_clicked", #_tooltip",
    #         # 'zoom'
    #     ],
    #     )
    # st.write(output)
    # st.stop()


# ###########################
# ##### START OF SCRIPT #####
# ###########################
page_setup()

# Title:
st.markdown('# Leafmap')


# Outcome type input:
outcome_type_str = st.radio(
    'Select the outcome measure',
    ['Added utility', 'Mean shift in mRS', 'mRS <= 2'],
    horizontal=True
)
# Match the input string to the file name string:
outcome_type_dict = {
    'Added utility': 'added~utility',
    'Mean shift in mRS': 'mean~shift',
    'mRS <= 2': 'mrs<=2'
}
outcome_type = outcome_type_dict[outcome_type_str]

startTime = datetime.now()

# Load data files
# Hospital info
df_hospitals = pd.read_csv("./data_maps/stroke_hospitals_22_reduced.csv")

# Select a hospital of interest
hospital_input = st.selectbox(
    'Pick a hospital',
    df_hospitals['Stroke Team']
)

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

# All hospital postcodes:
hospital_postcode_list = df_hospitals_regions['Postcode']

# travel times
# df_travel_times = pd.read_csv("./data_maps/clinic_travel_times.csv")
df_travel_matrix = pd.read_csv('./data_maps/lsoa_travel_time_matrix_calibrated.csv')
LSOA_names = df_travel_matrix['LSOA']
# st.write(len(LSOA_names), LSOA_names[:10])
placeholder = np.random.rand(len(LSOA_names))
table_placeholder = np.stack([LSOA_names, placeholder], axis=-1)
# st.write(table_placeholder)
df_placeholder = pd.DataFrame(
    data=table_placeholder,
    columns=['LSOA11NMW', 'Placeholder']
)
# st.write(df_placeholder)

# LSOA lat/long:

df_lsoa_regions = pd.read_csv('./data_maps/LSOA_regions.csv')

# # geojson_ew = import_geojson(group_hospital)

# region_list = [
#     'Devon',
#     'Dorset',
#     'Cornwall and the Isles of Scilly',
#     'Somerset'
# ]
# region_list = ['South West']

geojson_list = []
# nearest_hospital_geojson_list = []
# nearest_mt_hospital_geojson_list = []
# for region in region_list:
#     geojson_ew = import_geojson(region)
#     geojson_list.append(geojson_ew)

# # geojson_file = 'LSOA_South~West_t.geojson'


# # Make a list of the order of LSOA codes in the geojson that made the geotiff
# LSOA_names = []
# for i in geojson_ew['features']:
#     LSOA_names.append(i['properties']['LSOA11CD'])
# # st.write(LSOA_names)

# st.write(LSOA_names[])

# # st.write(len(LSOA_names), LSOA_names[:10])
# # LSOA_names = df_travel_matrix['LSOA']
# placeholder = np.random.rand(len(LSOA_names))
# table_placeholder = np.stack(np.array([LSOA_names, placeholder], dtype=object), axis=-1)
# # st.write(table_placeholder)
# df_placeholder = pd.DataFrame(
#     data=table_placeholder,
#     columns=['LSOA11CD', 'Placeholder']
# )

# st.write(df_placeholder)


# st.write(geojson_ew)

# # Copy the LSOA11CD code to features.id within geojson
# for i in geojson_ew['features']:
#     i['id'] = i['properties']['LSOA11NMW']

# for i in geojson_ew['objects']['LSOA_South~West']['geometries']:
#     i['id'] = i['properties']['LSOA11NMW']
# geojson_list = [geojson_ew]

# for hospital_postcode in hospital_postcode_list:
#     try:
#         nearest_hospital_geojson = import_hospital_geojson(hospital_postcode)
#         nearest_hospital_geojson_list.append(nearest_hospital_geojson)
#     except FileNotFoundError:
#         pass

#     try:
#         nearest_mt_hospital_geojson = import_hospital_geojson(hospital_postcode, MT=True)
#         nearest_mt_hospital_geojson_list.append(nearest_mt_hospital_geojson)
#     except FileNotFoundError:
#         pass

# st.write(geojson_ew['features'][0])

time4 = datetime.now()

with st.spinner(text='Drawing map'):
    draw_map_leafmap(
        lat_hospital, long_hospital, geojson_list,
        # region_list,
        df_placeholder, df_hospitals,
        # nearest_hospital_geojson_list,
        # nearest_mt_hospital_geojson_list,
        choro_bins=6
        )


time5 = datetime.now()
st.write('Time to draw map:', time5 - time4)
