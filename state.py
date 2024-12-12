from utils import parseManifest

class State:
    def __init__(self, 
                 state_representation=None, 
                 depth=0, 
                 last_moved_container=None, 
                 time=0, 
                 parent_state=None, 
                 move_time=0, 
                 num_moves=0, 
                 last_moved_location=None, 
                 target_location=None,
                 priority=0) -> None:
        
        self.state_representation = state_representation
        self.depth = depth
        self.last_moved_container = last_moved_container if last_moved_container is not None else [None, None]
        self.time = time
        self.parent_state = parent_state
        self.move_time = move_time
        self.num_moves = num_moves
        self.last_moved_location = last_moved_location if last_moved_location is not None else [-1, -1]
        self.target_location = target_location
        self.priority = priority

    def __lt__(self, other):
        return self.priority < other.priority

    def __eq__(self, other):
        if not isinstance(other, State):
            return False
        return self.priority == other.priority

#MANIFEST = parseManifest("sampleManifest.txt")
    
    def _initialize_empty_ship(self, num_rows: int, num_cols: int):
        return [[None] * num_cols for _ in range(num_rows)]
    
    def init_start_state(self, manifest):
        self.state_representation = self._initialize_empty_ship(num_rows=8, num_cols=12)
        
        for container in manifest:
            position = container.get_position()
            row, col = position[0] - 1, position[1] - 1
            self.state_representation[row][col] = container
                    
        return self
    
    def print_state_representation(self):
        cell_width = 9
        header = " | ".join(f"Col {i+1:<{cell_width-5}}" for i in range(12))
        print(header)
        print("-" * len(header))
        
        for row in reversed(self.state_representation):
            row_repr = []
            for cell in row:
                if cell:
                    row_repr.append(f"({cell.weight}, {cell.description[:5]})".ljust(cell_width))
                else:
                    row_repr.append("(Empty)".ljust(cell_width))
            print(" | ".join(row_repr))

    def get_state_representation(self):
        """
        Returns a deep copy of the state representation 
        
        Returns:
            list: A 2D list representing the current state of the ship's container arrangement
        """
        if self.state_representation is None:
            return None
    
        return [row.copy() for row in self.state_representation]

