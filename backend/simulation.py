from rendering.data.car_ui import CarUI
from rendering.data.road_node_ui import *
from backend.translator import Translator

from backend.car import Car
from backend.car_follow import Car_follow
from backend.loader import Loader
import random
from backend.utils import *
from rendering.data.traffic_light_ui import TrafficLightUI


class UIState:
    def __init__(self, roadNodes, roadConnections, cars, trafficLights):
        self.roadNodes = roadNodes
        self.roadConnections = roadConnections
        self.cars = cars
        self.trafficLights = trafficLights


class Simulation:
    def __init__(self):
        loader = Loader("./data/predefined_level2.traiffic")
        self.graph = loader.graph
        self.coord_map = loader.coord_map
        self.spawners = loader.spawners
        self.cars = []
        self.translator = Translator()
        self.spawn_interval = 1.0
        self.time_since_last_spawn = 2.0
        self.road_bounds = get_road_bounds(
            self.graph, self.coord_map, margin=0.2, car_radius=0.5
        )
        self.destinations = loader.destinations
        self.trafficlights = loader.trafficlights
        self.trafficlighttimer = 0
        self.trafficlightMap = {}
        i = 0
        for trafficlight in self.trafficlights:
            key = trafficlight[0]
            if key in self.trafficlightMap:
                self.trafficlightMap[key].append(i)
            else:
                self.trafficlightMap[key] = [i]
            i += 1

    def update(self, dt):
        # if self.cars.__len__() == 0:
        #    Adds one car at a time
        #    self.spawn_car(self.cars)
        #    self.spawn_car(self.cars)
        self.time_since_last_spawn += dt
        if self.time_since_last_spawn >= self.spawn_interval:
            self.time_since_last_spawn = 0.0
            self.spawn_car(self.cars)
            self.spawn_car(self.cars)
        for car in self.cars[:]:
            if (
                not car.update(dt, all_cars=self.cars, road_bounds=self.road_bounds, trafficLights = self.trafficlights, coordmap = self.coord_map)
                or car.crashed == True
            ):
                self.cars.remove(car)
        self.update_trafficlights(dt)

    def update_trafficlights(self,dt):
        self.trafficlighttimer += dt
        if self.trafficlighttimer > 2.0:
            for key,value in self.trafficlightMap.items():
                for i,idx in enumerate(value):
                    light = self.trafficlights[idx]
                    if light[2] == False:
                        light[2] = True
                        next_light = (i+1)%len(value)
                        self.trafficlights[value[next_light]][2] = False
                        self.trafficlighttimer = 0
                        return
            self.trafficlighttimer = 0



    # Car spawner method for easier testing
    def spawn_car(self, all_cars):
        sources = list(self.spawners)
        random.shuffle(sources)
        source = None
        for src in sources:
            source_pos = np.array(self.coord_map[int(src)])
            is_blocked = False

            for car in all_cars:
                if np.linalg.norm(car.position - source_pos) < 0.9:
                    is_blocked = True
                    break
                
            if not is_blocked:
                source = src
                break 

        if source is None:
            return


        [destination] = random.sample(self.destinations,1)
        path = self.graph.traverse(source,destination)
        source = int(source)
        destination = int(destination)
        coords = path_to_coords(path, self.coord_map)
        if not coords:
            return
        new_car = Car_follow(self.coord_map[source],self.graph,coords)
        self.cars.append(new_car)

    def reset_cars(self, num_cars=1):
        """
        Reset the simulation: spawn `num_cars` RL-controlled cars
        and some traffic cars.
        """
        self.cars = []

        # Spawn RL car
        for _ in range(num_cars):
            self._spawn_rl_car()

        # Spawn some traffic cars
        for _ in range(3):  # adjust number of traffic cars
            self._spawn_controller_car()

    def _spawn_rl_car(self):
        """Spawn one RL-controlled car at an available spawner."""
        sources = list(self.spawners)
        random.shuffle(sources)
        source = None
        for src in sources:
            source_pos = np.array(self.coord_map[int(src)])
            if all(np.linalg.norm(car.position - source_pos) >= 0.9 for car in self.cars):
                source = src
                break
        if source is None:
            return

        [destination] = random.sample(self.destinations, 1)
        path = self.graph.traverse(source, destination)
        coords = path_to_coords(path, self.coord_map)
        if not coords:
            return

        new_car = Car_follow(self.coord_map[int(source)], self.graph, coords)
        new_car.is_rl = True
        self.cars.append(new_car)

    def _spawn_controller_car(self):
        """Spawn a traffic car using your existing spawn logic."""
        self.spawn_car(self.cars)

    def export_ui_state(self):
        roadNodes = [RoadNodeUI(int(x), int(y)) for (x, y) in self.coord_map.values()]
        roadConnections = [
            [int(t[0]) for t in self.graph.adj_list[key]]
            for key in sorted(self.graph.adj_list.keys())
        ]
        cars = self.translator.translate(self.cars)
        trafficLights = []
        for light in self.trafficlights:
            idx = int(light[0])
            direction = light[1]
            trafficLights.append(TrafficLightUI(self.coord_map[idx][0],self.coord_map[idx][1],int(direction),light[2]))
        return UIState(roadNodes, roadConnections, cars, trafficLights)
