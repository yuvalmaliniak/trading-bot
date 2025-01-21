import yfinance as yf
import pandas as pd

def fetch_stock_data(symbol: str, start_date: str, end_date: str):

    data = yf.download(symbol, start=start_date, end=end_date)
    
    data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
    
    # Reset index to include Date column
    data.reset_index(inplace=True)

    return data[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]

def save_data_to_csv(data, symbol):
    output_file = f"{symbol}_processed_data.csv"
    data.to_csv(output_file, index=False, header=True)
    print(f"Data saved to {output_file}")

if __name__ == "__main__":
    stock_symbol = "SPY"  
    start_date = "2022-01-01"
    end_date = "2023-12-31"

    stock_data = fetch_stock_data(stock_symbol, start_date, end_date)
    if stock_data is not None and not stock_data.empty:
        save_data_to_csv(stock_data, stock_symbol)
    else:
        print("No data found for the given symbol and date range.")
