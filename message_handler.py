import json
import paho.mqtt.client as mqtt
import requests
import tkinter as tk

from dataclasses import dataclass
from pymongo import MongoClient


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
    collection_devices = database["devices"]
    collection_notifications = database["notifications"]

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
        self.collection_devices.insert_one(device_data)

    def disconnection_message(self, client, userdata, msg):
        device_data = json.loads(msg.payload)
        print("Device disconnected from the system.")
        # Delete device data from database on disconnection
        self.collection_devices.delete_one({"mqtt_id": device_data["device_id"]})

    def check_policy_message(self, client, userdata, msg):
        device_data = json.loads(msg.payload)
        # Get the device type over the device id.
        device_type = device_data["device_id"]
        if "room_id" in device_data:
            device_location = device_data["room_id"]
        else:
            device_location = "N/A"
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
        # TODO Safe notifications in database
        if result:
            notification = {"message": f"All policies for the {device_type} are satisfied."}
            print(notification["message"])
            self.collection_notifications.insert_one(notification)
        elif priority == "mandatory":
            notification = {"message": f"Mandatory policies for the {device_type} are not satisfied."}
            print(notification["message"])
            self.collection_notifications.insert_one(notification)
        elif priority == "double_check":
            notification = {"message": f"Double check policies for the {device_type} are not satisfied."}
            print(notification["message"])
            self.collection_notifications.insert_one(notification)

            def get_failed_policy_actions(failed_sub_policies):
                # Make a request to the API to get the actions for the failed policies
                response = requests.get(f"http://localhost:8080/failed_policy_actions",
                                        params={"failed_sub_policies": failed_sub_policies,
                                                "device_type": device_type})
                # Parse the response and return the actions
                return response.json()["actions"]

            def yes_button_policy():
                # Manually set the result to True, so that the device executes the actions of the failed policies.
                # User overrules the policy decision.
                nonlocal result
                result = True
                # Update the policy_actions list with the actions for the failed policies
                nonlocal policy_actions
                failed_policy_action = get_failed_policy_actions(failed_sub_policies)
                policy_actions.extend(failed_policy_action)
                root.destroy()

            def no_button_policy():
                # Execute only the actions for the successful policies
                root.destroy()

            root = tk.Tk()
            root.title("Double-check")

            text = f"The following policies for the {device_type} are NOT satisfied." \
                   f" Do you want to manually override this decision? \n" \
                   + "\n".join(failed_sub_policies)
            label = tk.Label(root, text=text, wraplength=300)
            label.pack(fill=tk.X, pady=(0, 10))

            frame = tk.Frame(root)
            frame.pack(padx=50)

            left_button = tk.Button(frame, text="Yes", command=yes_button_policy)
            left_button.pack(side=tk.LEFT, padx=(0, 5))

            right_button = tk.Button(frame, text="No", command=no_button_policy, bg="blue")
            right_button.pack(side=tk.RIGHT)

            root.mainloop()
        elif priority == "optional":
            print(f"Optional policies for the {device_type} are not satisfied.")
        else:
            raise Exception("Unknown priority: " + priority)

        # Publish result to the requesting_device
        policy_topic = f"policy_result/{device_type}"
        client.publish(policy_topic, str(result))

        # Execute actions if there are any
        if policy_actions:
            def action_button_action(action, button):
                # Send action to device because the user clicked "Yes"
                notification = {"message": f"The following action was executed: {action}"}
                print(notification["message"])
                self.collection_notifications.insert_one(notification)
                button.configure(background='red', state=tk.DISABLED)
                device = action['device']
                if device_location != "N/A":
                    action_topic = f"action/{device_location}/{device}"
                else:
                    action_topic = f"action/{device}"
                payload = action['to_do']
                client.publish(action_topic, payload)

            def close_button_action():
                # Do not send actions to devices because the user clicked "No"
                root.destroy()

            def execute_all_actions():
                # Send all actions to devices because the user clicked "Execute all actions" or 30 seconds passed
                for action in policy_actions:
                    device = action['device']
                    if device_location != "N/A":
                        action_topic = f"action/{device_location}/{device}"
                    else:
                        action_topic = f"action/{device}"
                    payload = action['to_do']
                    client.publish(action_topic, payload)
                notification = {"message": f"The following actions were executed: {policy_actions}"}
                print(notification["message"])
                self.collection_notifications.insert_one(notification)
                root.destroy()

            root = tk.Tk()
            root.title("Actions")

            label = tk.Label(root, text=f"The following actions got triggered by the {device_type}\n"
                                        f"Do you want to execute these actions?")
            label.pack()

            mutually_exclusive_actions = []
            for action in policy_actions:
                device = action['device']
                payload = action['to_do']
                # If the action is open or close, it is mutually exclusive with other open/close actions
                if 'open' in payload or 'close' in payload:
                    mutually_exclusive_actions.append(action)
                else:
                    action_frame = tk.Frame(root)
                    action_frame.pack(fill=tk.X)
                    device_label = tk.Label(action_frame, text=device, width=10)
                    device_label.pack(side=tk.LEFT)
                    action_button = tk.Button(action_frame, text=payload.capitalize().replace('_', ' '))
                    action_button.config(command=lambda a=action, b=action_button: action_button_action(a, b))
                    action_button.pack(side=tk.RIGHT, padx=5)

            # If there are mutually exclusive actions, show them in a separate frame
            if len(mutually_exclusive_actions) > 1:
                label = tk.Label(root,
                                 text="The following actions are mutually exclusive, please select one to continue:")
                label.pack()
            for action in mutually_exclusive_actions:
                device = action['device']
                payload = action['to_do']
                action_frame = tk.Frame(root)
                action_frame.pack(fill=tk.X)
                device_label = tk.Label(action_frame, text=device, width=10)
                device_label.pack(side=tk.LEFT)
                action_button = tk.Button(action_frame, text=payload.capitalize().replace('_', ' '))
                action_button.config(command=lambda a=action, b=action_button: action_button_action(a, b))
                action_button.pack(side=tk.RIGHT, padx=5)

            all_button = tk.Button(root, text="Execute all actions", command=execute_all_actions)
            all_button.pack()

            button_frame = tk.Frame(root)
            button_frame.pack()

            close_button = tk.Button(button_frame, text="Close", command=close_button_action)
            close_button.pack(side=tk.RIGHT)

            # Schedule the execute_all_actions function to be called after 30 seconds
            root.after(30000, execute_all_actions)

            root.mainloop()

        else:
            print("No actions to execute.")

    def clear_db(self):
        self.collection_devices.delete_many({})
        print("Database cleared.")
