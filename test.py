import main
from state import State
from container import Container
from utils import parseManifest
from main import load
from balance2 import a_star
import utils
from load_unload import load
import load_unload

MANIFEST = utils.parseManifest("ShipCase1.txt")

state = State()
state.init_start_state(MANIFEST)


# ADITI TESTING STUFF ===============================================================================================
def adititest():
    state.print_state_representation()
    
    result_state = a_star(state)
    print(result_state)
    #result_state.print_state_representation()

adititest()

# SUHANI TESTING STUFF ===============================================================================================
# def suhani_test():
#     updated_state.print_state_representation()
    
#     containers = [Container(position=None, weight=10.0 + i, description=f"Container {i}") for i in range(1)]
#     for container in containers:
#         print(container.print_node_description())
        
#     result_state = load(updated_state, containers)
#     result_state.print_state_representation()

# suhani_test()

# load(updated_state, MANIFEST)

state = state.init_start_state(MANIFEST)
state.print_state_representation()

containers = [Container(position=None, weight=10.0 + i, description=f"Box{i}") for i in range(11)]

loaded_state, operations = load(state, containers) # operations is for if printing steps is needed later
loaded_state.print_state_representation()

utils.updateMaifest(loaded_state, "updatedManifest.txt")

# #USING MOCK MANIFEST------------------------------------------------------------------------------------------------------------
# def test_load():
    
#     mock_manifest = [
#         Container([1, 0], 10, 'UNUSED'),
#         Container([2, 0], 15, 'UNUSED'),
#         Container([3, 0], 20, 'USED')
#     ]
    
    
#     global MANIFEST
#     original_manifest = MANIFEST
#     MANIFEST = mock_manifest
    
    
#     start_state = State()
#     start_state.init_start_state()
    
    
#     load_list = [c for c in mock_manifest if c.get_description() == 'UNUSED']
    
    
#     result_state = load(start_state, load_list)
    
    
#     assert result_state is not None, "Load function should return a state"
#     assert len(load_list) == 0, "All containers should be loaded"
    
    
#     result_state.print_state_representation()
    
    
#     MANIFEST = original_manifest

#     print("Load test completed successfully!")


# test_load()


