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
    
#the feature to add a comment
def add_comment_section():
    # frame for the comment section
    comment_frame = tk.Frame(root)
    comment_frame.pack(side=tk.BOTTOM, pady=20)
    
    tk.Label(comment_frame, text="Add Comment:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
    
    # enter comment in field
    comment_entry = tk.Entry(comment_frame, width=50)
    comment_entry.pack(side=tk.LEFT, padx=5)
    
    def submit_comment():
        comment = comment_entry.get().strip()
        if comment:
            utils.updateLog(comment)
            comment_entry.delete(0, tk.END)  # clear entry field
            # show confirmation
            confirm_label = tk.Label(comment_frame, text="Comment added to log file!", fg="green", font=("Arial", 10))
            confirm_label.pack(side=tk.RIGHT, padx=5)
            # remove confirmation after 2 seconds
            root.after(2000, confirm_label.destroy)
    
    # Add submit button
    tk.Button(comment_frame, text="Submit Comment", command=submit_comment, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)

#displays choice for choosing load/unload or balance
def go_to_option_selection():
    global chosen_option
    chosen_option = None  # Reset chosen option

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

    add_comment_section()

#calls the ShipBalancer, and gets the trace, leads to the animation right away
def balance_menu(parsed_data):
    for widget in root.winfo_children():
    #    if isinstance(widget, tk.Canvas):  # Keep the grid
          widget.destroy()
    tk.Label(root, text="Balance Containers", font=("Arial", 24, "bold"), fg="blue").pack(pady=10)
    balancer = ShipBalancer(manifest_filename)
    optimal_moves, final_state = balancer.balance_ship()
    print(optimal_moves)
    total_time = 0
    
    global current_instruction, instruction_label
    current_instruction = 0

    # Create a label for instructions
    instruction_label = tk.Label(root, text="", font=("Arial", 14))
    instruction_label.pack(pady=10)
    
     # Draw the initial state
    start_position = convert_to_grid_indices(*optimal_moves[0][0])
    end_position = convert_to_grid_indices(*optimal_moves[0][1])

    # Next button
    next_button = tk.Button(root, text="Next", command=lambda: next_instruction_balance_and_unload(optimal_moves, parsed_data, total_time), font=("Arial", 14))
    next_button.pack(pady=10)
    # Draw the initial state
    draw_grid_balance_and_unload(parsed_data, start_position=start_position, end_position=end_position, cost=optimal_moves[0][2], moves=optimal_moves)
    update_instruction_label_balance_and_unload(optimal_moves, total_time)
    
    add_comment_section()
    
#gets the containers to unload, and leads to load_menu
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
    add_comment_section()
    
# gets what containers to load and leads to instructions
def load_menu(parsed_data):
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
    
    add_comment_section()

# helper to change the (0,0) to be scaled to start at (1,1) for the manifest's format
def convert_to_grid_indices(row, col):
    return row + 1, col + 1

#gets the next load instruction in animation
def next_instruction(load_list, load_moved_positions, parsed_manifest_data, total_time_load):
    global current_instruction
    if current_instruction < len(load_list):
        print(f"Move container {load_list[current_instruction].description} to position {load_moved_positions[current_instruction + 1]}, total time for all load operations: {total_time_load} minutes.")
        current_instruction += 1
        draw_grid(parsed_manifest_data, load_moved_positions[current_instruction + 1], load_list[current_instruction].description, load_list[current_instruction].weight)
        update_instruction_label(load_list, load_moved_positions, total_time_load)
    else:
        done_with_operations()

#updates the instruction for what container to move for load 
def update_instruction_label(load_list, load_moved_positions, total_time_load):
    global current_instruction
    if current_instruction < len(load_list):
        instruction_label.config(text=f"Move container {load_list[current_instruction].description} to position {load_moved_positions[current_instruction+1]}, total time for all load operations: {total_time_load} minutes.")
    else:
        instruction_label.config(text="All containers moved!")
        done_with_operations()

#draws grid for load only, single container to be highlighted (spot to move it to)
def draw_grid(parsed_manifest, highlight_position=None, new_description=None, new_weight=None):
    """
    Updates and redraws the grid using the latest `parsed_manifest`.
    Optionally highlights a position and updates its container details.
    """
    # Clear the previous grid
    for widget in root.winfo_children():
        if isinstance(widget, tk.Canvas):
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

#calls the unload instructions first before load if there are containers to unload
def get_instructions(parsed_manifest_data):
    """Main function to handle both unload and load operations in sequence"""
    if len(containers_to_unload) > 0:
        get_instructions_unload(parsed_manifest_data)
    else:
        get_instructions_load(parsed_manifest_data)

#unload animation calls the unload, updates manifest with final state and calls draw_grid_balance_and_unload 
def get_instructions_unload(parsed_manifest_data):
    """Handle unloading operations and visualization"""
    global current_instruction, containers_to_unload
    for widget in root.winfo_children():
        widget.destroy()
    
    # Initialize unload state
    tk.Label(root, text="Unload instructions", font=("Arial", 24, "bold"), fg="blue").pack(pady=10)
    start_state = State()
    start_state.init_start_state(parsed_manifest_data)
    
    # Perform unload operations
    final_unload_state, unload_moves, blocking_containers = load_unload.unload(start_state, containers_to_unload, (8,0))
    trace, time_for_unload = load_unload.unload_time_trace(final_unload_state, unload_moves, blocking_containers)
    
    trace = [[(0, 3), (8, 0)], [(1, 1), (1, 0)], [(0, 1), (8, 0)]]
    utils.updateMaifest(final_unload_state, output_manifest_filename)
    
    # Initialize visualization
    global instruction_label
    instruction_label = tk.Label(root, text="Move container ___ to position ___", font=("Arial", 14))
    instruction_label.pack(pady=10)
    
    current_instruction = 0
    
    if trace:  # Only proceed if there are moves to make
        start_position = convert_to_grid_indices(*trace[0][0])
        end_position = convert_to_grid_indices(*trace[0][1])
        
        # Draw initial grid state
        draw_grid_balance_and_unload(
            parsed_manifest_data,
            start_position=start_position,
            end_position=end_position,
            moves=trace
        )
        
        # Store final unload state for next operations
        global final_manifest_after_unload
        final_manifest_after_unload = parseManifest(output_manifest_filename)
        
        # Set up next button for unload operations
        next_button = tk.Button(
            root, 
            text="Next", 
            command=lambda: next_instruction_balance_and_unload(trace, parsed_manifest_data, time_for_unload),
            font=("Arial", 14)
        )
        next_button.pack(pady=10)
        
        update_instruction_label_balance_and_unload(trace, time_for_unload)
    else:
        # If no unload moves, proceed to loading with original manifest
        get_instructions_load(parsed_manifest_data)

#calls load and begins animation using draw_grid(), and updates manifest with final state 
def get_instructions_load(parsed_manifest_data):
    """Handle loading operations with updated manifest data"""
    global current_instruction
    for widget in root.winfo_children():
        widget.destroy()
    
    if len(containers_to_load) == 0:
        done_with_operations()
        return
        
    # Initialize load state with updated manifest data
    tk.Label(root, text="Load instructions", font=("Arial", 24, "bold"), fg="blue").pack(pady=10)
    start_state = State()
    start_state.init_start_state(parsed_manifest_data)  # Using updated manifest
    
    # Perform load operations
    load_list = containers_to_load.copy()
    final_state, load_moved_positions = load_unload.load(start_state, containers_to_load)
    total_time_load = final_state.time
    
    # Update final manifest
    utils.updateMaifest(final_state, output_manifest_filename)
    
    # Convert positions to (1,1) corner instead of (0,0)
    load_moved_positions = [convert_to_grid_indices(row, col) for row, col in load_moved_positions]
    
    # Initialize visualization
    current_instruction = 0
    
    # Instruction label
    global instruction_label
    instruction_label = tk.Label(root, text="Move container ___ to position ___", font=("Arial", 14))
    instruction_label.pack(pady=10)

    # Next button to move through instructions
    next_button = tk.Button(root, text="Next", command=lambda: next_instruction(load_list, load_moved_positions, parsed_manifest_data, total_time_load), font=("Arial", 14))
    next_button.pack(pady=10)

    # Draw the first grid state
    draw_grid(parsed_manifest_data, load_moved_positions[current_instruction+1], load_list[current_instruction].description, load_list[current_instruction].weight)
    update_instruction_label(load_list, load_moved_positions, total_time_load)

#same as draw_grid, but highlights 2 locations... start and end positions
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
        
#goes to the next instruction for balance and unload
def next_instruction_balance_and_unload(moves, parsed_manifest_data, total_time):
    global current_instruction, final_manifest_after_unload

    if current_instruction < len(moves):
        # Process current move
        move = moves[current_instruction]
        if len(move) == 3:
            start, end, cost = move
        else:
            start, end = move
            cost = 0
        start_position = convert_to_grid_indices(*start)
        end_position = convert_to_grid_indices(*end)

        # Update container positions in the manifest data
        start_container = None
        end_container = None
        # Update the parsed_manifest data with the new positions
        for container in parsed_manifest_data:
            #find start and end containers so that you can set the properties right
            if container.position == start_position:
                start_container = container
            if container.position == end_position:
                end_container = container
                
        #make end container have start container and make start container unused
        start_weight = start_container.weight
        start_descrip = start_container.description
        for container in parsed_manifest_data:
            #find start and end containers so that you can set the properties right
            if container.position == start_position:
                container.weight = 0
                container.description= "UNUSED"
            if container.position == end_position:
                container.weight = start_weight
                container.description = start_descrip
        current_instruction += 1
        
        if current_instruction < len(moves):
            # Setup next move visualization
            move1 = moves[current_instruction]
            if len(move1) == 3:
                start1, end1, cost1 = move1
            else:
                start1, end1 = move1
                cost1 = 0
            start_position1 = convert_to_grid_indices(*start1)
            end_position1 = convert_to_grid_indices(*end1)
            
            draw_grid_balance_and_unload(
                parsed_manifest_data,
                start_position=start_position1,
                end_position=end_position1,
                cost=cost1,
                moves=moves
            )
            update_instruction_label_balance_and_unload(moves, total_time)
        else:
            # If this was the last unload move
            if len(containers_to_load) > 0:
                # Use the final unload state for loading
                # final_manifest_after_unload = parsed_manifest_data
                get_instructions_load(final_manifest_after_unload)
            else:
                done_with_operations()
    else:
        if len(containers_to_load) > 0:
            # Use the final unload state for loading
            get_instructions_load(final_manifest_after_unload)
        else:
            done_with_operations()

#gets the move instruction for balance and unload
def update_instruction_label_balance_and_unload(moves, total_time):
    global current_instruction
    if current_instruction < len(moves):
        # start,end,cost = None
        move = moves[current_instruction]
        if len(move) == 3:
            start, end, cost = move
        else:
            start, end = move
            cost = 0 
        # start, end, cost = moves[current_instruction]
        start_position = convert_to_grid_indices(*start)
        end_position = convert_to_grid_indices(*end)
        if chosen_option =="balance":
            instruction_label.config(text=f"Move container at {start_position} to {end_position} (Total Time for Balance Operations: {total_time} min)")
        else:
            instruction_label.config(text=f"Move container at {start_position} to {end_position} (Total Time for Unload Operations: {total_time} min)")

    else:
        instruction_label.config(text="All moves completed!")

#gets the filename for the output manifest(OUTBOUND)
def get_output_filename(input_file_path):

    # gets an output file name by adding 'OUTBOUND.txt' to the input file's name.
    print("manifest name is ", input_file_path)
    # split at the '.txt' extension
    base_filename = ""
    if input_file_path.endswith(".txt"):
        base_filename = input_file_path[:-4]  # get rid of the '.txt' 
    else:
        raise ValueError("The input file is not a .txt file.")
    
    # Append 'OUTBOUND' to the base filename
    output_filename = f"{base_filename}OUTBOUND.txt"
    
    print("manifest output name is ", output_filename)

    return output_filename

#the ending screen! tells the crane operator where the manifest is and reminds him to email the captain
def done_with_operations():
    for widget in root.winfo_children():
        widget.destroy()    
    #save the manifest here 
    #update manifest should already be called 
    tk.Label(root, text=f"Success! Manifest: {output_manifest_filename}, has been saved.", font=("Arial", 15)).pack(pady=50)
    tk.Label(root, text=f"Don't forget to send an email to the captain of the ship!", font=("Arial", 15)).pack(pady=30)

    print("done with all operations")
    print(manifest_filename)
    add_comment_section()


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


def getMoves():
    # insert code


    if __name__=="__main__":
        main()