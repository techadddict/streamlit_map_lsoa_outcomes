import streamlit as st
import numpy as np
import pandas as pd

# Importing libraries
import folium
# For importing colour maps:
import matplotlib.pyplot as plt
# For opening the cloud-optimised geotiff:
from rasterio import open as rast_open
# For the colour bar:
import branca
from branca.element import MacroElement
from jinja2 import Template
import json
from datetime import datetime

from utilities_maps.fixed_params import page_setup


def import_cog(out_cog):
    with rast_open(out_cog, 'r') as ds:
        myarray_colours = ds.read()

    # For plotting, the array needs to be in the shape NxMx4.
    # When imported using rasterio, the array is in the shape 4xNxM.
    # `np.transpose()` reshapes the array to the required dimensions.
    myarray_colours = np.transpose(myarray_colours, axes=(1, 2, 0))
    return myarray_colours


def draw_cog_on_map(
        clinic_map, file_name, layer_name='Cog layer',
        alpha=1.0, visible=True, featuregroup=None, which_map=0
        ):

    cog_array = import_cog(file_name)
    # TO DO - pull out bounds from the input array
    # (something in the notebook does this already)

    # To prevent incorrect colours being displayed
    # (some sort of folium autoscaling for small colour range?),
    # set some pixels to red, green, blue, black, white:
    cog_array[0][1] = [1.0, 0.0, 0.0, 1]
    cog_array[0][2] = [0.0, 1.0, 0.0, 1]
    cog_array[0][3] = [0.0, 0.0, 1.0, 1]
    cog_array[0][4] = [0.0, 0.0, 0.0, 1]
    cog_array[0][5] = [1.0, 1.0, 1.0, 1]
    # These live in the Inner Hebrides and currently our data does
    # not cover Scotland, so nobody should notice these random pixels.

    image = folium.raster_layers.ImageOverlay(
        name=layer_name,
        image=cog_array,  # out_cog,#out_cog,
        bounds=[[49.8647411589999976, -6.4185476299999999],
                [55.8110685409999974, 1.7629415090000000]],
        # bounds=[[49.6739854059999999, -6.6230848580000004],
        # [56.0018242949999987, 1.9674787370000004]],
        opacity=alpha,
        mercator_project=True,
        # colormap=colour_func,
        # interactive=True,
        # cross_origin=False,
        # zindex=1,
        overlay=False,
        show=visible
    )

    if which_map == 0:
        image.add_to(clinic_map)
    elif which_map == 1:
        image.add_to(clinic_map.m1)
    elif which_map == 2:
        image.add_to(clinic_map.m2)
    return image, clinic_map

    # if featuregroup is None:
    #     image.add_to(clinic_map)
    #     return image, clinic_map
    # else:
    #     featuregroup.add_child(image)
    #     return image, featuregroup
    # # return image, clinic_map


def draw_LSOA_outlines_on_map(clinic_map, which_map=0):
    geojson_ew = import_geojson()

    lsoa_outlines = folium.GeoJson(
        data=geojson_ew,
        popup=GeoJsonPopup(
            fields=['LSOA11NM'],
            aliases=[''],
            localize=True
            ),
        name='LSOA outlines',
        style_function=lambda y:{  
                'fillColor': 'rgba(0, 0, 0, 0)',
                'color': 'rgba(0, 0, 0, 0)',
                'weight':0.1,
            },
        highlight_function=lambda y:{'weight': 2.0, 'color': 'black'},  # highlight_function / hover_dict
        # smooth_factor=1.5,  # 2.0 is about the upper limit here
        # show=False if g > 0 else True
        )

    if which_map == 0:
        lsoa_outlines.add_to(clinic_map)
    elif which_map == 1:
        lsoa_outlines.add_to(clinic_map.m1)
    elif which_map == 2:
        lsoa_outlines.add_to(clinic_map.m2)
    # lsoa_outlines.add_to(clinic_map)
    return lsoa_outlines, clinic_map


