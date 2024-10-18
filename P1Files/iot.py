import base64
import json
import time # for sleep
from kafka import KafkaProducer, KafkaConsumer, TopicPartition  # producer of events
from PIL import Image, ImageFilter
from torchvision import datasets, transforms
import io
import random
import uuid
import threading

# NOTE: Change num.partitions=1 to 4 in kafka sever.properties file, based on number of producers expected at installation

# Load CIFAR-10 dataset
dataset = datasets.CIFAR10(root='./data', download=True, transform=transforms.ToTensor())

BROKER_SERVER = '192.168.5.54:9092'

sentImageTimes = {}

def emulate_camera_feed():
    # randomly select img and correct label from dataset
    img, label = random.choice(dataset)

    # add blurriness/noise by converting img to PIL and add blur
    img_pil = transforms.ToPILImage()(img).filter(ImageFilter.GaussianBlur(radius=2))

    # convert img to bytes for transmission
    buffered = io.BytesIO()
    img_pil.save(buffered, format='JPEG')
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

    ID = str(uuid.uuid4())
    groundtruth = dataset.classes[label]
    
    # create JSON object
    data = {
        "ID": ID,
        "GroundTruth": groundtruth,
        "Data": img_str
    }

    # return JSON obj
    return data

# encode JSON to bytes
def serialize_json(value):
    json_string = json.dumps(value)
    json_bytes = json_string.encode('utf-8')
    return json_bytes

def run_producer():
    # acquire the producer
    producer = KafkaProducer(
        bootstrap_servers=BROKER_SERVER, 
        acks=1,
        value_serializer=serialize_json  # serialize JSON to bytes
    )

    # send the contents 5 times after a sleep of 1 sec in between
    for i in range(5):
        print("Sending image")
        # generate the data
        data = emulate_camera_feed()

        # track the images sent and the times or each
        sentImageTimes[data.get("ID")] = time.time()

        # send the data under topic images
        producer.send("images", value=data)
        producer.flush()

        # sleep 1 second
        time.sleep(1)

    producer.close()

def run_consumer():
    consumer = KafkaConsumer(
        'predictions',
        group_id='performance-consumer'+uuid.uuid4().hex,
        bootstrap_servers=[BROKER_SERVER],
        value_deserializer=lambda m: json.loads(m.decode('ascii')),
        auto_offset_reset='earliest'
    )

    producer = KafkaProducer(
        bootstrap_servers=BROKER_SERVER, 
        acks=1,
        value_serializer=serialize_json  # serialize JSON to bytes
    )

    for message in consumer:
        if message.value.get("ID") not in sentImageTimes:
            continue
        new_data = {
            "ID": message.value.get("ID"),
            "elapsedTime": time.time() - sentImageTimes[message.value.get("ID")],
        }
        print(json.dumps(new_data))
        producer.send("performance", value=new_data)
        print("message received")
        consumer.commit()

def run_threads():
    producer_thread = threading.Thread(target=run_producer)
    consumer_thread = threading.Thread(target=run_consumer)

    producer_thread.start()
    consumer_thread.start()

    producer_thread.join()
    consumer_thread.join()

if __name__ == '__main__':
    run_threads()