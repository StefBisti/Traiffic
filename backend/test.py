from backend.simulation import Simulation
from singlecarenv import SingleCarEnv
from stable_baselines3 import PPO

sim = Simulation()
env = SingleCarEnv(simulation=sim)

model = PPO.load("ppo_single_car")  # load trained policy

obs, _ = env.reset()
done = False
while not done:
    action, _ = model.predict(obs, deterministic=True)
    obs, reward, terminated, truncated, info = env.step(action)
    env.render()  # now draws map + traffic + RL car
    if terminated:
        obs, _ = env.reset()

