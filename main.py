from state import State
from utils import parseManifest
import state


#may have to delete line below!! MANIFEST cuz we open it in state.py!

#MANIFEST = parseManifest("sampleManifest.txt")

def main():
    state = State()
    updated_state = state.init_start_state()
    #updated_state.print_state_representation() 
      

# def updateMaifest():
#     # insert code

def load(start_state, load_list):
    """
    Helper function for the load algo

    Args:
        start_state (State): starting state
        load_list (list): list of containers to load

    Returns:
        State
    """

    print("we in load")


    while len(load_list) != 0:
        #pop last container from list to use it
        node = load_list.pop()
        #center of the ship
        source = [7,0]

        move_options = []
        
        for col_index, col in enumerate(start_state.state_representation):
            for row_index, container in enumerate(col):
                 # Check if the container exists and has 'UNUSED' description
                if container is not None and container.get_description() == 'UNUSED':
                    target = [row_index, col_index]
                    
                    # Time is from source, to above top corner of grid [0,9], to truck, to [0,9], to target
                    # Switch to this once the 12x12 is fixed to 8x12
                    # time = (abs(source[0] - 0) + abs(source[1] - 9)) + (2 + 2) + (abs(0 - target[0]) + abs(9 - target[1]))
                    time = (abs(source[0] - 0) + abs(source[1] - 12)) + (2 + 2) + (abs(0 - target[0]) + abs(12 - target[1])) 
                    print(abs(source[0] - 0),abs(source[1] - 12),4,abs(0 - target[0]),abs(12 - target[1]))    
                                   
                    state_rep = start_state.get_state_representation()
                    state_rep[row_index][col_index] = node

                    #new state object with the new and updated representation
                    new_state = State(
                        state_rep,                #updated state representation
                        start_state.depth + 1,    #depth is +1
                        target,                   #target location of the loaded container WHATS THE DIFFERENCE??           
                        start_state.time + time,  
                        start_state,              #link back to the parent state
                        time,                     #time taken for THIS action
                        0,                        
                        [-1, -1],                 #target location of the loaded container WHATS THE DIFFERENCE??               
                        target                    #target location of the loaded container WHATS THE DIFFERENCE??
                    )
                    move_options.append(new_state)
                    print("New State:", new_state.time, "\t", new_state.last_moved_container, "Old container spot:", container.position, container.description)

                    break

        start_state = min(move_options, key=lambda state: state.time)
        source = start_state.last_moved_container

    return start_state


# def unload():
#     # insert code

# def balance():
#     # insert code

# def getMoves():
#     # insert code

if __name__=="__main__":
    main()
