import mesa
import numpy as np
from .agents import SemaphoreAgent, CarAgent

class CityModel(mesa.Model):
    def __init__(self, car_count, seed=None):
        super().__init__(seed=seed)
        self.width = 12
        self.height = 12
        self.structure_arr = [
           (2,2),(3,2),(4,2),(7,2),(8,2),(9,2),
           (2,3),(3,3),(4,3),(7,3),(8,3),(9,3),
           (2,4),(3,4),(4,4),(7,4),(8,4),(9,4),
           (2,7),(3,7),(4,7),(7,7),(8,7),(9,7),
           (2,8),(3,8),(4,8),(7,8),(8,8),(9,8),
           (2,9),(3,9),(4,9),(7,9),(8,9),(9,9)
        ]
        self.semaphore_arr = [
            # First pair
            [{"coordinates":[(4,0),(4,1)], "green_counter": 0, "car_counter": 0},
            {"coordinates":[(5,2),(6,2)], "green_counter": 0, "car_counter": 0}],
            # Second pair
            [{"coordinates":[(2,5),(2,6)], "green_counter": 0, "car_counter": 0},
            {"coordinates":[(0,7),(1,7)], "green_counter": 0, "car_counter": 0}],
            # Third pair
            [{"coordinates":[(7,5),(7,6)], "green_counter": 0, "car_counter": 0},
            {"coordinates":[(6,7),(5,7)], "green_counter": 0, "car_counter": 0}]
        ]
        self.directions_dict = {
            ((0,0), (1,11)): "left",
            ((0,0), (11,1)): "down",
            ((10,0), (11,11)): "right",
            ((0,10), (11,11)): "up",
            ((0,5),(11,6)): "up",
            ((5,0),(6,11)): "left"
        }
        self.semaphore_area_arr = [
            # First pair
            [(2,0),(4,1)],
            [(5,2),(6,4)],
            #Second pair
            [(2,5),(4,6)],
            [(0,7),(1,9)],
            #Third pair
            [(7,5),(9,6)],
            [(5,7),(6,9)]
        ]
        
        self.structure_layer = mesa.space.PropertyLayer("structure",self.width, self.height,np.float64(0), np.int64)
        self.semaphore_layer = mesa.space.PropertyLayer("semaphore", self.width, self.height, np.float64(0), np.int64)
        self.grid = mesa.space.MultiGrid(self.width, self.height, False, (self.structure_layer, self.semaphore_layer))
        self.running = True
        self.datacollector = mesa.DataCollector()

        # Create building grid
        for x, y in self.structure_arr:
            self.grid.properties["structure"].set_cell((x, y), 1)

        # Generate semaphore agents
        for i in range(len(self.semaphore_arr)):
            SemaphoreAgent(self, self.semaphore_arr[i])

        #Generate car agents
        semaphore_coordinates = [
            coord
            for semaphore_pair in self.semaphore_arr
            for semaphore in semaphore_pair
            for coord in semaphore["coordinates"]
        ]

        restricted_positions = set(self.structure_arr).union(semaphore_coordinates)

        all_positions = [(x, y) for x in range(self.width) for y in range(self.height)]

        valid_positions = [pos for pos in all_positions if pos not in restricted_positions]

        for i in range(car_count):  
            position = self.random.choice(valid_positions)
            self.grid.place_agent(CarAgent(self), position)
            valid_positions.remove(position)

    def step(self):
        self.datacollector.collect(self)

        self.agents_by_type[CarAgent].shuffle_do("move")
        self.agents_by_type[SemaphoreAgent].shuffle_do("toggle_state")
        