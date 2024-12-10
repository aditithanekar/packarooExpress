from state import State
from utils import parseManifest
import state
from container import Container
import utils
import tkinter as tk
from tkinter import filedialog

    
# Global variable to track the chosen option load unload or balance
chosen_option = None
containers_to_load = [] #load list global
containers_to_unload = []
parsed_manifest = [] # this doesn't really work as a global properly but it's passed as an arg

MANIFEST = parseManifest("sampleManifest.txt")

def main():
    state = State()
    updated_state = state.init_start_state(MANIFEST)
    #updated_state.print_state_representation() 

def load(start_state, load_list):
    source = [7,0]
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
                    time = source[1] + (9 - source[0]) + 4 + target[1] + (9 - target[0])
                    print(target, time)
    
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
                start_state = o
            
        track_moves.append(start_state.target_location)
        source = start_state.last_moved_location
        
    return start_state, track_moves


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

def unload(start_state, unload_target, load_list, unload_position):
    state_queue = PriorityQueue()
    visited_costs = {}
    crane_position = (7, 0)

    heuristic = calculate_heuristic(start_state, unload_target, unload_position)
    state_queue.put((start_state.time + heuristic, start_state, crane_position))
    visited_costs[start_state.to_string()] = start_state.time

    while not state_queue.empty():
        _, current_state, crane_position = state_queue.get()

        if current_state.is_unload_goal_test([unload_target]):
            return current_state

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

    return None

#displays choice for choosing load/unload or balance
def go_to_option_selection():
    global chosen_option
    chosen_option = None  # Reset chosen option
    # Clear current widgets
    # for widget in root.winfo_children():
    #     widget.destroy()

    # Create and display options
    tk.Label(root, text="Choose an Option:", font=("Arial", 18)).pack(pady=20)

    tk.Button(root, text="Load/Unload", font=("Arial", 14), width=20, 
              command=lambda: set_option_and_go("load_unload", go_to_file_selector)).pack(pady=10)
    tk.Button(root, text="Balance", font=("Arial", 14), width=20, 
              command=lambda: set_option_and_go("balance", go_to_file_selector)).pack(pady=10)

def set_option_and_go(option, next_screen_func):
    global chosen_option
    chosen_option = option
    next_screen_func()
  
#displays the 8X12 grid color coded  
def display_grid(parsed_data):
    for widget in root.winfo_children():
        widget.destroy()

    canvas = tk.Canvas(root, width=600, height=400, bg="white")
    canvas.pack(pady=20)

    cell_width = 50
    cell_height = 50
    rows = 8
    cols = 12
    current_containers_on_ship = [] # this is a list of green containers, possibly unloadable ones
    
    #makes it so that NAN spots are gray, UNUSED are blue, and filled containers are green
    color_mapping = {
        "NAN": "gray",
        "UNUSED": "lightblue"
    }

    # Draw grid cells
    for container in parsed_data:
        position, weight, description = container.position, container.weight, container.description
        x, y = position
        x -= 1
        y -= 1

        adjusted_x = y
        adjusted_y = rows - 1 - x

        color = color_mapping.get(description, "lightgreen" if weight > 0 else "white")
        if color == "lightgreen":
            current_containers_on_ship.append(container)#add to unloadable list

        x1 = adjusted_x * cell_width
        y1 = adjusted_y * cell_height
        x2 = x1 + cell_width
        y2 = y1 + cell_height
        canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")

        canvas.create_text(
            x1 + cell_width / 2,
            y1 + cell_height / 2,
            text=description,
            font=("Arial", 8),
            fill="black"
        )

    if chosen_option == "load_unload":
        unload_menu(parsed_data, current_containers_on_ship)

