from goibibo import get_data
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
import joblib
from sklearn.ensemble import RandomForestRegressor
from pandas.api.types import CategoricalDtype
import re
import matplotlib.pyplot as plt
import altair as alt
import json
from utils import read_csv, build_station_map, load_model
import traceback

st.set_page_config(page_title="Train information", page_icon=":train:")


@st.cache_data(show_spinner=False)
def get_unique_trains():
    return [""] + train["name"].unique().tolist()


st.title("Train information")
geo = read_csv("data/geo.csv")
analysis = read_csv("data/analysis.csv")
train = read_csv("data/train.csv")
model = load_model("delay_pred.sav")
numeric = re.compile(r"\d+\.?\d*")


unique_trains = get_unique_trains()
train_name = st.selectbox("Select Train", unique_trains)


def extract_station_data(train_no, data):
    original_delays = {}
    extracted_station_data = {
        "code": [],
        "latitude": [],
        "longitude": [],
        "name": [],
    }
    df = analysis[analysis["train_number"] == train_no].copy()
    try:
        current_station = data["response"]["current_station"]["code"]
    except KeyError:
        current_station = None

    if data["error"] != "":
        for stn in data["response"]["data"]["train_schedule"]:
            code = stn["station_irctc_code"]

            row = geo[geo["code"] == code]
            latitude = row["latitude"].values[0]
            longitude = row["longitude"].values[0]
            name = row["name"].values[0]

            extracted_station_data["code"].append(code)
            extracted_station_data["latitude"].append(latitude)
            extracted_station_data["longitude"].append(longitude)
            extracted_station_data["name"].append(name)
    else:
        for station_data in data["response"]["station_data"]:
            for station in station_data["values"]:
                code = station["station"]["code"]
                original_delays[code] = float(
                    re.search(numeric, station["delay"]).group(0)
                )
                row = geo[geo["code"] == code]
                extracted_station_data["code"].append(code)
                extracted_station_data["latitude"].append(row["latitude"].values[0])
                extracted_station_data["longitude"].append(row["longitude"].values[0])
                extracted_station_data["name"].append(row["name"].values[0])
    station_data = pd.DataFrame(extracted_station_data)
    station_order = CategoricalDtype(
        categories=station_data.code.tolist(), ordered=True
    )
    df["station_code"] = df["station_code"].astype(station_order)
    df.sort_values("station_code", inplace=True)
    return station_data, df, original_delays, current_station


