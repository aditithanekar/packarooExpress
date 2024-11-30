import main
from state import State
from utils import parseManifest
from main import load



#TESTING THE LOAD FUNCTION------------------------------------------------------------------------------------------------------------

#create a starting state
state = State()
updated_state = state.init_start_state()

#define the manifest
MANIFEST = parseManifest("sampleManifest.txt")


load(updated_state, MANIFEST)