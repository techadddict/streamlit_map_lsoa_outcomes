"""
Streamlit demo of two England maps with LSOA-level colour bands.

Because a long app quickly gets out of hand,
try to keep this document to mostly direct calls to streamlit to write
or display stuff. Use functions in other files to create and
organise the stuff to be shown. In this example, most of the work is
done in functions stored in files named container_(something).py
"""
# ----- Imports -----
import streamlit as st
import pandas as pd
import numpy as np

import plotly.graph_objs as go
from plotly.subplots import make_subplots
import rasterio
from rasterio import features
import rasterio.plot
import os
import geopandas
from shapely.validation import make_valid  # for fixing dodgy polygons

# Custom functions:
import stroke_maps.load_data
import utilities_maps.maps as maps
import utilities_maps.plot_maps as plot_maps
import utilities_maps.container_inputs as inputs


# ###########################
# ##### START OF SCRIPT #####
# ###########################
# page_setup()
st.set_page_config(
    page_title='Colour band map demo',
    page_icon=':rainbow:',
    layout='wide'
    )

container_maps = st.empty()


# Import the full travel time matrix:
df_travel_times = pd.read_csv(
    './data_maps/lsoa_travel_time_matrix_calibrated.csv', index_col='LSOA')
# Rename index to 'lsoa':
df_travel_times.index.name = 'lsoa'


# #################################
# ########## USER INPUTS ##########
# #################################

# User inputs for which hospitals to pick:
df_units = stroke_maps.load_data.stroke_unit_region_lookup()

# Limit to England:
df_units = df_units.loc[~df_units['icb'].isna()].copy()
# Sort by ISDN (approximates sort by region):
df_units = df_units.sort_values('isdn')

# Find where in the list the default options are.
# Ugly conversion to int from int64 so selectbox() can take it.
ind1 = int(np.where(df_units.index == 'LE15WW')[0][0])
ind2 = int(np.where(df_units.index == 'TA15DA')[0][0])

# Select hospitals by name...
unit1_name = st.selectbox(
    'Hospital 1',
    options=df_units['stroke_team'],
    index=ind1
)
unit2_name = st.selectbox(
    'Hospital 2',
    options=df_units['stroke_team'],
    index=ind2
)

# ... then convert names to postcodes for easier lookup.
unit1 = df_units.loc[df_units['stroke_team'] == unit1_name].index.values[0]
unit2 = df_units.loc[df_units['stroke_team'] == unit2_name].index.values[0]


# Colourmap selection
cmap_names = [
    'cosmic_r', 'viridis_r', 'inferno_r', 'neutral_r',
    ]
cmap_diff_names = [
    'iceburn_r', 'seaweed', 'fusion', 'waterlily'
    ]
with st.sidebar:
    st.markdown('### Colour schemes')
    cmap_name, cmap_diff_name = inputs.select_colour_maps(
        cmap_names, cmap_diff_names)

    with st.form('Colour band setup'):
        v_min = st.number_input(
            'LHS vmin',
            min_value=0,
            max_value=480,
            step=5,
            value=0,
            )
        v_max = st.number_input(
            'LHS vmax',
            min_value=0,
            max_value=480,
            step=5,
            value=120,
            )
        step_size = st.number_input(
            'LHS step',
            min_value=5,
            max_value=60,
            step=5,
            value=30,
            )

        v_min_diff = st.number_input(
            'RHS vmin',
            min_value=-480,
            max_value=0,
            step=5,
            value=-120,
            )
        v_max_diff = st.number_input(
            'RHS vmax',
            min_value=0,
            max_value=480,
            step=5,
            value=120,
            )
        step_size_diff = st.number_input(
            'RHS step',
            min_value=5,
            max_value=120,
            step=5,
            value=30,
            )
        submitted = st.form_submit_button('Submit')


# Display names:
subplot_titles = [
    'Time to hospital 1',
    'Time benefit of hospital 2 over hospital 1'
]
cmap_titles = [f'{s} (minutes)' for s in subplot_titles]


# #######################################
# ########## MAIN CALCULATIONS ##########
# #######################################
# While the main calculations are happening, display a blank map.
# Later, when the calculations are finished, replace with the actual map.
with container_maps:
    plot_maps.plotly_blank_maps(['', ''], n_blank=2)

# Pick out the data for hospitals 1 and 2 only:
df_data = df_travel_times[[unit1, unit2]]

# Calculate the time difference between hospitals 1 and 2:
if unit1 != unit2:
    df_data['diff'] = df_data[unit1] - df_data[unit2]
else:
    # Difference is zero when the same unit is selected twice.
    df_data['diff'] = 0.0

# Maximum values:
tmax = df_data.max().max()
tmax_diff = tmax


# ####################################
# ########## SETUP FOR MAPS ##########
# ####################################