if train_name:
    try:
        train_no = train[train["name"] == train_name]["train_number"].values[0]
        # Train information
        st.subheader("Train information")
        try:
            train_info = (
                analysis[analysis["train_number"] == train_no].iloc[0, :].to_dict()
            )
            train_info["train_number"] = train_no
            train_info["train_name"] = train_name
            col1, col2 = st.columns(2)
            with col1:
                basic_info = {
                    "train_number": "Train Number",
                    "train_name": "Train Name",
                    "zone": "Zone",
                    "type": "Type",
                    "distance": "Distance (KMs)",
                    "duration": "Duration (mins)",
                }
                row_data = ""
                for key, label in basic_info.items():
                    if key == "duration":
                        train_info[key] = round(train_info[key] * 60)
                    row_data += f"<tr><td><strong>{label}</strong></td><td>{train_info[key]}</td></tr>"
                html_table = f"<table style='width:100%'>{row_data}</table>"
                st.write(html_table, unsafe_allow_html=True)

            def create_box(label, value):
                html = f"""
                <span style="display:inline-block; background:{"#228B22" if value else "#880808"}; color:#fff;padding: 2px 20px;  border-radius: 5px; margin: 10px;  box-shadow:inset 0px 0px 5px 1px #000;">
                        <p style="margin:0px">
                                {label}
                        </p>
                        <p style="margin: 0px; font-size:20px; text-align: center">
                                <strong>{"Yes" if value else "No"}</strong>
                        </p>
                </span>
                """
                return html

            with col2:
                coach_info = {
                    "first_ac": "First AC",
                    "second_ac": "Second AC",
                    "third_ac": "Third AC",
                    "sleeper": "Sleeper",
                    "chair_car": "Chair Car",
                    "first_class": "First Class",
                }
                html_content = []
                for key, label in coach_info.items():
                    html_content.append(create_box(label, train_info[key]))
                st.write("".join(html_content), unsafe_allow_html=True)

        except Exception as e:
            traceback.print_exc()
            st.error("No data available for this train")

        # Train Route Map
        st.subheader("Train Route")
        with st.spinner("Fetching realtime data..."):
            data = get_data(int(train_no))
            station_data, df, original_delays, current_station = extract_station_data(
                train_no, data
            )
            X = df[
                [
                    "third_ac",
                    "zone",
                    "chair_car",
                    "first_class",
                    "sleeper",
                    "second_ac",
                    "type",
                    "first_ac",
                    "distance",
                    "duration",
                    "month",
                    "month_3",
                    "month_6",
                    "year",
                    "train_delay_level",
                    "station_delay_level",
                ]
            ].copy()
            station_order = station_data.code.tolist()
            delays = model.predict(X)
            delay_order = dict(zip(station_order, delays))
            expected_delays = []
            mean_diff_delay = 0
            current_station_idx = 0
            if current_station is not None:
                for i, stn in enumerate(station_order):
                    try:
                        if i == 0:
                            mean_diff_delay = delay_order[stn] - original_delays[stn]
                            expected_delays.append(original_delays[stn])
                            if stn == current_station:
                                expected_delays = list(delay_order.values())
                                expected_delays[0] = original_delays[stn]
                                break
                        elif stn == current_station:
                            current_station_idx = i
                            for j in range(i, len(station_order)):
                                expected_delays.append(
                                    delay_order[station_order[j]] - mean_diff_delay
                                )
                            break
                        else:
                            expected_delays.append(delay_order[stn] - mean_diff_delay)
                            mean_diff_delay = (
                                mean_diff_delay * (i + 1)
                                + (delay_order[stn] - original_delays[stn])
                            ) / (i + 1)
                    except:
                        expected_delays.append(0)
                        if current_station == stn:
                            break
                expected_delays = [0 if x < 0 else x for x in expected_delays]
            else:
                expected_delays = list(delay_order.values())
        if data["error"] == "":
            st.info(data["message_struct"]["title"])
        else:
            st.error(data["message_struct"]["title"])
            st.info("Showing offline data")
        try:
            build_station_map(station_data, route=True)
            if current_station:
                st.markdown(
                    f"### Currently at **:green[{station_data[station_data['code']==current_station]['name'].values[0]}]**"
                )
            else:
                st.markdown("### :red[Cannot determine current station]")
        except:
            st.error("Map not available")

        # Delay Analysis
        try:
            station_name_order = CategoricalDtype(
                station_data.name.tolist(), ordered=True
            )
            st.subheader("Delay Analysis (in minutes)")
            if current_station:
                org_df = pd.DataFrame(
                    {
                        "Station Name": station_data.name.tolist()[
                            : current_station_idx + 1
                        ],
                        "Delay": list(original_delays.values())[
                            : current_station_idx + 1
                        ],
                    }
                )
                org_df = org_df.assign(source="Original")
                expected_df = pd.DataFrame(
                    {
                        "Station Name": station_data.name.tolist(),
                        "Delay": expected_delays,
                    }
                )
                expected_df = expected_df.assign(source="Predicted")
                new_df = pd.concat([org_df, expected_df])
            else:
                st.warning("Delay Prediction might not work well")
                expected_delays = [100 if x > 100 else x for x in expected_delays]
                expected_df = pd.DataFrame(
                    {
                        "Station Name": station_data.name.tolist(),
                        "Delay": expected_delays,
                    }
                )
                new_df = expected_df.assign(source="Predicted")

            new_df["Station Name"] = new_df["Station Name"].astype(station_name_order)
            new_df.sort_values("Station Name", inplace=True)
            new_df.reset_index(drop=True, inplace=True)
            original = (
                alt.Chart(new_df)
                .mark_line(point=True)
                .encode(
                    x=alt.X("Station Name", sort=list(station_name_order.categories)),
                    y="Delay",
                    color=alt.Color(
                        "source", legend=alt.Legend(title="", orient="top-right")
                    ),
                )
            )
            st.altair_chart(original, use_container_width=True)
        except:
            st.error("Delay not available")
    except Exception as e:
        st.error("Error Occured in fetching data")
else:
    st.info("Select a train to view details")