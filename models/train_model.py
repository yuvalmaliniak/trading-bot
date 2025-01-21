# Gym stuff
import gymnasium as gym
import gym_anytrading

# Stable baselines - RL stuff
from stable_baselines3.common.monitor import Monitor
from sb3_contrib import RecurrentPPO
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
env_maker = lambda: Monitor(gym.make('stocks-v0', df=df, frame_bound=(5, 100), window_size=5))
env = DummyVecEnv([env_maker])

# Define the model
model = RecurrentPPO("MlpLstmPolicy", env, verbose=1)

# Stop training when the average reward reaches the threshold
stop_callback = StopTrainingOnRewardThreshold(reward_threshold=1000, verbose=1)
eval_callback = EvalCallback(env, callback_on_new_best=stop_callback, eval_freq=5000, verbose=1)

# Train the model with the callback
model.learn(total_timesteps=10000, callback=eval_callback)

# Save the trained model
model.save("recurrent_ppo_trading_model")

print("Training completed successfully!")

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
