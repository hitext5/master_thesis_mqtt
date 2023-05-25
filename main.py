import time

from pymongo import MongoClient

from electronic_device import ElectronicDevice
from message_handler import MessageHandler
from smartphone import Smartphone
from solar_panel import SolarPanel
from thermostat import Thermostat
from weather_station import WeatherStation
from window import Window

# C:\Program Files\mosquitto
# mosquitto -v
# If the port is already listening
# netstat -ano | findstr :1883
# taskkill /pid 7392 /F
# Run mosquitto -v in a terminal to see the messages being sent and received.

atlas_uri = "mongodb://Kleriakanus:test123@ac-s2miieu-shard-00-00.s0mnged.mongodb.net:27017," \
            "ac-s2miieu-shard-00-01.s0mnged.mongodb.net:27017," \
            "ac-s2miieu-shard-00-02.s0mnged.mongodb.net:27017/?ssl=true&replicaSet=atlas-vihgip-shard-0" \
            "&authSource=admin&retryWrites=true&w=majority"
db_name = 'Cluster0'
mongo_client = MongoClient(atlas_uri)
database = mongo_client[db_name]
collection = database["devices"]


def solar_panel_example():
    message_handler = MessageHandler()
    washing_machine = ElectronicDevice(device_id="washing_machine", work_power=400, last_cleaning=4)
    washer = ElectronicDevice(device_id="washer", work_power=200, last_cleaning=0)
    solar_panel = SolarPanel(device_id="solar_panel", provided_power=500)

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
    # time.sleep(5)

    washer.connect()
    washer.client.loop_start()
    print("Washing machine loop started")
    while washer.rc != 0:
        time.sleep(1)
    # time.sleep(5)

    solar_panel.connect()
    solar_panel.client.loop_start()
    print("Solar panel loop started")
    while solar_panel.rc != 0:
        time.sleep(1)
    # time.sleep(5)

    # In the real world these updates will be done by the devices themselves.
    if washing_machine.turn_on():
        collection.update_one({"device_id": washing_machine.device_id},
                              {"$set": {"powered_by": solar_panel.device_id}})
        collection.update_one(
            {"device_id": washing_machine.device_id},
            {"$set": {"last_cleaning": washing_machine.last_cleaning}}
        )


# solar_panel_example()


def window_example():
    message_handler = MessageHandler()
    weather_station = WeatherStation(device_id="weather_station", temperature=20, rain_sensor=False,
                                     wind_speed=0)
    smartphone = Smartphone(device_id="smartphone", at_home=True)
    thermostat = Thermostat(device_id="thermostat", temperature=30, air_quality=100, room_id="room1", fan_on=False,
                            heating_on=True, ac_on=False)
    window = Window(device_id="window", window_open=False, room_id="room1")
    window2 = Window(device_id="window", window_open=False, room_id="room2")

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
    # time.sleep(5)

    smartphone.connect()
    smartphone.client.loop_start()
    print("Smartphone loop started")
    while smartphone.rc != 0:
        time.sleep(1)
    # time.sleep(5)

    thermostat.connect()
    thermostat.client.loop_start()
    print("Thermostat loop started")
    while thermostat.rc != 0:
        time.sleep(1)
    # time.sleep(5)

    window.connect()
    window.client.loop_start()
    print("Window loop started")
    while window.rc != 0:
        time.sleep(1)
    # time.sleep(5)

    window2.connect()
    window2.client.loop_start()
    print("Window2 loop started")
    while window2.rc != 0:
        time.sleep(1)
    # time.sleep(5)

    if thermostat.send_current_status():
        # collection.update_one({"device_id": window.device_id},
        #                       {"$set": {"window_open": True}})
        # collection.update_one(
        #     {"device_id": thermostat.device_id},
        #     {"$set": {"ac_on": False}}
        # )
        # collection.update_one(
        #     {"device_id": thermostat.device_id},
        #     {"$set": {"heating_on": True}}
        # )
        time.sleep(5)


window_example()
