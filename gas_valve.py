import json
import threading
import uuid

import paho.mqtt.client as mqtt
from dataclasses import dataclass, field


@dataclass
class GasValve:
    device_type = "gas_valve"
    device_id: str = field(init=False)
    gas_valve_open: bool
    policy_result: bool = False
    broker = "127.0.0.1"
    port = 1883
    rc = 1
    event = threading.Event()

    def __post_init__(self):
        self.device_id = f"{self.device_type}/{str(uuid.uuid4())}"
        self.client = mqtt.Client(client_id=self.device_id)

    def on_connect(self, client, userdata, flags, rc):
        self.rc = rc
        if rc == 0:
            print("GasValve connected to MQTT Broker!")
            policy_topic = f"policy_result/{self.device_type}"
            client.subscribe(policy_topic)
            client.message_callback_add(policy_topic, self.policy_message)
            action_topic_device = f"action/{self.device_type}"
            client.subscribe(action_topic_device)
            client.message_callback_add(action_topic_device, self.action_message)
        else:
            print("Failed to connect, return code %d\n" % rc)

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
        topic = f"device/{self.device_type}/connected"
        payload = {"device_type": self.device_type, "device_id": self.device_id, "gas_valve_open": self.gas_valve_open}
        self.client.publish(topic, json.dumps(payload))

    def subscribe(self, topic):
        self.client.subscribe(topic)

    def disconnect(self):
        topic = f"device/{self.device_type}/disconnected"
        payload = {"device_id": self.device_id}
        self.client.publish(topic, json.dumps(payload))
        self.client.disconnect()

    def open_valve(self):
        self.gas_valve_open = True
        print("Gas Valve Opened")

    def close_valve(self):
        self.gas_valve_open = False
        print("Gas Valve Closed")