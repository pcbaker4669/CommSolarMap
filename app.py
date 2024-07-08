import math
import matplotlib.pyplot as plt
import matplotlib as mpl
import geopandas as gpd
import streamlit as st
import mplcursors

# Import your custom modules
import load_data as ld
import plant_info as pi

# Set GDAL configuration options
from pyogrio import set_gdal_config_options
set_gdal_config_options({
    'SHAPE_RESTORE_SHX': 'YES',
})

# Load the shapefile
states = gpd.read_file('data/cb_2018_us_state_500k.shp')
states = states.to_crs("EPSG:4326")

# Filter out Hawaii and Alaska
states = states[~states['STUSPS'].isin(['HI', 'AK'])]

# Normalize and color map setup
norm = mpl.colors.Normalize(vmin=0, vmax=math.log10(2000000), clip=True)
mapper = mpl.cm.ScalarMappable(norm=norm, cmap='coolwarm')

# Load data
df_arr = ld.load_data()
plant_arr = pi.load_plant_array(df_arr)
ll_df = ld.load_lat_lngs()
plant_arr = pi.match_lat_lngs(plant_arr, ll_df)

# Initialize scatter plot data containers
lats_arr = []
lngs_arr = []
cap_arr = []
city_arr = []
tot_cap = 0

# Function to update the plot data for each year
def update_plot_data(year):
    global tot_cap
    for obj in plant_arr:
        obj_year = obj.get_year()
        state = obj.get_state()
        if obj_year == year and not (state == 'AK' or state == 'HI'):
            lats_arr.append(obj.get_lat())
            lngs_arr.append(obj.get_lng())
            s = "{}, {}, {:.3f}(MW-AC)".format(obj.get_city(), state, obj.get_capacity_mw())
            city_arr.append(s)
            tot_cap += obj.get_capacity_mw()
            cap_arr.append(math.log10(obj.get_capacity_kw()))

# Function to redraw the plot
def redraw_plot(year):
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    states.boundary.plot(ax=ax, color='green', linewidth=1)
    ax.axis('off')
    ax.set_aspect('auto')
    ax.set_xlim(-125, -65)
    ax.set_ylim(24, 50)
    tl_str = "Community Solar 2006-2024"
    ax.set_title(tl_str, fontsize=18, color='green', weight='bold')

    color_map = [mapper.to_rgba(i) for i in cap_arr]
    points = ax.scatter(lngs_arr, lats_arr, c=color_map)

    tx_str = f"Year: {year}\nLocations: {len(lngs_arr)}\nTotal MW-AC: {tot_cap:.1f}"
    ax.text(-127, 25, tx_str, fontsize=17, color='green', weight='bold')
    # Add color bar
    cbar = plt.colorbar(mapper, ax=ax, orientation='vertical', fraction=0.036, pad=0.04)
    cbar.set_label('Log(Capacity) kW-AC', fontsize=12)

    # Add mplcursors hover functionality
    cursor = mplcursors.cursor(points, hover=True)

    @cursor.connect("add")
    def on_add(sel):
        sel.annotation.set_text(city_arr[sel.index])

    st.pyplot(fig)

# Streamlit app setup
st.title("Community Solar 2006-2024 in Contiguous States")
year_slider = st.slider("Select Year", 2006, 2024, 2024)

# Initialize data for the selected year
lats_arr.clear()
lngs_arr.clear()
cap_arr.clear()
city_arr.clear()
tot_cap = 0
for y in range(2006, year_slider + 1):
    update_plot_data(y)

# Redraw the plot based on the selected year
redraw_plot(year_slider)
