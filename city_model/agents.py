import mesa
from collections import deque

class CarAgent(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)
        self.notified = False

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
    
    def is_car_in_area(self, coord):
        for index, ((x1, y1), (x2, y2)) in enumerate(self.model.semaphore_area_arr):
            # Check if the coordinate falls within the rectangle defined by the two points
            if x1 <= coord[0] <= x2 and y1 <= coord[1] <= y2:
                return True, index
        return False, -1
    
    def move(self):
        neighborhood = self.model.grid.get_neighborhood(
            self.pos, moore=False, include_center=False
        )

        filtered_coordinates = [coord for coord in neighborhood if coord not in self.model.structure_arr]

        filtered_directions = self.get_directions_neighbors(self.pos, filtered_coordinates)

        for coord in filtered_directions:
            if (self.model.grid.properties["semaphore"].data[coord] == 2):
                return

        agents_neighborhood = self.model.grid.get_neighbors(
            self.pos, moore=False, include_center=False
        )

        neighbor_agents = [agent.pos for agent in agents_neighborhood]

        filtered_neighbors = [coord for coord in filtered_directions if coord not in neighbor_agents]
        
        if(filtered_neighbors):
            prev_area_data = self.is_car_in_area(self.pos)
            new_position = self.random.choice(filtered_neighbors)
            self.model.grid.move_agent(self, new_position)
            area_data = self.is_car_in_area(new_position)
            semaphores = self.model.agents_by_type[SemaphoreAgent]
            group = area_data[1] // 2

            if (area_data[0]):
                if (self.notified == False):
                    self.notified = True
                    if (area_data[1] % 2 == 0):
                        if (semaphores[group].moving == None):
                            print("Hello")
                            semaphores[group].moving = semaphores[group].neighbor1
                            semaphores[group].moving["car_counter"] += 1
                            for i in range(2):
                                self.model.grid.properties["semaphore"].set_cell(semaphores[group].neighbor1["coordinates"][i], 1)
                                self.model.grid.properties["semaphore"].set_cell(semaphores[group].neighbor2["coordinates"][i], 2)
                        else:
                            semaphores.moving["car_counter"] += 1
                    elif (area_data[1] % 2 == 1):
                        if (semaphores[group].moving == None):
                            semaphores[group].moving = semaphores[group].neighbor2
                            semaphores[group].moving["car_counter"] += 1
                            for i in range(2):
                                self.model.grid.properties["semaphore"].set_cell(semaphores[group].neighbor1["coordinates"][i], 2)
                                self.model.grid.properties["semaphore"].set_cell(semaphores[group].neighbor2["coordinates"][i], 1)
                        else:
                            semaphores.moving["car_counter"] += 1
            elif (area_data[0] == False and self.notified == True):
                print("sali")
                self.notified = False
                print("next")
                semaphores[prev_area_data[1] // 2].moving["car_counter"] -= 1
                print("final")

class SemaphoreAgent(mesa.Agent):
    def __init__(self, model, neighbor1, neighbor2):
        super().__init__(model)
        self.neighbor1 = neighbor1
        self.neighbor2 = neighbor2
        self.moving = None
        for i in range(2):
            self.model.grid.properties["semaphore"].set_cell(self.neighbor1["coordinates"][i], 3)
            self.model.grid.properties["semaphore"].set_cell(self.neighbor2["coordinates"][i], 3)

    def toggle_state(self):
        if (self.moving):
            if(self.moving["green_counter"] > 10):
                self.moving["green_counter"] = 0
                if (self.moving == self.neighbor1):
                    if (self.neighbor2["car_counter"] > 0):
                        for i in range(2):
                            self.model.grid.properties["semaphore"].set_cell(self.neighbor1["coordinates"][i], 2)
                            self.model.grid.properties["semaphore"].set_cell(self.neighbor2["coordinates"][i], 1)
                        self.moving = self.neighbor2
                else:
                    if (self.neighbor1["car_counter"] > 0):
                        for i in range(2):
                            self.model.grid.properties["semaphore"].set_cell(self.neighbor1["coordinates"][i], 1)
                            self.model.grid.properties["semaphore"].set_cell(self.neighbor2["coordinates"][i], 2)
                        self.moving = self.neighbor1
            elif(self.moving["car_counter"] == 0):
                self.moving["green_counter"] = 0
                if (self.moving == self.neighbor1):
                    if (self.neighbor2["car_counter"] > 0):
                        for i in range(2):
                            self.model.grid.properties["semaphore"].set_cell(self.neighbor1["coordinates"][i], 2)
                            self.model.grid.properties["semaphore"].set_cell(self.neighbor2["coordinates"][i], 1)
                        self.moving = self.neighbor2
                    elif (self.neighbor2["car_counter"] == 0):
                        for i in range(2):
                            self.model.grid.properties["semaphore"].set_cell(self.neighbor1["coordinates"][i], 3)
                            self.model.grid.properties["semaphore"].set_cell(self.neighbor2["coordinates"][i], 3)
                        self.moving = None
                else:
                    if (self.neighbor1["car_counter"] > 0):
                        for i in range(2):
                            self.model.grid.properties["semaphore"].set_cell(self.neighbor1["coordinates"][i], 1)
                            self.model.grid.properties["semaphore"].set_cell(self.neighbor2["coordinates"][i], 2)
                        self.moving = self.neighbor1
                    elif (self.neighbor1["car_counter"] == 0):
                        for i in range(2):
                            self.model.grid.properties["semaphore"].set_cell(self.neighbor1["coordinates"][i], 3)
                            self.model.grid.properties["semaphore"].set_cell(self.neighbor2["coordinates"][i], 3)
                        self.moving = None
            else:
                self.moving["green_counter"] += 1