"""
Change lat/long to x/y and plot maps with plotly.

"""
import streamlit as st
import geopandas
import numpy as np
from shapely.validation import make_valid  # for fixing dodgy polygons
import plotly.graph_objects as go
from plotly.subplots import make_subplots

@st.cache_data
def read_gdf(path_to_file):
    gdf_catchment = geopandas.read_file(path_to_file)
    # Make geometry valid:
    gdf_catchment['geometry'] = [
        make_valid(g) if g is not None else g
        for g in gdf_catchment['geometry'].values
        ]
    return gdf_catchment


def convert_shapely_polys_into_xy(gdf):
    x_list = []
    y_list = []
    for i in gdf.index:
        geo = gdf.loc[i, 'geometry']
        if geo.geom_type == 'Polygon':
            # Can use the data pretty much as it is.
            x, y = geo.exterior.coords.xy
            x_list.append(list(x))
            y_list.append(list(y))
        elif geo.geom_type == 'MultiPolygon':
            # Put None values between polygons.
            x_combo = []
            y_combo = []
            for poly in geo.geoms:
                x, y = poly.exterior.coords.xy
                x_combo += list(x) + [None]
                y_combo += list(y) + [None]
            x_list.append(np.array(x_combo))
            y_list.append(np.array(y_combo))
        else:
            st.write('help', i)
    return x_list, y_list


# Import data:
gdf_catchment = read_gdf('./data_maps/outline_nearest_ivt.geojson')

# Turn polygons into x and y coordinates:
x_list, y_list = convert_shapely_polys_into_xy(gdf_catchment)
gdf_catchment['x'] = x_list
gdf_catchment['y'] = y_list

# Assign random colours:
colours = ['red', 'blue', 'green', 'orange']
colour_list = np.random.choice(colours, size=len(gdf_catchment))
gdf_catchment['colour'] = colour_list


# ----- Plotting -----
fig = make_subplots(rows=1, cols=2)

# Add each row of the dataframe separately.
# Scatter the edges of the polygons and use "fill" to colour
# within the lines.
for i in gdf_catchment.index:
    fig.add_trace(go.Scatter(
        x=gdf_catchment.loc[i, 'x'],
        y=gdf_catchment.loc[i, 'y'],
        fill="toself",
        fillcolor=gdf_catchment.loc[i, 'colour'],
        line_color='black',
        name=gdf_catchment.loc[i, 'nearest_ivt_unit'],
        ), row='all', col='all')

# Equivalent to pyplot set_aspect='equal':
fig.update_yaxes(col=1, scaleanchor='x', scaleratio=1)
fig.update_yaxes(col=2, scaleanchor='x2', scaleratio=1)

# Shared pan and zoom settings:
fig.update_xaxes(matches='x')
fig.update_yaxes(matches='y')

st.plotly_chart(fig)
