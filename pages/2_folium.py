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
from folium.features import GeoJsonPopup, GeoJsonTooltip
import pandas as pd
import json
import numpy as np
# import pickle
# import cPickle
# For the colour bar:
import branca
from geojson_rewind import rewind

# Custom functions:
from utilities_maps.fixed_params import page_setup

from datetime import datetime


# def import_geojson(group_hospital):
#     # Choose which geojson to open:
#     geojson_file = 'LSOA_' + group_hospital.replace(' ', '~') + '.geojson'
#     # geojson_file = './old/LSOA_2011.geojson'
#     # geojson_file = 'LSOA_(Dec_2011)_Boundaries_Super_Generalised_Clipped_(BSC)_EW_V3.geojson'

#     # lsoa geojson
#     # with open('./data_maps/lhb_scn_geojson/' + geojson_file) as f:
#     with open('./data_maps/lhb_stp_geojson/' + geojson_file) as f:
#         geojson_ew = json.load(f)

#     ## Copy the LSOA11CD code to features.id within geojson
#     for i in geojson_ew['features']:
#         i['id'] = i['properties']['LSOA11NMW']
#     return geojson_ew



def import_hospital_geojson(hospital_postcode, MT=False):
    # Choose which geojson to open:
    geojson_file = 'lsoa_nearest_'
    if MT is True:
        geojson_file += 'MT_'
    else:
        geojson_file += 'to_'
    geojson_file += hospital_postcode
    geojson_file += '.geojson'

    # geojson_file = './old/LSOA_2011.geojson'
    # geojson_file = 'LSOA_(Dec_2011)_Boundaries_Super_Generalised_Clipped_(BSC)_EW_V3.geojson'

    # lsoa geojson
    # with open('./data_maps/lhb_scn_geojson/' + geojson_file) as f:
    with open('./data_maps/lsoa_nearest_hospital/' + geojson_file) as f:
        geojson_ew = json.load(f)

    # ## Copy the LSOA11CD code to features.id within geojson
    # for i in geojson_ew['features']:
    #     i['id'] = i['properties']['LSOA11NMW']
    return geojson_ew


def import_geojson(geojson_file=''):
    if len(geojson_file) < 1:
        geojson_file = 'LSOA_(Dec_2011)_Boundaries_Super_Generalised_Clipped_(BSC)_EW_V3_reduced3.geojson'
    with open('./data_maps/' + geojson_file) as f:
        geojson_ew = json.load(f)
    return geojson_ew


