import mesa
from collections import deque

class CarAgent(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)
        self.steps = 0
        self.path = []
        self.path_pointer = 1

    def get_directions(self, point):
        directions = []
        for (start, end), direction in self.model.directions_dict.items():
            if (min(start[0], end[0]) <= point[0] <= max(start[0], end[0]) and
                min(start[1], end[1]) <= point[1] <= max(start[1], end[1])):
                directions.append(direction)
        return directions if directions else ["No direction found"]
    
    def get_directions_neighbors(self, point, coordinates):

        possible_direction = self.get_directions(point)

        filtered_neighbors = coordinates

        for direction in possible_direction:
            if (direction == "up"):
                filtered_neighbors = [coord for coord in filtered_neighbors if coord[0] <= point[0]]
            elif (direction == "down"):
                filtered_neighbors = [coord for coord in filtered_neighbors if coord[0] >= point[0]]
            elif (direction == "left"):
                filtered_neighbors = [coord for coord in filtered_neighbors if coord[1] <= point[1]]
            elif (direction == "right"):
                filtered_neighbors = [coord for coord in filtered_neighbors if coord[1] >= point[1]]

        return filtered_neighbors
    
    def move(self):

        neighborhood = self.model.grid.get_neighborhood(
            self.pos, moore=False, include_center=False
        )

        filtered_coordinates = [coord for coord in neighborhood if coord not in self.model.structure_arr]

        filtered_directions = self.get_directions_neighbors(self.pos, filtered_coordinates)

        for coord in filtered_directions:
            if (self.model.grid.properties["semaphore"].data[coord] == 1):
                return

        agents_neighborhood = self.model.grid.get_neighbors(
            self.pos, moore=False, include_center=False
        )

        neighbor_agents = [agent.pos for agent in agents_neighborhood]

        filtered_neighbors = [coord for coord in filtered_directions if coord not in neighbor_agents]
        
        if(filtered_neighbors):
            self.model.grid.move_agent(self, self.random.choice(filtered_neighbors))

        self.steps += 1

class SemaphoreAgent(mesa.Agent):
    def __init__(self, model, controlled_cells, state):
        super().__init__(model)
        # A state equal to False means green
        self.state = state
        self.controlled_cells = controlled_cells
        for cell in self.controlled_cells:
            self.model.grid.properties["semaphore"].set_cell(cell, self.state)

    def toggle_state(self):
        if self.model.global_steps % 5 == 0:
            self.state = not self.state
            for cell in self.controlled_cells:
                self.model.grid.properties["semaphore"].set_cell(cell, self.state)