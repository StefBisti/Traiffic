from backend.graph import Graph
from backend.car import Car
from rendering.data.car_ui import CarUI
import numpy as np


class Translator:
    """
    Commutes car_UI and other car backend classes
    """

    def translate(self, cars):
        carsUI = list()
        for car in cars:
            carUI = CarUI(
                car.id, car.position[0], car.position[1], car.facing[0], car.facing[1], car.is_rl
            )
            carsUI.append(carUI)
        return carsUI
