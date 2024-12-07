from pyspark.sql import SparkSession

# Initialize Spark session
spark = SparkSession.builder \
    .appName("InferenceErrorCount") \
    .config("spark.mongodb.input.uri", "mongodb+srv://ryanhsullivan:tGWVn60E5ylc1btz@imagesdb.ecwkq.mongodb.net/?retryWrites=true&w=majority&appName=ImagesDB/ImagesDB.images?retryWrites=true&w=majority") \
    .config("spark.mongodb.output.uri", "mongodb+srv://ryanhsullivan:tGWVn60E5ylc1btz@imagesdb.ecwkq.mongodb.net/?retryWrites=true&w=majority&appName=ImagesDB/ImagesDB.error_counts?retryWrites=true&w=majority") \
    .getOrCreate()

# Load data from MongoDB
data = spark.read.format("mongo").load()

# Filter incorrect inferences
incorrect_inferences = data.filter(data["GroundTruth"] != data["InferredValue"])

# Count incorrect inferences by producer
results = incorrect_infereces.groupBy("ID").count()

# Show results (for debugging)
results.show()

# Save results back to MongoDB
results.write.format("mongo").mode("append").save()