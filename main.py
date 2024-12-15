from state import State
from utils import parseManifest
import state
from container import Container
import utils
import tkinter as tk
from tkinter import filedialog
import load_unload
import os
from balance2 import ShipBalancer
    
# Global variable to track the chosen option load unload or balance
chosen_option = None
containers_to_load = [] #load list global
containers_to_unload = []
parsed_manifest = [] # this doesn't really work as a global properly but it's passed as an arg
# global manifest_filename = ""
output_manifest_filename= ""

#MANIFEST = parseManifest("ShipCase1.txt")

def main():
    # state = State()
    # updated_state = state.init_start_state(MANIFEST)
    
    # Main screen
    root = tk.Tk()
    root.title("Packeroo Express")
    root.geometry("1200x900")

    # Initial widgets
    tk.Label(root, text="Enter Your Name:", font=("Arial", 14)).pack(pady=10)
    name_entry = tk.Entry(root, width=30)
    name_entry.pack(pady=5)
    tk.Button(root, text="Next", command=go_to_option_selection).pack(pady=20)

    root.mainloop()

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
    if chosen_option == "balance":
        balance_menu(parsed_data)

def balance_menu(parsed_data):
    for widget in root.winfo_children():
    #    if isinstance(widget, tk.Canvas):  # Keep the grid
          widget.destroy()
    tk.Label(root, text="Balance Containers", font=("Arial", 24, "bold"), fg="blue").pack(pady=10)
    balancer = ShipBalancer(manifest_filename)
    optimal_moves, final_state = balancer.balance_ship()
    print(optimal_moves)
    
    global current_instruction, instruction_label
    current_instruction = 0

    # Create a label for instructions
    instruction_label = tk.Label(root, text="", font=("Arial", 14))
    instruction_label.pack(pady=10)
    
     # Draw the initial state
    start_position = convert_to_grid_indices(*optimal_moves[0][0])
    end_position = convert_to_grid_indices(*optimal_moves[0][1])

    # Next button
    next_button = tk.Button(root, text="Next", command=lambda: next_instruction_balance_and_unload(optimal_moves, parsed_data), font=("Arial", 14))
    next_button.pack(pady=10)
    # Draw the initial state
    draw_grid_balance_and_unload(parsed_data, start_position=start_position, end_position=end_position, cost=optimal_moves[0][2], moves=optimal_moves)
    update_instruction_label_balance_and_unload(optimal_moves)
    
#displays spot to enter in what containers to load, and calls unload()
def load_menu(parsed_data):
    print("current containers to unload: ")
    print(containers_to_unload)
    #call unload here:
    start_state = State()
    start_state.init_start_state(parsed_data)
    start_state.print_state_representation()
    # balancer = ShipBalancer(manifest_filename)
    # final_state, unload_moves = balancer.unload(start_state, containers_to_unload)
    final_state, unload_moves = load_unload.unload(start_state, containers_to_unload, (7,0))
    final_state.print_state_representation()
    print("unload moves, ", unload_moves)
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
    # tk.Label(root, text="Unload Containers", font=("Arial", 24, "bold"), fg="blue").pack(pady=10)
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
#changes the (0,0) to be scaled to start at (1,1)
def convert_to_grid_indices(row, col):
    return row + 1, col + 1
def next_instruction(load_list, load_moved_positions, parsed_manifest_data):
    global current_instruction
    if current_instruction < len(load_list):
        print(f"Move container {load_list[current_instruction].description} to position {load_moved_positions[current_instruction + 1]}")
        current_instruction += 1
        draw_grid(parsed_manifest_data, load_moved_positions[current_instruction + 1], load_list[current_instruction].description, load_list[current_instruction].weight)
        update_instruction_label(load_list, load_moved_positions)
    else:
        done_with_operations()

def update_instruction_label(load_list, load_moved_positions):
    global current_instruction
    if current_instruction < len(load_list):
        instruction_label.config(text=f"Move container {load_list[current_instruction].description} to position {load_moved_positions[current_instruction+1]}")
    else:
        instruction_label.config(text="All containers moved!")
        done_with_operations()

