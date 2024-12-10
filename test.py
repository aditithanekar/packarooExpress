import main
from state import State
from container import Container
import utils
from main import load



#TESTING THE LOAD FUNCTION------------------------------------------------------------------------------------------------------------
#define the manifest
MANIFEST = utils.parseManifest("sampleManifest.txt")

#create a starting state
state = State()
updated_state = state.init_start_state(MANIFEST)



# SUHANI TESTING STUFF ===============================================================================================
updated_state.print_state_representation()

containers = [Container(position=None, weight=10.0 + i, description=f"Container {i}") for i in range(11)]
for container in containers:
    print(container.print_node_description())
    
end_state, operations = load(updated_state, containers)
        # operations is where the crane ends after loading each container

utils.updateMaifest(end_state, "updatedManifest.txt")
NEW_MANIFEST = utils.parseManifest("updatedManifest.txt")
state = State()
updated_state = state.init_start_state(NEW_MANIFEST)
updated_state.print_state_representation()

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