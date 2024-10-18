from kafka import KafkaConsumer
import json
import requests

url = "http://192.168.5.251:5000/predict"
BROKER_SERVER = '192.168.5.54:9092'

mlConsumer = KafkaConsumer(
    'images',
    group_id='dbb-consumer',
    bootstrap_servers=[BROKER_SERVER],
    value_deserializer=lambda m: json.loads(m.decode('ascii')),
    consumer_timeout_ms=2000,
    auto_offset_reset='earliest'
)

print("Consumer created")

for message in mlConsumer:
    # print("Sending Message...")
    # outgoing = {"ID": message.value.get("ID"), "Data": message.value.get("Data")}
    # # Send just the id and data field of the json message
    # requests.post(url, json=outgoing)
    print("Message sent")
    mlConsumer.commit()