#calls load here after getting a list of containers to load
def get_instructions(parsed_manifest_data):
    global current_instruction
    for widget in root.winfo_children():
        widget.destroy()
    
    # Initialize the UI and state
    tk.Label(root, text="Load instructions", font=("Arial", 24, "bold"), fg="blue").pack(pady=10)
    start_state = state.State()
    start_state.init_start_state(parsed_manifest_data)
    print("Initial state:")
    start_state.print_state_representation()
    print(containers_to_load)

    load_list = containers_to_load.copy() 
    final_state, load_moved_positions = load_unload.load(start_state, containers_to_load)
    final_state.print_state_representation()
    
    #update/write to the manifest here: 
    #it's spelt wrong but we're going with it..
    
    utils.updateMaifest(final_state, output_manifest_filename)
    
    load_moved_positions = [convert_to_grid_indices(row, col) for row, col in load_moved_positions]
    
    # Start with the first instruction
    current_instruction = 0
    
    # Instruction label
    global instruction_label
    instruction_label = tk.Label(root, text="Move container ___ to position ___", font=("Arial", 14))
    instruction_label.pack(pady=10)

    # Next button to move through instructions
    next_button = tk.Button(root, text="Next", command=lambda: next_instruction(load_list, load_moved_positions, parsed_manifest_data), font=("Arial", 14))
    next_button.pack(pady=10)

    # Draw the first grid state
    draw_grid(parsed_manifest_data, load_moved_positions[current_instruction+1], load_list[current_instruction].description, load_list[current_instruction].weight)
    update_instruction_label(load_list, load_moved_positions)
#for load only
def draw_grid(parsed_manifest, highlight_position=None, new_description=None, new_weight=None):
    """
    Updates and redraws the grid using the latest `parsed_manifest`.
    Optionally highlights a position and updates its container details.
    """
    # Clear the previous grid
    for widget in root.winfo_children():
        if isinstance(widget, tk.Canvas):
            widget.destroy()
        if isinstance(widget, tk.Button):
            widget.destroy()


    canvas = tk.Canvas(root, width=600, height=400, bg="white")
    canvas.pack(pady=20)
    cell_width = 50
    cell_height = 50
    rows = 8
    cols = 12
    current_containers_on_ship = []

    # Update container data if needed
    if highlight_position:
        for container in parsed_manifest:
            print(container.position)
            if container.position == highlight_position:
                print("found the spot")
                container.description = new_description 
                container.weight = new_weight 

    # Color mapping for containers
    color_mapping = {
        "NAN": "gray",
        "UNUSED": "lightblue",
    }

    # Draw grid cells
    for container in parsed_manifest:
        position, weight, description = container.position, container.weight, container.description
        x, y = position
        x -= 1
        y -= 1

        adjusted_x = y
        adjusted_y = rows - 1 - x

        # Determine the color for the container
        if position == highlight_position:
            color = "yellow"  # Highlighted color
        else:
            color = color_mapping.get(description, "lightgreen" if weight > 0 else "white")

        x1 = adjusted_x * cell_width
        y1 = adjusted_y * cell_height
        x2 = x1 + cell_width
        y2 = y1 + cell_height
        canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")

        # Add text to the cell
        canvas.create_text(
            x1 + cell_width / 2,
            y1 + cell_height / 2,
            text=description,
            font=("Arial", 8),
            fill="black"
        )

# Function to reset the highlighted cell to green
def reset_highlight(parsed_data, highlight_position):
    for container in parsed_data:
        if container.position == highlight_position:
            container.description = "FULL"  # Reset description
            container.weight = 50  # Reset weight
    draw_grid()


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
            global manifest_filename 
            manifest_filename= file_path
            global output_manifest_filename
            output_manifest_filename = get_output_filename(manifest_filename)
            print(manifest_filename)
            parsed_manifest = parseManifest(file_path)
            tk.Button(root, text="Next", command=lambda: display_grid(parsed_manifest)).pack(pady=10)

    tk.Label(root, text="Select a File:", font=("Arial", 14)).pack(pady=20)
    tk.Button(root, text="Browse", command=select_file).pack(pady=10)
    label_selected_file = tk.Label(root, text="No file selected", fg="gray")
    label_selected_file.pack(pady=10)
    
    
