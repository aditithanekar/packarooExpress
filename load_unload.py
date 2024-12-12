from state import State
from utils import parseManifest
import state
from container import Container
import utils

def load(start_state, load_list):
    source = [7,0]
    track_moves = []
    track_moves.append(source)

    while len(load_list) != 0:
        node = load_list.pop()
        move_options = []
    
        for col_index, column in enumerate(zip(*start_state.state_representation)):
            for row_index in range(len(column)):
                container = column[row_index]
                if container is not None and container.get_description() == 'UNUSED':
                    target = [row_index, col_index]
                    time = source[1] + (9 - source[0]) + 4 + target[1] + (9 - target[0])
    
                    state_rep = start_state.get_state_representation()
                    state_rep[row_index][col_index] = node

                    #new state object with the new and updated representation
                    new_state = State(
                        state_rep,
                        start_state.depth + 1,
                        node,           
                        start_state.time + time,  
                        start_state,
                        time,                     #time taken for THIS action
                        start_state.num_moves + 1,                        
                        source,            
                        target
                    )
                    move_options.append(new_state)

                    break
    
        best = float('inf')
        for o in move_options:
            if o.time < best: 
                best = o.time
                start_state = o
            
        track_moves.append(start_state.target_location)
        source = start_state.last_moved_location
        
    return start_state, track_moves

def is_unload_goal_test(self, unload_targets):
    for target in unload_targets:
        if self.find_container(target):
            return False
        return True

def find_container(self, container_description: str):
    for row_index, row in enumerate(self.state_representation):
        for col_index, col in enumerate(row): 
            if container and container != "NAN" and container.get_description() == container_description:
                return (row_index, col_index)
    return None

def can_pick_up(self, col):
    for row in range(8):
        if self.state_representation[row][col] is not None and self.state_representation[row][col] != "NAN":
            return True
    return False

def pick_up(self, col, crane_position, target_container_description=None):
    target_row = None
    blocking_containers = []

    for row in range(8):
        container = self.state_representation[row][col]
        if container is not None and container != "NAN":  
            if container.get_description() == target_container_description:
                target_row = row
                break
            else:
                blocking_containers.append((row, container))

    if target_row is None:  
        return None

    new_representation = self.get_state_representation()
    current_time = self.time
    new_crane_position = crane_position

    for row, container in blocking_containers:
        empty_pos = self.find_empty_position(new_representation, exclude_col=col)
        if empty_pos is None or new_representation[empty_pos[0]][empty_pos[1]] == "NAN":  
            continue

        crane_move_cost = abs(new_crane_position[1] - col) + abs(new_crane_position[0] - row)
        current_time += crane_move_cost

        new_representation[row][col] = None
        new_representation[empty_pos[0]][empty_pos[1]] = container
        current_time += 1  
        new_crane_position = empty_pos

    crane_move_cost = abs(new_crane_position[1] - col) + abs(new_crane_position[0] - target_row)
    current_time += crane_move_cost

    new_representation[target_row][col] = None
    new_crane_position = (target_row, col)

    return State(
        state_representation=new_representation,
        depth=self.depth + 1,
        last_moved_container=self.state_representation[target_row][col],
        time=current_time,
        parent_state=self,
        crane_position=new_crane_position,
    )

def find_empty_position(self, grid, exclude_col=None):
    for col in range(12):
        if col == exclude_col:
            continue
        for row in range(7, -1, -1):
            if grid[row][col] is None:
                return (row, col)
    return None

def put_down_load(self, col, unload_targets):
    for row in range(7, -1, -1):  
        if self.state_representation[row][col] is None:  
            if unload_targets:  
                container_to_place = unload_targets.pop(0)  
                new_representation = self.get_state_representation()
                new_representation[row][col] = container_to_place

                return State(
                    state_representation=new_representation,
                    depth=self.depth + 1,
                    last_moved_container=container_to_place,
                    time=self.time + 1, 
                    parent_state=self
                )
    return None

def calculate_heuristic(state: State, unload_target: str, unload_position: tuple):
    container_pos = state.find_container(unload_target)

    if container_pos:
        return abs(container_pos[0] - unload_position[0]) + abs(container_pos[1] - unload_position[1])
    return float('inf') 

def unload(start_state, unload_target, load_list, unload_position):
    state_queue = PriorityQueue()
    visited_costs = {}
    crane_position = (7, 0)
    current_state = start_state

    for unload_target in unload_targets:
        heuristic = calculate_heuristic(current_state, unload_target, unload_position)
        state_queue.put((current_state.time + heuristic, current_state, crane_position))
        visited_costs[current_state.to_string()] = current_state.time

        while not state_queue.empty():
            _, current_state, crane_position = state_queue.get()

            if current_state.is_unload_goal_test([unload_target]):
                break

            next_states = []
            for col in range(12):
                next_state = current_state.pick_up(col, crane_position, target_container_description=unload_target)
                if next_state:
                    next_states.append(next_state)

            for next_state in next_states:
                if next_state is None:
                    continue

                next_time = next_state.time
                heuristic = calculate_heuristic(next_state, unload_target, unload_position)
                total_cost = next_time + heuristic

                state_string = next_state.to_string()
                if state_string not in visited_costs or next_time < visited_costs[state_string]:
                    state_queue.put((total_cost, next_state, next_state.crane_position))
                    visited_costs[state_string] = next_time

    return current_state
