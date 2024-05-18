import pandas as pd
import geopandas as gpd
import folium
import random
from folium import Choropleth, GeoJsonTooltip
import json

# Paths to the uploaded shapefile components
shapefile_path = "shapefile/state/tl_2020_us_state.shp"
shx_path = "shapefile/state/tl_2020_us_state.shx"
dbf_path = "shapefile/state/tl_2020_us_state.dbf"

# Load the shapefile using GeoPandas
gdf = gpd.read_file(shapefile_path)

# Assign each state a random number from 1 to 100
gdf["random_value"] = [random.randint(1, 100) for _ in range(len(gdf))]

# Initialize a Folium map
m = folium.Map(location=[37.8, -96], zoom_start=4)

# Create a Choropleth map
choropleth = Choropleth(
    geo_data=gdf.to_json(),
    data=gdf,
    columns=["STUSPS", "random_value"],
    key_on="feature.properties.STUSPS",
    fill_color="YlGnBu",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Random Values from 1 to 100"
).add_to(m)

# Add labels to show the random values on hover
tooltip = GeoJsonTooltip(
    fields=['STUSPS', 'random_value'],
    aliases=['State: ', 'Random Value: '],
    localize=True
)
folium.GeoJson(
    gdf.to_json(),
    style_function=lambda x: {'fillColor': 'transparent', 'color': 'transparent', 'weight': 0},
    tooltip=tooltip
).add_to(m)

# Save the map to an HTML file
output_html = "us_states_random_values.html"
m.save(output_html)