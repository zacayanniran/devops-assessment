import os, json, time
from google.cloud import pubsub_v1
from pymongo import MongoClient
 
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path("assessment-project", "writes-sub")
 
mongo = MongoClient(os.getenv("MONGODB_URI"))
db = mongo.get_database()
 
def callback(message):
    items = json.loads(message.data.decode("utf-8"))
    db.col.insert_many(items, ordered=False)   # batch insert
    message.ack()
 
subscriber.subscribe(subscription_path, callback)
 
print("Worker started")
while True:
    time.sleep(1)
