from datetime import datetime
from zoneinfo import ZoneInfo
from ntplib import NTPClient, NTPException
from ..datasource_base import DataSource

class TimeDataSource(DataSource):
    def __init__(self, inputs: dict, uid: int):
        super().__init__(inputs, uid)
        self.ntp_server = self.inputs.get('NTP server (if not defined using server time)', None)
        self.update_interval = self.inputs.get('Update interval (s)', 60)
        self.locale = self.inputs.get('Time zone in utc format (Continent/City)', 'Europe/London')
        self.format = self.inputs.get('Date format', 'DD/MM/YYYY')

    def fetch_data(self):
        try:
            if self.ntp_server:
                client = NTPClient()
                response = client.request(self.ntp_server, version=3)
                utc_time = datetime.fromtimestamp(response.tx_time, tz=ZoneInfo("UTC"))
                source = "ntp"
            else:
                raise ValueError("No NTP server specified")
        except (NTPException, Exception):
            utc_time = datetime.now(tz=ZoneInfo("UTC"))
            source = "system"

        # Localize using zoneinfo
        try:
            localized_time = utc_time.astimezone(ZoneInfo(self.locale))
        except Exception:
            print(f"[TIME] Time zone not set or invalid '{self.locale}', using UTC.")
            localized_time = utc_time

        # Format output
        if self.format.upper() == "DD/MM/YYYY":
            date_str = localized_time.strftime("%d/%m/%Y")
            month_day = localized_time.strftime("%d/%m")
        elif self.format.upper() == "MM/DD/YYYY":
            date_str = localized_time.strftime("%m/%d/%Y")
            month_day = localized_time.strftime("%m/%d")
        elif self.format.upper() == "YYYY/MM/DD":
            date_str = localized_time.strftime("%Y/%m/%d")
            month_day = localized_time.strftime("%m/%d")
        else:
            date_str = localized_time.strftime("%Y-%m-%d")
            month_day = localized_time.strftime("%m-%d")

        self.cached_data = {
            "source": {"value": source, "type": "string"},
            "datetime": {"value": localized_time.isoformat(), "type": "string"},
            "time": {"value": localized_time.strftime("%H:%M"), "type": "string"},
            "hours": {"value": int(localized_time.strftime("%H")), "type": "number"},
            "minutes": {"value": int(localized_time.strftime("%M")), "type": "number"},
            "date": {"value": date_str, "type": "string"},
            "day_month_key": {"value": month_day, "type": "string"},
        }


    def get_data(self):
        return self.cached_data

    def get_update_interval(self):
        return self.update_interval

    def get_name(self):
        return f"TimeDataSource - {self.locale}"
