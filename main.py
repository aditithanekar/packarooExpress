from datetime import datetime
import pytz
import requests
from container import container
import tkinter as tk
from tkinter import filedialog

    
# Global variable to track the chosen option load unload or balance
chosen_option = None

def main():
    updateLog("Insert Message to log.txt")
    
    manifestData = parseManifest("sampleManifest.txt")
    for container in manifestData:
        container.printContainer()
        
# To store each container object from manifest.txt into a list
def parseManifest(filePath):
    manifest = []

    with open(filePath, 'r') as file:
        updateLog("Manifest {} is opened".format(filePath))
        for line in file:
            line = line.strip()
            locationPart, weightPart, descriptionPart = line.split(", ")
            
            location = tuple(map(int, locationPart.strip("[]").split(',')))
            weight = int(weightPart.strip("{}"))
            description = descriptionPart

            newContainer = container(location, weight, description)
            manifest.append(newContainer)

    return manifest

# def updateMaifest():
#     # insert code

# def load():
#     # insert code   

# def unload():
#     # insert code

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
        print("Falling back to local system time (PST).")
        return datetime.now(pytz.timezone('America/Los_Angeles'))
        #return None

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
    # Clear current widgets
    for widget in root.winfo_children():
        widget.destroy()

    # Create a canvas for the grid
    canvas = tk.Canvas(root, width=600, height=400, bg="white")
    canvas.pack(pady=20)

    # Grid dimensions
    cell_width = 50
    cell_height = 50
    rows = 8
    cols = 12

    # Color mapping
    color_mapping = {
        "NAN": "gray",
        "UNUSED": "lightblue"
    }

    # Draw grid cells
    for container in parsed_data:
        location, weight, description = container.location, container.weight, container.description
        x, y = location  # Extract grid coordinates (1-based indexing)
        x -= 1  # Convert to zero-based index
        y -= 1

        # Adjust x for column (same as before), but reverse y for rows
        adjusted_x = y  # Column stays the same
        adjusted_y = rows - 1 - x  # Reverse the row order

        # Determine cell color
        color = color_mapping.get(description, "lightgreen" if weight > 0 else "white")

        # Draw the rectangle
        x1 = adjusted_x * cell_width
        y1 = adjusted_y * cell_height
        x2 = x1 + cell_width
        y2 = y1 + cell_height
        canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")

        # Add text inside the cell
        canvas.create_text(
            x1 + cell_width / 2,
            y1 + cell_height / 2,
            text = description,
            #text=str(weight) if weight > 0 else description,
            font=("Arial", 8),
            fill="black"
        )
        if chosen_option =="load_unload":
            tk.Label(root, text="What do you want to load? Enter description:", font=("Arial", 12)).pack(pady=10)
            load_input = tk.Entry(root, width=40)
            load_input.pack(pady=5)
            tk.Button(root, text="Load", font=("Arial", 14)).pack(pady=10)
            
            # Create a frame to display the entered descriptions
            description_frame = tk.Frame(root)
            description_frame.pack(pady=10)
            tk.Label(description_frame, text="Loaded Items:", font=("Arial", 14)).pack(anchor="w")

            # Add a scrolling listbox for user-entered descriptions
            listbox = tk.Listbox(description_frame, width=50, height=10)
            listbox.pack(side="left", fill="y")

            # Add scrollbar for the listbox
            scrollbar = tk.Scrollbar(description_frame, orient="vertical", command=listbox.yview)
            scrollbar.pack(side="right", fill="y")
            listbox.config(yscrollcommand=scrollbar.set)
            
            def load_item():
                description = load_input.get().strip()
                if description:
                    # Display the description in the listbox
                    listbox.insert(tk.END, description)
                    # Clear the input field
                    load_input.delete(0, tk.END)
                    # Optionally, update the log or perform further actions
                    updateLog(f"Loaded item with description: {description}")
                else:
                    tk.Label(root, text="Please enter a description!", font=("Arial", 12), fg="red").pack(pady=5)

            tk.Button(root, text="Load", font=("Arial", 14), command=load_item).pack(pady=10)

# Function to go to the next screen
def go_to_file_selector():
    entered_name = name_entry.get()
    if entered_name.strip():
        sign_in_message = entered_name + " signed in"
        print(sign_in_message)
        updateLog(sign_in_message)

    for widget in root.winfo_children():
        widget.destroy()

    def select_file():
        file_path = filedialog.askopenfilename(title="Select a File")
        if file_path:
            label_selected_file.config(text=f"Selected: {file_path}")
            parsed_data = parseManifest(file_path)
            tk.Button(root, text="Next", command=lambda: display_grid(parsed_data)).pack(pady=10)

    tk.Label(root, text="Select a File:", font=("Arial", 14)).pack(pady=20)
    tk.Button(root, text="Browse", command=select_file).pack(pady=10)
    label_selected_file = tk.Label(root, text="No file selected", fg="gray")
    label_selected_file.pack(pady=10)
    

# Main screen
root = tk.Tk()
root.title("Packeroo Express")
root.geometry("800x600")

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
