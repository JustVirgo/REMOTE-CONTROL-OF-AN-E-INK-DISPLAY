# mqtt_source.py

from ..datasource_base import DataSource
from .mqtt import MQTTClientWrapper
import json

class MQTTSource(DataSource):
    def __init__(self, inputs: dict, uid: int):
        super().__init__(inputs, uid)
        self.broker = inputs.get("Broker URL")
        self.port = inputs.get("Broker Port") or 1883
        self.topics = inputs.get("Topics", []) 

        if not isinstance(self.topics, list) or not self.topics:
            raise ValueError("MQTTSource expects a non-empty list of topics under 'Topics' input")

        self.client = MQTTClientWrapper(self.broker, self.port)
        for topic in self.topics:
            self.client.subscribe(topic)
        
        self.client.wait_for_messages(self.topics)
    

    def get_name(self):
        return (f"{','.join(self.topics)}")

    def fetch_data(self):
        values = {}
        for topic in self.topics:
            raw = self.client.get_latest_message(topic)
            parsed = raw

            # try JSON decode
            if isinstance(raw, str):
                try:
                    parsed = json.loads(raw)
                except json.JSONDecodeError:
                    parsed = raw

            if isinstance(parsed, dict):
                values[topic] = parsed
            else:
                values[topic] = {"value": parsed}

        self.cached_data = values


    def detect_type(self,val):
        if isinstance(val, bool):
            return "bool"
        elif isinstance(val, int):
            return "int"
        elif isinstance(val, float):
            return "float"
        elif isinstance(val, dict):
            return "dict"
        elif isinstance(val, list):
            return "list"
        elif isinstance(val, str):
            # Try to decode JSON
            try:
                parsed = json.loads(val)
                return self.detect_type(parsed)
            except (json.JSONDecodeError, TypeError):
                return "string"
        else:
            return "string"

    def get_data(self):
        out = {}
        for topic, raw in (self.cached_data or {}).items():
            wrapped = {"value": raw}
            val_type = self.detect_type(raw)
            out[topic] = {
                "value": wrapped,
                "type":  val_type
            }
        return out


    def get_update_interval(self):
        return int(self.inputs.get("interval", 180))

    def __del__(self):
        try:
            for topic in self.topics:
                self.client.unsubscribe(topic)
            self.client.disconnect()
            print(f"[MQTTSource] Cleaned up MQTT client and unsubscribed from all topics.")
        except Exception as e:
            print(f"[MQTTSource] Cleanup failed: {e}")
