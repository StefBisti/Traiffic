import pygame
from backend.simulation import Simulation
from ui.systems.camera import Camera
from ui.systems.renderer import Renderer
from core.settings import MAP_WIDTH, MAP_HEIGHT, GRID_ROWS, GRID_COLUMNS

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    # Create simulation and spawn cars
    sim = Simulation()
    sim.reset_cars(num_cars=1)  # 1 RL car + traffic

    # Mark the first car as RL for rendering
    if sim.cars:
        sim.cars[0].is_rl = True

    # Camera & renderer
    camera = Camera(0, 0, 1)
    renderer = Renderer(camera, screen, MAP_WIDTH, MAP_HEIGHT, GRID_ROWS, GRID_COLUMNS)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update simulation
        sim.update(dt)

        camera.update(dt)

        # Export UI state and render
        state = sim.export_ui_state()
        renderer.draw(state)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
