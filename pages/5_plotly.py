import streamlit as st
import pandas as pd
import json
import plotly.graph_objs as go
import plotly.express as px
from geojson_rewind import rewind
from datetime import datetime

from utilities_maps.fixed_params import page_setup


def import_geojson(geojson_file=''):
    if len(geojson_file) < 1:
        geojson_file = 'LSOA_(Dec_2011)_Boundaries_Super_Generalised_Clipped_(BSC)_EW_V3_reduced3.geojson'
    with open('./data_maps/' + geojson_file) as f:
        geojson_ew = json.load(f)
    return geojson_ew


def draw_map_plotly(df_placeholder, geojson_ew, lat_hospital, long_hospital):

    fig = px.choropleth_mapbox(
        df_placeholder,
        geojson=geojson_ew,
        locations='LSOA11NMW',
        color='Placeholder',
        color_continuous_scale="Viridis",
        # range_color=(0, 12),
        mapbox_style="carto-positron",
        zoom=9,
        center={"lat": lat_hospital, "lon": long_hospital},
        opacity=0.5,
        # labels={'unemp':'unemployment rate'}
    )
    # fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    # fig.show()
    st.plotly_chart(fig)


def plotly_big_map():
    fig = go.Figure()

    fig.update_layout(
        width=1200,
        height=1200
        )

    fig.add_trace(go.Choropleth(
        geojson=geojson_ew,
        locations=df_outcomes['lsoa'],
        z=df_outcomes['drip_ship_lvo_mt_added_utility'],
        featureidkey='properties.LSOA11NM',
        coloraxis="coloraxis",
        # colorscale='Inferno',
        # autocolorscale=False
    ))

    fig.update_layout(
        geo=dict(
            scope='world',
            projection=go.layout.geo.Projection(type='airy'),
            fitbounds='locations',
            visible=False
        ))
    # Remove LSOA borders:
    fig.update_traces(marker_line_width=0, selector=dict(type='choropleth'))

    # The initial colour map setting can take very many options,
    # but the later update with the drop-down menu only has a small list
    # of about ten coded in. You can't even provide a list of colours instead.
    # The available options are:
    # Blackbody, Bluered, Blues, Cividis, Earth, Electric, Greens, Greys,
    # Hot, Jet, Picnic, Portland, Rainbow, RdBu, Reds, Viridis, YlGnBu, YlOrRd.
    # As listed in: https://plotly.com/python-api-reference/generated/
    # plotly.graph_objects.Choropleth.html

    fig.update_layout(
        coloraxis_colorscale='Electric',
        coloraxis_colorbar_title_text='Added utility',
        coloraxis_cmin=outcome_vmin,
        coloraxis_cmax=outcome_vmax,
        )

    fig.update_layout(title_text='<b>Drip and Ship</b>', title_x=0.5)

    fig.update_layout(
        updatemenus=[go.layout.Updatemenu(
            x=0, xanchor='right', y=1.15, type="dropdown",
            pad={'t': 5, 'r': 20, 'b': 0, 'l': 30},
            # ^ around all buttons (not indiv buttons)
            buttons=list([
                dict(
                    args=[
                        {
                            'z': [df_outcomes[
                                'drip_ship_lvo_mt_added_utility']],
                        },
                        {
                            'coloraxis.colorscale': 'Electric',
                            'coloraxis.reversescale': False,
                            'coloraxis.cmin': outcome_vmin,
                            'coloraxis.cmax': outcome_vmax,
                            'title.text': '<b>Drip and Ship</b>'
                        }],
                    label='Drip & Ship',
                    method='update'
                ),
                dict(
                    args=[
                        {
                            'z': [df_outcomes[
                                'mothership_lvo_mt_added_utility']],
                        },
                        {
                            'coloraxis.colorscale': 'Electric',
                            'coloraxis.reversescale': False,
                            'coloraxis.cmin': outcome_vmin,
                            'coloraxis.cmax': outcome_vmax,
                            'title.text': '<b>Mothership</b>'
                        }],
                    label='Mothership',
                    method='update'
                ),
                dict(
                    args=[
                        {
                            'z': [df_outcomes['diff_lvo_mt_added_utility']],
                        },
                        {
                            'coloraxis.colorscale': 'RdBu',
                            'coloraxis.reversescale': True,
                            'coloraxis.cmin': diff_vmin,
                            'coloraxis.cmax': diff_vmax,
                            'title.text': '<b>Difference</b>'
                        }],
                    label='Diff',
                    method='update'
                )
                ])
        )]
    )
    fig.update_traces(hovertemplate='%{z}<extra>%{location}</extra>')

    fig.write_html('data_maps/plotly_test.html')

    st.plotly_chart(fig)


