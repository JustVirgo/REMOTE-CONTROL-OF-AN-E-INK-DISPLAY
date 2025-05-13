import paho.mqtt.client as mqtt

BROKER = "test.mosquitto.org"
PORT = 1883
USERNAME = "wildcart"
TOPIC = "#"  # Subscribe to all topics

def on_connect(client, userdata, flags, rc):
    print(f"[MQTT] Connected with result code {rc}")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    print(f"[{USERNAME}] Topic: {msg.topic} | Message: {msg.payload.decode()}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# NOTE: No username/password needed for test.mosquitto.org
client.connect(BROKER, PORT, 60)
client.loop_forever()
