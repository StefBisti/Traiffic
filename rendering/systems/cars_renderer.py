import pygame

# different colored cars
carsImages = [
    "./assets/cars/green_car.png",
    "./assets/cars/blue_car.png",
    "./assets/cars/red_car.png",
]

rlcarsImage = "./assets/cars/orange_car.png"


class CarsRenderer:
    def __init__(self, camera, screen, mapWidth, mapHeight, gridRows, gridColumns):
        self.camera = camera
        self.screen = screen
        self.mapWidth = mapWidth
        self.mapHeight = mapHeight
        self.gridRows = gridRows
        self.gridColumns = gridColumns
        self.loadCarImages()

    # loading the cars assets right at the start of the game
    def loadCarImages(self):
        self.rlcarImage = pygame.image.load(rlcarsImage).convert_alpha()
        for index in range(0, len(carsImages)):
            carsImages[index] = pygame.image.load(carsImages[index])

    # called every frame, uses the cars positions given by the simulation
    def draw(self, cars):
        cellWidth = self.mapWidth / self.gridColumns
        cellHeight = self.mapHeight / self.gridRows

        for car in cars:
            # world x, y positions
            worldX = car.x * cellWidth
            worldY = car.y * cellHeight

            # conversion to screen x, y positions using the camera parameters
            screenX = (worldX - self.camera.x) * self.camera.zoom
            screenY = (worldY - self.camera.y) * self.camera.zoom

            # choosing a random colored car
            # img = carsImages[car.id % len(carsImages)]
            if car.is_rl:
                img = self.rlcarImage  # rl car is orange
            else:
                img = carsImages[car.id % len(carsImages)]

            # scaling the image using the camera parameters
            scaled_img = pygame.transform.scale(
                img, (cellWidth * self.camera.zoom, cellHeight * self.camera.zoom)
            )

            # rotating using the car facing vector (its speed)
            rotated_img = pygame.transform.rotate(scaled_img, car.get_direction())

            # blitting directly on screen
            self.screen.blit(rotated_img, (screenX, screenY))
