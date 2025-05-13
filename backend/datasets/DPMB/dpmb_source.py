from ..datasource_base import DataSource
from datetime import datetime
from .dpmb import update_data, get_departures, get_all_stops
from datetime import datetime
from zoneinfo import ZoneInfo
from ntplib import NTPClient

NTP_SERVER = "pool.ntp.org"  # NTP server to synchronize time

class DPMBSource(DataSource):
    def __init__(self, inputs: dict, uid):
        super().__init__(inputs, uid)
        self.cached_data = None
        self.week_downloaded = False

    def get_name(self):
        return "DPMB - " + self.inputs.get("Stop name")

    def save_all_stops_to_txt(self):
        df = get_all_stops()["stop_name"].drop_duplicates()
        with open("./static/DPMB/stops.txt", "w", encoding="utf-8") as f:
            f.write(df.to_string(index=False))

    def fetch_data(self):
        stop_name = self.inputs.get("Stop name")
        platform = self.inputs.get("Platform code") or None
        direction = self.inputs.get("Direction")

        client = NTPClient()
        response = client.request("pool.ntp.org")
        utc_time = datetime.fromtimestamp(response.tx_time, tz=ZoneInfo("UTC"))
        now = utc_time.astimezone(ZoneInfo("Europe/Prague"))

        if not self.week_downloaded and now.weekday() == 6 and 0 < now.hour:
            update_data()
            self.save_all_stops_to_txt()
            self.week_downloaded = True

        if now.weekday() == 0 and self.week_downloaded:
            self.week_downloaded = False

        current_time = now.strftime("%H:%M:%S")

        try:
            lmt = self.inputs.get("Maximum departures shown (default 5)") or 5
            #print(lmt)
            line = self.inputs.get("Line number") or None

            departures_list = get_departures(stop_name, direction, platform, current_time, line_number=line, limit=lmt)
            #print(departures_list)
            if departures_list is None:
                raise ValueError("get_departures returned None")
            
            if departures_list:
                def format_time(gtfs_time):
                    hours, minutes, seconds = map(int, gtfs_time.split(":"))
                    if hours >= 24:
                        hours -= 24
                        next_day = True
                    else:
                        next_day = False
                    dt = datetime.strptime(f"{hours:02}:{minutes:02}:{seconds:02}", "%H:%M:%S")
                    return dt.strftime("%H:%M") + (" (+1d)" if next_day else "")


                departures_dict = {
                    str(i)+". row": {
                        "departure_time": format_time(dep["departure_time"]),
                        "direction": dep["trip_headsign"],
                        "number": dep["line_number"],
                        "type": dep.get("vehicle_type", "Unknown")
                    }
                    for i, dep in enumerate(departures_list, start=1)
                }
                self.cached_data = {"departures": departures_dict}
                #print(self.cached_data)
            else:
                self.cached_data = {"departures": []}
        except Exception as e:
            print(f"[DPMBSource] Error fetching departures: {e}")
            self.cached_data = {"departures": []}

    def get_data(self):
        departures_raw = self.cached_data["departures"] if self.cached_data else {}

        return {
            "departures": {
                "value": departures_raw,
                "type": "dict"
            }
        }

    def get_update_interval(self):
        return 180  # Update every 3 mins
