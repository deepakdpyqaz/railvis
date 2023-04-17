import numpy as np
import base64
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
from utils import read_csv, build_station_map, get_img_as_base64

st.set_page_config(page_title="Indian Railways", page_icon=":train:")

img = get_img_as_base64("4.jpg")
page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
# background-image: url("https://www.shutterstock.com/image-illustration/background-composition-lights-fractal-custom-600w-147776588.jpg");
background-image: url("data:image/png;base64,{img}");
background-size: 110%;
height:100%;
background-position: top left;
background-repeat: no-repeat;
# background-attachment: local;
}}

[data-testid="stHeader"] {{
background: rgba(0,0,0,0);
}}

[data-testid="stToolbar"] {{
right: 2rem;
}}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)


# Set Title
st.title("Indian Railways")

# First Para Information
st.write(
    "Indian Railways is the largest railway network in Asia and the fourth largest in the world, connecting over 7,000 stations across India. It is owned and operated by the Indian government and serves millions of passengers every day, offering a range of services from local trains to long-distance express trains. Indian Railways has played a crucial role in connecting people across the country and has been instrumental in the economic growth of India. The railway network has undergone significant modernization and expansion in recent years, with the introduction of high-speed trains, electrification of routes, and implementation of digital technologies."
)


# Second Para Map view of all stations
st.subheader("Map View of railway stations in India")
df = read_csv("data/geo.csv")
build_station_map(df)


# Third Para Data Analysis
st.subheader("Data Analysis")
st.write(
    "Indian Railways generates an enormous amount of data on a daily basis, including information on train schedules, ticket bookings, passenger traffic, freight traffic, and more. This data can be analyzed to identify trends and patterns, optimize operations, and improve customer service. For example, predictive analytics can be used to forecast demand for specific trains and routes, while machine learning algorithms can help identify potential maintenance issues before they cause disruptions. Additionally, data analysis can help Indian Railways improve safety and security by identifying potential security threats and enhancing the effectiveness of security measures. With the advent of digital technologies, Indian Railways is increasingly leveraging data analytics to drive efficiencies and enhance the overall customer experience. Currently we are showing an anlaysis of data having approxiamately 600 trains and 1200 railway stations."
)

data = read_csv("data/full_data.csv")

# Display data visualization
st.write("Chart showing the number of trains on particular station")
st.line_chart(data.groupby("station")["train_number"].count(), height=500)
