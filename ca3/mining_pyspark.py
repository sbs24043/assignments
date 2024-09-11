import argparse

from pyspark.sql import SparkSession

from pyspark.mllib.util import MLUtils
from pyspark.mllib.regression import LabeledPoint

from pyspark.ml.classification import MultilayerPerceptronClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

from pyspark.ml.linalg import Vectors



def calculate_averages(data_source, output_uri):
    """
    Processes iron mining impurities dataset and calculate averages for the rounded percentage of silica concentrate

    :param data_source: The URI of the Mining Process Flotation dataset, such as 's3://DOC-EXAMPLE-BUCKET/food-establishment-data.csv'.
    :param output_uri: The URI where output is written, such as 's3://DOC-EXAMPLE-BUCKET/restaurant_violation_results'.
    """
    with SparkSession.builder.appName("Mining Flotation Averages").getOrCreate() as spark:
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

def create_libsvm(data_source, output_uri):
    with SparkSession.builder.appName("Mining Flotation Averages").getOrCreate() as spark:
      # Load training data and convert to LibSVM format
      data = spark.read.option("header", "true").csv(data_source)
      data_rdd = data.rdd
      data_libsvm = data_rdd.map(lambda line: LabeledPoint(round(float(line[23])),[float(i, 2) for i in line[1:23]]))
      MLUtils.saveAsLibSVMFile(data_libsvm, output_uri + "/data/libsvm-mining-flotation")

# https://spark.apache.org/docs/latest/ml-classification-regression.html#multilayer-perceptron-classifier
# python3 mining_pyspark.py --data_source=/Users/olenapleshan/data_analytics/ca3/Cleaned_MiningProcess_Flotation_Plant_Database.csv --output_uri=mining_output --step=classifier
def create_classifier(data_source, output_uri):
    with SparkSession.builder.appName("Mining Flotation Averages").getOrCreate() as spark:
        # Split the data into train and test
        data = spark.read.format("libsvm").load(output_uri +"/data/libsvm-mining-flotation/part-00000")
        splits = data.randomSplit([0.6, 0.4], 1234)
        train = splits[0]
        test = splits[1]
        
        # specify layers for the neural network:
        # input layer of size 4 (features), two intermediate of size 5 and 4
        # and output of size 3 (classes)
        # layers = [4, 5, 4, 3]
        layers = [21, 22, 21, 6]
        
        # create the trainer and set its parameters
        trainer = MultilayerPerceptronClassifier(maxIter=100, layers=layers, blockSize=128, seed=1234)
        
        # train the model
        model = trainer.fit(train)
        
        # compute accuracy on the test set
        result = model.transform(test)
        predictionAndLabels = result.select("prediction", "label")
        evaluator = MulticlassClassificationEvaluator(metricName="accuracy")
    
        print("Test set accuracy = " + str(evaluator.evaluate(predictionAndLabels)))

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

    if args.step == 'classifier':
      create_classifier(args.data_source, args.output_uri)