#displays spot to enter in what containers to load, and calls unload()
def load_menu(parsed_data):
    print("current containers to unload: ")
    print(containers_to_unload)
    #call unload here:
    start_state = State()
    start_state.init_start_state(parsed_data)
    unload(start_state, containers_to_unload)
    tk.Label(root, text="Load Containers", font=("Arial", 24, "bold"), fg="blue").pack(pady=10)
    tk.Label(root, text="Enter Container Name:", font=("Arial", 12)).pack(pady=5)
    name_input = tk.Entry(root, width=30)
    name_input.pack(pady=5)

    tk.Label(root, text="Enter Container Weight:", font=("Arial", 12)).pack(pady=5)
    weight_input = tk.Entry(root, width=30)
    weight_input.pack(pady=5)

    def load_container():
        name = name_input.get().strip()
        weight = weight_input.get().strip()
        if name and weight.isdigit():
            weight = int(weight)
            new_container = Container(None, weight, name)
            containers_to_load.append(new_container)
            tk.Label(root, text=f"Loaded container: {name} with weight {weight}",
                     font=("Arial", 10), fg="red").pack(pady=5)
            name_input.delete(0, tk.END)
            weight_input.delete(0, tk.END)
            utils.updateLog(f"Loaded container: {name} with weight {weight}")
        else:
            tk.Label(root, text="Invalid input. Please enter a valid name and numeric weight.",
                     font=("Arial", 10), fg="red").pack(pady=5)

    tk.Button(root, text="Load", font=("Arial", 14), command=load_container).pack(pady=10)
    def go_to_get_instructions():
        get_instructions(parsed_data)
    tk.Button(root, text="Next", font=("Arial", 14), command=go_to_get_instructions).pack(pady=10)

def unload_menu(parsed_data, unloadable_containers):
    tk.Label(root, text="Unload Containers", font=("Arial", 24, "bold"), fg="blue").pack(pady=10)
    tk.Label(root, text="Select containers to unload:", font=("Arial", 12)).pack(pady=5)

    # Listbox to select containers
    listbox = tk.Listbox(root, width=50, height=10, selectmode=tk.MULTIPLE)
    listbox.pack(pady=5)

    # Populate the listbox with loaded containers
    for idx, container in enumerate(unloadable_containers):
        listbox.insert(idx, f"{container.description} (Weight: {container.weight})")

    def unload_containers():
        selected_indices = listbox.curselection()
        for idx in selected_indices:
            containers_to_unload.append(unloadable_containers[idx])
        tk.Label(root, text="Selected containers for unloading.",
                 font=("Arial", 10), fg="red").pack(pady=5)
        utils.updateLog(f"Unloaded containers: {', '.join([unloadable_containers[idx].description for idx in selected_indices])}")

    tk.Button(root, text="Unload", font=("Arial", 14), command=unload_containers).pack(pady=10)
    def go_to_load_menu():
        for widget in root.winfo_children():
            if not isinstance(widget, tk.Canvas):  # Keep the grid
                widget.destroy()
        load_menu(parsed_data)

    tk.Button(root, text="Next", font=("Arial", 14), command=go_to_load_menu).pack(pady=10)

#calls load here after getting a list of containers to load
def get_instructions(parsed_manifest_data):
    for widget in root.winfo_children():
        widget.destroy()
    tk.Label(root,text="instructions coming here")
    start_state = state.State()
    #if parsed_manifest_data:
    start_state.init_start_state(parsed_manifest_data)
    #start_state.init_start_state()
    load(start_state, containers_to_load)
    # else:
    #     print("there's no manifest!!!!!")

# Function to go to the next screen
def go_to_file_selector():
    global parsed_manifest #declare that it's global so that we can access it again
    entered_name = name_entry.get()
    if entered_name.strip():
        sign_in_message = entered_name + " signed in"
        print(sign_in_message)
        utils.updateLog(sign_in_message)

    for widget in root.winfo_children():
        widget.destroy()

    def select_file():
        file_path = filedialog.askopenfilename(title="Select a File")
        if file_path:
            label_selected_file.config(text=f"Selected: {file_path}")
            parsed_manifest = parseManifest(file_path)
            tk.Button(root, text="Next", command=lambda: display_grid(parsed_manifest)).pack(pady=10)

    tk.Label(root, text="Select a File:", font=("Arial", 14)).pack(pady=20)
    tk.Button(root, text="Browse", command=select_file).pack(pady=10)
    label_selected_file = tk.Label(root, text="No file selected", fg="gray")
    label_selected_file.pack(pady=10)
    

# # Main screen
# root = tk.Tk()
# root.title("Packeroo Express")
# root.geometry("1200x900")

# # Initial widgets
# tk.Label(root, text="Enter Your Name:", font=("Arial", 14)).pack(pady=10)
# name_entry = tk.Entry(root, width=30)
# name_entry.pack(pady=5)
# tk.Button(root, text="Next", command=go_to_option_selection).pack(pady=20)


# root.mainloop()

# def getMoves():
#     # insert code

if __name__=="__main__":
    main()