import heapq
from state import State
from container import Container
from utils import parseManifest, updateLog

class ShipBalancer:
    ROWS, COLS = 8, 12
    THRESHOLD_PERCENT = 10
    
    def __init__(self, manifest_path):
        self.manifest = parseManifest(manifest_path)
        self.initial_state = State().init_start_state(self.manifest)
        updateLog("Ship balancer initialized with manifest")

    def manhattan_distance(self, x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def calculate_weights(self, state):
        state_repr = state.get_state_representation()
        left_weight = 0
        right_weight = 0
        
        for row in range(self.ROWS):
            # Calculate left side weight
            for col in range(self.COLS // 2):
                container = state_repr[row][col]
                if container and not container.IsUNUSED and not container.IsNAN:
                    left_weight += container.weight
            
            # Calculate right side weight
            for col in range(self.COLS // 2, self.COLS):
                container = state_repr[row][col]
                if container and not container.IsUNUSED and not container.IsNAN:
                    right_weight += container.weight
                    
        return left_weight, right_weight

    def get_total_weight(self, state):
        left_weight, right_weight = self.calculate_weights(state)
        return left_weight + right_weight

    def is_goal(self, state):
        total_weight = self.get_total_weight(state)
        left_weight, right_weight = self.calculate_weights(state)
        threshold = (self.THRESHOLD_PERCENT / 100) * total_weight
        return abs(left_weight - right_weight) <= threshold

    def is_valid_position(self, state_repr, row, col):
        if not state_repr[row][col]:
            return True
        return state_repr[row][col].IsUNUSED or state_repr[row][col].IsNAN

    def generate_moves(self, state):
        moves = []
        state_repr = state.get_state_representation()
        
        for row in range(self.ROWS):
            for col in range(self.COLS):
                container = state_repr[row][col]
                if container and not container.IsUNUSED and not container.IsNAN:
                    # Check Up
                    if row > 0 and self.is_valid_position(state_repr, row - 1, col):
                        moves.append(((row, col), (row - 1, col), 
                                    self.manhattan_distance(row, col, row - 1, col)))
                    
                    # Check Down
                    if row < self.ROWS - 1 and self.is_valid_position(state_repr, row + 1, col):
                        # Check no containers blocking from above
                        if all(not state_repr[r][col] or 
                              state_repr[r][col].IsUNUSED or 
                              state_repr[r][col].IsNAN 
                              for r in range(row + 1, self.ROWS)):
                            moves.append(((row, col), (row + 1, col),
                                        self.manhattan_distance(row, col, row + 1, col)))
                    
                    # Check Left
                    if col > 0 and self.is_valid_position(state_repr, row, col - 1):
                        moves.append(((row, col), (row, col - 1),
                                    self.manhattan_distance(row, col, row, col - 1)))
                    
                    # Check Right
                    if col < self.COLS - 1 and self.is_valid_position(state_repr, row, col + 1):
                        moves.append(((row, col), (row, col + 1),
                                    self.manhattan_distance(row, col, row, col + 1)))
        
        return moves

    def apply_move(self, state, move):
        (x1, y1), (x2, y2), cost = move
        new_state = State(
            state_representation=state.get_state_representation(),
            depth=state.depth + 1,
            last_moved_container=state.state_representation[x1][y1],
            time=state.time + cost,
            parent_state=state,
            move_time=cost,
            num_moves=state.num_moves + 1,
            last_moved_location=[x1, y1],
            target_location=[x2, y2],
            priority=0  # Will be set in a_star()
        )
        
        # Swap containers
        new_state.state_representation[x2][y2] = new_state.state_representation[x1][y1]
        new_state.state_representation[x1][y1] = Container((x1+1,y1+1), 0, "UNUSED") #set it to be UNUSED after we move it out
        new_state.fix_floating_containers()

        return new_state, cost

    def heuristic(self, state):
        total_weight = self.get_total_weight(state)
        left_weight, right_weight = self.calculate_weights(state)
        imbalance = abs(left_weight - right_weight)
        
        if imbalance <= (self.THRESHOLD_PERCENT / 100) * total_weight:
            return 0
            
        state_repr = state.get_state_representation()
        min_cost = float('inf')
        
        for row in range(self.ROWS):
            for col in range(self.COLS):
                container = state_repr[row][col]
                if container and not container.IsUNUSED and not container.IsNAN:
                    target_col = self.COLS // 2 - 1 if col >= self.COLS // 2 else self.COLS // 2
                    for target_row in range(self.ROWS):
                        if self.is_valid_position(state_repr, target_row, target_col):
                            move_cost = self.manhattan_distance(row, col, target_row, target_col)
                            min_cost = min(min_cost, move_cost)
        
        return min_cost

    def state_to_tuple(self, state):
        return tuple(
            tuple(
                (cell.weight if cell and not cell.IsUNUSED and not cell.IsNAN else 0)
                for cell in row
            )
            for row in state.state_representation
        )

    def a_star(self):
        open_set = []
        initial_priority = 0
        self.initial_state.priority = initial_priority
        heapq.heappush(open_set, (initial_priority, id(self.initial_state), self.initial_state, []))  # (priority, unique_id, state, path)
        visited = set()
        updateLog("Starting A* search for optimal balance solution")

        while open_set:
            priority, _, current_state, path = heapq.heappop(open_set)
            
            if self.is_goal(current_state):
                updateLog("Found solution for balancing")
                return path, current_state
            
            state_tuple = self.state_to_tuple(current_state)
            if state_tuple in visited:
                continue
            visited.add(state_tuple)
            
            for move in self.generate_moves(current_state):
                new_state, move_cost = self.apply_move(current_state, move)
                new_path = path + [move]
                new_priority = priority + move_cost + self.heuristic(new_state)
                new_state.priority = new_priority
                heapq.heappush(open_set, (new_priority, id(new_state), new_state, new_path))
        
        updateLog("No solution found for balancing")
        return None, None

    def balance_ship(self):
        print("Before Balancing:")
        self.initial_state.print_state_representation()
        
        initial_left, initial_right = self.calculate_weights(self.initial_state)
        total_weight = initial_left + initial_right
        threshold = (self.THRESHOLD_PERCENT / 100) * total_weight
        difference = abs(initial_left - initial_right)
        
        print(f"Initial Left Weight: {initial_left} kg")
        print(f"Initial Right Weight: {initial_right} kg")
        print(f"Threshold Difference Allowed: {threshold:.2f} kg")
        print(f"Current Difference: {difference:.2f} kg")
        print(f"Balanced: {'Yes' if difference <= threshold else 'No'}\n")
        
        optimal_moves, final_state = self.a_star()
        
        if optimal_moves:
            print("After Balancing:")
            final_state.print_state_representation()
            
            final_left, final_right = self.calculate_weights(final_state)
            final_difference = abs(final_left - final_right)
            
            print(f"Time Taken to Balance: {sum(move[2] for move in optimal_moves)} mins")
            print(f"Total Number of Moves: {len(optimal_moves)}")
            print("\nOptimal Moves List:")
            
            for move in optimal_moves:
                move_msg = f"Move container from {move[0]} to {move[1]} (Cost: {move[2]} mins)"
                print(f"  {move_msg}")
                updateLog(move_msg)
            
            print(f"\nFinal Left Weight: {final_left} kg")
            print(f"Final Right Weight: {final_right} kg")
            print(f"Threshold Difference Allowed: {threshold:.2f} kg")
            print(f"Final Difference: {final_difference:.2f} kg")
            print(f"Balanced: {'Yes' if final_difference <= threshold else 'No'}")
            
            return optimal_moves, final_state
        else:
            print("No solution found!")
            return None, None
    #helper used with unload to get the path    
    def find_path_to_target(self, start_row, start_col, target_row, target_col, state_repr):
        # A basic pathfinding function that could be used to find the shortest path to (0, 0)
        # For simplicity, assume this function uses Manhattan distance and generates a valid path.
        path = []
        
        # While we're not at the target position, move towards it
        current_row, current_col = start_row, start_col
        while (current_row, current_col) != (target_row, target_col):
            if current_row > target_row:
                # Move up
                if self.is_valid_position(state_repr, current_row - 1, current_col):
                    path.append(((current_row, current_col), (current_row - 1, current_col), 1))  # cost = 1 for simplicity
                    current_row -= 1
            elif current_row < target_row:
                # Move down
                if self.is_valid_position(state_repr, current_row + 1, current_col):
                    path.append(((current_row, current_col), (current_row + 1, current_col), 1))
                    current_row += 1
            elif current_col > target_col:
                # Move left
                if self.is_valid_position(state_repr, current_row, current_col - 1):
                    path.append(((current_row, current_col), (current_row, current_col - 1), 1))
                    current_col -= 1
            elif current_col < target_col:
                # Move right
                if self.is_valid_position(state_repr, current_row, current_col + 1):
                    path.append(((current_row, current_col), (current_row, current_col + 1), 1))
                    current_col += 1
        
        return path


    def unload(self, state, containers_to_unload):
        # Start from the grid and attempt to unload containers one by one.
        # state = self.initial_state
        moves = []  # Store the sequence of moves
        state_repr = state.get_state_representation()

        # Assuming we want to unload containers to the top-left corner (0, 0)
        target_row, target_col = 7, 0  # Top-left corner as target

        # Iterate over the containers to unload (given as an argument)
        for container in containers_to_unload:
            # Find the position of the container in the state grid
            container_position = None
            for row in range(self.ROWS):
                for col in range(self.COLS):
                    if state_repr[row][col] == container:
                        container_position = (row, col)
                        break
                if container_position:
                    break
            
            if container_position:
                start_row, start_col = container_position

                # Find the path to the target position (0, 0)
                path_to_target = self.find_path_to_target(start_row, start_col, target_row, target_col, state_repr)

                # If there's a valid path to the target
                if path_to_target:
                    # Add the moves from the path to the moves list
                    moves.extend(path_to_target)

                    # Apply the moves to the state one by one
                    for move in path_to_target:
                        state, cost = self.apply_move(state, move)
                        state_repr = state.get_state_representation()
                    
                    # Once the container is at (7, 0)(the corner), replace it with an UNUSED container so it can get out of the grid
                    state_repr[target_row][target_col] = Container((7,0), None, "UNUSED")
                    state.state_representation = state_repr


        # Return the final state after all unloading is complete, along with the path taken
        return state, moves



def main():
    manifest_path = "test_cases/SilverQueen.txt"
    
    try:
        balancer = ShipBalancer(manifest_path)
        optimal_moves, final_state = balancer.balance_ship()
        
        if optimal_moves:
            updateLog("Ship successfully balanced")
        else:
            updateLog("Failed to find balancing solution")
            
    except Exception as e:
        updateLog(f"Error during ship balancing: {str(e)}")
        raise

if __name__ == "__main__":
    main()