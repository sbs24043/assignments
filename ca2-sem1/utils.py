import pandas as pd
from os import listdir

# Returns a cleaned up dataframe with columns dropped and column names converted into 'variable name' like format
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
          print(file, df_part.shape)
          df = pd.concat([df, df_part], ignore_index=True)
      except Exception as e:
         print(e)
    return df

def filter_df(df, item, metric, area, year=0):
    return df[(df.value > 0.0) & (df.item == item) & (df.element == metric) & (df.area == area) & (df.year >= year)]

  
# CONSTS
PERCENTILE_LABELS = ["0-25%", "25-50%", "50-75%", "75-100%"]
