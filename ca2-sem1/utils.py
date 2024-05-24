import requests
import csv
import json
import math
import calendar

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

NUMPY_INTS = [np.dtypes.Float64DType, np.dtypes.Float32DType, np.dtypes.Int64DType, np.dtypes.Int32DType]
default_style = sns.axes_style()

# Based on the URL provided, fetch_data will featch the data and put it into the output path
# The output will be in CSV format
def fetch_data(url, out_file):
  res = requests.get(url)
  if res.content:
    with open(out_file, "w") as csv_file:
      writer = csv.writer(csv_file)
      content = res.content.decode("utf-8").split("\n")
      for line in content:
        line = [entry.replace('"', '').replace('\r', '') for entry in line.split(",")]
        writer.writerow(line)

# Returns a cleaned up dataframe with columns dropped and column names converted into 'variable name' like format
def do_basic_cleanup(df, drop_cols):
    df = df.rename(columns={c: c.lower().replace(" ", "_").replace("(", "").replace(")", "") for c in df.columns})
    try:
      df = df.drop(columns=drop_cols)
    except Exception as e:
      print(e)
    return df
  
# CONSTS
PERCENTILE_LABELS = ["0-25%", "25-50%", "50-75%", "75-100%"]
