import os
import re
import requests
import pandas as pd
from datetime import datetime
import gtfs_kit as gk

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "DPMB-GTFS")
GTFS_ZIP_PATH = os.path.join(DATA_DIR, "gtfs.zip")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Download GTFS
async def update_data():
    url = "https://www.arcgis.com/sharing/rest/content/items/379d2e9a7907460c8ca7fda1f3e84328/data"
    print("Downloading GTFS...")
    response = await requests.get(url)
    if response.ok:
        with open(GTFS_ZIP_PATH, "wb") as f:
            f.write(response.content)
        print("GTFS downloaded.")
    else:
        print("Download failed.")

# Load GTFS
def load_feed():
    return gk.read_feed(GTFS_ZIP_PATH, dist_units="km")


# All stops
def get_all_stops():
    feed = load_feed()
    return feed.stops[['stop_id', 'stop_name', 'platform_code']].drop_duplicates().sort_values(by='stop_name')

def time_to_seconds(t):
    h, m, s = map(int, t.split(":"))
    return h * 3600 + m * 60 + s

ROUTE_TYPE_MAP = {
    0: "Tram",
    1: "Subway",
    2: "Rail",
    3: "Bus",
    4: "Ferry",
    5: "Cable car",
    6: "Gondola",
    7: "Funicular",
    800: "Trolleybus",
    32: "Trolleybus"
}

def get_departures(stop_name, direction_id=None, platform_code=None, current_time_str=None, line_number=None, limit=10):
    try:
        feed = gk.read_feed(GTFS_ZIP_PATH, dist_units="km")
    except Exception as e:
        raise RuntimeError(f"Failed to read GTFS feed: {e}")

    try:
        stops = feed.stops
        if platform_code:
            stop_ids = stops[
                (stops['stop_name'] == stop_name) &
                (stops['platform_code'].astype(str) == str(platform_code))
            ]['stop_id'].unique()
        else:
            stop_ids = stops[stops['stop_name'] == stop_name]['stop_id'].unique()

        if len(stop_ids) == 0:
            raise RuntimeError(f"No stop IDs found for stop_name='{stop_name}' and platform_code='{platform_code}'")

        if not current_time_str:
            current_time_str = datetime.now().strftime('%H:%M:%S')

        def time_to_seconds(t):
            try:
                h, m, s = map(int, t.split(":"))
                return h * 3600 + m * 60 + s
            except Exception:
                raise RuntimeError(f"Invalid time format: '{t}'")

        current_secs = time_to_seconds(current_time_str)

        try:
            active_service_ids = feed.get_active_services(date=datetime.now().strftime("%Y%m%d"))
        except Exception as e:
            raise RuntimeError(f"Failed to get active service IDs: {e}")

        st = feed.stop_times[feed.stop_times['stop_id'].isin(stop_ids)]

        trips_today = feed.trips[feed.trips['service_id'].isin(active_service_ids)]
        st = st[st['trip_id'].isin(trips_today['trip_id'])]

        st = st[st["departure_time"].apply(time_to_seconds) >= current_secs]

        merged = st.merge(feed.trips, on='trip_id').merge(feed.routes, on='route_id')

        if direction_id is not None:
            try:
                merged = merged[merged["direction_id"] == int(direction_id)]
            except ValueError:
                raise RuntimeError(f"Invalid direction_id value: '{direction_id}'")

        def extract_line_number(route_id):
            match = re.search(r"L(\d+)D", str(route_id))
            if not match:
                return ""
            return match.group(1)

        merged["line_number"] = merged["route_id"].apply(extract_line_number)
        merged["vehicle_type"] = merged["route_type"].apply(lambda x: ROUTE_TYPE_MAP.get(x, "Unknown"))

        if line_number:
            merged = merged[merged["line_number"] == str(line_number)]

        try:
            merged['departure_timedelta'] = pd.to_timedelta(merged['departure_time'])
        except Exception as e:
            raise RuntimeError(f"Failed to convert departure_time to timedelta: {e}")

        result = merged.sort_values('departure_timedelta')[['departure_time', 'trip_headsign', 'line_number', 'vehicle_type']]
        return result.head(limit).to_dict(orient="records")

    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred in get_departures: {e}")

# Trip planning
def plan_trip(feed, start_stop_id, end_stop_id):
    try:
        path = gk.find_route(feed, start_stop_id, end_stop_id)
        return path.to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}

