from state import State
from utils import parseManifest
import state
from container import Container
import utils
import heapq

def load(start_state, load_list):
    source = [8,0]
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
                    time = source[1] + (8 - source[0]) + 4 + target[1] + (8 - target[0])

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
                # print(o.time, o.target_location)
                start_state = o
            
        track_moves.append(start_state.target_location)
        source = start_state.target_location
        
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


def calculate_heuristic(state: State, unload_target, unload_position: tuple):
    container_pos = state.find_container(unload_target)

    if container_pos:
        return abs(container_pos[0] - unload_position[0]) + abs(container_pos[1] - unload_position[1])
    return float('inf')

def unload(start_state, unload_targets, unload_position):
    trace = []
    blocking_containers = [] 
    
    
    if not unload_targets:
        return start_state, trace, blocking_containers
    
    current_state = start_state

    for unload_target in unload_targets:
        container_pos = current_state.find_container(unload_target)
        trace.append(container_pos)
        if not container_pos:
            raise ValueError(f"Container '{unload_target}' not found in the grid.")

        target_row, target_col = container_pos

        if current_state.last_moved_location[1] != target_col:
            crane_move_cost = 2*(target_col) + 2*(8-target_row) + 4
            current_state.time += crane_move_cost
            current_state.last_moved_location = (0,8)

        try:
            print(f"Attempting to pick up container '{unload_target}'...")
            new_blocking_containers, next_state = current_state.pick_up(
                target_col,  
                current_state.last_moved_location,
                unload_target
            )
            
            if new_blocking_containers:
                blocking_containers = new_blocking_containers
            current_state = next_state
        except ValueError as e:
            raise e

    current_state.target_location = (8,0)
    current_state.print_state_representation()
    current_state.fix_floating_containers()
    
    return current_state, trace, blocking_containers

def unload_time_trace(unloaded_state, trace, blocking_containers):
    
    unload_total_trace = []
    for t in trace: unload_total_trace.append([t,(8,0)])
    for row, bc in blocking_containers:
        new_location = unloaded_state.find_container(bc)
        pos = (bc.position[0] - 1, bc.position[1] - 1)
        unload_total_trace.append([pos,new_location])
        unloaded_state.time += 2*(abs(pos[0]-new_location[0]) + abs(pos[1]-new_location[1]))
    # print("unsorted = ", unload_total_trace)
    sorted_unload_total_trace = sorted(
            unload_total_trace, 
            key=lambda pair: (-pair[0][1], -pair[0][0])  # Sort by column descending, then row descending
        )
    # print("sorted = ", sorted_unload_total_trace)

    return sorted_unload_total_trace, unloaded_state.time
