from state import State
from utils import parseManifest
import state
from container import Container
import utils
import heapq

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

def find_initial_crane_position(grid, unload_targets):
    for target_description in unload_targets:
        for row_index, row in enumerate(grid):
            for col_index, container in enumerate(row):
                if isinstance(container, Container) and container.get_description() == target_description:
                    return (row_index, col_index)
    return (7, 0)


def can_pick_up(self, col):
    for row in range(8):
        container = self.state_representation[row][col]
        if container is not None and isinstance(container, Container) and not container.IsNAN:
            return True
    return False


def calculate_heuristic(state: State, unload_target: str, unload_position: tuple):
    container_pos = state.find_container(unload_target)

    if container_pos:
        return abs(container_pos[0] - unload_position[0]) + abs(container_pos[1] - unload_position[1])
    return float('inf')

def unload(start_state, unload_targets, unload_position):
    state_queue = []
    visited_costs = {}
    path = []
    start_state.last_moved_location = unload_position

    # Initialize current state
    current_state = start_state

    for unload_target in unload_targets:
        # Reset the priority queue and visited costs for each unload target
        state_queue = []
        visited_costs = {}

        # Calculate heuristic for the starting state
        heuristic = calculate_heuristic(current_state, unload_target, unload_position)
        heapq.heappush(state_queue, (current_state.time + heuristic, current_state))
        visited_costs[current_state.state_to_tuple()] = current_state.time

        while state_queue:
            _, current_state = heapq.heappop(state_queue)

            # Check if the goal is reached for the current target
            if current_state.is_unload_goal_test([unload_target]):
                break

            # Generate possible next states by picking up containers
            next_states = []
            for col in range(12):
                next_state = current_state.pick_up(col, current_state.last_moved_location, target_container_description=unload_target)
                if next_state:
                    next_states.append(next_state)

            # Process each generated state
            for next_state in next_states:
                if next_state is None:
                    continue

                next_time = next_state.time
                heuristic = calculate_heuristic(next_state, unload_target, unload_position)
                total_cost = next_time + heuristic

                state_tuple = next_state.state_to_tuple()
                if state_tuple not in visited_costs or next_time < visited_costs[state_tuple]:
                    heapq.heappush(state_queue, (total_cost, next_state))
                    visited_costs[state_tuple] = next_time

        # Perform the put-down operation for the current target
        next_state = current_state.put_down_load(unload_position[1], [Container(None, None, unload_target)])
        if next_state:
            path.append((current_state.last_moved_location, unload_position))
            current_state = next_state
        else:
            raise ValueError(f"Unable to unload container {unload_target}.")

    return current_state, path
