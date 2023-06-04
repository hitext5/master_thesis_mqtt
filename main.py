from pymongo import MongoClient
from flask import Flask, render_template

from message_handler import MessageHandler


atlas_uri = "mongodb://Kleriakanus:test123@ac-s2miieu-shard-00-00.s0mnged.mongodb.net:27017," \
            "ac-s2miieu-shard-00-01.s0mnged.mongodb.net:27017," \
            "ac-s2miieu-shard-00-02.s0mnged.mongodb.net:27017/?ssl=true&replicaSet=atlas-vihgip-shard-0" \
            "&authSource=admin&retryWrites=true&w=majority"
db_name = 'Cluster0'
mongo_client = MongoClient(atlas_uri)
database = mongo_client[db_name]
collection = database["devices"]
policies_collection = database['policies']
thing_collection = database['things']
collection_notifications = database["notifications"]
message_handler = MessageHandler()
app = Flask(__name__)


@app.route('/')
@app.route('/home')
def home():
    """
    Render the home page for the 'dashboard' module
    This returns the names and URLs of adjacent directories
    """
    return render_template("homescreen.html", tagname='home')


@app.route('/policylist')
def policylist():
    """
    List of objects
    """
    policies = policies_collection.find()
    policies_ids = {policy["id"]: {"description": policy["description"], "device_actor": policy["device_actor"],
                                   "device_actee": policy["device_actee"]} for policy in policies}
    return render_template('policylist.html', tagname='policylist', policies_ids=policies_ids)


if __name__ == "__main__":
    app.run()
