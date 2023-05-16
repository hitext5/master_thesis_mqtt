import json
import paho.mqtt.client as mqtt
from dataclasses import dataclass


@dataclass
class Thermostat:
    device_id: str
    inside_temperature: float
    ac_on: bool
    heater_on: bool
    air_quality: int
    room_id: str
    policy_result: bool = False
    broker = "127.0.0.1"
    port = 1883
    rc = 1

    def __post_init__(self):
        self.client = mqtt.Client(client_id=self.device_id)

    def on_connect(self, client, userdata, flags, rc):
        self.rc = rc
        if rc == 0:
            print("SolarPanel connected to MQTT Broker!")
            topic = f"policy_result/{self.device_id}"
            client.subscribe(topic)
        else:
            print("Failed to connect, return code %d\n", rc)

    def on_message(self, client, userdata, msg):
        if msg.payload.decode():
            self.policy_result = True
            print("Success SolarPanel")
        else:
            self.policy_result = False
            print("Failed SolarPanel")

    def connect(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker, self.port)
        topic = f"device/{self.device_id}/connected"
        payload = {"device_id": self.device_id, "inside_temperature": self.inside_temperature,
                   "ac_on": self.ac_on, "heater_on": self.heater_on, "air_quality": self.air_quality,
                   "room_id": self.room_id}
        self.client.publish(topic, json.dumps(payload))

    def subscribe(self, topic):
        self.client.subscribe(topic)

    def disconnect(self):
        topic = f"device/{self.device_id}/disconnected"
        payload = {"device_id": self.device_id}
        self.client.publish(topic, json.dumps(payload))
        self.client.disconnect()
