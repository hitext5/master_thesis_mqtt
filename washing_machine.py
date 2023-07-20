import json
import uuid

import paho.mqtt.client as mqtt
import threading
from dataclasses import dataclass, field


@dataclass
class WashingMachine:
    device_type = "washing_machine"
    device_id: str = field(init=False)
    work_power: int
    last_cleaning: int
    machine_on: bool = False
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
            print(f"{self.device_id.capitalize()} connected to MQTT Broker!")
            policy_topic = f"policy_result/{self.device_type}"
            client.subscribe(policy_topic)
            client.message_callback_add(policy_topic, self.policy_message)
            action_topic = f"action/{self.device_type}"
            client.subscribe(action_topic)
            client.message_callback_add(action_topic, self.action_message)
        else:
            print("Failed to connect, return code %d\n" % rc)

    def on_message(self, client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    def policy_message(self, client, userdata, msg):
        payload = msg.payload.decode()
        if payload == "True":
            self.last_cleaning += 1
            self.policy_result = True
            self.machine_on = True
            # Create a dictionary with the updated information
            data = {
                'device_id': self.device_id,
                'powered_by': "solar_panel", 'last_cleaning': self.last_cleaning, 'machine_on': self.machine_on
            }

            # Convert the dictionary to a JSON string
            payload = json.dumps(data)

            # Publish the message to the desired topic
            self.client.publish(f"update_device/{self.device_type}", payload)
            print("Success WashingMachine")
        else:
            self.policy_result = False
            print("Failed WashingMachine")
        # After receiving the policy result, the event is set to True to continue
        # the execution of the program which is the turn_on method
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
        payload = {"device_type": self.device_type, "device_id": self.device_id, "work_power": self.work_power,
                   "last_cleaning": self.last_cleaning, "machine_on": self.machine_on}
        self.client.publish(topic, json.dumps(payload))

    def turn_on(self):
        topic = f"check_policy/{self.device_type}"
        payload = {"device_type": self.device_type, "work_power": self.work_power, "last_cleaning": self.last_cleaning}
        self.client.publish(topic, json.dumps(payload))
        # The event is set too False to wait for the policy result (see policy_message method)
        self.event.wait()
        return self.policy_result

    def subscribe(self, topic):
        self.client.subscribe(topic)

    def disconnect(self):
        topic = f"device/{self.device_type}/disconnected"
        payload = {"device_id": self.device_id}
        self.client.publish(topic, json.dumps(payload))
        self.client.disconnect()
