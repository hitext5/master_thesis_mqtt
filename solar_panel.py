import json
import uuid

import paho.mqtt.client as mqtt
from dataclasses import dataclass, field


@dataclass
class SolarPanel:
    device_type = "solar_panel"
    device_id: str = field(init=False)
    provided_power: int
    policy_result: bool = False
    broker = "127.0.0.1"
    port = 1883
    rc = 1

    def __post_init__(self):
        self.device_id = f"{self.device_type}/{str(uuid.uuid4())}"
        self.client = mqtt.Client(client_id=self.device_id)

    def on_connect(self, client, userdata, flags, rc):
        self.rc = rc
        if rc == 0:
            print("SolarPanel connected to MQTT Broker!")
            topic = f"policy_result/{self.device_type}"
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
        topic = f"device/{self.device_type}/connected"
        payload = {"device_type": self.device_type, "device_id": self.device_id, "provided_power": self.provided_power}
        self.client.publish(topic, json.dumps(payload))

    def subscribe(self, topic):
        self.client.subscribe(topic)

    def disconnect(self):
        topic = f"device/{self.device_type}/disconnected"
        payload = {"device_id": self.device_id}
        self.client.publish(topic, json.dumps(payload))
        self.client.disconnect()