def plotly_two_subplots():
    from plotly.subplots import make_subplots
    fig = make_subplots(
        rows=1, cols=2, subplot_titles=['a', 'b'],
        specs=[[{"type": "choropleth"}, {"type": "choropleth"}]]
    )

    fig.update_layout(
        width=1200,
        height=1200
        )
    fig.add_trace(go.Choropleth(
        geojson=geojson_ew,
        locations=df_outcomes['lsoa'],
        z=df_outcomes['drip_ship_lvo_mt_added_utility'],
        featureidkey='properties.LSOA11NM',
        coloraxis="coloraxis",
        # colorscale='Inferno',
        # autocolorscale=False
    ), row=1, col=1
    )

    fig.add_trace(go.Choropleth(
        geojson=geojson_ew,
        locations=df_outcomes['lsoa'],
        z=df_outcomes['mothership_lvo_mt_added_utility'],
        featureidkey='properties.LSOA11NM',
        coloraxis="coloraxis",
        # colorscale='Inferno',
        # autocolorscale=False
    ), row=1, col=2
    )

    fig.update_layout(
        geo=dict(
            scope='world',
            projection=go.layout.geo.Projection(type='airy'),
            fitbounds='locations',
            visible=False, domain_row=1, domain_column=1))
    fig.update_layout(
        geo=dict(
            scope='world',
            projection=go.layout.geo.Projection(type='airy'),
            fitbounds='locations',
            visible=False, domain_row=1, domain_column=2))
    # Remove LSOA borders:
    fig.update_traces(marker_line_width=0, selector=dict(type='choropleth'))

    # The initial colour map setting can take very many options,
    # but the later update with the drop-down menu only has a small list
    # of about ten coded in. You can't even provide a list of colours instead.
    # The available options are:
    # Blackbody, Bluered, Blues, Cividis, Earth, Electric, Greens, Greys,
    # Hot, Jet, Picnic, Portland, Rainbow, RdBu, Reds, Viridis, YlGnBu, YlOrRd.
    # As listed in: https://plotly.com/python-api-reference/generated/
    # plotly.graph_objects.Choropleth.html

    fig.update_layout(
        coloraxis_colorscale='Electric',
        coloraxis_colorbar_title_text='Added utility',
        coloraxis_cmin=outcome_vmin,
        coloraxis_cmax=outcome_vmax,
        )

    fig.update_layout(title_text='<b>Drip and Ship</b>', title_x=0.5)
    fig.update_layout(
        updatemenus=[go.layout.Updatemenu(
            x=0, xanchor='right', y=1.15, type="dropdown",
            pad={'t': 5, 'r': 20, 'b': 0, 'l': 30},
            # ^ around all buttons (not indiv buttons)
            buttons=list([
                dict(
                    args=[
                        {
                            'z': [df_outcomes[
                                'drip_ship_lvo_mt_added_utility']],
                            },
                        {
                            'coloraxis.colorscale': 'Electric',
                            'coloraxis.reversescale': False,
                            'coloraxis.cmin': outcome_vmin,
                            'coloraxis.cmax': outcome_vmax,
                            'title.text': '<b>Drip and Ship</b>'
                        }],
                    label='Drip & Ship',
                    method='update'
                ),
                dict(
                    args=[
                        {
                            'z': [df_outcomes[
                                'mothership_lvo_mt_added_utility']],
                            'z1': [df_outcomes[
                                'mothership_nlvo_ivt_added_utility']],
                        },
                        {
                            'coloraxis.colorscale': 'Electric',
                            'coloraxis.reversescale': False,
                            'coloraxis.cmin': outcome_vmin,
                            'coloraxis.cmax': outcome_vmax,
                            'title.text': '<b>Mothership</b>'
                        }],
                    label='Mothership',
                    method='update'
                ),
                dict(
                    args=[
                        {
                            'z': [df_outcomes['diff_lvo_mt_added_utility']],
                        },
                        {
                            'coloraxis.colorscale': 'RdBu',
                            'coloraxis.reversescale': True,
                            'coloraxis.cmin': diff_vmin,
                            'coloraxis.cmax': diff_vmax,
                            'title.text': '<b>Difference</b>'
                        }],
                    label='Diff',
                    method='update'
                )
                ])
        )]
    )
    fig.update_traces(hovertemplate='%{z}<extra>%{location}</extra>')

    fig.write_html('data_maps/plotly_dual_test.html')

    st.plotly_chart(fig)


# ###########################
# ##### START OF SCRIPT #####
# ###########################
page_setup()

# Title:
st.markdown('# Plotly')

startTime = datetime.now()

# Load data files
# Hospital info
df_hospitals = pd.read_csv("./data_maps/stroke_hospitals_22_reduced.csv")

df_outcomes = pd.read_csv("./data_maps/lsoa_base.csv")

df_outcomes = df_outcomes.round(3)
# df_outcomes['drip_ship_lvo_mt_added_utility'] = \
# round(df_outcomes['drip_ship_lvo_mt_added_utility'], 3)
# df_outcomes['mothership_lvo_mt_added_utility'] = \
# round(df_outcomes['mothership_lvo_mt_added_utility'], 3)
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

# Colour bar limits:
added_utility_cols = [
    'drip_ship_nlvo_ivt_added_utility',
    'mothership_nlvo_ivt_added_utility',
    'drip_ship_lvo_ivt_added_utility',
    'mothership_lvo_ivt_added_utility',
    'drip_ship_lvo_mt_added_utility',
    'mothership_lvo_mt_added_utility',
]
diff_added_utility_cols = [
    'diff_nlvo_ivt_added_utility',
    'diff_lvo_ivt_added_utility',
    'diff_lvo_mt_added_utility',
]
vmin_added_utility = df_outcomes[added_utility_cols].min().min()
vmax_added_utility = df_outcomes[added_utility_cols].max().max()
vlim_diff_added_utility = df_outcomes[
    diff_added_utility_cols].abs().max().max()
vmin_diff_added_utility = -vlim_diff_added_utility
vmax_diff_added_utility = +vlim_diff_added_utility


# Temporary before function
outcome_vmin = vmin_added_utility
outcome_vmax = vmax_added_utility
diff_vmin = vmin_diff_added_utility
diff_vmax = vmax_diff_added_utility


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

time4 = datetime.now()

with st.spinner(text='Drawing map'):
    plotly_big_map()
# plotly_two_subplots()
time5 = datetime.now()
st.write('Time to draw map:', time5 - time4)
