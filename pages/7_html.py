import streamlit as st
from datetime import datetime

from utilities_maps.fixed_params import page_setup


@st.cache_data
def load_map_added_utility(path_to_html):
    with open(path_to_html, 'r') as f:
        html_data = f.read()
    return html_data


@st.cache_data
def load_map_mean_shift(path_to_html):
    with open(path_to_html, 'r') as f:
        html_data = f.read()
    return html_data


@st.cache_data
def load_map_mrs_leq2(path_to_html):
    with open(path_to_html, 'r') as f:
        html_data = f.read()
    return html_data


@st.cache_resource
def draw_map_added_utility(html_data):
    return st.components.v1.html(html_data, height=600)


@st.cache_resource
def draw_map_mean_shift(html_data):
    return st.components.v1.html(html_data, height=600)


@st.cache_resource
def draw_map_mrs_leq2(html_data):
    return st.components.v1.html(html_data, height=600)


# ###########################
# ##### START OF SCRIPT #####
# ###########################
page_setup()

# Title:
st.markdown('# Load map from HTML')


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
path_to_html = f'./html_dualmap_{outcome_type}.html'
# path_to_html = './html_dual_test.html'
# path_to_html = 'https://github.com/samuel-book/streamlit_map_lsoa_outcomes/blob/main/html_test.html'

if outcome_type == 'added~utility':
    html_data = load_map_added_utility(path_to_html)
elif outcome_type == 'mean~shift':
    html_data = load_map_mean_shift(path_to_html)
elif outcome_type == 'mrs<=2':
    html_data = load_map_mrs_leq2(path_to_html)

cols = st.columns(2)
with cols[0]:
    st.markdown('## nLVO')
with cols[1]:
    st.markdown('## LVO')

time4 = datetime.now()

with st.spinner(text='Drawing map'):
    if outcome_type == 'added~utility':
        draw_map_added_utility(html_data)
    elif outcome_type == 'mean~shift':
        draw_map_mean_shift(html_data)
    elif outcome_type == 'mrs<=2':
        draw_map_mrs_leq2(html_data)


time5 = datetime.now()
st.write('Time to draw map:', time5 - time4)
