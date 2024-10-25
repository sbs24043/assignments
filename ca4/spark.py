import argparse
import os
import sys

os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

from pyspark.sql import SparkSession
from pyspark.context import SparkContext

from pyspark.mllib.util import MLUtils
from pyspark.mllib.regression import LabeledPoint

from pyspark.ml.regression import LinearRegression

from pyspark.ml.classification import MultilayerPerceptronClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator



# /usr/local/bin/python3.11 spark.py --step=read
def read_data():
    """
    Get Data from DB """
    # Initialize the Spark session
    spark = SparkSession.builder \
        .appName("MongoDBIntegration") \
        .config("spark.mongodb.input.uri", "mongodb://localhost:27017/stocks.PROCESSED_DB") \
        .config("spark.mongodb.output.uri", "mongodb://localhost:27017/stocks.PROCESSED_DB") \
        .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector:10.0.2') \
        .getOrCreate()
    
    # Read data from MongoDB
    all_data = spark.read \
        .format("mongodb") \
        .option("uri", "mongodb://localhost:27017/stocks") \
        .option("database", "stocks") \
        .option("collection", "PROCESSED_DB") \
        .load()
    
    all_data.createOrReplaceTempView("all_data")

    tickers = spark.sql(
        "SELECT * FROM all_data LIMIT 10")
    
    tickers.printSchema()

    # Query 1: Select all columns
    query1 = spark.sql("SELECT * FROM all_data")
    query1.show()
    
    # Query 2: Count the number of rows
    query2 = spark.sql("SELECT COUNT(*) AS row_count FROM all_data")
    query2.show()
    
    # Query 3: Calculate the average bert_score of the bert_score column
    query3 = spark.sql("SELECT AVG(bert_score) AS avg_score FROM all_data")
    query3.show()
    
    # Query 4: Find the maximum bert_score of the bert_score column
    query4 = spark.sql("SELECT MAX(bert_score) AS max_bert_score FROM all_data GROUP BY ticker")
    query4.show()
    
    # Query 5: Select stocks with large bert_score
    query5 = spark.sql("SELECT date, close, ticker FROM all_data WHERE bert_score > 0.5")
    query5.show()
    
    # Stop the Spark session
    spark.stop()


# To run locally:
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--step', help="The step to run: 'averages' or 'classifier'")
    args = parser.parse_args()
    
    if args.step == 'read':
      read_data()
