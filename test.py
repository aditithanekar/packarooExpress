import main
from state import State
from container import Container
import utils
from load_unload import load
import load_unload

##### TIME AND TRACE IMPLEMENTATION #######################################################################

MANIFEST = utils.parseManifest("test_cases/ShipCase3.txt")

state = State()
state = state.init_start_state(MANIFEST)
state.print_state_representation()

# UNLOADING
target = Container([1,0], 99, "Cow")
unload_targets = [target]
unloaded_state, trace, blocking_containers = load_unload.unload(state, unload_targets, (8,0))
    # unload() now returns a state, a trace without blocking containers, and a list of blocking containers
use_this_trace, time = load_unload.unload_time_trace(unloaded_state, trace, blocking_containers)
    # unload_time_trace() returns a total time and a list of pairs of coordinates showing old&new location of each container moved (unloaded containers AND moving blocking containers)
print(use_this_trace)
print("Total unload time = ", time)

# LOADING
containers = [Container(position=None, weight=10.0 + i, description=f"Box{i}") for i in range(2)]
loaded_state, operations = load(unloaded_state, containers)
print(operations) # operations is a list of coordinates where each container was loaded (IGNORE THE FIRST ONE, ITS JUST 8,0)

loaded_state.print_state_representation()
print(loaded_state.time)

utils.updateMaifest(loaded_state, "updatedManifest.txt")

# BALANCE (TIME)
balance_input = [((0, 3), (0, 4), 1), ((0, 4), (0, 5), 1), ((0, 2), (1, 2), 1), ((0, 1), (0, 2), 1), ((0, 2), (0, 3), 1), ((0, 3), (0, 4), 1), ((0, 4), (1, 4), 1), ((1, 4), (1, 5), 1), ((1, 5), (1, 6), 1)]
def get_balance_time(balance_input):
    first_start = balance_input[0][0]
    total_cost = (8 - first_start[0]) + first_start[1]
    
    for i in range(len(balance_input)):
        total_cost += balance_input[i][2]
        if i < len(balance_input) - 1:
            current_end = balance_input[i][1]
            next_start = balance_input[i + 1][0]
            total_cost += abs(current_end[0] - next_start[0]) + abs(current_end[1] - next_start[1])

    last_end = balance_input[-1][1]
    total_cost += (8 - last_end[0]) + last_end[1]

    return total_cost

print(get_balance_time(balance_input))
#################################################################################################################################