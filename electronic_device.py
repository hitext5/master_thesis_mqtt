import json
import paho.mqtt.client as mqtt
import threading
from dataclasses import dataclass


@dataclass
class ElectronicDevice:
    device_id: str
    work_power: int
    last_cleaning: int
    policy_result: bool = False
    broker = "127.0.0.1"
    port = 1883
    rc = 1
    event = threading.Event()

    def __post_init__(self):
        self.client = mqtt.Client(client_id=self.device_id)

    def on_connect(self, client, userdata, flags, rc):
        self.rc = rc
        if rc == 0:
            print(f"{self.device_id.capitalize()} connected to MQTT Broker!")
            topic = f"policy_result/{self.device_id}"
            client.subscribe(topic)
        else:
            print("Failed to connect, return code %d\n", rc)

    def on_message(self, client, userdata, msg):
        if msg.payload.decode() == "True":
            self.policy_result = True
            self.last_cleaning += 1
            print("Success ElectronicDevice")
        else:
            self.policy_result = False
            print("Failed ElectronicDevice")
        self.event.set()

    def connect(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker, self.port)
        # topic = f"device/{self.device_id}/connected"
        # payload = {"device_id": self.device_id, "work_power": self.work_power, "last_cleaning": self.last_cleaning}
        # self.client.publish(topic, json.dumps(payload))

    def turn_on(self):
        topic = f"check_policy/{self.device_id}"
        payload = {"device_id": self.device_id, "work_power": self.work_power, "last_cleaning": self.last_cleaning}
        self.client.publish(topic, json.dumps(payload))
        self.event.wait()
        return self.policy_result

    def subscribe(self, topic):
        self.client.subscribe(topic)
