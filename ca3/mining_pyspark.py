import argparse
# import os
# import sys

from pyspark.sql import SparkSession
from pyspark.context import SparkContext

from pyspark.mllib.util import MLUtils
from pyspark.mllib.regression import LabeledPoint

from pyspark.ml.regression import LinearRegression

from pyspark.ml.classification import MultilayerPerceptronClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

# os.environ['PYSPARK_PYTHON'] = sys.executable
# os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable


# python3 mining_pyspark.py --data_source=/Users/olenapleshan/data_analytics/ca3/Cleaned_MiningProcess_Flotation_Plant_Database.csv --output_uri=mining_output/sql --step=averages
def calculate_averages(data_source, output_uri):
    """
    Processes iron mining impurities dataset and calculate averages for the rounded percentage of silica concentrate

    :param data_source: The URI of the Mining Process Flotation dataset, such as 's3://DOC-EXAMPLE-BUCKET/food-establishment-data.csv'.
    :param output_uri: The URI where output is written, such as 's3://DOC-EXAMPLE-BUCKET/restaurant_violation_results'.
    """
    with SparkSession.builder.appName("MiningAvg").getOrCreate() as spark:
        # Load the mining flotation CSV data
        if data_source is not None:
            mining_df = spark.read.option("header", "true").csv(data_source)

        # Create an in-memory DataFrame to query
        mining_df.createOrReplaceTempView("mining_df")

        process_flotation_avgs = spark.sql("""
          SELECT ROUND(pct_silica_concentrate) as rnd_pct_silica_concentrate,
                 AVG(ore_pulp_ph) AS avg_ore_pulp_ph,
                 AVG(pct_iron_feed) as avg_pct_iron_feed,
                 AVG(pct_silica_feed) as avg_pct_silica_feed
          FROM mining_df 
          GROUP BY ROUND(pct_silica_concentrate)
          """)

        # Write the results to the specified output URI
        process_flotation_avgs.write.option("header", "true").mode("overwrite").csv(output_uri)


# python3 mining_pyspark.py --data_source=/Users/olenapleshan/data_analytics/ca3/Cleaned_MiningProcess_Flotation_Plant_Database.csv --output_uri=mining_output/libsvm --step=createlibsvm
def create_libsvm(data_source, output_uri):
    with SparkSession.builder.appName("MiningLibsvm").getOrCreate() as spark:
      # Load training data and convert to LibSVM format
      data = spark.read.option("header", "true").csv(data_source)
      data_rdd = data.rdd

      data_libsvm = data_rdd.map(lambda line: LabeledPoint(int(float(line[23])),
                                                           [round(float(i), 4) for i in line[1:23]]))
      MLUtils.saveAsLibSVMFile(data_libsvm, output_uri + "/classification")
      
      data_libsvm = data_rdd.map(lambda line: LabeledPoint(float(line[23]),
                                                           [round(float(i), 4) for i in line[1:23]]))
      MLUtils.saveAsLibSVMFile(data_libsvm, output_uri + "/regression")


# python3 mining_pyspark.py --data_source=mining_output/libsvm/regression --output_uri=mining_output/ml-results --step=regression
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


# https://spark.apache.org/docs/latest/ml-classification-regression.html#multilayer-perceptron-classifier
# python3 mining_pyspark.py --data_source=mining_output/libsvm/classification --output_uri=mining_output/ml-results --step=classification
def create_classifier(input_source, output_uri):
    sc = SparkContext('local')

    with SparkSession.builder.appName("MiningClassification").getOrCreate() as spark:
        # Split the data into train and test
        data = spark.read.format("libsvm").option("numFeatures", "22").load(input_source)

        splits = data.randomSplit([0.6, 0.4], 1234)
        train = splits[0]
        test = splits[1]
        
        # specify layers for the neural network:
        # input layer of size 22 (features), two intermediate of size 8 and 7
        # and output of size 6 (classes)
        layers = [22, 8, 7, 6] # 5 classes in file 1
        
        # create the trainer and set its parameters
        trainer = MultilayerPerceptronClassifier(maxIter=10, layers=layers, blockSize=128, seed=1234)
        model = trainer.fit(train)
        
        # compute accuracy on the test set
        result = model.transform(test)
        predictionAndLabels = result.select("prediction", "label")
        evaluator = MulticlassClassificationEvaluator(metricName="accuracy")
        print("Test set accuracy = " + str(evaluator.evaluate(predictionAndLabels)))
        
        model.write().overwrite().save(output_uri + "/classification")


# To run locally:
# python3 mining_pyspark.py --data_source=/Users/olenapleshan/data_analytics/ca3/Cleaned_MiningProcess_Flotation_Plant_Database.csv --output_uri=mining_output.txt --step=averages
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--data_source', help="The URI for the Mining Process Flotation data, like an S3 bucket location.")
    parser.add_argument(
        '--output_uri', help="The URI where output is saved, like an S3 bucket location.")
    parser.add_argument(
        '--step', help="The step to run: 'averages' or 'classifier'")
    args = parser.parse_args()
    
    if args.step == 'averages':
      calculate_averages(args.data_source, args.output_uri)

    if args.step == 'createlibsvm':
      create_libsvm(args.data_source, args.output_uri)

    if args.step == 'classification':
      create_classifier(args.data_source, args.output_uri)
    
    if args.step == 'regression':
      create_regression(args.data_source, args.output_uri)