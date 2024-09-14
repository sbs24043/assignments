import argparse

from pyspark.sql import SparkSession

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--data_source', help="The URI for you CSV restaurant data, like an S3 bucket location.")
    parser.add_argument(
        '--output_uri', help="The URI where output is saved, like an S3 bucket location.")
    args = parser.parse_args()

    calculate_averages(args.data_source, args.output_uri)