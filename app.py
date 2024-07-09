import math
import pandas as pd
import geopandas as gpd
import streamlit as st
import plotly.express as px

# Import your custom modules
import load_data as ld
import plant_info as pi

# Set GDAL configuration options
from pyogrio import set_gdal_config_options
set_gdal_config_options({
    'SHAPE_RESTORE_SHX': 'YES',
})

# Load the shapefile once and cache it
@st.cache_data
def load_shapefile():
    states = gpd.read_file('data/cb_2018_us_state_500k.shp')
    return states.to_crs("EPSG:4326")

states = load_shapefile()

# Filter out Hawaii and Alaska
# states = states[~states['STUSPS'].isin(['HI', 'AK'])]

# Load data once and cache it
@st.cache_data
def load_data():
    df_arr = ld.load_data()
    plant_arr = pi.load_plant_array(df_arr)
    ll_df = ld.load_lat_lngs()
    return pi.match_lat_lngs(plant_arr, ll_df)

plant_arr = load_data()

# Function to update the plot data for each year
def update_plot_data(year):
    lats_arr = []
    lngs_arr = []
    cap_arr = []
    city_arr = []
    tot_cap = 0

    for obj in plant_arr:
        obj_year = obj.get_year()
        state = obj.get_state()
        if obj_year == year: # and not (state == 'AK' or state == 'HI'):
            lats_arr.append(obj.get_lat())
            lngs_arr.append(obj.get_lng())
            s = "{}, {}, {:.3f}(MW-AC)".format(obj.get_city(), state, obj.get_capacity_mw())
            city_arr.append(s)
            tot_cap += obj.get_capacity_mw()
            cap_arr.append(math.log10(obj.get_capacity_kw()))

    return lats_arr, lngs_arr, cap_arr, city_arr, tot_cap

# Function to create the plot
def create_plot(year):
    lats_arr, lngs_arr, cap_arr, city_arr, tot_cap = [], [], [], [], 0
    for y in range(2006, year + 1):
        lats, lngs, caps, cities, total_capacity = update_plot_data(y)
        lats_arr.extend(lats)
        lngs_arr.extend(lngs)
        cap_arr.extend(caps)
        city_arr.extend(cities)
        tot_cap += total_capacity

    # Create a DataFrame for Plotly
    data = pd.DataFrame({
        'Latitude': lats_arr,
        'Longitude': lngs_arr,
        'City_State': city_arr,
        'Capacity_Log': cap_arr
    })

    fig = px.scatter_geo(
        data,
        lat='Latitude',
        lon='Longitude',
        hover_name='City_State',

        color='Capacity_Log',
        color_continuous_scale='Viridis',
        projection='albers usa',
        title=f"Community Solar Progress {year}"
    )

    fig.update_geos(
        visible=True,
        resolution=110,
        scope="usa",
        showcountries=True,
        countrycolor="Black",
        showsubunits=True,
        subunitcolor="Blue"
    )

    fig.update_layout(
        margin={"r":0,"t":30,"l":0,"b":0},
        title_x=0.5,
        coloraxis_colorbar={
            'title': 'Log Capacity (kW-AC)',
            'lenmode': 'fraction',
            'len': 0.75,
            'yanchor': 'middle',
            'y': 0.5
        }
    )

    return fig

# Streamlit app setup
st.title("Community Solar 2006-2024 in Contiguous States")
year_slider = st.slider("Select Year", 2006, 2024, 2024)

# Create and display the plot based on the selected year
fig = create_plot(year_slider)
st.plotly_chart(fig, use_container_width=True)
