import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="DOL - OSHA Dashboard",
    layout="wide",
)

path_to_html = "sample-data-map.html" 

# Read file and keep in variable
with open(path_to_html,'r') as f: 
    html_data = f.read()

components.html(html_data,height=1000)
