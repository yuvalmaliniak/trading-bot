import gymnasium as gym
import gym_anytrading
from sb3_contrib import RecurrentPPO
import pandas as pd
import numpy as np

df = pd.read_csv('AAPL_processed_data.csv')
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)

# Load the trained model for testing
model = RecurrentPPO.load("recurrent_ppo_trading_model")

# Step-by-step evaluation of the trained model
eval_env = gym.make('stocks-v0', df=df, frame_bound=(90, 110), window_size=5, render_mode="human")

# Reset the environment and get the initial observation
obs, _ = eval_env.reset()

while True:
    obs = obs[np.newaxis, ...]  # Expand dimensions for model input
    action, _states = model.predict(obs)
    
    obs, reward, terminated, truncated, info = eval_env.step(action)
    
    if terminated or truncated:
        print("Evaluation completed.")
        print("Final Info:", info)
        break

# Render the results
eval_env.render()
