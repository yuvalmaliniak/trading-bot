import gymnasium as gym
import gym_anytrading
from stable_baselines3 import PPO
import pandas as pd
import numpy as np
from datetime import datetime

df = pd.read_csv('SPY_processed_data.csv')
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)

# Load the trained model for testing
model = PPO.load("PPO_trading_model")

# Step-by-step evaluation of the trained model
eval_env = gym.make('stocks-v0', df=df, frame_bound=(7538, 7787), window_size=50, render_mode="human")

# Dictionary to store actions with corresponding dates
actions_dict = {}

# Reset the environment and get the initial observation
obs, _ = eval_env.reset()

# Get the date range for the selected data
date_range = df.index[7538:7787]

for i in range(len(date_range)):
    obs = obs[np.newaxis, ...]  # Expand dimensions for model input
    action, _states = model.predict(obs)
    
    # Store the action corresponding to the current date
    current_date = date_range[i]
    actions_dict[current_date] = action[0]

    obs, reward, terminated, truncated, info = eval_env.step(action)
    
    if terminated or truncated:
        print("Evaluation completed.")
        print("Final Info:", info)
        break

# Save the actions along with dates to a CSV file
df_actions = pd.DataFrame(list(actions_dict.items()), columns=["Date", "Action"])
df_actions.to_csv("actions_by_date.csv", index=False)

print("Actions and corresponding dates saved to actions_by_date.csv")
