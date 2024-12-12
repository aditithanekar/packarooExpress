import main
from state import State
from container import Container
import utils
from load_unload import load
import load_unload

MANIFEST = utils.parseManifest("ShipCase1.txt")

state = State()
state = state.init_start_state(MANIFEST)
state.print_state_representation()

containers = [Container(position=None, weight=10.0 + i, description=f"Box{i}") for i in range(11)]

loaded_state, operations = load(state, containers) # operations is for if printing steps is needed later
loaded_state.print_state_representation()

utils.updateMaifest(loaded_state, "updatedManifest.txt")
