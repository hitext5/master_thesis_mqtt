import json
import threading

import paho.mqtt.client as mqtt
from dataclasses import dataclass


@dataclass
class CarbonMonoxideDetector:
    device_id: str
    gas_level: float
    room_id: str
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
            print("CarbonMonoxideDetector connected to MQTT Broker!")
            policy_topic = f"policy_result/{self.device_id}"
            client.subscribe(policy_topic)
            client.message_callback_add(policy_topic, self.policy_message)
            action_topic_location = f"action/{self.room_id}/{self.device_id}"
            client.subscribe(action_topic_location)
            client.message_callback_add(action_topic_location, self.action_message)
            action_topic_device = f"action/{self.device_id}"
            client.subscribe(action_topic_device)
            client.message_callback_add(action_topic_device, self.action_message)
        else:
            print("Failed to connect, return code %d\n", rc)

    def on_message(self, client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    def policy_message(self, client, userdata, msg):
        payload = msg.payload.decode()
        if payload == "True":
            self.policy_result = True
            print("Success Window")
        else:
            self.policy_result = False
            print("Failed Window")
        self.event.set()

    def action_message(self, client, userdata, msg):
        to_do = msg.payload.decode()
        method = getattr(self, to_do, None)
        if callable(method):
            method()

    def connect(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker, self.port)
        topic = f"device/{self.device_id}/connected"
        payload = {"device_id": self.device_id, "gas_level": self.gas_level, "room_id": self.room_id}
        self.client.publish(topic, json.dumps(payload))

    def subscribe(self, topic):
        self.client.subscribe(topic)

    def disconnect(self):
        topic = f"device/{self.device_id}/disconnected"
        payload = {"device_id": self.device_id}
        self.client.publish(topic, json.dumps(payload))
        self.client.disconnect()
