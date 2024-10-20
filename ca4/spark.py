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

# /usr/local/bin/python3.11 spark.py --step=train
def create_regression(input_source, output_uri):
    with SparkSession.builder.appName("MiningRegression").getOrCreate() as spark:
        # Split the data into train and test
        data = spark.read.format("libsvm").option("numFeatures", "22").load(input_source)
        lr = LinearRegression(maxIter=10, regParam=0.3, elasticNetParam=0.8)

        # Fit the model
        lrModel = lr.fit(data)

        # Print the coefficients and intercept for linear regression
        print("Coefficients: %s" % str(lrModel.coefficients))
        print("Intercept: %s" % str(lrModel.intercept))

        # Summarize the model over the training set and print out some metrics
        trainingSummary = lrModel.summary
        print("numIterations: %d" % trainingSummary.totalIterations)
        print("objectiveHistory: %s" % str(trainingSummary.objectiveHistory))
        trainingSummary.residuals.show()
        print("RMSE: %f" % trainingSummary.rootMeanSquaredError)
        print("r2: %f" % trainingSummary.r2)

        lrModel.write().overwrite().save(output_uri + "/regression")



# To run locally:
# python3 mining_pyspark.py --data_source=/Users/olenapleshan/data_analytics/ca3/Cleaned_MiningProcess_Flotation_Plant_Database.csv --output_uri=mining_output.txt --step=averages
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--step', help="The step to run: 'averages' or 'classifier'")
    args = parser.parse_args()
    
    if args.step == 'read':
      read_data()
    
        
    if args.step == 'train':
      read_data()