def draw_map_tiff(df_hospitals, cog_files, layer_names, outcome_cbar_dict,
                  diff_cbar_dict, alpha=0.6, savename='html_test.html'):

    # Create a map base without tiles:
    # outcome_map = leafmap.Map(
    outcome_map = folium.plugins.DualMap(
        location=[53, -2.5],  # Somewhere in the middle of the map
        zoom_start=6,
        # Override how much people can zoom in or out:
        # min_zoom=0,
        # max_zoom=18,
        # width=1200,
        # height=600,
        # Remove extra controls for stuff we don't need:
        draw_control=False,
        scale_control=False,
        search_control=False,
        measure_control=False,
        # control=False
        tiles=None,
        # layout='vertical'
        )

    # # Now add the tiles and remove the option to toggle them on and off.
    # # This means that no matter what layers we add later,
    # # the tiles will never be removed.
    # # https://stackoverflow.com/questions/61345801/
    # # featuregroup-layer-control-in-folium-only-one-active-layer
    # # New feature group:
    # base_map = folium.FeatureGroup(
    #     name='Base map', overlay=True, control=False)
    # # Place the tiles in the feature group:
    # folium.TileLayer(tiles='cartodbpositron').add_to(base_map)
    # # Draw on the map:
    # base_map.add_to(outcome_map)

    # Draw the coloured background images.
    # Set one to be visible on load and the others to appear when
    # selected.

    tiff_layers = []
    for t, c_file in enumerate(cog_files):
        m = 1 if t < 3 else 2
        # Set whether this layer will be shown on startup:
        v = False if t > 0 else True
        tiff_layer, outcome_map = draw_cog_on_map(
            outcome_map,
            c_file,
            layer_name=layer_names[t],
            alpha=alpha,
            visible=v,
            which_map=m
            )
        tiff_layers.append(tiff_layer)

    colourmaps = []
    for m in [outcome_map.m1, outcome_map.m2]:
        # --- Outcome colourbar ---
        # Use these points as fixed colours with labels:
        choro_bins = np.linspace(
            outcome_cbar_dict['min'], outcome_cbar_dict['max'], 7)
        # Get colours as (R, G, B, A) arrays:
        colours = plt.get_cmap(outcome_cbar_dict['cmap'])(
            np.linspace(0, 1, len(choro_bins)))
        # Update alpha to match the opacity of the background image:
        colours[:, 3] = alpha
        # Convert colours to tuple so that branca understands them:
        colours = [tuple(colour) for colour in colours]

        # Drip and ship colour bar:
        colormap_dripship = branca.colormap.LinearColormap(
            vmin=outcome_cbar_dict['min'],
            vmax=outcome_cbar_dict['max'],
            colors=colours,
            caption=outcome_cbar_dict['cbar_label'],
            index=choro_bins
        )
        colourmaps.append(colormap_dripship)
        # outcome_map.add_child(colormap_dripship)
        # colormap_dripship.add_to(outcome_map.m2)

        # Mothership colour bar:
        colormap_mothership = branca.colormap.LinearColormap(
            vmin=outcome_cbar_dict['min'],
            vmax=outcome_cbar_dict['max'],
            colors=colours,
            caption=outcome_cbar_dict['cbar_label'],
            index=choro_bins
        )
        # outcome_map.add_child(colormap_mothership)
        colourmaps.append(colormap_mothership)

        # --- Difference colourbar ---
        # Use these points as fixed colours with labels:
        choro_bins = np.linspace(
            diff_cbar_dict['min'], diff_cbar_dict['max'], 7)
        # Get colours as (R, G, B, A) arrays:
        colours = plt.get_cmap(
            diff_cbar_dict['cmap'])(np.linspace(0, 1, len(choro_bins)))
        # Update alpha to match the opacity of the background image:
        colours[:, 3] = alpha
        # Convert colours to tuple so that branca understands them:
        colours = [tuple(colour) for colour in colours]

        # Make a new discrete colour map:
        colormap_diff = branca.colormap.LinearColormap(
            vmin=diff_cbar_dict['min'],
            vmax=diff_cbar_dict['max'],
            colors=colours,
            caption=diff_cbar_dict['cbar_label'],
            index=choro_bins
        )
        # outcome_map.add_child(colormap_diff)
        colourmaps.append(colormap_diff)

    # Bind colourmaps to each tiff image so that only one bar shows
    # up at once.
    for i in range(len(tiff_layers)):
        if i < 3:
            # m = outcome_map.m1 if i < 3 else outcome_map.m2
            # m.add_child(BindColormap(tiff_layers[i], colourmaps[i]))
            # BindColormap(tiff_layers[i], colourmaps[i]).add_to(m)
            # st.write(i, 'top')
            colourmaps[i].add_to(outcome_map.m1)
            BindColormap(tiff_layers[i], colourmaps[i]).add_to(outcome_map.m1)
        else:
            # pass

            colourmaps[i].add_to(outcome_map.m2)
            BindColormap(tiff_layers[i], colourmaps[i]).add_to(outcome_map.m2)

            # st.write(i, 'bottom')
            # colourmaps[i].add_to(outcome_map)
            # BindColormap(tiff_layers[i], colourmaps[i]).add_to(outcome_map)
    # outcome_map.add_child(BindColormap(tiff_layers[1], colormap_mothership))
    # outcome_map.add_child(BindColormap(tiff_layers[2], colormap_diff))

    # Nearest IVT hospitals:
    ivt_outlines, outcome_map = draw_catchment_IVT_on_map(
        outcome_map, which_map=1)
    ivt_outlines_2, outcome_map = draw_catchment_IVT_on_map(
        outcome_map, which_map=2)

    # Nearest MT hospitals:
    mt_outlines, outcome_map = draw_catchment_MT_on_map(
        outcome_map, which_map=1)
    mt_outlines_2, outcome_map = draw_catchment_MT_on_map(
        outcome_map, which_map=2)

    # # LSOA outlines:
    # lsoa_outlines, outcome_map = draw_LSOA_outlines_on_map(outcome_map)

    # Hospital markers:
    # Place all markers into a FeatureGroup so that
    # in the layer controls they can be shown or removed
    # with a single click, instead of toggling each marker
    # individually.
    fg_markers = folium.FeatureGroup(
        name='Hospital markers',
        # Remove from the layer control:
        control=False
        )
    # Iterate over the dataframe to get hospital coordinates
    # and to choose the colour of the marker.
    for (index, row) in df_hospitals.iterrows():
        if row.loc['Use_MT'] > 0:
            colour = 'red'
        elif row.loc['Use_IVT'] > 0:
            colour = 'white'
        else:
            colour = ''
        if len(colour) > 0:
            fg_markers.add_child(
                folium.CircleMarker(
                    radius=2.6,  # pixels
                    location=[row.loc['lat'], row.loc['long']],
                    # popup=pop_up_text,
                    color='black',
                    tooltip=row.loc['Stroke Team'],
                    fill=True,
                    fillColor=colour,
                    fillOpacity=1,
                    weight=1,
                )
            )
    fg_markers.add_to(outcome_map)

    polygons = [
        # lsoa_outlines,
        ivt_outlines,
        mt_outlines,
        # # fg_nearest_hospitals
        ]

    # Put everything not later specified in this layer control:
    # outcome_map.add_layer_control(collapsed=False)
    folium.LayerControl(
        collapsed=False,
        name='Background image'
        ).add_to(outcome_map.m1)
    folium.LayerControl(
        collapsed=False,
        name='Background image'
        ).add_to(outcome_map.m2)

    # Anything specified in further GroupedLayerControl boxes
    # will be removed from the previous control and appear in here:
    folium.plugins.GroupedLayerControl(
        {'Shapes': polygons},
        collapsed=False,
        exclusive_groups=False,  # True for radio, false for checkbox
    ).add_to(outcome_map.m1)

    folium.plugins.GroupedLayerControl(
        {'Shapes': [ivt_outlines_2, mt_outlines_2]},
        collapsed=False,
        exclusive_groups=False,  # True for radio, false for checkbox
    ).add_to(outcome_map.m2)

    # Set z-order of the elements:
    # (can add multiple things in here but the lag increases)
    outcome_map.m1.keep_in_front(fg_markers)
    outcome_map.m2.keep_in_front(fg_markers)

    # Generate map
    # For single map:
    # outcome_map.to_streamlit()
    # For DualMap:
    st.components.v1.html(outcome_map._repr_html_(), height=1200, width=1200)
    # st.write(outcome_map)
    # outcome_map.show()
    # outcome_map.save(savename)


