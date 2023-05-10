import json
import paho.mqtt.client as mqtt
from dataclasses import dataclass


@dataclass
class SolarPanel:
    device_id: str
    provided_power: int
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
        # topic = f"device/{self.device_id}/connected"
        # payload = {"device_id": self.device_id, "provided_power": self.provided_power}
        # self.client.publish(topic, json.dumps(payload))

    def subscribe(self, topic):
        self.client.subscribe(topic)
