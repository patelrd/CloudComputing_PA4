from kafka import KafkaConsumer
import json
import requests

url = "http://192.168.5.247:5000/predict"

mlConsumer = KafkaConsumer(
    'images',
    group_id='dbb-consumer',
    bootstrap_servers=['192.168.5.18:9092'],
    value_deserializer=lambda m: json.loads(m.decode('ascii')),
    consumer_timeout_ms=2000,
    auto_offset_reset='earliest'
)

print("Consumer created")

for message in mlConsumer:
    print("Sending Message...")
    outgoing = {"ID": message.value.get("ID"), "Data": message.value.get("Data")}
    # Send just the id and data field of the json message
    requests.post(url, json=outgoing)
    print("Message sent")
    mlConsumer.commit()