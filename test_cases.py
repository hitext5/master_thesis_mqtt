import time
import requests

from Washer import Washer
from message_handler import MessageHandler
from smartphone import Smartphone
from solar_panel import SolarPanel
from thermostat import Thermostat
from washing_machine import WashingMachine
from weather_station import WeatherStation
from window import Window

# C:\Program Files\mosquitto
# mosquitto -v
# If the port is already listening
# netstat -ano | findstr :1883
# taskkill /pid 7392 /F
# Run mosquitto -v in a terminal to see the messages being sent and received.

message_handler = MessageHandler()
# Reset the database before running the examples
# message_handler.clear_db()


def solar_panel_example():
    washing_machine = WashingMachine(work_power=400, last_cleaning=3)
    washer = Washer(work_power=200)
    solar_panel = SolarPanel(provided_power=500)

    message_handler.connect()
    message_handler.client.loop_start()
    print("MessageHandler loop started")
    while message_handler.rc != 0:
        time.sleep(1)

    washing_machine.connect()
    washing_machine.client.loop_start()
    print("Washer loop started")
    while washing_machine.rc != 0:
        time.sleep(1)
    time.sleep(5)

    washer.connect()
    washer.client.loop_start()
    print("Washing machine loop started")
    while washer.rc != 0:
        time.sleep(1)
    time.sleep(5)

    solar_panel.connect()
    solar_panel.client.loop_start()
    print("Solar panel loop started")
    while solar_panel.rc != 0:
        time.sleep(1)
    time.sleep(5)

    if washing_machine.turn_on():
        time.sleep(5)


# solar_panel_example()


def window_example():
    weather_station = WeatherStation(temperature=20, rain_sensor=False,
                                     wind_speed=0)
    smartphone = Smartphone(at_home=True)
    thermostat = Thermostat(temperature=30, air_quality=100, room_id="room1", fan_on=False,
                            heating_on=True, ac_on=False)
    window = Window(window_open=True, room_id="room1")
    window2 = Window(window_open=True, room_id="room2")

    message_handler.connect()
    message_handler.client.loop_start()
    print("MessageHandler loop started")
    while message_handler.rc != 0:
        time.sleep(1)

    weather_station.connect()
    weather_station.client.loop_start()
    print("WeatherStation loop started")
    while weather_station.rc != 0:
        time.sleep(1)
    time.sleep(5)

    smartphone.connect()
    smartphone.client.loop_start()
    print("Smartphone loop started")
    while smartphone.rc != 0:
        time.sleep(1)
    time.sleep(5)

    thermostat.connect()
    thermostat.client.loop_start()
    print("Thermostat loop started")
    while thermostat.rc != 0:
        time.sleep(1)
    time.sleep(5)

    window.connect()
    window.client.loop_start()
    print("Window loop started")
    while window.rc != 0:
        time.sleep(1)
    time.sleep(5)

    window2.connect()
    window2.client.loop_start()
    print("Window2 loop started")
    while window2.rc != 0:
        time.sleep(1)
    time.sleep(5)

    if thermostat.send_current_status():
        time.sleep(5)


# window_example()

# Test to add a policy and delete it
def policy_example():
    response = requests.post(
        f"http://localhost:8080/add_sub_policy",
        json={
            "priority": "mandatory",
            "actions": [{"device": "window", "to_do": "close_window"}],
            "sub_policy_name": "eval_policy_owner_home",
            "sub_policy_code":
                "return requesting_device['at_home'] and not eval_policy_gas_detected(requesting_device, collection)",
            "imports": ["from policies.carbon_monoxide_detector import eval_policy_gas_detected"],
            "device_type": "smartphone"
        }
    )
    print(response.text)

    response = requests.put(
        f"http://localhost:8080/update_policies/smartphone")
    print(response.text)

    response = requests.delete(
        f"http://localhost:8080/delete_sub_policy/local/smartphone/eval_policy_owner_home")
    print(response.text)

# policy_example()
# response = requests.get(
#     f"http://localhost:8080/change_sub_policy/community/smartphone/eval_policy_owner_home")
# print(response.json())


response = requests.get(
    f"http://localhost:8080/get_possible_actions/thermostat")
print(response.json())

# response = requests.delete(
#     f"http://localhost:8080/delete_sub_policy/local/smartphone/eval_policy_owner_home")
# print(response.text)
#
# response = requests.get(
#     f"http://localhost:8080/get_sub_policies/local/smartphone")
# print(response.text)
