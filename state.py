from utils import parseManifest
from container import Container

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
     
    def find_container(self, container_description: str):
        for row_index, row in enumerate(self.state_representation):
            for col_index, container in enumerate(row):
                if isinstance(container, Container) and container.get_description() == container_description:
                    return (row_index, col_index)
        return None
    
    def state_to_tuple(self):
        return tuple(
            tuple(
                (cell.weight if cell and not cell.IsUNUSED and not cell.IsNAN else 0)
                for cell in row
            )
            for row in self.state_representation
        )
        
    def is_unload_goal_test(self, unload_targets):
        for target in unload_targets:
            if self.find_container(target):
                return False
        return True
    
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
                        parent_state=self,
                        last_moved_location=(row, col),
                        target_location=None
                    )
        return None
    
    def pick_up(self, col, crane_position, target_container_description=None):
        target_row = None
        blocking_containers = []

        for row in range(8):
            container = self.state_representation[row][col]
            if container is not None and isinstance(container, Container) and not container.IsNAN:
                if container.get_description() == target_container_description:
                    target_row = row
                    break
                else:
                    blocking_containers.append((row, container))

        if target_row is None:
            return None

        new_representation = self.get_state_representation()
        current_time = self.time
        crane_position = self.last_moved_location or (7, 0)  # Use last moved location as crane's current position

        for row, container in blocking_containers:
            empty_pos = self.find_empty_position(new_representation, exclude_col=col)
            if empty_pos is None or (isinstance(new_representation[empty_pos[0]][empty_pos[1]], Container) and
                                    new_representation[empty_pos[0]][empty_pos[1]].IsNAN):
                continue

            crane_move_cost = abs(crane_position[1] - col) + abs(crane_position[0] - row)
            current_time += crane_move_cost

            new_representation[row][col] = None
            new_representation[empty_pos[0]][empty_pos[1]] = container
            current_time += 1
            crane_position = empty_pos

        crane_move_cost = abs(crane_position[1] - col) + abs(crane_position[0] - target_row)
        current_time += crane_move_cost

        new_representation[target_row][col] = None
        crane_position = (target_row, col)

        return State(
            state_representation=new_representation,
            depth=self.depth + 1,
            last_moved_container=self.state_representation[target_row][col],
            time=current_time,
            parent_state=self,
            last_moved_location=crane_position,
            target_location=None
        )
    
    def find_empty_position(self, grid, exclude_col=None):
        for col in range(12):
            if col == exclude_col:
                continue
            for row in range(7, -1, -1):
                if grid[row][col] is None:
                    return (row, col)
        return None



