import time
from stable_baselines3 import PPO
from backend.singlecarenv import SingleCarEnv
from backend.simulation import Simulation
import pygame
import os

# Create simulation and environment
sim = Simulation()
env = SingleCarEnv(simulation=sim)


MODEL_FILE = "ppo_single_car.zip"

if os.path.exists(MODEL_FILE):
    # Load existing model and continue training
    print(f"Loading existing model from {MODEL_FILE} and continuing training.")
    model = PPO.load(MODEL_FILE, env=env, verbose=1)
else:
    # Start training from scratch
    print("No existing model found. Starting training from scratch.")
    model = PPO("MlpPolicy", env, verbose=1)

model = PPO("MlpPolicy", env, verbose=1)

TIMESTEPS = 10000
print(f"Starting training for {TIMESTEPS} timesteps...")

#Start the training process
model.learn(total_timesteps=TIMESTEPS, progress_bar=True)

#Save the trained policy to the file.
model.save("ppo_single_car")
print("Model trained and saved to 'ppo_single_car.zip'.")

obs, _ = env.reset()

running = True
for step in range(5000):
    if not running:
        break

    # Handle Pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
            break

    # Use the trained model to predict the action
    # We use deterministic=True to see the learned, "best" policy
    action, _ = model.predict(obs, deterministic=True)
    obs, reward, terminated, truncated, info = env.step(action)

    # Render the environment
    env.render()

    # Slow it down
    time.sleep(1 / 60.0)

    if terminated or truncated:
        obs, _ = env.reset()

env.close()
print("Simulation finished or manually stopped.")