def draw_map(
        lat_hospital, long_hospital, geojson_list, region_list,
        df_placeholder, df_hospitals,
        # nearest_hospital_geojson_list, nearest_mt_hospital_geojson_list,
        choro_bins=6
        ):
    # Create a map
    clinic_map = folium.Map(location=[lat_hospital, long_hospital],
                            zoom_start=9,
                            tiles='cartodbpositron',
                            # prefer_canvas=True,
                            # Override how much people can zoom in or out:
                            min_zoom=0,
                            max_zoom=18,
                            width=1200,
                            height=600
                            )

    # # Add markers
    # for (index, row) in df_clinics.iterrows():
    #     pop_up_text = f"The postcode for {row.loc['Name']} " + \
    #                     f"({row.loc['Clinic']}) is {row.loc['postcode']}"
    #     folium.Marker(location=[row.loc['lat'], row.loc['long']], 
    #                   popup=pop_up_text, 
    #                   tooltip=row.loc['Name']).add_to(clinic_map)
    # folium.features.GeoJsonTooltip(['travel_time_mins'])

    outcome_min = 0
    outcome_max = 1
    choro_bins = np.linspace(outcome_min, outcome_max, 7)

    # Make a new discrete colour map:
    # (colour names have to be #000000 strings or names)
    colormap = branca.colormap.StepColormap(
        vmin=outcome_min,
        vmax=outcome_max,
        colors=["red", "orange", "lightblue", "green", "darkgreen", 'blue'],
        caption='Placeholder',
        index=choro_bins
    )
    colormap.add_to(clinic_map)
    # fg.add_child(colormap)  # doesn't work


    # fg = folium.FeatureGroup(name="test")
    
    # Add choropleth
    for g, geojson_ew in enumerate(geojson_list):
        # a = folium.Choropleth(geo_data=geojson_ew,
        #                 name=region_list[g], # f'choropleth_{g}',
        #                 bins=choro_bins,
        #                 data=df_placeholder,
        #                 columns=['LSOA11NMW', 'Placeholder'],
        #                 key_on='feature.id',
        #                 fill_color='OrRd',
        #                 fill_opacity=0.5,
        #                 line_opacity=0.5,
        #                 legend_name='Placeholder',
        #                 highlight=True,
        #                 #   tooltip='travel_time_mins',
        #                 smooth_factor=1.5,
        #                 show=False if g > 0 else True
        #                 ).add_to(clinic_map)
        # st.write(g)
        # st.write(a)
        # st.write(' ')



        # # fg.add_child(
        folium.GeoJson(
            data=geojson_ew,
            tooltip=GeoJsonTooltip(
                fields=['LSOA11NMW'],
                aliases=[''],
                localize=True
                ),
            # lambda x:f"{x['properties']['LSOA11NMW']}",
            # popup=popup,
            name=region_list[g],
            style_function= lambda y:{
                # "fillColor": colormap(y["properties"]["Estimate_UN"]),
                "fillColor": colormap(df_placeholder[df_placeholder['LSOA11NMW'] == y['properties']['LSOA11NMW']]['Placeholder'].iloc[0]),
                # "fillColor": colormap(df_placeholder[df_placeholder['LSOA11NMW'] == y['geometries']['properties']['LSOA11NMW']]['Placeholder'].iloc[0]),
                'stroke':'false',
                'opacity': 0.5,
                'color':'black',  # line colour
                'weight':0.5,
                # 'dashArray': '5, 5'
            },
            highlight_function=lambda x: {'weight': 2.0},
            smooth_factor=1.5,  # 2.0 is about the upper limit here
            show=False if g > 0 else True
            ).add_to(clinic_map)
        # ))

        # folium.TopoJson(
        #     data=geojson_ew,
        #     # tooltip=GeoJsonTooltip(
        #     #     fields=['LSOA11NMW'],
        #     #     aliases=[''],
        #     #     localize=True
        #     #     ),
        #     # lambda x:f"{x['properties']['LSOA11NMW']}",
        #     # popup=popup,
        #     # name=region_list[g],
        #     object_path='LSOA_South~West',
        #     # style_function= lambda y:{
        #     #     # "fillColor": colormap(y["properties"]["Estimate_UN"]),
        #     #     # "fillColor": colormap(df_placeholder[df_placeholder['LSOA11NMW'] == y['properties']['LSOA11NMW']]['Placeholder'].iloc[0]),
        #     #     "fillColor": colormap(df_placeholder[df_placeholder['LSOA11NMW'] == y['geometries']['properties']['LSOA11NMW']]['Placeholder'].iloc[0]),
        #     #     'stroke':'false',
        #     #     'opacity': 0.5,
        #     #     'color':'black',  # line colour
        #     #     'weight':0.5,
        #     #     # 'dashArray': '5, 5'
        #     # },
        #     # highlight_function=lambda x: {'weight': 2.0},
        #     # smooth_factor=1.5,  # 2.0 is about the upper limit here
        #     # show=False if g > 0 else True
        #     ).add_to(clinic_map)

    # import matplotlib.colors
    # colours = list(matplotlib.colors.cnames.values())
    # # st.write(colours)
    # for g, geojson_ew in enumerate(nearest_hospital_geojson_list):
    #     colour_here = colours[g]


    #     # fg.add_child(
    #     folium.GeoJson(
    #         data=geojson_ew,
    #         # tooltip=GeoJsonTooltip(
    #         #     fields=['LSOA11NMW'],
    #         #     aliases=[''],
    #         #     localize=True
    #         #     ),
    #         # lambda x:f"{x['properties']['LSOA11NMW']}",
    #         # popup=popup,
    #         name='placeholder_'+str(g), #region_list[g],
    #         style_function= lambda y:{
    #             # "fillColor": , #f'{colour_here}',# 'rgba(0, 0, 0, 0)',
    #             'stroke':'false',
    #             'opacity': 0.5,
    #             'color':'black',  # line colour
    #             'weight': 3,
    #             'dashArray': '5, 5'
    #         },
    #         # highlight_function=lambda x: {'fillOpacity': 0.8},
    #         smooth_factor=1.5,  # 2.0 is about the upper limit here
    #         show=True, # if g > 0 else True
    #         overlay=False
    #     # ))
    #         ).add_to(clinic_map)


    # Problem - no way to set colour scale max and min,
    # get a new colour scale for each choropleth.


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
        icon = None


        # fg.add_child(
        folium.Marker(location=[row.loc['lat'], row.loc['long']], 
                    # popup=pop_up_text, 
                    tooltip=row.loc['Stroke Team']
        # ))
                    ).add_to(clinic_map)
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


    # # This works for starting the map in this area
    # # with the max zoom possible.
    # folium.map.FitBounds(
    #     bounds=[(50, -4), (51, -3)],
    #     padding_top_left=None,
    #     padding_bottom_right=None,
    #     padding=None,
    #     max_zoom=None
    #     ).add_to(clinic_map)

    folium.map.LayerControl().add_to(clinic_map)
    # fg.add_child(folium.map.LayerControl())

    # Generate map
    # clinic_map
    output = st_folium(
        clinic_map,
        # feature_group_to_add=fg,
        returned_objects=[
            # 'bounds',
            # 'center',
            # "last_object_clicked", #_tooltip",
            # 'zoom'
        ],
        )
    st.write(output)
    # st.stop()





