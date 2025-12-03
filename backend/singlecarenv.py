import gymnasium as gym
from gymnasium import spaces
import pygame
import numpy as np
from ui.systems.camera import Camera
from ui.systems.renderer import Renderer
from core.settings import MAP_WIDTH, MAP_HEIGHT, GRID_ROWS, GRID_COLUMNS

class SingleCarEnv(gym.Env):
    """
    One AI-controlled car in the simulation, always rendering with Pygame.
    """
    metadata = {"render_modes": ["human"], "render_fps": 60}

    def __init__(self, simulation):
        super().__init__()
        self.simulation = simulation
        self.simulation.reset_cars(num_cars=1)  # spawn one RL car + traffic
        self.car = self.simulation.cars[0]  # the RL-controlled car

        # Action space: [acceleration, steering]
        self.action_space = spaces.Box(
            low=np.array([-1.0, -1.0]),
            high=np.array([1.0, 1.0]),
            dtype=np.float32
        )

        # Observation space
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(7,),
            dtype=np.float32
        )

        # Initialize Pygame renderer
        pygame.init()

        self.screen = pygame.display.set_mode((MAP_WIDTH, MAP_HEIGHT))
        self.camera = Camera(0, 0, 1)
        self.renderer = Renderer(
            self.camera,
            self.screen,
            MAP_WIDTH,
            MAP_HEIGHT,
            GRID_ROWS,
            GRID_COLUMNS
        )

        pygame.display.set_caption("Traiffic RL Car")
        self.TERMINATED_SUCCESS_THRESHOLD = 1.0  # Constant for proximity check

        # New: Initialize Pygame Clock to control frame rate and prevent freezing
        self.clock = pygame.time.Clock()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.simulation.reset_cars(num_cars=1)
        self.car = self.simulation.cars[0]
        self.render()
        return self._get_obs(), {}

    def step(self, action):
        dt = 1 / 60.0
        accel, steer = action
        self.car.move(accel, steer, dt)

        # Store car object and its final target for termination checks
        car_obj = self.car

        if hasattr(self.car, 'path') and self.car.path:
            final_target_pos = self.car.path[-1]
        else:
            final_target_pos = self.car.position

        # The simulation update runs and might remove car_obj from the list
        self.simulation.update(dt)

        obs = self._get_obs()
        reward = self._get_reward()

        # Check if the car was removed from the simulation's active list
        car_removed = car_obj not in self.simulation.cars

        terminated_finished = False
        terminated_failure = False

        if car_removed:
            # If the car was removed, check why it was removed:
            distance_to_target = np.linalg.norm(car_obj.position - final_target_pos)

            if distance_to_target < self.TERMINATED_SUCCESS_THRESHOLD:
                terminated_finished = True
            else:
                terminated_failure = True

        terminated = terminated_finished or terminated_failure
        truncated = False

        if terminated:
            # Apply final episode reward/penalty and print message
            if terminated_failure:
                print(f"RL CAR FAILED (Crash or Bounds)! Applying penalty...")
                reward -= 100.0
            elif terminated_finished:
                print(f"RL CAR reached destination! Applying bonus...")
                reward += 100.0

                # Reset logic happens here
            self.simulation.reset_cars(num_cars=1)
            self.car = self.simulation.cars[0]

        # Always render
        self.render()

        return obs, reward, terminated, truncated, {}

    def _get_obs(self):
        obs = np.array([
            self.car.position[0],
            self.car.position[1],
            self.car.facing[0],
            self.car.facing[1],
            self.car.speed,
            *(self.car.target - self.car.position)
        ], dtype=np.float32)
        return obs

    def _get_reward(self):
        if self.car.crashed:
            return -10.0
        return np.linalg.norm(self.car.facing * self.car.speed)

    def render(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # This ensures the window doesn't crash if the user tries to close it
                pass
        self.screen.fill((0, 0, 0))  # Fills the background with black

        dt = 1 / 60.0
        self.camera.update(dt)
        state = self.simulation.export_ui_state()
        self.renderer.draw(state)
        pygame.display.flip()

        self.clock.tick(self.metadata["render_fps"])

    def close(self):
        pygame.quit()