# Message Handler
The message handler takes the requests for a policy check of MQTT clients and sends the answer of the policy server back to the requesting device aswell as the devices where an action got triggered.
Only the message_handler.py is required. Changes to it will effect the policy check. 
On line 93 of the message_handler.py the policy server is called by API of the project https://github.com/hitext5/master_thesis_python 
The MQTT clients like washing_machine.py are just devices created for test purposes. 

## To Bootstrap the Project
Install packages: pip install -r requirements.txt

Setup database:
1. Create account and database on https://cloud.mongodb.com/ (You can also use the same database as for the project https://github.com/hitext5/master_thesis_python)
2. Select "Connect" -> "Drivers" -> Copy the link from bulletpoint 3 into message_handler.py line 18 (atlas_uri_admin).
     If your IDE can not connect to the database use the Driver Link for Python 3.3 or earlier even with an older version (as in the current version commit 15).
3. Replace line 22 (db_name) with your database name.

Install MQTT Broker: https://mosquitto.org/download/
Start the MQTT broker with mosquitto -v in the terminal under the path where you installed mosquitto, e.g., C:\Program Files\mosquitto.

## How it works
To test a policy adjust the file test_cases.py and run it. 
When adding an MQTT client to the MQTT broker make sure to use the line while message_handler.rc != 0: time.sleep(1), as on line 35 and 36, to ensure that the MQTT client is connected before adding a second one. 
