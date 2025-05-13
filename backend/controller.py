import json
import os
from datasets.Open_weather.open_weather_source import OpenWeatherSource
from datasets.DPMB.dpmb_source import DPMBSource
from datasets.datasource_base import DataSource
from datasets.MQTT.mqtt_source import MQTTSource
from datasets.Time.time_source import TimeDataSource
import threading
import time
import datetime

DATASETS_PATH = 'data/datasets.json'
DATASOURCES_PATH = 'data/datasources.json'
SCREENS_PATH = 'data/screens.json'
DISPLAYS_PATH = 'data/displays.json'


# In-memory instance registry
INSTANCE_REGISTRY = {}

SOURCE_CLASSES = {
    "Weather-OPEN_WEATHER": OpenWeatherSource,
    "DPMB-departures from stop for Brno": DPMBSource,
    "MQTT-protocol": MQTTSource,
    "Date and time": TimeDataSource
}

def get_all_screens():
    return load_json(SCREENS_PATH)

def get_all_displays():
    return load_json(DISPLAYS_PATH)

def log(*args, filename="log.txt"):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    message = " ".join(str(arg) for arg in args)
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {message}\n")

def get_screen_by_id(screen_id):
    screens = load_json(SCREENS_PATH)
    for screen in screens:
        if screen.get("id") == screen_id:
            return screen
    raise ValueError(f"Display with ID {screen_id} not found")

def get_display_by_id(display_id):
    displays = load_json(DISPLAYS_PATH)
    for display in displays:
        if display.get("id") == display_id:
            return display
    raise ValueError(f"Display with ID {display_id} not found")


def save_screen(screen_data):
    screens = load_json(SCREENS_PATH)
    if not isinstance(screens, list):
        screens = []

    if not screen_data["id"]:
        existing_ids = {d.get("id") for d in screens if "id" in d}
        new_id = 1
        while new_id in existing_ids:
            new_id += 1
        screen_data["id"] = new_id

    screens.append(screen_data)
    save_json(SCREENS_PATH, screens)
    return screen_data

def delete_screen(screen_id):
    screens = load_json(SCREENS_PATH)
    filtered = [s for s in screens if s.get("id") != screen_id]
    save_json(SCREENS_PATH, filtered)

def update_screen(screen_id, new_data):
    screens = load_json(SCREENS_PATH)
    updated = False

    for i, d in enumerate(screens):
        if d.get("id") == screen_id:
            screens[i].update(new_data)
            updated = True
            break

    if not updated:
        raise ValueError(f"Display with ID {screen_id} not found")

    save_json(SCREENS_PATH, screens)
    return screens[i]


def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_all_data_sets():
    return load_json(DATASETS_PATH)


def create_source_instance(source_name, inputs, uid) -> DataSource:
    cls = SOURCE_CLASSES.get(source_name)
    if not cls:
        raise ValueError(f"No implementation for source: {source_name}")
    return cls(inputs, uid)

def save_datasource(source_data):
    try:
        # Validate input
        if not isinstance(source_data, dict):
            raise ValueError("Expected a dictionary as input for source_data")

        if "source" not in source_data:
            raise KeyError("Missing 'source' key in source_data")

        if "inputs" not in source_data or not isinstance(source_data["inputs"], dict):
            raise KeyError("Missing or invalid 'inputs' in source_data")

        current_data = load_json(DATASOURCES_PATH)
        if not isinstance(current_data, list):
            print("[Warning] datasources.json content is not a list. Initializing empty list.")
            current_data = []

        # Generate UID
        existing_ids = {item.get("uid") for item in current_data if "uid" in item}
        new_uid = 1
        while new_uid in existing_ids:
            new_uid += 1

        source_data["uid"] = new_uid

        # Create the instance
        try:
            instance = create_source_instance(source_data["source"], source_data["inputs"], new_uid)
        except Exception as e:
            print(source_data)
            raise RuntimeError(f"Failed to create source instance: {e}")

        # Force initial data fetch
        try:
            instance.update_data(force=True)
        except Exception as e:
            raise RuntimeError(f"Failed to update data for new instance (UID {new_uid}): {e}")

        # Store instance in memory
        INSTANCE_REGISTRY[new_uid] = instance

        # Store fetched data
        try:
            source_data["data"] = {
                key: val["value"] for key, val in instance.get_data().items()
            }
        except Exception as e:
            raise RuntimeError(f"Failed to extract data from instance UID {new_uid}: {e}")

        # Patch displays with this data if needed
        displays = load_json(SCREENS_PATH)
        for display in displays:
            changed = False
            for widget in display.get("widgets", []):
                if widget.get("sourceUid") == new_uid:
                    field = widget.get("fieldName")
                    if field and field in instance.get_data():
                        widget["value"] = instance.get_data()[field]["value"]
                        changed = True
            if changed:
                print(f"[Save Source] Patched display ID {display.get('id')} with latest values")

        save_json(SCREENS_PATH, displays)

        # Add human-friendly name
        source_data["name"] = f'ID:{new_uid} - {instance.get_name()}'

        # Save to file
        current_data.append(source_data)
        current_data.sort(key=lambda x: x.get("uid", float("inf")))
        save_json(DATASOURCES_PATH, current_data)

        print(f"[Save Source] Successfully saved source with UID {new_uid}")
        return source_data

    except Exception as e:
        print(f"[Save Source] ERROR: {e}")
        raise



