from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import os

# Function to fetch stock data
def fetch_stock_data(symbol: str, start_date: str, end_date: str):
    data = yf.download(symbol, start=start_date, end=end_date)
    data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
    data.reset_index(inplace=True)
    return data

# Function to calculate Simple Moving Average (SMA)
def calculate_sma(df, window):
    df[f'SMA_{window}'] = df['Close'].rolling(window=window).mean()
    return df

# Function to calculate Relative Strength Index (RSI)
def calculate_rsi(df, period=14):
    delta = df['Close'].diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    df['RSI_14'] = 100 - (100 / (1 + rs))
    return df

# Function to calculate Bollinger Bands
def calculate_bollinger_bands(df, window=20, num_std=2):
    rolling_mean = df['Close'].rolling(window=window).mean()
    rolling_std = df['Close'].rolling(window=window).std()
    
    df['BBL_20'] = rolling_mean - (num_std * rolling_std)  # Lower Band
    df['BBM_20'] = rolling_mean                           # Middle Band
    df['BBU_20'] = rolling_mean + (num_std * rolling_std)  # Upper Band
    
    return df

# Function to normalize data using MinMaxScaler
def normalize_data(df):
    scaler = MinMaxScaler()
    columns_to_normalize = ['Open', 'High', 'Low', 'Close', 'Volume', 
                            'SMA_50', 'SMA_200', 'RSI_14', 'BBL_20', 'BBM_20', 'BBU_20']

    # Ensure required columns exist before normalizing
    for col in columns_to_normalize:
        if col not in df.columns:
            df[col] = np.nan

    # Fill NaN values to avoid dropping rows
    df.ffill(inplace=True)  # Forward-fill missing values
    df.bfill(inplace=True)  # Backward-fill missing values)  # Backward-fill in case of leading NaNs
    df.fillna(0, inplace=True)  # Ensure no NaNs remain

    df[columns_to_normalize] = scaler.fit_transform(df[columns_to_normalize])
    return df

# Function to remove second line from CSV
def remove_second_line(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()
    
    if len(lines) > 1:
        with open(file_path, "w") as f:
            f.writelines([lines[0]] + lines[2:])  # Keep first line, skip second
    print(f"✅ Cleaned second line from {file_path}")


# Function to append new data and update CSV
def update_data(symbol):
    file_path = f"{symbol}_processed_data.csv"

    start_date = datetime(1960, 1, 1).date()  # Default start date
    end_date = datetime.today().strftime("%Y-%m-%d")

    new_data = fetch_stock_data(symbol, start_date, end_date)

    if new_data is not None and not new_data.empty:

        # Compute indicators using the full dataset
        new_data = calculate_sma(new_data, window=50)
        new_data = calculate_sma(new_data, window=200)
        new_data = calculate_rsi(new_data, period=14)
        new_data = calculate_bollinger_bands(new_data, window=20)
        new_data = normalize_data(new_data)

        # Save updated dataset **without duplicate headers**
        new_data.to_csv(file_path, index=False)
        remove_second_line(file_path)  # Ensure second line is removed
        print(f"✅ Updated dataset saved to {file_path}")
    else:
        print("⚠️ No new data to update.")

# Run the daily update
if __name__ == "__main__":
    stock_symbols = ["SPY", "AAPL"]
    for symbol in stock_symbols:
        update_data(symbol)
