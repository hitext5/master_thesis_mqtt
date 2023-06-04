import json
import threading
import uuid

import paho.mqtt.client as mqtt
from dataclasses import dataclass, field


@dataclass
class Thermostat:
    device_type = "thermostat"
    device_id: str = field(init=False)
    temperature: float
    air_quality: float
    room_id: str
    fan_on: bool
    heating_on: bool
    ac_on: bool
    possible_actions = ["turn_on_fan", "turn_off_fan", "turn_on_heating", "turn_off_heating",
                        "turn_on_ac", "turn_off_ac"]
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
            print("Thermostat connected to MQTT Broker!")
            policy_topic = f"policy_result/{self.device_type}"
            client.subscribe(policy_topic)
            client.message_callback_add(policy_topic, self.policy_message)
            action_topic_location = f"action/{self.room_id}/{self.device_type}"
            client.subscribe(action_topic_location)
            client.message_callback_add(action_topic_location, self.action_message)
            action_topic_device = f"action/{self.device_type}"
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
        else:
            print("No method")

    def connect(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker, self.port)
        topic = f"device/{self.device_type}/connected"
        payload = {"device_type": self.device_type, "device_id": self.device_id, "temperature": self.temperature,
                   "ac_on": self.ac_on, "heating_on": self.heating_on, "air_quality": self.air_quality,
                   "room_id": self.room_id, "possible_actions": self.possible_actions, "fan_on": self.fan_on}
        self.client.publish(topic, json.dumps(payload))

    def subscribe(self, topic):
        self.client.subscribe(topic)

    def disconnect(self):
        topic = f"device/{self.device_type}/disconnected"
        payload = {"device_type": self.device_type}
        self.client.publish(topic, json.dumps(payload))
        self.client.disconnect()

    def ac_on(self):
        self.ac_on = True
        print("AC turned on")

    def ac_off(self):
        self.ac_on = False
        # Create a dictionary with the updated information
        data = {
            'client_id': self.device_id,
            'ac_on': self.ac_on
        }

        # Convert the dictionary to a JSON string
        payload = json.dumps(data)

        # Publish the message to the desired topic
        self.client.publish(f"update_device/{self.device_type}", payload)
        print("AC turned off")

    def turn_heating_on(self):
        self.heating_on = True
        # Create a dictionary with the updated information
        data = {
            'client_id': self.device_id,
            'heating_on': self.heating_on
        }

        # Convert the dictionary to a JSON string
        payload = json.dumps(data)

        # Publish the message to the desired topic
        self.client.publish(f"update_device/{self.device_type}", payload)
        print("Heating turned on")

    def turn_heating_off(self):
        self.heating_on = False
        print("Heating turned off")

    def turn_fan_on(self):
        self.fan_on = True
        # Create a dictionary with the updated information
        data = {
            'client_id': self.device_id,
            'fan_on': self.fan_on
        }

        # Convert the dictionary to a JSON string
        payload = json.dumps(data)

        # Publish the message to the desired topic
        self.client.publish(f"update_device/{self.device_type}", payload)
        print("Fan turned on")

    def turn_fan_off(self):
        self.fan_on = False
        print("Fan turned off")

    def send_current_status(self):
        # In this virtual scenario the method is called in the main method
        # but in the real scenario it would be sent every x seconds
        topic = f"check_policy/{self.device_type}"
        payload = {"device_type": self.device_type, "device_id": self.device_id, "temperature": self.temperature,
                   "air_quality": self.air_quality, "room_id": self.room_id, "fan_on": self.fan_on, "ac_on": self.ac_on,
                   "heating_on": self.heating_on}
        self.client.publish(topic, json.dumps(payload))
        self.event.wait()
        return self.policy_result