# Load LSOA geometry:
# path_to_lsoa = os.path.join('data', 'outline_lsoa11cds.geojson')
path_to_lsoa = os.path.join('data_maps', 'LSOA_(Dec_2011)_Boundaries_Super_Generalised_Clipped_(BSC)_EW_V3_reduced4_simplified.geojson')
gdf = geopandas.read_file(path_to_lsoa)
# Merge in column:
gdf = pd.merge(gdf, df_data,
                left_on='LSOA11NM', right_on='lsoa', how='right')
gdf.index = range(len(gdf))

# Convert to British National Grid:
gdf = gdf.to_crs('EPSG:27700')

# Make geometry valid:
gdf['geometry'] = [
    make_valid(g) if g is not None else g
    for g in gdf['geometry'].values
    ]

# Code source for conversion to raster: https://gis.stackexchange.com/a/475845
# Prepare some variables
xmin, ymin, xmax, ymax = gdf.total_bounds
pixel_size = 1000
width = int(np.ceil((pixel_size + xmax - xmin) // pixel_size))
height = int(np.ceil((pixel_size + ymax - ymin) // pixel_size))
transform = rasterio.transform.from_origin(xmin, ymax, pixel_size, pixel_size)

im_xmax = xmin + (pixel_size * width)
im_ymax = ymin + (pixel_size * height)

# Burn geometries for left-hand map:
shapes_lhs = ((geom, value) for geom, value in zip(gdf['geometry'], gdf[unit1]))
burned_lhs = features.rasterize(
    shapes=shapes_lhs,
    out_shape=(height, width),
    fill=np.NaN,
    transform=transform,
    all_touched=True
)
burned_lhs = np.flip(burned_lhs, axis=0)


# Burn geometries for right-hand map:
shapes_rhs = ((geom, value) for geom, value in zip(gdf['geometry'], gdf['diff']))
burned_rhs = features.rasterize(
    shapes=shapes_rhs,
    out_shape=(height, width),
    fill=np.NaN,
    transform=transform,
    all_touched=True
)
burned_rhs = np.flip(burned_rhs, axis=0)

# Load colour info:
cmap_lhs = inputs.make_colour_list(cmap_name)
cmap_rhs = inputs.make_colour_list(cmap_diff_name)


# Load stroke unit coordinates:
gdf_unit_coords = stroke_maps.load_data.stroke_unit_coordinates()

# ----- Plotting -----
fig = make_subplots(
    rows=1, cols=2,
    horizontal_spacing=0.0,
    subplot_titles=subplot_titles
    )

fig.add_trace(go.Heatmap(
    z=burned_lhs,
    transpose=False,
    x0=xmin,
    dx=pixel_size,
    y0=ymin,
    dy=pixel_size,
    zmin=0,
    zmax=tmax,
    colorscale=cmap_lhs,
    colorbar=dict(
        thickness=20,
        # tickmode='array',
        # tickvals=tick_locs,
        # ticktext=tick_names,
        # ticklabelposition='outside top'
        title='Times (minutes)'
        ),
    name='times'
), row='all', col=1)

fig.add_trace(go.Heatmap(
    z=burned_rhs,
    transpose=False,
    x0=xmin,
    dx=pixel_size,
    y0=ymin,
    dy=pixel_size,
    zmin=-tmax_diff,
    zmax=tmax_diff,
    colorscale=cmap_rhs,
    colorbar=dict(
        thickness=20,
        # tickmode='array',
        # tickvals=tick_locs,
        # ticktext=tick_names,
        # ticklabelposition='outside top'
        title='Difference in times (minutes)'
        ),
    name='diff'
), row='all', col=2)

fig.update_traces(
    {'colorbar': {
        'orientation': 'h',
        'x': 0.0,
        'y': -0.2,
        'len': 0.5,
        'xanchor': 'left',
        'title_side': 'bottom'
        # 'xref': 'paper'
        }},
    selector={'name': 'times'}
    )
fig.update_traces(
    {'colorbar': {
        'orientation': 'h',
        'x': 1.0,
        'y': -0.2,
        'len': 0.5,
        'xanchor': 'right',
        'title_side': 'bottom'
        # 'xref': 'paper'
        }},
    selector={'name': 'diff'}
    )

# Stroke unit locations:
fig.add_trace(go.Scatter(
    x=gdf_unit_coords['BNG_E'],
    y=gdf_unit_coords['BNG_N'],
    mode='markers',
    name='units'
), row='all', col='all')

# Equivalent to pyplot set_aspect='equal':
fig.update_yaxes(col=1, scaleanchor='x', scaleratio=1)
fig.update_yaxes(col=2, scaleanchor='x2', scaleratio=1)

# Shared pan and zoom settings:
fig.update_xaxes(matches='x')
fig.update_yaxes(matches='y')

# Remove axis ticks:
fig.update_xaxes(showticklabels=False, showgrid=False, zeroline=False)
fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False)

with container_maps:
    # Write to streamlit:
    st.plotly_chart(
        fig,
        use_container_width=True,
        # config=plotly_config
        )
