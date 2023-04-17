import pandas as pd
import streamlit as st
import altair as alt
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import altair as alt
from utils import read_csv

# Read the CSV file
df = read_csv("data/full_data.csv")

st.header("Station Analysis")

@st.cache_data
def get_unique_stations():
    return df["station"].unique()
# Add multiselect to select stations
station_options = get_unique_stations()
selected_stations = st.multiselect("Select Stations", station_options)

# Filter data by selected stations
filtered_data = df[df["station"].isin(selected_stations)]
st.write("")
st.write("")
# Display data visualization
st.subheader("Data Visualization")
st.write("")
st.write("")
st.write("")
cols1, cols2 = st.columns(2)
# Add padding between the columns
cols1.markdown(
    """
    <style>
        div.stHorizontal {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
        }
        .css-1aumxhk {
            margin-right: 20px;
            margin-bottom: 20px;
        }
    </style>
""",
    unsafe_allow_html=True,
)

with cols1:
    # Group the data by station and count the number of train numbers
    count_by_station = (
        filtered_data.groupby("station")["train_number"].count().reset_index()
    )

    # Create a bar chart using Altair
    chart = (
        alt.Chart(count_by_station)
        .mark_bar()
        .encode(x="station", y="train_number", tooltip=["station", "train_number"])
        .properties(title="Train Counts by Station")
    )

    # Display the chart in the Streamlit app
    st.altair_chart(chart, use_container_width=True)

with cols2:
    # group by station name and calculate the average delay
    avg_month_3_per_station = (
        filtered_data.groupby("station")["month_3"].mean().reset_index()
    )

    # sort the stations in descending order based on the percentage of journeys in the first quarter of the year
    avg_month_3_per_station = avg_month_3_per_station.sort_values(
        "month_3", ascending=False
    )

    # create a bar chart using Altair
    chart = (
        alt.Chart(avg_month_3_per_station)
        .mark_bar()
        .encode(
            x=alt.X("station", sort="-y"),
            y="month_3:Q",
            color=alt.Color("month_3", scale=alt.Scale(scheme="greens")),
            tooltip=["station", "month_3:Q"],
        )
        .properties(
            title="Average Delay in 3 month on particular Stations",
            width=400,
            height=400,
        )
    )

    # display the chart in the streamlit app
    st.altair_chart(chart)

# -------------------------
box_chart = (
    alt.Chart(filtered_data)
    .mark_boxplot()
    .encode(x="type", y="train_delay_level", color="type")
    .properties(title="Distribution of Delays by Train Type")
)

st.altair_chart(box_chart, use_container_width=True)


# ------------------------- Plotting top 10 busiest train stations -------------------------

@st.cache_data
def get_unique_trains_per_station():
    # Calculate the number of unique trains for each station
    unique_trains_per_station = (
        df.groupby("station")["train_number"].nunique().reset_index()
    )
    unique_trains_per_station = unique_trains_per_station.sort_values(
        "train_number", ascending=False
    ).reset_index(drop=True)
    unique_trains_per_station.index = unique_trains_per_station.index + 1
    return unique_trains_per_station

# # Display the top 10 busiest train stations
st.write("Top 10 stations with most trains visiting:")
unique_trains_per_station = get_unique_trains_per_station()
st.table(unique_trains_per_station.head(10))

# Display a bar chart showing the number of unique trains for each station
bar_chart = (
    alt.Chart(unique_trains_per_station)
    .mark_bar()
    .encode(
        x=alt.X("station", sort="-y"),
        y="train_number",
        color=alt.Color("train_number", scale=alt.Scale(scheme="reds")),
        tooltip=["station", "train_number"],
    )
    .properties(width=800, height=400, title="Number of Trains per Station")
)
st.write(bar_chart)


st.header("Station Delay Analysis")

# Compute average delay per station
avg_delays = df.groupby("station")["station_delay_level"].mean().reset_index()

# Create chart using Altair
chart = (
    alt.Chart(avg_delays)
    .mark_bar()
    .encode(
        x=alt.X("station", sort="-y"),
        y="station_delay_level",
        tooltip=["station", "station_delay_level"],
    )
    .properties(width=800, height=500, title="Average Delay by Station")
)

# Display chart
st.altair_chart(chart, use_container_width=True)

# -----------------------

# chart_data = filtered_data.groupby(["year", "month"])["month_3"].mean().reset_index()
# line_chart = (
#     alt.Chart(chart_data)
#     .mark_line()
#     .encode(
#         x="month:T",
#         y="month_3:Q",
#         color=alt.Color("year:N"),
#         tooltip=["year", "month", alt.Tooltip("month_3:Q", format=".2f")],
#     )
#     .properties(width=600, height=300, title="Trend of Delay over Time")
# )
# st.altair_chart(line_chart)


