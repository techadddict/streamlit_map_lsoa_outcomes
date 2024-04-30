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

# Invent some value to colour by:
np.random.seed(42)
vals = (np.random.rand(len(gdf_catchment)) - 0.5) * 8.0
v_max = 4.0
v_min = -4.0
# Set a few values to be outside the specified colour range:
mask = np.random.binomial(1, 0.2, size=len(vals)) == 1
vals[mask] = -5.0
mask = np.random.binomial(1, 0.2, size=len(vals)) == 1
vals[mask] = 5.0
gdf_catchment['z'] = vals

# Colours:
colour_under = 'magenta'
colour_over = 'LimeGreen'
colours = [colour_under, 'SteelBlue', 'blue', 'SkyBlue', 'MidnightBlue', colour_over]
# Colour bounds:
# red for 0.0 to 0.1,
# blue for 0.1 to 0.5,
# green for 0.5 to 0.6,
# orange for 0.6 to 1.0.
# bounds = [0.00, 0.10, 0.50, 0.60, 1.00]
v_bounds = [-4.0, -2.0, 0.0, 3.0, 4.0]


# Assign colours to the data:
inds = np.digitize(gdf_catchment['z'], v_bounds)
gdf_catchment['colour'] = np.array(colours)[inds]

# Normalise the data bounds:
bounds = (
    (np.array(v_bounds) - np.min(v_bounds)) /
    (np.max(v_bounds) - np.min(v_bounds))
)
# Add extra bounds so that there's a tiny space at either end
# for the under/over colours.
bounds_for_cs = [bounds[0], bounds[0] + 1e-7, *bounds[1:-1], bounds[-1] - 1e-7, bounds[-1]]

# Need separate data values and colourbar values.
# e.g. translate 32 in the data means colour 0.76 on the colourmap.

# Create a colour scale from these colours.
# To get the discrete colourmap (i.e. no continuous gradient of
# colour made between the defined colours),
# double up the bounds so that colour A explicitly ends where
# colour B starts.
colourscale = []
for i in range(len(colours)):
    colourscale += [[bounds_for_cs[i], colours[i]], [bounds_for_cs[i+1], colours[i]]]

# Dummy coordinates:
x_dummy = np.linspace(10, 100000, len(v_bounds))
y_dummy = np.linspace(10, 100000, len(v_bounds))
# Have to show the full colour scale otherwise the colourbar
# colours will look right but the ticks will appear in the wrong
# location. e.g. if don't plot a point with colour 0.0, first colour
# is 0.1, then the bottom of the colourbar will be labelled with
# tick 0.1 instead of the intended tick 0.0.
z_dummy = np.array(v_bounds)#[1:] - 1e-3

# ----- Plotting -----
fig = make_subplots(rows=1, cols=2)

# Sometimes the ticks don't show at the very ends of the colour bars.
# In that case, cheat with e.g.
# tick_locs = [bounds[0] + 1e-2, *bounds[1:-1], bounds[-1] - 1e-3]
tick_locs = v_bounds
tick_names = v_bounds

# Add dummy scatter:
fig.add_trace(go.Scatter(
    x=x_dummy,
    y=y_dummy,
    marker=dict(
        color=z_dummy,
        colorscale=colourscale,
        colorbar=dict(
            thickness=20,
            tickmode='array',
            tickvals=tick_locs,
            ticktext=tick_names,
            # ticklabelposition='outside top'
            ),
        size=1e-4,
        ),
    showlegend=False,
    mode='markers',
    hoverinfo='skip'
))

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
        showlegend=False
        ), row='all', col='all')

# Equivalent to pyplot set_aspect='equal':
fig.update_yaxes(col=1, scaleanchor='x', scaleratio=1)
fig.update_yaxes(col=2, scaleanchor='x2', scaleratio=1)

# Shared pan and zoom settings:
fig.update_xaxes(matches='x')
fig.update_yaxes(matches='y')

st.plotly_chart(fig)
