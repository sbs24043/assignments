import argparse

from pyspark.sql import SparkSession
from pyspark.ml.regression import LinearRegression


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--data_source', help="The URI for you CSV restaurant data, like an S3 bucket location.")
    parser.add_argument(
        '--output_uri', help="The URI where output is saved, like an S3 bucket location.")
    args = parser.parse_args()

    create_regression(args.data_source, args.output_uri)