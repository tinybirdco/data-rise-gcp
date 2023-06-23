"""Publishes multiple random messages to a Pub/Sub topic."""

from google.cloud import pubsub_v1
from datetime import datetime
import random
import json

project_id = <YOUR_PROJECT>
topic_id = <YOUR_TOPIC_ID>

browsers = ['Chrome','Opera','Firefox','Safari']
OSs = ['Windows','Linux','OSX','iOS','Android']
products = ['6cHumpSxTvs', 'Fg15LdqpWrs', 'Zu7A1GCSjZE', 'fSdBxY0NxVI', 'xFmXLq_KJxg', '5d0cgAl5BTk', 'YY4YaHKh2jQ', 'p8Drpg_duLw', 'sZzx0cUDX98']
event_types = ['view','cart','sale']
events_weights = [60, 33, 24]


publisher = pubsub_v1.PublisherClient()
# The `topic_path` method creates a fully qualified identifier
# in the form `projects/{project_id}/topics/{topic_id}`
topic_path = publisher.topic_path(project_id, topic_id)

while True:
    product_id = random.choice(prods)
    units = random.randrange(1, 3, 1)
    event_type = random.choice(event_types)
    event = {
        'timestamp': datetime.utcnow().isoformat(),
        'event': random.choices(event_types, weights=events_weights,k=1)[0],
        'product': random.choice(products),
        'browser': random.choice(browsers),
        'OS': random.choice(OSs),
    }

    data_str = json.dumps(event)
    data = data_str.encode("utf-8")

    # When you publish a message, the client returns a future.
    future = publisher.publish(topic_path, data)
    print(future.result())