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
        new_state.state_representation[x1][y1] = None
        
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

def main():
    manifest_path = "SilverQueen.txt"
    
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