def draw_map_circles(lat_hospital, long_hospital, df_placeholder, df_hospitals, df_lsoa_regions):
    # Create a map
    # import leafmap.foliumap as leafmap

    # clinic_map = leafmap.Map(
    clinic_map = folium.Map(
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
        colors=["red", "orange", "lightblue", "green", "darkgreen", 'blue'],
        caption='Placeholder',
        index=choro_bins
    )
    colormap.add_to(clinic_map)
    # fg.add_child(colormap)  # doesn't work

    # Add markers
    for (index, row) in df_hospitals.iterrows():
        # pop_up_text = f'{row.loc["Stroke Team"]}'

        if last_object_clicked_tooltip == row.loc['Stroke Team']:
            icon = folium.Icon(
                # color='black',
                # icon_color='white',
                icon='star', #'fa-solid fa-hospital',#'info-sign',
                # angle=0,
                prefix='glyphicon')#, prefix='fa')
        else:
            icon = None


        # fg.add_child(
        folium.Marker(location=[row.loc['lat'], row.loc['long']], 
                    # popup=pop_up_text, 
                    tooltip=row.loc['Stroke Team']
        # ))
                    ).add_to(clinic_map)

    marker_list = []
    for i, row in df_lsoa_regions.iterrows():
        # # folium.Circle(
        # # folium.PolyLine(
        #     # radius=100, # metres
        #     locations=[[row.loc['LSOA11LAT'], row.loc['LSOA11LONG']]],
        #     # popup=pop_up_text,
        #     color='black',
        #     tooltip=row.loc['LSOA11NM'],
        #     fill=True,
        #     weight=1
        # ).add_to(clinic_map)
        # pass
        marker_list.append(
        folium.Marker(
            [row.loc['LSOA11LAT'], row.loc['LSOA11LONG']],
        ))#.add_to(clinic_map)

    marker_list.add_to(clinic_map)

    # folium.plugins.FastMarkerCluster(
    #     np.transpose([df_lsoa_regions['LSOA11LAT'], df_lsoa_regions['LSOA11LONG']]),
    # ).add_to(clinic_map)

    # folium.plugins.HeatMap(
    #     np.transpose([df_lsoa_regions['LSOA11LAT'], df_lsoa_regions['LSOA11LONG']]),
    # ).add_to(clinic_map)

    folium.map.LayerControl().add_to(clinic_map)

    # Generate map
    output = st_folium(
        clinic_map,
        returned_objects=[
        ],
        )
    st.write(output)



