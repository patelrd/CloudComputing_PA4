import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
from torchvision import datasets, transforms
from PIL import Image
import io
import base64
import random
from flask import Flask, request, jsonify
from kafka import KafkaProducer
import json

app = Flask(__name__)

BROKER_SERVER = 'kafka-service:9092'

# Define the SimpleCNN model
class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.fc1 = nn.Linear(64 * 8 * 8, 128)
        self.fc2 = nn.Linear(128, 10)
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        x = self.pool(nn.ReLU()(self.conv1(x)))
        x = self.pool(nn.ReLU()(self.conv2(x)))
        x = x.view(-1, 64 * 8 * 8)
        x = self.dropout(nn.ReLU()(self.fc1(x)))
        x = self.fc2(x)
        return x

# CIFAR-10 dataset transformations
transform = transforms.Compose([
    transforms.Resize((32, 32)),  # Ensure the image size is 32x32
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))  # CIFAR-10 mean and std
])

# Load CIFAR-10 Dataset
trainset = datasets.CIFAR10(root='./data', train=True, download=True, transform=transform)
trainloader = torch.utils.data.DataLoader(trainset, batch_size=64, shuffle=True)

# Instantiate model, loss function, and optimizer
model = SimpleCNN()
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training function
def train_model(model, trainloader, criterion, optimizer, num_epochs=1):
    try:
        for epoch in range(num_epochs):
            for i, (inputs, labels) in enumerate(trainloader):
                optimizer.zero_grad()
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()
    except Exception as e:
        print(f"Training failed with error: {e}")

# Function to decode the base64 image and convert it to a tensor
def decode_image_from_base64(image_str):
    # Decode the base64 string to bytes
    image_bytes = base64.b64decode(image_str)
    
    # Convert the bytes to a PIL image
    image_pil = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    
    # Resize and preprocess the image
    image_tensor = transform(image_pil)
    
    return image_tensor

# Function to predict the class of the base64 image
def predict_from_base64(base64_image, model):
    model.eval()  # Set the model to evaluation mode

    # Decode the base64 image and convert it to a tensor
    image_tensor = decode_image_from_base64(base64_image)
    image_tensor = image_tensor.unsqueeze(0)  # Add batch dimension

    # Make prediction using the model
    with torch.no_grad():
        output = model(image_tensor)
        _, predicted = torch.max(output.data, 1)

    # Print the predicted class
    return trainset.classes[predicted.item()]

# Set up Kafka producer to stream predictions
def serialize_json(value):
    json_string = json.dumps(value)
    json_bytes = json_string.encode('utf-8')
    return json_bytes

producer = KafkaProducer(
    bootstrap_servers=BROKER_SERVER,
    acks=1,
    value_serializer=serialize_json
)

# Train the model
print("Training the model...")
train_model(model, trainloader, criterion, optimizer, num_epochs=1)
print("Model trained!")

@app.route('/predict', methods=['POST'])
def predict():
    message = request.get_json()
    data = message.get("Data")
    print("Data received: ", data)
    inferredValue = predict_from_base64(data, model)

    print("Inferred value: ", inferredValue)

    # Create a new Kafka message with the data and prediction
    result_data = {
        "ID": message.get("ID"),  # You can assign a unique ID to this prediction
        "InferredValue": inferredValue,  # The predicted class
        "starttime": message.get("starttime")
    }

    # Send the result to a Kafka topic (e.g., 'predictions')
    producer.send("predictions", value=result_data)
    producer.flush()

    return jsonify({"message": "Data received"}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)