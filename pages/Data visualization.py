import streamlit as st
import pandas as pd
import altair as alt
from matplotlib import pyplot as plt
import seaborn as sns
import math
from utils import read_csv

pi = math.pi


st.set_option("deprecation.showPyplotGlobalUse", False)

df = read_csv("data/data.csv")
full_data = read_csv("data/full_data.csv")
st.header("Exploratory Data Analysis")


st.subheader("Mostly trains travel less than 1000 km")

chart_data = df.groupby("number")["distance"].sum().reset_index()

chart = (
    alt.Chart(chart_data)
    .mark_line()
    .encode(x="number", y="distance")
    .properties(
        width=800, height=400  # Set the width in pixels  # Set the height in pixels
    )
)

st.altair_chart(chart)

# ------------------------
# Filter data for relevant columns
st.subheader("Plot showing distance duration relationship of various delay levels")
@st.cache_data
def get_delay_level_data():
    delay_data = full_data[["train_number","distance", "duration", "train_delay_level"]].groupby("train_number").mean().reset_index(drop=True)
    return delay_data


scatterplot_data = get_delay_level_data()
# Create scatterplot matrix using Altair
scatterplot_matrix = (
    alt.Chart(scatterplot_data)
    .mark_point()
    .encode(
        alt.X("distance"),
        alt.Y("duration"),
        color="train_delay_level:N",
    )
    .repeat(row=["distance"], column=["duration"])
)

# Display scatterplot matrix in Streamlit app
st.altair_chart(scatterplot_matrix, use_container_width=True)


st.subheader("Plot showing average distance travelled by various types of trains")
df2 = df[["type", "distance"]].groupby("type").mean().reset_index()

chart = (
    alt.Chart(df2)
    .mark_bar()
    .encode(
        x=alt.X(
            "type", axis=alt.Axis(labelAngle=90)
        ),  # Set the x-axis label and rotate it 90 degrees
        y="distance",  # Set the y-axis label
        color=alt.Color(
            "type", legend=None
        ),  # Set the color to differentiate between bars
    )
    .properties(
        width=800, height=400  # Set the width in pixels  # Set the height in pixels
    )
)

st.altair_chart(chart)


# Create a scatter plot showing the relationship between distance and duration
st.subheader("The relationship between distance and duration and type of train")
chart = (
    alt.Chart(df)
    .mark_point()
    .encode(x="distance", y="duration", color="type")
    .properties(width=800, height=400)
)

# Create a line chart showing the change in the number of trains over time
st.subheader("The change in the number of trains over time")
line_data = df.groupby("arrival")["number"].count().reset_index()
line_data["arrival"] = pd.to_datetime(line_data["arrival"])
line_chart = (
    alt.Chart(line_data)
    .mark_line()
    .encode(x="arrival", y="number")
    .properties(width=800, height=400)
)
# Display the line chart in Streamlit
st.altair_chart(line_chart)


st.header("Plot showing the types of seats available in various types of trains")
st.subheader(
    "100% of GR trains have third AC, 100% of Mail trains have sleeper and 95% of JShtb have chair_car"
)

df2 = (
    df[
        [
            "type",
            "first_class",
            "first_ac",
            "second_ac",
            "third_ac",
            "sleeper",
            "chair_car",
        ]
    ]
    .groupby("type")
    .mean()
)
sns.heatmap(df2, annot=True, fmt=".1%")
plt.xlabel("Types of seats")
plt.ylabel("Types of trains")
st.pyplot()

# -------------------------------

st.header("Plot showing the split of trains accross various zones")
st.subheader("Plot shows that the NR, WR, and SR occupies the major portion")
colors = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
]  # define your colors here
data = df["zone"].value_counts()
plt.pie(data, labels=data.index, colors=colors, autopct="%.0f%%")
st.pyplot()


# --------------------------------

st.header("Plot showing the distance trains travel in various zones")
st.subheader(" Trains in NFR zone travel more distances")
boxplot = (
    alt.Chart(df)
    .mark_boxplot()
    .encode(
        y=alt.Y("distance:Q", title="Distance (In Kms)"),
        x=alt.X("zone:N", title="Zones"),
    )
    .properties(width=600, height=400)
)

st.altair_chart(boxplot)

df_long = pd.melt(df, id_vars=["zone"], value_vars=["distance"])