class BindColormap(MacroElement):
    """Binds a colormap to a given layer.

    https://nbviewer.org/gist/BibMartin/f153aa957ddc5fadc64929abdee9ff2e

    Parameters
    ----------
    colormap : branca.colormap.ColorMap
        The colormap to bind.
    """
    def __init__(self, layer, colormap):
        super(BindColormap, self).__init__()
        self.layer = layer
        self.colormap = colormap
        # # For overlays layers:
        # self._template = Template(u"""
        # {% macro script(this, kwargs) %}
        #     {{this.colormap.get_name()}}.svg[0][0].style.display = 'block';
        #     {{this._parent.get_name()}}.on('overlayadd', function (eventLayer) {
        #         if (eventLayer.layer == {{this.layer.get_name()}}) {
        #             {{this.colormap.get_name()}}.svg[0][0].style.display = 'block';
        #         }});
        #     {{this._parent.get_name()}}.on('overlayremove', function (eventLayer) {
        #         if (eventLayer.layer == {{this.layer.get_name()}}) {
        #             {{this.colormap.get_name()}}.svg[0][0].style.display = 'none';
        #         }});
        # {% endmacro %}
        # """)  # noqa

        # For base layers:
        self._template = Template(u"""
        {% macro script(this, kwargs) %}
            {{this.colormap.get_name()}}.svg[0][0].style.display = 'block';
            {{this._parent.get_name()}}.on('layeradd', function (eventLayer) {
                if (eventLayer.layer == {{this.layer.get_name()}}) {
                    {{this.colormap.get_name()}}.svg[0][0].style.display = 'block';
                }});
            {{this._parent.get_name()}}.on('layerremove', function (eventLayer) {
                if (eventLayer.layer == {{this.layer.get_name()}}) {
                    {{this.colormap.get_name()}}.svg[0][0].style.display = 'none';
                }});
        {% endmacro %}
        """)  # noqa


