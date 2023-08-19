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
message_handler.clear_db()


def test_solar_panel_example():
    washing_machine = WashingMachine(work_power=400, last_cleaning=6)
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

    assert washing_machine.turn_on()


# solar_panel_example()


def test_window_example():
    weather_station = WeatherStation(temperature=20, rain_sensor=False,
                                     wind_speed=0)
    smartphone = Smartphone(at_home=True)
    thermostat = Thermostat(device_id="thermostat_bathroom", temperature=30, air_quality=110, room_id="bathroom", fan_on=False,
                            heating_on=True, ac_on=False)
    window = Window(window_open=True, room_id="bathroom")
    window2 = Window(window_open=True, room_id="kitchen")

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

    assert thermostat.send_current_status()

# window_example()

# Test to add a policy and delete it
# def policy_example():
#     response = requests.post(
#         f"http://localhost:8080/add_policy",
#         json={
#             "priority": "mandatory",
#             "actions": [{'device': 'window', 'to_do': 'open_window'},
#                         {'device': 'gas_valve', 'to_do': 'turn_off'}],
#             "policy_name": "test",
#             "policy_code": "def eval_policy_gas_detected(requesting_device, collection):"
#                                "return requesting_device['gas_level'] > 30",
#             "imports": [],
#             "device_type": "carbon_monoxide_detector"
#         }
#     )
#
#     print(response.text)
#
#
# policy_example()
#
# response = requests.get(
#     f"http://localhost:8080/get_policies/local/carbon_monoxide_detector")
# print(response.text)
#
# response = requests.get(
#     f"http://localhost:8080/pending_new_policies/carbon_monoxide_detector")
# print(response.text)
#
# response = requests.put(
#     f"http://localhost:8080/update_policies/carbon_monoxide_detector")
# print(response.text)
#
# response = requests.get(
#     f"http://localhost:8080/get_policies/local/carbon_monoxide_detector")
# print(response.text)

# response = requests.delete(
#     f"http://localhost:8080/delete_policy/local/smartphone/eval_policy_owner_home")
# print(response.text)

# policy_example()

# response = requests.post(
#     f"http://localhost:8080/share_policy/thermostat/eval_policy_ac_on")
# print(response.text)

# response = requests.post(
#     f"http://localhost:8080/add_policy_from_db/community/thermostat/eval_policy_ac_on")
# print(response.text)

# response = requests.get(
#     f"http://localhost:8080/get_devices")
# print(response.json())
#
# response = requests.delete(
#     f"http://localhost:8080/delete_policy/local/carbon_monoxide_detector/eval_policy_gas_detected")
# print(response.text)
#
# response = requests.get(
#     f"http://localhost:8080/change_policy/local/thermostat/eval_policy_ac_on")
# print(response.json())
#
# response = requests.post(
#     f"http://localhost:8080/share_policy/thermostat/eval_policy_ac_on")
# print(response.text)
