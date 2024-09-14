import argparse

from pyspark.sql import SparkSession
from pyspark.mllib.util import MLUtils
from pyspark.mllib.regression import LabeledPoint


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--data_source', help="The URI for you CSV restaurant data, like an S3 bucket location.")
    parser.add_argument(
        '--output_uri', help="The URI where output is saved, like an S3 bucket location.")
    args = parser.parse_args()

    create_libsvm(args.data_source, args.output_uri)