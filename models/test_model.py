import gymnasium as gym
import gym_anytrading
from stable_baselines3 import PPO
import pandas as pd
import numpy as np
import os
from datetime import datetime

# Load the dataset
df = pd.read_csv('SPY_processed_data.csv')
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)

# Load the trained model
model = PPO.load("PPO_trading_model", custom_objects={"clip_range": 0.2, "lr_schedule": lambda _: 0.0003})

# Define window size
window_size = 50

# Dictionary to store predictions
actions_dict = {}

# Iterate through all dates in the dataset where we have enough past data
for i in range(7538, len(df)):  
    today = df.index[i]  # Target date for prediction

    # Select only past data (excluding today)
    past_data = df.iloc[:i-1].copy()

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
output_file = "predictions_by_date.csv"
df_actions.to_csv(output_file, index=False)

print(f"✅ Predicted actions saved to {output_file}")