def draw_grid_balance_and_unload(parsed_manifest, start_position=None, end_position=None, cost=None, moves=None):
    # Clear the previous grid
    for widget in root.winfo_children():
        if isinstance(widget, tk.Canvas):
            widget.destroy()
        # if isinstance(widget, tk.Button):
        #     widget.destroy()


    canvas = tk.Canvas(root, width=600, height=400, bg="white")
    canvas.pack(pady=20)
    cell_width = 50
    cell_height = 50
    rows = 8
    cols = 12
    current_containers_on_ship = []

    # Update container data if needed
    if start_position and end_position:
        for container in parsed_manifest:
            print(container.position)
            if container.position == start_position:
                print("found the spot")
                # container.description = new_description 
                # container.weight = new_weight 

    # Color mapping for containers
    color_mapping = {
        "NAN": "gray",
        "UNUSED": "lightblue",
    }

    # Draw grid cells
    for container in parsed_manifest:
        if container is None:
            continue
        position, weight, description = container.position, container.weight, container.description
        if position is None:  # Skip unused cells without position
           continue
        x, y = position
        x -= 1
        y -= 1

        adjusted_x = y
        adjusted_y = rows - 1 - x

        # Determine the color for the container
        if position == start_position:
            color = "yellow"  # Highlighted color
        elif position == end_position:
            color = "orange"
        else:
            color = color_mapping.get(description, "lightgreen" if weight > 0 else "white")

        x1 = adjusted_x * cell_width
        y1 = adjusted_y * cell_height
        x2 = x1 + cell_width
        y2 = y1 + cell_height
        canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")

        # Add text to the cell
        canvas.create_text(
            x1 + cell_width / 2,
            y1 + cell_height / 2,
            text=description,
            font=("Arial", 8),
            fill="black"
        )
    # # Clear the previous canvas if it exists
    # for widget in root.winfo_children():
    #     if isinstance(widget, tk.Canvas):
    #         widget.destroy()

    # canvas = tk.Canvas(root, width=600, height=400, bg="white")
    # canvas.pack(pady=20)

    # cell_width = 50
    # cell_height = 50
    # rows = 8
    # cols = 12

    # # Draw grid cells
    # for container in parsed_manifest:
    #     position, weight, description = container.position, container.weight, container.description
    #     if position is None:  # Skip unused cells without position
    #         continue
    #     x, y = position
    #     x -= 1
    #     y -= 1

    #     adjusted_x = y
    #     adjusted_y = rows - 1 - x

    #     # Determine the color for the container
    #     color = "white"  # Default color

    #     # Handle specific cases for positions:
    #     if description == "UNUSED":
    #         color = "lightblue"  # UNUSED is light blue
    #     elif description == "NAN":
    #         color = "gray"  # NAN is gray
    #     elif position == start_position:
    #         color = "red"  # Start position is marked in red
    #     elif position == end_position:
    #         color = "yellow"  # End position is marked in yellow
    #     else:
    #         color = "green"  # Containers are marked in green by default

    #     # Draw the rectangle for the current grid cell
    #     x1 = adjusted_x * cell_width
    #     y1 = adjusted_y * cell_height
    #     x2 = x1 + cell_width
    #     y2 = y1 + cell_height
    #     canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black", width=3 if color != "white" else 1)

    #     # Add text to the cell to describe the container
    #     canvas.create_text(
    #         x1 + cell_width / 2,
    #         y1 + cell_height / 2,
    #         text=description,
    #         font=("Arial", 8),
    #         fill="black"
    #     )

    # # Display the cost if available
    # if cost is not None:
    #     tk.Label(root, text=f"Cost: {cost} min", font=("Arial", 14)).pack(pady=10)


