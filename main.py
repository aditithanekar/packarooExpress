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

        for col in start_state.state_representation:
            for container in col:
            # Check if the container exists and has 'UNUSED' description
                if container is not None and container.get_description() == 'UNUSED':
                    print("unused")
                    #target = [row,0]
                    #time = abs(source[0] - target[0]) + abs(source[1] - target[1]) + 2
                    #state_rep = start_state.get_state_representation()



        
            

    return start_state


# def unload():
#     # insert code

# def balance():
#     # insert code

# def getMoves():
#     # insert code

if __name__=="__main__":
    main()
