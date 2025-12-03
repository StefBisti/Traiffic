import pygame
from backend.simulation import Simulation
from core.settings import *
from rendering.systems.camera import Camera
from rendering.systems.renderer import Renderer


class GameLoop:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.simulation = Simulation()
        self.simulation.reset_cars(num_cars=1)  # spawn RL + traffic

        # mark RL car
        if self.simulation.cars:
            self.simulation.cars[0].is_rl = True
        self.camera = Camera(0, 0, 1)
        self.renderer = Renderer(
            self.camera,
            screen,
            MAP_WIDTH,
            MAP_HEIGHT,
            GRID_ROWS,
            GRID_COLUMNS,
        )

    def run(self):
        running = True
        while running:
            # delta time between frames - used for movements
            dt = self.clock.tick(60) / 1000.0

            # exiting
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            state = self.simulation.export_ui_state()

            for car in state.cars:  # or however your state is structured
                if car.is_rl:
                    print("RL CAR:", car.id, "pos =", (car.x, car.y))

            # update simulation
            self.simulation.update(dt)

            # update camera based on input
            self.camera.update(dt)

            # update rendering based on simulation state
            state = self.simulation.export_ui_state()
            self.renderer.draw(state)

            pygame.display.flip()
