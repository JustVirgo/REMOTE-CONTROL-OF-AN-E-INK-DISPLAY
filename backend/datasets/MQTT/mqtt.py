# mqtt.py

import paho.mqtt.client as mqtt
from collections import defaultdict
import threading
import time

class MQTTClientWrapper:
    def __init__(self, broker, port=1883, keepalive=60):
        self.broker = broker
        self.port = port
        self.keepalive = keepalive

        self._client = mqtt.Client()
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message

        self._lock = threading.Lock()
        self._latest_messages = defaultdict(lambda: None)
        self._subscriptions = set()

        self._client.connect(broker, port, keepalive)
        self._client.loop_start()

    def wait_for_messages(self, topics, timeout=2.0):
        """Wait until all specified topics receive a message or timeout."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            with self._lock:
                if all(self._latest_messages[topic] is not None for topic in topics):
                    return True  # All topics received
            time.sleep(0.05)  # avoid busy waiting
        print(f"[MQTT] Timeout while waiting for messages on: {topics}")
        return False
    
    def _on_connect(self, client, userdata, flags, rc):
        print(f"[MQTT] Connected to {self.broker}:{self.port} with result code {rc}")
        # Re-subscribe after reconnect
        for topic in self._subscriptions:
            client.subscribe(topic)

    def _on_message(self, client, userdata, msg):
        with self._lock:
            self._latest_messages[msg.topic] = msg.payload.decode("utf-8")
            print(f"[MQTT] Received {msg.topic}: {self._latest_messages[msg.topic]}")

    def subscribe(self, topic):
        if topic not in self._subscriptions:
            try:
                self._client.subscribe(topic)
                self._subscriptions.add(topic)
                print(f"[MQTT] Subscribed to {topic}")
            except Exception as e:
                print(f"[MQTT] Failed to subscribe to {topic}: {e}")

    def unsubscribe(self, topic):
        if topic in self._subscriptions:
            self._client.unsubscribe(topic)
            self._subscriptions.remove(topic)
            print(f"[MQTT] Unsubscribed from {topic}")

    def get_latest_message(self, topic):
        with self._lock:
            return self._latest_messages.get(topic)

    def get_all_latest_messages(self):
        with self._lock:
            return dict(self._latest_messages)

    def disconnect(self):
        self._client.loop_stop()
        self._client.disconnect()
        print(f"[MQTT] Disconnected from {self.broker}")
