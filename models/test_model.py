import gymnasium as gym
import gym_anytrading
from stable_baselines3 import PPO
import pandas as pd
import numpy as np
import os
from datetime import datetime

def test_model():

    # List of stock symbols to process
    stock_symbols = ["SPY", "AAPL"]  # can add more symbols

    # Define window size
    window_size = 50

    # Process each stock symbol
    for symbol in stock_symbols:
        print(f"🔄 Processing {symbol}...")

        # Load the dataset
        csv_path = os.path.join(os.path.dirname(__file__), f"{symbol}_processed_data.csv")
        if not os.path.exists(csv_path):
            print(f"⚠️ Skipping {symbol}, data file not found: {csv_path}")
            continue

        df = pd.read_csv(csv_path)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)

        # Load the trained model
        model_path = os.path.join(os.path.dirname(__file__), f"PPO_trading_model_{symbol}")
        if not os.path.exists(model_path + ".zip"):  # Ensure the model file exists
            print(f"⚠️ Skipping {symbol}, model file not found: {model_path}.zip")
            continue

        model = PPO.load(model_path, custom_objects={"clip_range": 0.2, "lr_schedule": lambda _: 0.0003})

        # Dictionary to store predictions
        actions_dict = {}

        # Iterate through all dates in the dataset where we have enough past data
        for i in range(7538, len(df)):
            today = df.index[i]  # Target date for prediction

            # Select only past data (excluding today)
            past_data = df.iloc[:i].copy()

            # Create a new environment using only past data
            eval_env = gym.make(
                'stocks-v0',
                df=past_data,
                frame_bound=(max(0, len(past_data) - window_size), len(past_data)),
                window_size=window_size,
                render_mode=None
            )
            obs, _ = eval_env.reset()

            # Predict action using only past data
            obs = obs[np.newaxis, ...]  # Expand dimensions for model input
            action, _ = model.predict(obs)

            # Store prediction
            actions_dict[today] = action[0]

        # Convert predictions to DataFrame
        df_actions = pd.DataFrame(list(actions_dict.items()), columns=["Date", "Action"])

        # Save predictions to CSV
        output_file = f"{symbol}_predictions.csv"
        df_actions.to_csv(output_file, index=False)

        print(f"✅ Predictions for {symbol} saved to {output_file}")

    print("🎉 Done processing all symbols!")
if __name__ == "__main__":
    test_model()