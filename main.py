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

        for col_index, col in enumerate(start_state.state_representation):
            for row_index, container in enumerate(col):
                 # Check if the container exists and has 'UNUSED' description
                if container is not None and container.get_description() == 'UNUSED':
                    #print("unused")
                    target = [row_index, 0]
                    time = abs(source[0] - target[0]) + abs(source[1] - target[1]) + 2
                    state_rep = start_state.get_state_representation()
                    state_rep[row_index][0] = node

                    #new state object with the new and updated representation
                    new_state = State(
                        state_rep,                #updated state representation
                        start_state.depth,        #depth is same
                        [None, None],             
                        start_state.time + time,  
                        start_state,              #link back to the parent state
                        time,                     #time taken for THIS action
                        0,                        
                        [-1, -1],                 
                        target                    #target location of the loaded container
                    )

                    start_state = new_state

                    break

    return start_state


# def unload():
#     # insert code

# def balance():
#     # insert code

# def getMoves():
#     # insert code

if __name__=="__main__":
    main()
