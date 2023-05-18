import json
import paho.mqtt.client as mqtt
import requests
import tkinter as tk

from dataclasses import dataclass
from pymongo import MongoClient

from electronic_device import ElectronicDevice
from solar_panel import SolarPanel


# TODO Only this mqtt client has to be in the user interface project,
#  the devices should be able to communicate over mqtt
@dataclass
class MessageHandler:
    device_id = "message_handler"
    broker: str = "127.0.0.1"
    port: int = 1883
    client = mqtt.Client(client_id=device_id)
    rc = 1
    atlas_uri = "mongodb://Kleriakanus:test123@ac-s2miieu-shard-00-00.s0mnged.mongodb.net:27017," \
                "ac-s2miieu-shard-00-01.s0mnged.mongodb.net:27017," \
                "ac-s2miieu-shard-00-02.s0mnged.mongodb.net:27017/?ssl=true&replicaSet=atlas-vihgip-shard-0" \
                "&authSource=admin&retryWrites=true&w=majority"
    db_name = 'Cluster0'
    mongo_client = MongoClient(atlas_uri)
    database = mongo_client[db_name]
    collection = database["devices"]

    def on_connect(self, client, userdata, flags, rc):
        # When the client successfully connects to the broker, rc will be set to 0.
        # We have to introduce the rc variable here, because the connection has to be established before
        # the code continues to run. Not in the real world, but in this simulation.
        self.rc = rc
        if rc == 0:
            print("MessageHandler connected to MQTT Broker!")
            # Basic MQTT topics (we assume that all devices publish to these topics)
            client.subscribe("device/+/connected")
            # Specify the callback function for the subscribed topics
            client.message_callback_add("device/+/connected", self.connection_message)
            client.subscribe("device/+/disconnected")
            client.message_callback_add("device/+/disconnected", self.disconnection_message)
            client.subscribe("check_policy/+")
            client.message_callback_add("check_policy/+", self.check_policy_message)
        else:
            print("Failed to connect, return code %d\n", rc)
        pass

    def on_message(self, client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    def connect(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker, self.port)

    def subscribe(self, topic):
        self.client.subscribe(topic)

    def connection_message(self, client, userdata, msg):
        device_data = json.loads(msg.payload)
        print(f"{device_data} connected to the system.")
        # Save device data to database on first connection
        self.collection.insert_one(device_data)

    def disconnection_message(self, client, userdata, msg):
        device_data = json.loads(msg.payload)
        print("Device disconnected from the system.")
        # Delete device data from database on disconnection
        self.collection.delete_one({"mqtt_id": device_data["device_id"]})

    def check_policy_message(self, client, userdata, msg):
        device_data = json.loads(msg.payload)
        # Get the device type over the device id.
        device_type = device_data["device_id"]
        response = requests.post(
            f"http://localhost:8080/check_policies/{device_type}",
            json=device_data
        )
        if response.status_code != 200:
            raise Exception("Error evaluating policy: " + response.text)
        # Get the result of the policy evaluation as a boolean.
        result = response.json()["result"]
        # Can be "mandatory", "double_check" or "N/A" (if all policies are satisfied)
        priority = response.json()["priority"]
        # List of double_check policies that are not satisfied
        failed_sub_policies = response.json()["failed_sub_policies"]
        # List of actions that have to be executed for the successful policies
        policy_actions = response.json()["actions"]

        if result:
            print(f"All policies for the {device_type} are satisfied.")
        elif priority == "mandatory":
            print(f"Mandatory policies for the {device_type} are not satisfied.")
        elif priority == "double_check":
            print(f"Not all policies for the {device_type} are satisfied.")

            def no_button():
                # Clear the list of actions, so that the device does not execute them when the user clicks "No"
                # because not all policies are satisfied.
                policy_actions.clear()
                root.destroy()

            def yes_button():
                # Manually set the result to True, so that the device executes the actions.
                # User overrules the policy decision.
                nonlocal result
                result = True
                root.destroy()

            root = tk.Tk()
            root.title("Window")

            text = f"The following policies for the {device_type} are NOT satisfied. Do you still want to continue? \n" \
                   + "\n".join(failed_sub_policies)
            label = tk.Label(root, text=text, wraplength=300)
            label.pack(fill=tk.X, pady=(0, 10))

            frame = tk.Frame(root)
            frame.pack(padx=50)

            left_button = tk.Button(frame, text="Yes", command=yes_button)
            left_button.pack(side=tk.LEFT, padx=(0, 5))

            right_button = tk.Button(frame, text="No", command=no_button, bg="blue")
            right_button.pack(side=tk.RIGHT)

            root.mainloop()
        else:
            raise Exception("Unknown priority: " + priority)

        # Publish result to the requesting_device
        policy_topic = f"policy_result/{device_type}"
        client.publish(policy_topic, str(result))

        # Send actions to devices
        for action in policy_actions:
            device = action['device']
            action_topic = f"action/{device}"
            payload = action['to_do']
            client.publish(action_topic, payload)

    def clear_db(self):
        self.collection.delete_many({})
        print("Database cleared.")
