import json
import threading

import paho.mqtt.client as mqtt
from dataclasses import dataclass


@dataclass
class WeatherStation:
    device_id: str
    temperature: float
    rain_sensor: bool
    wind_speed: float
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
            print("WeatherStation connected to MQTT Broker!")
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
            print("Success Weather_Station")
        else:
            self.policy_result = False
            print("Failed Weather_Station")
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
        #            "rain_sensor": self.rain_sensor, "wind_speed": self.wind_speed}
        # self.client.publish(topic, json.dumps(payload))

    def subscribe(self, topic):
        self.client.subscribe(topic)

    def disconnect(self):
        topic = f"device/{self.device_id}/disconnected"
        payload = {"device_id": self.device_id}
        self.client.publish(topic, json.dumps(payload))
        self.client.disconnect()

    def send_sensor_data(self):
        # One method for all possible cases, just the trigger is different (in this virtual scenario the method is
        # called in the main method but in the real scenario it would be started by, e.g. the rain sensor itself)
        topic = f"check_policy/{self.device_id}"
        payload = {"device_id": self.device_id, "temperature": self.temperature,
                   "rain_sensor": self.rain_sensor, "wind_speed": self.wind_speed}
        self.client.publish(topic, json.dumps(payload))
        self.event.wait()
        return self.policy_result
