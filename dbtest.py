from pymongo import MongoClient

connection_string = "mongodb+srv://ryanhsullivan:tGWVn60E5ylc1btz@imagesdb.ecwkq.mongodb.net/?retryWrites=true&w=majority&appName=ImagesDB"
try:
    client = MongoClient(connection_string)
    db = client.imagesdb
    collection = db.images
    print("Databases:", client.list_database_names())
    print("Collections in ImagesDB:", db.list_collection_names())
    print("Sample document:", collection.find_one())
    print("Connection successful!")
except Exception as e:
    print("Failed to connect to MongoDB:", str(e))