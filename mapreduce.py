from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, count

# Create a SparkSession with MongoDB support
spark = SparkSession.builder \
    .appName("MongoDBComparison") \
    .config("spark.mongodb.read.connection.uri", "mongodb+srv://ryanhsullivan:tGWVn60E5ylc1btz@imagesdb.ecwkq.mongodb.net/imagesdb.images") \
    .config("spark.mongodb.write.connection.uri", "mongodb+srv://ryanhsullivan:tGWVn60E5ylc1btz@imagesdb.ecwkq.mongodb.net/imagesdb.error_counts") \
    .config("spark.mongodb.input.partitioner", "MongoPaginateBySizePartitioner") \
    .config("spark.mongodb.input.partitionerOptions.partitionSizeMB", "16") \
    .config("partitionKey", "_id") \
    .config("numberOfPartitions", "4") \
    .getOrCreate()

# Read data from the MongoDB `images` collection
df = spark.read.format("mongodb").load()
df = df.repartition(4)

# Compare GroundTruth and InferredValue and add a new column `IsError`
df_with_errors = df.withColumn(
    "IsError",
    when(col("GroundTruth") != col("InferredValue"), 1).otherwise(0)
)

# Count total errors
error_count_df = df_with_errors.groupBy().agg(count(when(col("IsError") == 1, 1)).alias("ErrorCount"))

# Write error counts to the MongoDB `error_counts` collection
error_count_df.write.format("mongodb").mode("overwrite").save()

# Stop the SparkSession
spark.stop()