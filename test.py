import main
from state import State
from container import Container
from utils import parseManifest
from main import load
from balance2 import a_star



#TESTING THE LOAD FUNCTION------------------------------------------------------------------------------------------------------------
#define the manifest
MANIFEST = parseManifest("sampleManifest.txt")

#create a starting state
state = State()
updated_state = state.init_start_state(MANIFEST)


def adititest():
    updated_state.print_state_representation()
    
    result_state = a_star(updated_state)
    result_state.print_state_representation()

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

# #USING ACTUAL MANIFEST------------------------------------------------------------------------------------------------------------

# def manifest_test_load():
    
#     start_state = State()
#     start_state.init_start_state()
    
    
#     load_list = [c for c in MANIFEST if c.get_description() == 'UNUSED']
    
    
#     print("Initial Load List:")
#     for c in load_list:
#         print(c.print_node_description())
    
#     print("\nInitial State:")
#     start_state.print_state_representation()
    
    
#     result_state = load(start_state, load_list)
    
    
#     assert result_state is not None, "Load function should return a state"
#     assert len(load_list) == 0, "All containers should be loaded"
    
    
#     print("\nFinal State:")
#     result_state.print_state_representation()
    
#     print("Load test 2 completed successfully!")


# manifest_test_load()