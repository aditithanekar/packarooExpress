from state import State
from container import Container
import utils
import tkinter as tk
from tkinter import filedialog

    
# Global variable to track the chosen option load unload or balance
chosen_option = None
containers_to_load = [] #load list global
containers_to_unload = []


def main():
    state = State()
    updated_state = state.init_start_state()
    updated_state.print_state_representation()        

# def updateMaifest():
#     # insert code

# def load():
#     # insert code   

# def unload():
#     # insert code

# def balance():
#     # insert code


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
   
def display_grid(parsed_data):
    for widget in root.winfo_children():
        widget.destroy()

    canvas = tk.Canvas(root, width=600, height=400, bg="white")
    canvas.pack(pady=20)

    cell_width = 50
    cell_height = 50
    rows = 8
    cols = 12

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

    # Load UI
    if chosen_option == "load_unload":
        tk.Label(root, text="Load", font=("Arial", 24, "bold"), fg="blue").pack(pady=10)
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
                containers_to_load.append(new_container) #adds container to the list of containers to load
                tk.Label(root, text=f"Loading container: {name} with weight {weight}",font=("Arial", 10), fg="red").pack(pady=5)
                print(containers_to_load)
                name_input.delete(0, tk.END)
                weight_input.delete(0, tk.END)
                #parsed_data.append(new_container)  # Add to the parsed data
                #display_grid(parsed_data)  # Refresh grid
                utils.updateLog(f"Loading container: {name} with weight {weight}")
            else:
                tk.Label(root, text="Invalid input. Please enter a valid name and numeric weight.",
                         font=("Arial", 10), fg="red").pack(pady=5)

        tk.Button(root, text="Load", font=("Arial", 14), command=load_container).pack(pady=10)

# Function to go to the next screen
def go_to_file_selector():
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
            parsed_data = utils.parseManifest(file_path)
            tk.Button(root, text="Next", command=lambda: display_grid(parsed_data)).pack(pady=10)

    tk.Label(root, text="Select a File:", font=("Arial", 14)).pack(pady=20)
    tk.Button(root, text="Browse", command=select_file).pack(pady=10)
    label_selected_file = tk.Label(root, text="No file selected", fg="gray")
    label_selected_file.pack(pady=10)
    

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

# def getMoves():
#     # insert code

if __name__=="__main__":
    main()
