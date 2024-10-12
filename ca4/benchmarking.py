import pymongo
import time
import random

# MongoDB connection details
MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "stocks"
COLLECTION_NAME = "PROCESSED_DB"

# Number of reads to perform
NUM_READS = 1000

def connect_to_mongo():
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    return collection

def measure_read_time(collection):
    total_time = 0
    for _ in range(NUM_READS):
        # Generate a random query (adjust based on your data schema)
        query = {"ticker": random.choice(["TSLA", "AAPL", "GOOG", "AMZN", "MSFT"])}
        
        start_time = time.time()
        result = collection.find_one(query)
        end_time = time.time()
        
        if result:
            total_time += (end_time - start_time)
    
    avg_read_time = total_time / NUM_READS
    return avg_read_time


# /usr/local/bin/python3.11 benchmarking.py
def main():
    collection = connect_to_mongo()
    avg_read_time = measure_read_time(collection)
    print(f"Average read time for {NUM_READS} reads: {avg_read_time:.6f} seconds")

if __name__ == "__main__":
    main()