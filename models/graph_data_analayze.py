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

# Function to load existing data if available
def load_existing_data(file_path):
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    return None

# Function to save processed data to CSV
def save_data_to_csv(df, symbol):
    output_file = f"{symbol}_processed_data.csv"
    df.to_csv(output_file, index=False)
    print(f"Processed data saved to {output_file}")

# Function to append new data and update CSV
def update_data(symbol):
    file_path = f"{symbol}_processed_data.csv"

    # Load existing data
    existing_data = load_existing_data(file_path)

    if existing_data is not None and not existing_data.empty:
        last_date = existing_data['Date'].max().date()
    else:
        last_date = datetime(1960, 1, 1).date()  # Default start date

    start_date = (last_date + timedelta(days=1)).strftime("%Y-%m-%d")
    end_date = datetime.today().strftime("%Y-%m-%d")

    new_data = fetch_stock_data(symbol, start_date, end_date)

    if new_data is not None and not new_data.empty:
        # Combine new and existing data **before calculating indicators**
        if existing_data is not None:
            combined_data = pd.concat([existing_data, new_data], ignore_index=True)
        else:
            combined_data = new_data

        # Compute indicators using the full dataset
        combined_data = calculate_sma(combined_data, window=50)
        combined_data = calculate_sma(combined_data, window=200)
        combined_data = calculate_rsi(combined_data, period=14)
        combined_data = calculate_bollinger_bands(combined_data, window=20)
        combined_data = normalize_data(combined_data)

        # Save updated dataset **without duplicate headers**
        combined_data.to_csv(file_path, index=False)
        print(f"✅ Updated dataset saved to {file_path}")
    else:
        print("⚠️ No new data to update.")

# Run the daily update
if __name__ == "__main__":
    stock_symbol = "SPY"
    update_data(stock_symbol)