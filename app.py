
# --------------------------------------------
# Imports at the top - PyShiny EXPRESS VERSION
# --------------------------------------------

# From shiny, import just reactive and render
from shiny import reactive, render

# From shiny.express, import just ui
from shiny.express import ui

# Imports from Python Standard Library to simulate live data
import random
from datetime import datetime
from collections import deque
import pandas as pd
import plotly.express as px
from shinywidgets import render_plotly
from scipy import stats


# --------------------------------------------
# Import icons as you like
# --------------------------------------------

from faicons import icon_svg

# --------------------------------------------
# FOR LOCAL DEVELOPMENT
# --------------------------------------------
# Add all packages not in the Std Library
# to requirements.txt:
#
# faicons
# shiny
# shinylive
# 
# And install them into an active project virtual environment (usually in .venv)
# --------------------------------------------

# --------------------------------------------
# SET UP THE REACIVE CONTENT
# --------------------------------------------

# --------------------------------------------
# PLANNING: We want to get a fake temperature and 
# Time stamp every N seconds. 
# For now, we'll avoid storage and just 
# Try to get the fake live data working and sketch our app. 
# We can do all that with one reactive calc.
# Use constants for update interval so it's easy to modify.
# ---------------------------------------------------------

# --------------------------------------------
# First, set a constant UPDATE INTERVAL for all live data
# Constants are usually defined in uppercase letters
# Use a type hint to make it clear that it's an integer (: int)
# --------------------------------------------

UPDATE_INTERVAL_SECS: int = 5

# --------------------------------------------
# Initialize a REACTIVE VALUE with a common data structure
# The reactive value is used to store state (information)
# Used by all the display components that show this live data.
# This reactive value is a wrapper around a DEQUE of readings
# --------------------------------------------

DEQUE_SIZE: int = 8
reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))
# --------------------------------------------
# Initialize a REACTIVE CALC that our display components can call
# to get the latest data and display it.
# The calculation is invalidated every UPDATE_INTERVAL_SECS
# to trigger updates.
# It returns everything needed to display the data.
# Very easy to expand or modify.
#
# --------------------------------------------


@reactive.calc()
def reactive_calc_combined():
    # Invalidate this calculation every UPDATE_INTERVAL_SECS to trigger updates
    reactive.invalidate_later(UPDATE_INTERVAL_SECS)

    # Data generation logic. Get random between -18 and -16 C, rounded to 1 decimal place
    temp = round(random.uniform(-18, -16), 1)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_dictionary_entry = {"temp": temp, "timestamp": timestamp}

     # get the deque and append the new entry
    reactive_value_wrapper.get().append(new_dictionary_entry)

    # Get a snapshot of the current deque for any further processing
    deque_snapshot = reactive_value_wrapper.get()

    # For Display: Convert deque to DataFrame for display
    df = pd.DataFrame(deque_snapshot)

    # For Display: Get the latest dictionary entry
    latest_dictionary_entry = new_dictionary_entry

    # Return a tuple with everything we need
    # Every time we call this function, we'll get all these values
    return deque_snapshot, df, latest_dictionary_entry

# ------------------------------------------------
# Define the Shiny UI Page layout - Page Options
# ------------------------------------------------

# Call the ui.page_opts() function
# Set title to a string in quotes that will appear at the top
# Set fillable to True to use the whole page width for the UI

ui.page_opts(title="PyShiny Express: Live Data (Basic)", fillable=True)

# ------------------------------------------------
# Define the Shiny UI Page layout - Sidebar
# ------------------------------------------------

# Sidebar is typically used for user interaction/information
# Note the with statement to create the sidebar followed by a colon
# Everything in the sidebar is indented consistently

with ui.sidebar(open="open"):

    ui.h2("Antarctic Explorer", class_="text-center")

    ui.p(
        "A demonstration of real-time temperature readings in Antarctica.",
        class_="text-center",
    )

    ui.hr()

    ui.h6("Links:")

    ui.a(
        "GitHub Source",
        href="https://github.com/mkunta1/cintel-05-cintel",
        target="_blank",
    )
    ui.a("PyShiny", href="https://shiny.posit.co/py/", target="_blank")
    ui.a(
        "PyShiny Express",
        href="https://shiny.posit.co/blog/posts/shiny-express/",
        target="_blank",
    )


#---------------------------------------------------------------------
# In Shiny Express, everything not in the sidebar is in the main panel
#---------------------------------------------------------------------
    
with ui.layout_columns():
    # Changed theme and colors for value box
    with ui.value_box(
        showcase=icon_svg("snowflake"),
        theme="bg-gradient-yellow",  # Gradient theme
    ):

        "Current Temperature"

        @render.text
        def display_temp():
            """Get the latest reading and return a temperature string"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            current_temp = latest_dictionary_entry['temp']
        
            if current_temp < -17:
               message = "Very Cold!"
            elif -17 <= current_temp < -16:
               message = "Cold!"
            else:
               message = "Just Above Freezing!"

            return f"{current_temp} °C - {message}"

    # Changed the card background color
    with ui.card(full_screen=True, theme="bg-gradient-blue-purple"):
        ui.card_header("Current Date and Time")

        @render.text
        def display_time():
            """Get the latest reading and return a timestamp string"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['timestamp']}"

#with ui.card(full_screen=True, min_height="40%"):
with ui.card(full_screen=True, theme="bg-gradient-red-yellow"):
    ui.card_header("Most Recent Readings")

    @render.data_frame
    def display_df():
        """Get the latest reading and return a dataframe with current readings"""
        deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
        pd.set_option('display.width', None)        # Use maximum width
        return render.DataGrid( df,width="100%")

with ui.card(theme="bg-gradient-blue-green"):
    ui.card_header("Temperature Distribution")

    @render_plotly
    def display_plot():
        # Fetch from the reactive calc function
        deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()

        # Ensure the DataFrame is not empty before plotting
        if not df.empty:
            # Convert the 'timestamp' column to datetime for better plotting
            df["timestamp"] = pd.to_datetime(df["timestamp"])

            # Create histogram for temperature readings
            # Use 'temp' as the variable for the x-axis
            fig = px.histogram(df,
                x="temp",
                nbins=10,  # Adjust number of bins
                title="Temperature Distribution",
                labels={"temp": "Temperature (°C)"},
                color_discrete_sequence=["#007bff"],  # Color of the bars
                template="plotly_white"  # Dark theme for the plot
            )

            # Update layout as needed
            fig.update_layout(
                xaxis_title="Temperature (°C)",
                yaxis_title="Frequency",
                bargap=0.1  # Gap between bars
            )

        return fig
