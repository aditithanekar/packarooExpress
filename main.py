from state import State
from utils import parseManifest
import state
from container import Container
import utils
import tkinter as tk
from tkinter import filedialog


def main():
    updateLog("Insert Message to log.txt")
    
    manifestData = parseManifest("sampleManifest.txt")
    for container in manifestData:
        container.printContainer()
        
# To store each container object from manifest.txt into a grid
def parseManifest(filePath):
    manifest = []

    # Open the manifest file and read each line
    with open(filePath, 'r') as file:
        # Read each line in the file
        updateLog("Manifest {} is opened".format(filePath))
        # Read each line in the file
        for line in file:
            line = line.strip() # Remove leading/trailing whitespace
            locationPart, weightPart, descriptionPart = line.split(", ") # Split the line into parts
            
            location = tuple(map(int, locationPart.strip("[]").split(','))) # Convert the location to a tuple
            weight = int(weightPart.strip("{}")) # Convert the weight to an integer
            description = descriptionPart # Keep the description as a string

            newContainer = container(location, weight, description) # Create a new container object
            manifest.append(newContainer) # Add the container to the manifest list

    return manifest

# def updateMaifest():
def updateMaifest():
   try:
    with open(filePath, 'w') as file:
        for container in updatedManifest:
            # Format the container data into a string
            locationStr = f"[{container.location[0]:02}, {container.location[1]:02}]"
            # Format the weight as a 5-digit string with leading zeros
            weightStr = f"{{container.weight:05}}"
            # Get the description string
            descriptionStr = container.description

            file.write(f"{locationStr}, {weightStr}, {descriptionStr}\n")
    
    updateLog(f"Manifest {filePath} updated successfully.")

   except Exception as e:
       update(f"Error updating manifest: {e}")

# def load():
#     # insert code 
def load(start_state, load_list): # Clarify where the load_list is coming from 
    """
    Helper function for the load algorithm.

    Args:
        start_state (State): The current state of the ship.
        load_list (list): List of containers to load onto the ship.

    Returns:
        State: The updated state after loading the containers.
    """

    print("we in load")

    # Continue loading containers until the load list is empty
    while len(load_list) != 0:
        # Remove the last container from the load list
        node = load_list.pop()

        # Define the source (starting location) for loading (e.g., crane position)
        source = [7, 0]  # Example: crane is at row 7, column 0

        # Iterate through the grid (columns and rows) to find a target position
        for col_index, col in enumerate(start_state.state_representation):
            for row_index, container in enumerate(col):
                # Check if the cell is empty and marked as 'UNUSED'
                if container is not None and container.get_description() == 'UNUSED':
                    # Define the target position for the current container
                    target = [row_index, 0]

                    # Calculate the time taken to move from source to target
                    # Formula: Manhattan distance + extra 2 units for placement time
                    # Will replace this with A*
                    time = abs(source[0] - target[0]) + abs(source[1] - target[1]) + 2 

                    # Get the current state representation (grid)
                    state_rep = start_state.get_state_representation()

                    # Place the container in the target cell
                    state_rep[row_index][0] = node

                    # Create a new state object with the updated grid
                    new_state = State(
                        state_rep,                # Updated grid representation
                        start_state.depth,        # Same depth as the current state
                        [None, None],             # Placeholder (can store additional info)
                        start_state.time + time,  # Increment total time by the cost of this move
                        start_state,              # Link to the parent state for backtracking
                        time,                     # Cost for this specific action
                        0,                        # Placeholder for heuristic (if needed)
                        [-1, -1],                 # Placeholder for additional info
                        target                    # Final position of the loaded container
                    )

                    # Update the current state to this new state
                    start_state = new_state

                    # Break the loop once the container is placed
                    break

    # Return the updated state after all containers are loaded
    return start_state

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


# def unload():
#     # insert code
def unload(start_state, unload_targets, unload_position):
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


# def balance():
#     # insert code

# To get current PST time from an external source, for updateLog()
def getCurrentTime():
    try:
        response = requests.get("http://worldtimeapi.org/api/timezone/America/Los_Angeles")
        response.raise_for_status()  # Raises an exception if there is an error in the request
        data = response.json()
        datetimeString = data["datetime"]
        utcTime = datetime.strptime(datetimeString, "%Y-%m-%dT%H:%M:%S.%f%z")
        pstTimezone = pytz.timezone('America/Los_Angeles')
        pstTime = utcTime.astimezone(pstTimezone)
        return pstTime
    except requests.RequestException as e:
        print("Error fetching time:", e)
        return None

# To update log file with a message string
# USAGE: updateLog("Insert Message to log.txt")
def updateLog(message):
    pstTime = getCurrentTime()

    if 10<=pstTime.day % 100<=20: suffix = "th"
    else: suffix = {1:"st", 2:"nd", 3:"rd"}.get(pstTime.day % 10, "th")
    
    month_day_year = pstTime.strftime(f"%B {pstTime.day}{suffix} %Y")
    timePart = pstTime.strftime("%H:%M")
    pstTimeFormatted = f"{month_day_year}: {timePart}"
    logInput = f"{pstTimeFormatted} {message}"
    print(logInput)
    
    with open("log.txt", "a") as logFile:
        logFile.write(logInput + "\n")

# def getMoves():
#     # insert code

if __name__=="__main__":
    main()