# ###########################
# ##### START OF SCRIPT #####
# ###########################
page_setup()

# Title:
st.markdown('# Outcome maps')


startTime = datetime.now()


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



## Load data files
# Hospital info
df_hospitals = pd.read_csv("./data_maps/stroke_hospitals_22_reduced.csv")

df_outcomes = pd.read_csv("./data_maps/lsoa_base.csv")

df_outcomes = df_outcomes.round(3)
# df_outcomes['drip_ship_lvo_mt_added_utility'] = round(df_outcomes['drip_ship_lvo_mt_added_utility'], 3)
# df_outcomes['mothership_lvo_mt_added_utility'] = round(df_outcomes['mothership_lvo_mt_added_utility'], 3)
df_outcomes['diff_lvo_mt_added_utility'] = (
    df_outcomes['mothership_lvo_mt_added_utility'] -
    df_outcomes['drip_ship_lvo_mt_added_utility']
)
df_outcomes['diff_lvo_ivt_added_utility'] = (
    df_outcomes['mothership_lvo_ivt_added_utility'] -
    df_outcomes['drip_ship_lvo_ivt_added_utility']
)
df_outcomes['diff_nlvo_ivt_added_utility'] = (
    df_outcomes['mothership_nlvo_ivt_added_utility'] -
    df_outcomes['drip_ship_nlvo_ivt_added_utility']
)

# geojson_ew = import_geojson('LSOA_outcomes.geojson')
# geojson_ew = import_geojson('LSOA_(Dec_2011)_Boundaries_Super_Generalised_Clipped_(BSC)_EW_V3_reduced4.geojson')

geojson_ew = import_geojson('LSOA_(Dec_2011)_Boundaries_Super_Generalised_Clipped_(BSC)_EW_V3_reduced4_simplified.geojson')

# Sort out any problem polygons with coordinates in wrong order:
geojson_ew = rewind(geojson_ew, rfc7946=False)

# geojson_ew = import_geojson('LSOA_(Dec_2011)_Boundaries_Super_Generalised_Clipped_(BSC)_EW_V3_reduced4(3).geojson')
# geojson_ew = import_geojson('LSOA_(Dec_2011)_Boundaries_Super_Generalised_Clipped_(BSC)_EW_V3_mapshaper.geojson')
# geojson_ew = import_geojson('/lhb_scn_geojson/LSOA_South~West.geojson')


for feature in geojson_ew['features']:
    # if 'Wrexham' in feature['properties']['LSOA11NM']:
    #     st.write(feature)

    if feature['type'] != 'Feature':
        st.write(feature)
    try:
        a = feature['geometry']
        if a['type'] not in ['Polygon', 'MultiPolygon']:
            st.write(feature)
        if len(a['coordinates']) < 1:
            st.write(feature)
    except:
        st.write('PROBLEM: ', feature)




## Load data files
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

# # All hospital postcodes:
# hospital_postcode_list = df_hospitals_regions['Postcode']

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

region_list = [
    'Devon',
    'Dorset',
    'Cornwall and the Isles of Scilly',
    'Somerset'
]
# region_list = ['South West']

geojson_list = []
nearest_hospital_geojson_list = []
nearest_mt_hospital_geojson_list = []
for region in region_list:
    r = region.replace(' ', '~')
    f = f'lhb_stp_geojson/LSOA_{r}.geojson'
    geojson_ew = import_geojson(f)
    geojson_list.append(geojson_ew)

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

draw_map(
        lat_hospital, long_hospital,
        geojson_list,
        region_list,
        df_placeholder, df_hospitals,
        # nearest_hospital_geojson_list, nearest_mt_hospital_geojson_list,
        choro_bins=6
        )


# # ----- The end! -----