def force_refresh_datasource(uid):
    if uid not in INSTANCE_REGISTRY:
        raise ValueError(f"No data source with UID {uid} in memory")

    instance = INSTANCE_REGISTRY[uid]

    try:
        # Try updating the data
        instance.update_data(force=True)
    except Exception as e:
        print(f"[FORCE UPDATE] Failed to update data for UID {uid}: {e}")
        raise RuntimeError(f"Data update failed for UID {uid}: {e}")

    try:
        all_sources = load_json(DATASOURCES_PATH)
        if not isinstance(all_sources, list):
            raise ValueError("datasources.json must contain a list")

        for source in all_sources:
            if source.get("uid") == uid:
                # Update the stored data with fresh instance data
                source["data"] = {
                    k: v["value"] for k,v in instance.get_data().items()
                     
                }
                break
        else:
            raise ValueError(f"UID {uid} not found in file for updating.")

        # Check if this source is used in any display
        all_displays = load_json(SCREENS_PATH)
        for display in all_displays:
            updated_display = False
            for widget in display.get("widgets", []):
                if widget.get("sourceUid") == uid:
                    field = widget.get("fieldName")
                    if field and field in instance.get_data():
                        widget["value"] = instance.get_data()[field]["value"]
                        updated_display = True

            if updated_display:
                save_json(SCREENS_PATH, all_displays)
                print(f"[Auto-Refresh] Updated display ID {display.get('id')} due to UID {uid}")

        # Save updated sources
        save_json(DATASOURCES_PATH, all_sources)

    except Exception as e:
        print(f"[FORCE UPDATE] Failed to update JSON storage for UID {uid}: {e}")
        raise RuntimeError(f"Could not save updated data for UID {uid}: {e}")


def get_saved_datasources():
    return load_json(DATASOURCES_PATH)

def get_saved_datasource(uid):
    data = load_json(DATASOURCES_PATH)
    data = [item for item in data if item.get("uid") == uid]
    return data

def delete_datasource(uid):
    data = load_json(DATASOURCES_PATH)

    # Remove from instance registry and clean up
    if uid in INSTANCE_REGISTRY:
        try:
            del INSTANCE_REGISTRY[uid] 
            print(f"[Delete] Instance UID {uid} removed from registry and cleaned up.")
        except Exception as e:
            print(f"[Delete] Failed to delete instance UID {uid}: {e}")

    # Remove the item with the matching UID from file
    filtered = [item for item in data if item.get("uid") != uid]
    save_json(DATASOURCES_PATH, filtered)

def get_sleep_display(id):
    data = load_json(SCREENS_PATH)
    matching = [item for item in data if item.get("id") == id]

    if not matching:
        raise ValueError(f"No display found with ID {id}")

    return matching[0].get("refresh")

    
REFRESH_INTERVAL = 20  # seconds (how often the loop checks)

def _auto_refresh_loop():
    while True:
        time.sleep(REFRESH_INTERVAL)
        print("[Auto-Refresh] Auto refresh sequence has started")
        try:
            all_sources = load_json(DATASOURCES_PATH)

            updated = False

            for uid, instance in INSTANCE_REGISTRY.items():
                try:
                    if instance.update_data(force=False):
                        for source in all_sources:
                            if source.get("uid") == uid:
                                source["data"] = {
                                    k: v["value"] for k,v in instance.get_data().items()
                                }
                                updated = True
                                print(f"[{time.thread_time()}][Auto-Refresh] Updated UID {uid}")
                                break
                except Exception as e:
                    print(f"[Auto-Refresh] Failed to update instance {uid}: {e}")

                if updated:
                    save_json(DATASOURCES_PATH, all_sources)
                    # Check if this source is used in any display
                    all_displays = load_json(SCREENS_PATH)
                    for display in all_displays:
                        updated_display = False
                        for widget in display.get("widgets", []):
                            if widget.get("sourceUid") == uid:
                                field = widget.get("fieldName")
                                if field and field in instance.get_data():
                                    widget["value"] = instance.get_data()[field]["value"]
                                    updated_display = True

                        if updated_display:
                            print(f"[Auto-Refresh] Updated display ID {display.get('id')} due to UID {uid}")

                    save_json(SCREENS_PATH, all_displays)


        except Exception as global_e:
            print(f"[Auto-Refresh] Global failure: {global_e}")


def initialize_instances_from_file():
    """Load all saved data sources from JSON and create their live instances."""
    print("[Startup] Initializing existing instances")
    data = load_json(DATASOURCES_PATH)
    if not isinstance(data, list):
        return

    for item in data:
        uid = item.get("uid")
        source_name = item.get("source")
        inputs = item.get("inputs")

        if not uid or not source_name or not inputs:
            continue  # skip invalid entries

        try:
            instance = create_source_instance(source_name, inputs, uid)
            instance.update_data(force=True)  # fetch once immediately
            INSTANCE_REGISTRY[uid] = instance
            print(f"[Startup] Initialized instance {instance.get_name()}")

        except Exception as e:
            print(f"[Startup] Failed to initialize data source UID {uid}: {e}")
    print("[Startup] Initialization finished")

_auto_refresh_started = False

def start_auto_refresh():
    global _auto_refresh_started
    if not _auto_refresh_started:
        _auto_refresh_started = True
        threading.Thread(target=_auto_refresh_loop, daemon=True).start()


