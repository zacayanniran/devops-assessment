import os, json, time
from google.cloud import pubsub_v1
from pymongo import MongoClient

project_id = "assessment-project"  # Can be dummy for emulator
subscription_id = "writes-sub"
topic_id = "writes-topic"  # Assume this matches your publisher

# Create subscriber client
subscriber = pubsub_v1.SubscriberClient()

# Create topic and subscription if not exist (safe for emulator)
topic_path = subscriber.topic_path(project_id, topic_id)
try:
    subscriber.get_topic(request={"topic": topic_path})
except Exception:
    subscriber.create_topic(request={"name": topic_path})
    print(f"Created topic: {topic_path}")

subscription_path = subscriber.subscription_path(project_id, subscription_id)
try:
    subscriber.get_subscription(request={"subscription": subscription_path})
except Exception:
    subscriber.create_subscription(request={"name": subscription_path, "topic": topic_path})
    print(f"Created subscription: {subscription_path}")

mongo_uri = os.getenv("MONGODB_URI", "mongodb://mongo:27017/assessmentdb")  # Fallback
mongo = MongoClient(mongo_uri)
db = mongo.get_database()  # Uses db from URI
collection = db["records"]  # Fixed: Use db["records"]

def callback(message):
    items = json.loads(message.data.decode("utf-8"))
    collection.insert_many(items, ordered=False)  # Batch insert
    message.ack()

# Subscribe (streaming pull for efficiency)
streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print("Worker started, listening for messages...")

# Keep alive
with subscriber:
    try:
        streaming_pull_future.result()  # Blocks until cancelled
    except Exception as e:
        streaming_pull_future.cancel()
        print(f"Error in subscriber: {e}")