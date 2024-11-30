from utils import parseManifest

MANIFEST = parseManifest("sampleManifest.txt")


class State:
    
    def __init__(self) -> None:
        self.state_representation = None
    
    def _initialize_empty_ship(self, num_rows: int, num_cols: int):
        return [[None] * num_rows for _ in range(num_cols)]
    
    def init_start_state(self):
        self.state_representation = self._initialize_empty_ship(num_rows=12, num_cols=12)
        
        for container in MANIFEST:
            position = container.get_position()
            row, col = position[0] - 1, position[1] - 1
            self.state_representation[row][col] = container
                    
        # see if ship can balance here before return
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


        
            
            
            
        
        
