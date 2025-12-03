from backend.graph import Graph
import numpy as np
import random
from backend.utils import get_road_bounds

class Car:
    '''
    Car controller that implements movement
    '''
    id_crt = 0
    def __init__(self, position,facing):
        #self.id = self.id_crt
        self.id = Car.id_crt
        self.is_rl = False
        Car.id_crt +=1
        self.speed = 0
        self.friction = 0

        self.accelerate_step = 0.05
        self.max_speed = 0.5
        self.steer_step = 0.2

        self.position = np.array(position)
        self.facing = np.array(facing)
        self.radius_detect = 0.5
        self.crashed = False

    def move(self,accelerate, steer, dt):
        accelerate = np.clip(accelerate,-5,1)
        steer = np.clip(steer,-1,1)
        acceleration = accelerate * self.accelerate_step
        self.speed += acceleration * dt
        if self.speed > self.max_speed:
            self.speed = self.max_speed

        if self.speed < 0:
            self.speed = 0

        # if self.speed > 0:
            # self.speed -= self.friction
# 
        # if self.speed < 0:
            # self.speed += self.friction

        angle_to_steer = 0
        if self.speed > 0:
            angle_to_steer = self.steer_step * steer
        rotation_matrix = np.array([
        [np.cos(angle_to_steer), -np.sin(angle_to_steer)],
        [np.sin(angle_to_steer),  np.cos(angle_to_steer)]
        ])
        self.facing = rotation_matrix @ self.facing
        norm = np.linalg.norm(self.facing)
        if norm != 0:
            self.facing = self.facing / norm

        self.position = self.position + (self.facing * self.speed)


# Function will update current instance of car, returning 0  when car reached destination and 1 else
    def update(self, dt : float):
        return 1