def draw_catchment_IVT_on_map(clinic_map, fg=None, which_map=0):
    if fg is None:
        fg = folium.FeatureGroup(name='Nearest IVT hospitals', show=False)
    dir = './data_maps/lsoa_nearest_hospital/'
    import os
    files = os.listdir(dir)
    files = [file for file in files if '_MT_' not in file]
    for file in files:
        with open(dir + file) as f:
            geojson = json.load(f)
        fg.add_child(
            folium.GeoJson(
                data=geojson,
                # popup=GeoJsonPopup(
                #     fields=['LSOA11NM'],
                #     aliases=[''],
                #     localize=True
                #     ),
                # name='LSOA outlines',
                style_function=lambda y: {
                        'fillColor': 'rgba(0, 0, 0, 0)',
                        'color': 'rgba(255, 255, 255, 255)',
                        'weight': 1.0,
                    },
                highlight_function=lambda y: {
                    'weight': 2.0,
                    'fillColor': 'rgba(255, 255, 255, 127)'
                    },  # highlight_function / hover_dict
                # smooth_factor=1.5,  # 2.0 is about the upper limit here
                # show=False
                )
        )

    if which_map == 0:
        fg.add_to(clinic_map)
    elif which_map == 1:
        fg.add_to(clinic_map.m1)
    elif which_map == 2:
        fg.add_to(clinic_map.m2)
    # fg.add_to(clinic_map)
    return fg, clinic_map


