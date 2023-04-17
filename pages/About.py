import streamlit as st
import base64
from utils import get_img_as_base64, load_image
import os
# Set up the page layout
st.set_page_config(page_title="Services", page_icon=":train:", layout="wide")

st.header("Features of the website")
st.subheader("Data Visualization")
col1, col2 = st.columns([2,1])
with col1:
    st.write(open("text/visualization.txt").read())
with col2:
    st.image(load_image("img/visualization.jpeg"), use_column_width=True, caption="Data Visualization")

st.subheader("Station Analysis")
st.write(open("text/station_analysis.txt").read())
st.image(load_image("img/5.jpg"),  use_column_width=True, caption="Station Analysis")

st.subheader("Train Analysis")
st.write(open("text/train.txt").read())
st.image(load_image("img/1.png"),  use_column_width=True, caption="Station Analysis")