def next_instruction_balance_and_unload(moves, parsed_manifest_data):
    global current_instruction

    if current_instruction < len(moves):
        # Get the current move (start, end, and cost)
        start, end, cost = moves[current_instruction]
        start_position = convert_to_grid_indices(*start)
        end_position = convert_to_grid_indices(*end)

        print(f"Move container at {start_position} to {end_position} for a cost of {cost} min")

        start_container = None
        end_container = None
        # Update the parsed_manifest data with the new positions
        for container in parsed_manifest_data:
            #find start and end containers so that you can set the properties right
            if container.position == start_position:
                start_container = container
                # .description = "UNUSED"  # Mark start position as UNUSED
                # container.position = None  # Clear its position
            if container.position == end_position:
                end_container = container
                # container.description =   # Mark end position as container (green)
                # container.position = end_position
        #make end container have start container and make start container unused
        #end_container = Container(end_container.position, start_container.weight, start_container.description)
        #make start container unused
        #start_container = Container(start_container.position, 0, "UNUSED")
        start_weight = start_container.weight
        start_descrip = start_container.description
        for container in parsed_manifest_data:
            #find start and end containers so that you can set the properties right
            if container.position == start_position:
                container.weight = 0
                container.description= "UNUSED"
                # .description = "UNUSED"  # Mark start position as UNUSED
                # container.position = None  # Clear its position
            if container.position == end_position:
                container.weight = start_weight
                container.description = start_descrip
                # end_container = container
        # x1,y1 = start_position
        # x2,y2 = end_position
        
        # parsed_manifest_data[x1-1][y1-1] = Container(start_container.position, 0, "UNUSED")
        # parsed_manifest_data[x2-1][y2-1] = Container(end_container.position, start_container.weight, start_container.description)

        current_instruction += 1
        start1, end1, cost1 = moves[current_instruction]
        start_position1 = convert_to_grid_indices(*start1)
        end_position1 = convert_to_grid_indices(*end1)
        # Redraw the grid with the updated parsed manifest
        draw_grid_balance_and_unload(parsed_manifest_data, start_position=start_position1, end_position=end_position1, cost=cost1, moves=moves)
        
        # Update the instruction label
        update_instruction_label_balance_and_unload(moves)
        # Increment the instruction index
    else:
        instruction_label.config(text="All moves completed!")
        done_with_operations()

        
def update_instruction_label_balance_and_unload(moves):
    global current_instruction
    if current_instruction < len(moves):
        start, end, cost = moves[current_instruction]
        start_position = convert_to_grid_indices(*start)
        end_position = convert_to_grid_indices(*end)
        instruction_label.config(text=f"Move container at {start_position} to {end_position} (Cost: {cost} min)")
    else:
        instruction_label.config(text="All moves completed!")

#gets the filename for the output manifest(OUTBOUND)
def get_output_filename(input_file_path):

    # Generates an output file path by replacing the input file's name with 'ShipCaseOUTBOUND.txt'.
    
   # Extract the directory and input filename
    directory, input_filename = os.path.split(input_file_path)
    print("manifest name is ", input_file_path)
    # split at the '.txt' extension
    base_filename = ""
    if input_file_path.endswith(".txt"):
        base_filename = input_file_path[:-4]  # Remove the '.txt' extension
    else:
        raise ValueError("The input file does not have a .txt extension.")
    
    # Append 'OUTBOUND' to the base filename
    output_filename = f"{base_filename}OUTBOUND.txt"
    
    print("manifest output name is ", output_filename)
    # Combine the directory and the new output filename
    #output_file_path = os.path.join(directory, output_filename)
    
    return output_filename

def done_with_operations():
    for widget in root.winfo_children():
        widget.destroy()    
    tk.Label(root, text="done with all operations", font=("Arial", 14)).pack(pady=10)
    print("done with all operations")
    #print with tk that manifest is saved to (file location)
    print(manifest_filename)
    #save the manifest here 
    #update manifest should already be called 


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


def getMoves():
    # insert code


    if __name__=="__main__":
        main()