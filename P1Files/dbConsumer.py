from kafka import KafkaConsumer
import json
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import ssl

BROKER_SERVER = 'kafka-service:9092'

uri = "mongodb+srv://ryanhsullivan:tGWVn60E5ylc1btz@imagesdb.ecwkq.mongodb.net/?retryWrites=true&w=majority&appName=ImagesDB"
# Create a new client and connect to the server
client = MongoClient(uri)

database = client['imagesdb']
collection = database['images']

dbConsumer = KafkaConsumer(
    'images', 'predictions', 'performance',
    group_id='db-consumer',
    bootstrap_servers=[BROKER_SERVER],
    value_deserializer=lambda m: json.loads(m.decode('ascii')),
    consumer_timeout_ms=180000,
    auto_offset_reset='earliest'
)

for message in dbConsumer:
    collection.update_one(
        {"_id": message.value.get("ID")},
        { "$set": message.value },
        upsert=True
    )
    print("message received")
    dbConsumer.commit()