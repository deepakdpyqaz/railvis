import streamlit as st
import pandas as pd
import time
import folium
from streamlit_folium import folium_static
import joblib
import base64
from PIL import Image

@st.cache_data(show_spinner="Loading data...", persist=True)
def read_csv(file):
    return pd.read_csv(file)


@st.cache_data(show_spinner="Building map...", persist=True, max_entries=50)
def build_station_map(df, route=False):
    m = folium.Map(
        location=[df.latitude.mean(), df.longitude.mean()],
        zoom_start=5,
        control_scale=True,
    )
    for i, row in df.iterrows():
        # Setup the content of the popup
        iframe = folium.IFrame(f'{row["name"]} ({row["code"]})', width=100, height=100)

        # Initialise the popup using the iframe
        popup = folium.Popup(iframe, min_width=100, max_width=100)

        # Add each row to the map
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            popup=popup,
            c=row["name"],
        ).add_to(m)

    if route:
        folium.PolyLine(
            locations=df[["latitude", "longitude"]].values.tolist(),
            color="cadetblue",
            weight=2.5,
            opacity=1,
        ).add_to(m)
    st_data = folium_static(m, width=700)


@st.cache_data
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

@st.cache_data
def load_image(file):
    return Image.open(file)

@st.cache_resource(show_spinner="Loading model...")
def load_model(path):
    return joblib.load(path)
