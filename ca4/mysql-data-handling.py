# pip install pandas sqlalchemy mysql-connector-python

import pandas as pd
from sqlalchemy import create_engine
from os import listdir

def do_basic_cleanup(df, drop_cols):
    df = df.rename(columns={c: c.lower().replace(" ", "_").replace("(", "").replace(")", "") for c in df.columns})
    try:
      df = df.drop(columns=drop_cols)
    except Exception as e:
      print(e)
    return df

def get_df_from_dir(dir_name, cols_to_drop=[]):
    df = pd.DataFrame()
    for file in listdir(dir_name):
      try:
          df_part = pd.read_csv(f"{dir_name}/" + file, on_bad_lines='warn')
          df_part = do_basic_cleanup(df_part, cols_to_drop)
          if 'ticker' not in df_part.columns:
            ticker = file.split('.')[0]
            df_part['ticker'] = [ticker for i in range(0, df_part.shape[0])]
          print(file, df_part.shape)
          df = pd.concat([df, df_part], ignore_index=True)
      except Exception as e:
         print(e)
    return df

# Create DataFrame
stocks_df = get_df_from_dir('data/stock-tweet-and-price/stockprice')

stocks_df['date'] = pd.to_datetime(stocks_df['date'])

# Connect to MySQL
engine = create_engine('mysql+mysqlconnector://elena-test:<REDACTED>@localhost:3306/raw_data_all')
stocks_df.to_sql(name='merged_data', con=engine, if_exists='replace', index=False)

print("Data inserted into MySQL successfully!")