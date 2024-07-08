import math
import time
import matplotlib.pyplot as plt
import matplotlib as mpl
import geopandas as gpd
from pyogrio import set_gdal_config_options
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplcursors

# Import your custom modules
import load_data as ld
import plant_info as pi

set_gdal_config_options({
    'SHAPE_RESTORE_SHX': 'YES',
})
# cursor = None
annotations = []


# Function to update the plot for each year
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


def redraw_plot(year):
    ax.clear()
    states.boundary.plot(ax=ax, color='green', linewidth=1)
    ax.axis('off')
    ax.set_aspect('auto')
    ax.set_xlim(-125, -65)
    ax.set_ylim(24, 50)
    tl_str = "Community Solar 2006-2024"
    ax.set_title(tl_str, fontsize=18, color='green', weight='bold')

    color_map = [mapper.to_rgba(i) for i in cap_arr]
    points = ax.scatter(lngs_arr, lats_arr, c=color_map)

    tx_str = f"Year: {year}\nLocs #: {len(lngs_arr)}\nTot Cap(MW-AC): {tot_cap:.1f}"
    ax.text(-127, 25, tx_str, fontsize=18, color='green',
            weight='bold')
    # Use mplcursors to add hover functionality

    cursor = mplcursors.cursor(points, hover=True)

    @cursor.connect("add")
    def on_add(sel):
        annotation = sel.annotation
        annotation.set_text(city_arr[sel.index])
        annotations.append(sel)
        # Schedule the annotation removal after 10 seconds
        root.after(5000, lambda: remove_selection(cursor, sel))

    canvas.draw()


def remove_selection(cursor, sel):
    try:
        cursor.remove_selection(sel)
        canvas.draw()
    except ValueError:
        pass  # Annotation was already removed

# Load the shapefile
states = gpd.read_file('cb_2018_us_state_500k')
states = states.to_crs("EPSG:4326")

# Filter out Hawaii and Alaska
states = states[~states['STUSPS'].isin(['HI', 'AK'])]

# Create a plot with adjusted figure size
fig, ax = plt.subplots(1, 1, figsize=(10, 6))
ax.axis('off')
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
current_year = 2024

# Create the Tkinter window
root = tk.Tk()
root.title("Community Solar 2006-2024 in Contiguous States")

# Create a canvas for the Matplotlib figure
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)


# Create a button to start the animation
def start_animation(change_year):
    global current_year
    current_year += change_year
    if current_year < 2006:
        current_year = 2024
    if current_year > 2024:
        current_year = 2006
    year_lbl.config(text=str(current_year))
    lats_arr.clear()
    lngs_arr.clear()
    cap_arr.clear()
    city_arr.clear()
    global tot_cap
    tot_cap = 0
    for y in range(2006, current_year+1):
        update_plot_data(y)
    redraw_plot(current_year)
    root.update_idletasks()


def exit_comm_sol():
    root.quit()


button_frame = tk.Frame(root)
back_button = tk.Button(button_frame, text="Back", command=lambda: start_animation(-1))
back_button.pack(side=tk.LEFT, padx=10, pady=2)
year_lbl = tk.Label(button_frame, text=str(current_year))
year_lbl.pack(side=tk.LEFT, padx=10, pady=2)
forward_button = tk.Button(button_frame, text="Forward", command=lambda: start_animation(1))
forward_button.pack(side=tk.LEFT, padx=10, pady=2)
button_frame.pack(side="bottom", pady=5)

# draw initial plot
for year in range(2006, current_year + 1):
    update_plot_data(year)
redraw_plot(current_year)

root.protocol("WM_DELETE_WINDOW", exit_comm_sol)
# Run the Tkinter main loop
root.mainloop()
