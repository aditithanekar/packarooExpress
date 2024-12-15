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
     
    def find_container(self, container):
        container_description = container.description
        # print(f"--- FIND CONTAINER STARTED ---")
        # print("Looking for container with description ", container_description)

        for row_index, row in enumerate(self.state_representation):  # Iterate over each row in the grid.
            # print(f"Scanning Row {row_index}...")  # Log current row being scanned.

            for col_index, container in enumerate(row):  # Iterate over each column in the row.
                # print(f"  Checking cell at Row {row_index}, Col {col_index}...")  # Log current cell being checked.

                if isinstance(container, Container):  # Check if the cell contains a Container object.
                    # print(f"    Found a container: {container.get_description()} (Weight: {container.get_weight()}).")  # Log container details.

                    if container.get_description() == container_description:  # Compare descriptions.
                        # print(f"    MATCH FOUND: Container '{container_description}' is at Row={row_index}, Col={col_index}.")
                        return (row_index, col_index)  # Return the position if found.

        # print(f"ERROR: Container '{container_description}' not found in the grid.")  # Log if the container is not found.
        return None  # Return None if no match is found.

    
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
    
    def pick_up(self, col, crane_position, target_container):
        target_container_description = target_container.description
        # print(f"\n--- PICK UP PROCESS STARTED ---")
        # print(f"Attempting to pick up container '{target_container_description}' from column {col}.")
        # print(f"Crane position before pick_up: {crane_position}.")
        # print(f"Debug: Current column = {col}.")

        # Debug: Print the state of the column
        # print(f"Debug: State of Column {col}:")
        for row in range(8):  # Print all rows in the specified column.
            container = self.state_representation[row][col]
            # if container:
            #     print(f"  Row {row}: {container.get_description()} (Weight: {container.get_weight()})")
            # else:
            #     print(f"  Row {row}: EMPTY")

        target_row = None  # Initialize the variable to store the row of the target container.
        blocking_containers = []  # Initialize a list to store blocking containers.

        # Scan the column to find the target container and identify blocking containers.
        # print(f"Scanning column {col} to find target container '{target_container_description}'...")
        for row in range(8):
            container = self.state_representation[row][col]
            # print(f"  Checking Row {row} in Column {col}...")

            if container is not None and isinstance(container, Container):  # Check if there's a container in this cell.
                # print(f"    Found container '{container.get_description()}' at Row {row}.")

                if container.get_description() == target_container_description:  # Check if it's the target container.
                    # print(f"    TARGET CONTAINER FOUND: '{target_container_description}' at Row {row}.")
                    target_row = row  # Store the row of the target container.
                    break  # Stop scanning once the target is found.

        # Check if the target container was found.
        if target_row is None:
            # print(f"ERROR: Target container '{target_container_description}' not found in column {col}.")
            raise ValueError(f"Target container '{target_container_description}' not found in column {col}.")
        else:
            #find containers that are blocking above the target row
            for row in range(target_row + 1, 8):
                container = self.state_representation[row][col]
                if container is not None and isinstance(container, Container) and not container.IsUNUSED:
                    # print(f"    Blocking container found: {container.get_description()} (Weight: {container.get_weight()}).")
                    blocking_containers.append((row, container))  # Add blocking container to the list.
        # # Check if the crane is aligned with the target column.
        # if col != crane_position[1]:
        #     print(f"ERROR: Crane is not aligned with column {col}. Current crane column: {crane_position[1]}.")
        #     raise ValueError(f"Crane is not aligned with column {col}.")

        # Move blocking containers if necessary.
        # print(f"Blocking containers to move: {len(blocking_containers)}.")
        for row, container in blocking_containers:
            if not container.IsUNUSED:            
                # print(f"  Moving blocking container '{container.get_description()}' from Row={row}, Col={col}.")
                empty_pos = self.find_empty_position(row, col, exclude_col=col)
                if empty_pos is None:
                    print(f"ERROR: No empty positions available to unblock column {col}.")
                    raise ValueError(f"No empty positions available to unblock column {col}.")

                # print(f"    Found empty position at {empty_pos}.")
                #set the blocking location to be UNUSED again
                self.state_representation[row][col] = Container((row+1, col+1), 0, "UNUSED")
                self.state_representation[empty_pos[0]][empty_pos[1]] = container
                        
        # Attempt to pick up the target container.
        # print(f"Picking up target container '{target_container_description}' from Row {target_row}, Column {col}...")
        self.state_representation[target_row][col] = None  # Remove the container from the grid.
        # print(f"SUCCESS: Picked up container '{target_container_description}'.")
        
        #resets the unloaded container location as UNUSED location
        self.state_representation[target_row][col] = Container((target_row+1, col+1), 0, "UNUSED")

        return blocking_containers, State(
            state_representation=self.state_representation,
            depth=self.depth + 1,
            last_moved_container=self.state_representation[target_row][col],
            time=self.time + abs(crane_position[0] - target_row),
            parent_state=self,
            last_moved_location=(target_row, col),
            target_location=None,
        )

    def find_empty_position(self, target_row, target_col, exclude_col=None):
        grid = self.state_representation
        closest_position = None
        closest_distance = float('inf')  # Start with a very large distance.

        for col in range(12):
            if col == exclude_col:
                continue
            for row in range(7, -1, -1):  # Start from the topmost row and move downward.
                # Check if the spot is empty or UNUSED.
                if grid[row][col] is None or (isinstance(grid[row][col], Container) and grid[row][col].IsUNUSED):
                    # check the spot has a valid base (a NAN or a valid container directly below it) - no floating!
                    if row == 7 or self.is_valid_base(grid[row + 1][col]):
                        # Calculate Manhattan distance to the target container.
                        distance = abs(target_row - row) + abs(target_col - col)
                        # Update the closest position if this one is better.
                        if distance < closest_distance:
                            closest_position = (row, col)
                            closest_distance = distance

        return closest_position

    def is_valid_base(self, spot):
        return (
            spot.description == "NAN" or  # Spot is explicitly a NAN.
            (spot is not None and isinstance(spot, Container) and spot.description not in ["NAN", "UNUSED"])
        )
    def fix_floating_containers(self):
        #ship dimensions never change
        rows = 8
        cols = 12

        for col in range(cols):
            for row in range(rows - 1, -1, -1):  # start from the top of the ship and move downward
                container = self.state_representation[row][col]
                
                # don't check UNUSED or NAN containers
                if container is None or (isinstance(container, Container) and (container.IsNAN or container.IsUNUSED)):
                    continue

                current_row = row
                # move the container down until it sits on a valid base
                while current_row - 1 >= 0:  # Adjusted for the bottommost row being row 0
                    below_container = self.state_representation[current_row - 1][col]

                    # stop moving container down if it's the bottom
                    if current_row - 1 == 0:
                        break  # Row 0 is always valid to rest on
                    
                    # if the spot below is empty or UNUSED, continue checking below
                    if below_container is None or (isinstance(below_container, Container) and below_container.IsUNUSED):
                        # move container down by 1 row
                        self.state_representation[current_row - 1][col] = container
                        #reset the location that is moved from to be UNUSED
                        self.state_representation[current_row][col] = Container((current_row+1, col+1), 0, "UNUSED")
                        current_row -= 1
                    else:
                        # stop moving container down if its the bottom (sit on top of NAN)
                        break

                if current_row == 0:
                    continue  # check if container is at bottom row

                # make sure it sits on a NAN, bottom or not UNUSED container 
                below_container = self.state_representation[current_row - 1][col]
                if below_container is None or (isinstance(below_container, Container) and below_container.IsUNUSED):
                    # invalid base below to sit on, move it back to the original position
                    self.state_representation[current_row][col] = container
                    self.state_representation[row][col] = Container((current_row+1, col+1), 0, "UNUSED")

