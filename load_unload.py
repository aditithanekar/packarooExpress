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
    
    current_state = start_state
    # print("--- UNLOAD PROCESS STARTED ---")
    # print("Initial crane position: {current_state.last_moved_location}.")
    # print("Initial state representation:")
    # current_state.print_state_representation()

    for unload_target in unload_targets:
        # print(f"\n--- Processing target container: '{unload_target}' ---")
        
        # Locate the target container
        # print(f"Finding container '{unload_target}' in the grid...")
        container_pos = current_state.find_container(unload_target)
        trace.append(container_pos)
        if not container_pos:
            # print(f"ERROR: Container '{unload_target}' not found in the grid.")
            raise ValueError(f"Container '{unload_target}' not found in the grid.")

        target_row, target_col = container_pos
        # print(f"SUCCESS: Container '{unload_target}' found at Row={target_row}, Col={target_col}.")

        # Move crane to the correct column
        # print(f"Crane current position: {current_state.last_moved_location}. Moving to Column {target_col} if needed.")
        if current_state.last_moved_location[1] != target_col:
            crane_move_cost = 2*(target_col) + 2*(8-target_row) + 4
            current_state.time += crane_move_cost
            current_state.last_moved_location = (0,8)
            # print(f"Crane moved to Column {target_col}. Time cost: {crane_move_cost}.")
        # else:
            # print(f"Crane is already at Column {target_col}.")

        # Debug before calling pick_up
        # print(f"DEBUG BEFORE PICK_UP: target_col={target_col} (expected for '{unload_target}').")
        # print(f"DEBUG BEFORE PICK_UP: current crane position = {current_state.last_moved_location}.")
        # print(f"DEBUG BEFORE PICK_UP: target description = {unload_target}.")

        # Call pick_up to pick up the container
        try:
            print(f"Attempting to pick up container '{unload_target}'...")
            blocking_containers, next_state = current_state.pick_up(
                target_col,  
                current_state.last_moved_location,unload_target
            )
            # print(f"SUCCESS: Picked up container '{unload_target}'.")
            current_state = next_state
        except ValueError as e:
            # print(f"ERROR during pick_up: {e}")
            raise e

    # print(f"--- UNLOAD PROCESS COMPLETED ---")
    current_state.target_location = (8,0)
    # print(f"Final crane position: {current_state.last_moved_location}.")
    current_state.print_state_representation()
    current_state.fix_floating_containers()
    # print("print after fix floating stuff")
    # current_state.print_state_representation()
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
