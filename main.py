from datetime import datetime
import pytz
import requests
from container import container

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
  

# def unload():
#     # insert code
def unload(start_state, unload_target, load_list, unload_position):
    """
    Unloads a specified container from the grid and moves it to the back of the load_list.

    Args:
        start_state (State): The current state of the ship (grid representation).
        unload_target (str): The description of the container to unload.
        load_list (list): The list of containers on the ship.
        unload_position (list): Target position for unloading [row, col].

    Returns:
        State: The updated state after unloading the container.
        list: Updated load_list with the container moved to the back.
    """
    final_pos = unload_position
    unload_position = [0,0]

    # path = a_star


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