def draw_catchment_MT_on_map(clinic_map, fg=None, which_map=0):
    if fg is None:
        fg = folium.FeatureGroup(name='Nearest MT hospitals', show=False)
    dir = './data_maps/lsoa_nearest_hospital/'
    import os
    files = os.listdir(dir)
    files = [file for file in files if '_MT_' in file]
    for file in files:
        with open(dir + file) as f:
            geojson = json.load(f)
        fg.add_child(
            folium.GeoJson(
                data=geojson,
                # popup=GeoJsonPopup(
                #     fields=['LSOA11NM'],
                #     aliases=[''],
                #     localize=True
                #     ),
                # name='LSOA outlines',
                style_function=lambda y: {
                        'fillColor': 'rgba(0, 0, 0, 0)',
                        'color': 'rgba(127, 0, 0, 255)',
                        'weight': 3.0,
                        # 'dashArray': '5, 5'
                    },
                highlight_function=lambda y: {
                    'weight': 5.0,
                    'fillColor': 'rgba(127, 0, 0, 127)'
                    },  # highlight_function / hover_dict
                # smooth_factor=1.5,  # 2.0 is about the upper limit here
                # show=False
                )
        )

    if which_map == 0:
        fg.add_to(clinic_map)
    elif which_map == 1:
        fg.add_to(clinic_map.m1)
    elif which_map == 2:
        fg.add_to(clinic_map.m2)
    # fg.add_to(clinic_map)
    return fg, clinic_map


# ###########################
# ##### START OF SCRIPT #####
# ###########################
page_setup()

# Title:
st.markdown('# Cloud-optimised GeoTiff')

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

# Load data files
# Hospital info
df_hospitals = pd.read_csv("./data_maps/stroke_hospitals_22_reduced.csv")

tiff_file_strings = [
    f'drip~ship~nlvo~ivt~{outcome_type}',
    f'mothership~nlvo~ivt~{outcome_type}',
    f'mothership~minus~dripship~nlvo~ivt~{outcome_type}',
    f'drip~ship~lvo~mt~{outcome_type}',
    f'mothership~lvo~mt~{outcome_type}',
    f'mothership~minus~dripship~lvo~mt~{outcome_type}',
]

cog_files = [
    f'data_maps/LSOA_{s}_cog.tif'
    for s in tiff_file_strings
]

layer_names = [
    # nLVO
    'Drip and ship',  # 'Drip and ship IVT nLVO added utility',
    'Mothership',  # 'Mothership IVT/nLVO added utility',
    'Advantage of Mothership',  # nLVO advantage of Mothership (added utility)',
    # LVO
    'Drip and ship',  # 'Drip and ship IVT/MT LVO added utility',
    'Mothership',  # 'Mothership MT IVT/LVO added utility',
    'Advantage of Mothership',  # 'LVO advantage of Mothership (added utility)'
]


if outcome_type == 'added~utility':
    outcome_cbar_dict = dict(
        min=0.0261,
        max=0.1759,
        cmap='inferno',
        cbar_label='Added utility'
    )

    diff_cbar_dict = dict(
        min=-0.09620000000000009,
        max=0.09620000000000009,
        cmap='bwr_r',
        cbar_label='Advantage of Mothership (added utility)'
    )

elif outcome_type == 'mean~shift':
    outcome_cbar_dict = dict(
        min=-0.89,
        max=-0.1,
        cmap='inferno_r',
        cbar_label='mRS shift; negative is better'
    )

    diff_cbar_dict = dict(
        min=-0.51,
        max=0.51,
        cmap='bwr',
        cbar_label='Advantage of Mothership (mRS shift; negative is better)'
    )


elif outcome_type == 'mrs<=2':
    outcome_cbar_dict = dict(
        min=0.29,
        max=0.7,
        cmap='inferno',
        cbar_label='mRS <= 2'
    )

    diff_cbar_dict = dict(
        min=-0.10000000000000003,
        max=0.10000000000000003,
        cmap='bwr_r',
        cbar_label='Advantage of Mothership (mRS <= 2)'
    )

time4 = datetime.now()

with st.spinner(text='Drawing map'):
    draw_map_tiff(
        # myarray_colours,
        # geojson_list,
        df_hospitals,
        cog_files,
        layer_names,
        outcome_cbar_dict,
        diff_cbar_dict,
        savename=f'html_dualmap_{outcome_type}.html'
        )

time5 = datetime.now()

st.write('Time to draw map:', time5 - time4)
