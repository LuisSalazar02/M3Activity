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

    def get_building_by_coodinate(self, coordinate):
        for key, value in self.model.parking_spot_dict.items():
            for element in value:
                if element == coordinate:
                    return key
        return None

    def get_neighbors(self, coordinate):

        possible_steps = self.model.grid.get_neighborhood(
            coordinate, moore=False, include_center=False
        )
        
        filtered_coordinates = [coord for coord in possible_steps if coord not in self.model.structure_arr]

        filtered_coordinates = self.get_directions_neighbors(coordinate, filtered_coordinates)
        
        return filtered_coordinates

    def bfs(self, start, target_nodes):
        queue = deque([start])
        visited = set([start])
        prev_node = {start: None}
        
        # Perform BFS
        while queue:
            current_node = queue.popleft()
            
            if current_node in target_nodes:
                path = []
                while current_node is not None:
                    path.append(current_node)
                    current_node = prev_node[current_node]
                return path[::-1]
            
            neighbors = self.get_neighbors(current_node)
            
            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    prev_node[neighbor] = current_node
                    queue.append(neighbor)
        
        return []
    
    def move(self):
        print(self.pos)

        if(self.steps == 0):
            building = self.get_building_by_coodinate(self.pos)

            if (building):
                possible_parking_spots = [coord for key, spots in self.model.parking_spot_dict.items() if key != building for coord in spots]
            else:
                possible_parking_spots = [coord for spots in self.model.parking_spot_dict.values() for coord in spots]

            self.path = self.bfs(self.pos, possible_parking_spots)

            self.model.grid.move_agent(self, self.path[self.path_pointer])

            self.path_pointer += 1
            self.steps += 1
        else:
            if (self.path_pointer < len(self.path)):
                neighborhood = self.model.grid.get_neighborhood(
                    self.pos, moore=False, include_center=False
                )

                filtered_neighborhood = self.get_directions_neighbors(self.pos, neighborhood)

                move = True

                for coord in filtered_neighborhood:
                    if (self.model.grid.properties["semaphore"].data[coord] == 1):
                        move = False
                        break
                
                if(move):
                    self.model.grid.move_agent(self, self.path[self.path_pointer])
                    self.path_pointer += 1

                self.steps += 1
            elif (self.path_pointer == len(self.path)):
                self.model.grid.properties["parking_spot"].set_cell(self.pos, 0)

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