import numpy as np
from sklearn.preprocessing import MinMaxScaler


def prep_ticker_data(ticker, merged_df):
    filtered_df = merged_df[merged_df['ticker'] == ticker]
    filtered_df = filtered_df.sort_values('date')     # Sort by date as we are working with time series
    labels = filtered_df[['close']].values

    return filtered_df, labels


# Create sequences of data
def create_sequences(data, seq_length):
    X = []
    y = []
    for i in range(len(data) - seq_length):
        X.append(data[i:i + seq_length])
        y.append(data[i + seq_length])
    return np.array(X), np.array(y)


def scale_and_split(labels, seq_length):
    # Normalize the data
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(labels)

    X, y = create_sequences(scaled_data, seq_length)

    # Split the data into training and testing sets
    split = int(0.8 * len(X))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    return X_train, X_test, y_train, y_test, scaler, split
