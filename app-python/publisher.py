from google.cloud import pubsub_v1
import json, os
 
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path("assessment-demo", "writes-topic")
 
def publish_writes(writes):
    data = json.dumps(writes).encode("utf-8")
    future = publisher.publish(topic_path, data)
    return future. Result()
