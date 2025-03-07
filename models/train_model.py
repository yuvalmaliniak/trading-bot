# Gym stuff
import gymnasium as gym
import gym_anytrading

# Stable baselines - RL stuff
from stable_baselines3.common.monitor import Monitor
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import StopTrainingOnRewardThreshold, EvalCallback

# Processing libraries
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


df = pd.read_csv('AAPL_processed_data.csv')
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)

# Wrap the environment with Monitor inside the lambda function
env_maker = lambda: Monitor(gym.make('stocks-v0', df=df, frame_bound=(200, 7500), window_size=50))
env = DummyVecEnv([env_maker])

# Define the model
model = PPO("MlpPolicy", env, verbose=1, gamma=0.99, batch_size=256)

# Stop training when the average reward reaches the threshold
stop_callback = StopTrainingOnRewardThreshold(reward_threshold=1000, verbose=1)
eval_callback = EvalCallback(env, callback_on_new_best=stop_callback, eval_freq=500000, verbose=1)

# Train the model with the callback
model.learn(total_timesteps=200000000, callback=eval_callback)

# Save the trained model
model.save("PPO_trading_model_AAPL")

print("Training completed successfully!")
