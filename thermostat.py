import json
import threading

import paho.mqtt.client as mqtt
from dataclasses import dataclass


@dataclass
class Thermostat:
    device_id: str
    temperature: float
    air_quality: int
    room_id: str
    heater_on: bool
    ac_on: bool
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
            print("Thermostat connected to MQTT Broker!")
            policy_topic = f"policy_result/{self.device_id}"
            client.subscribe(policy_topic)
            client.message_callback_add(policy_topic, self.policy_message)
            action_topic = f"action/{self.device_id}"
            client.subscribe(action_topic)
            client.message_callback_add(action_topic, self.action_message)
        else:
            print("Failed to connect, return code %d\n", rc)

    def on_message(self, client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    def policy_message(self, client, userdata, msg):
        payload = msg.payload.decode()
        if payload == "True":
            self.policy_result = True
            print("Success Thermostat")
        else:
            self.policy_result = False
            print("Failed Thermostat")
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
        # topic = f"device/{self.device_id}/connected"
        # payload = {"device_id": self.device_id, "temperature": self.temperature,
        #            "ac_on": self.ac_on, "heater_on": self.heater_on, "air_quality": self.air_quality,
        #            "room_id": self.room_id}
        # self.client.publish(topic, json.dumps(payload))

    def subscribe(self, topic):
        self.client.subscribe(topic)

    def disconnect(self):
        topic = f"device/{self.device_id}/disconnected"
        payload = {"device_id": self.device_id}
        self.client.publish(topic, json.dumps(payload))
        self.client.disconnect()

    def ac_on(self):
        self.ac_on = True
        print("AC turned on")

    def ac_off(self):
        self.ac_on = False
        print("AC turned off")
