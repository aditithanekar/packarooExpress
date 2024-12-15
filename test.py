import main
from state import State
from container import Container
import utils
from load_unload import load
from load_unload import unload
import load_unload
import unittest
from balance2 import ShipBalancer

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


class ShipTests(unittest.TestCase):
    def setUp(self):
        
        self.manifest = utils.parseManifest("test_cases/ShipCase1.txt")
        self.initial_state = State()
        self.initial_state = self.initial_state.init_start_state(self.manifest)

    def test_initial_state(self):
        """Test that the initial state is loaded correctly"""
        
        state_rep = self.initial_state.state_representation
        
       
        self.assertIsInstance(state_rep[0][0], Container)
        self.assertEqual(state_rep[0][0].description, "NAN")
        
        
        self.assertIsInstance(state_rep[0][1], Container)
        self.assertEqual(state_rep[0][1].description, "Cat")
        self.assertEqual(state_rep[0][1].weight, 99)
        
        
        self.assertIsInstance(state_rep[0][2], Container)
        self.assertEqual(state_rep[0][2].description, "Dog")
        self.assertEqual(state_rep[0][2].weight, 100)

    def test_unload_cat(self):
        """Test unloading the Cat container"""
        target = Container([1,2], 99, "Cat")
        unload_targets = [target]
        
        
        unloaded_state, trace, blocking_containers = unload(self.initial_state, unload_targets, (8,0))
        
       
        state_rep = unloaded_state.state_representation
        found_cat = False
        for row in state_rep:
            for container in row:
                if container and container.description == "Cat":
                    found_cat = True
                    break
        
        self.assertFalse(found_cat, "Cat container should be removed")
        self.assertEqual(len(blocking_containers), 0, "No containers should be blocking Cat")

    def test_load_new_containers(self):
        """Test loading new containers onto the ship"""
        
        new_containers = [
            Container(position=None, weight=150, description="Box1"),
            Container(position=None, weight=200, description="Box2")
        ]
        
        
        loaded_state, operations = load(self.initial_state, new_containers)
        
        
        state_rep = loaded_state.state_representation
        found_containers = []
        for row in state_rep:
            for container in row:
                if container and container.description in ["Box1", "Box2"]:
                    found_containers.append(container.description)
        
        self.assertEqual(len(found_containers), 2, "Both containers should be loaded")
        self.assertIn("Box1", found_containers)
        self.assertIn("Box2", found_containers)

    

    def test_invalid_unload(self):
        """Test attempting to unload a non-existent container"""
        target = Container([1,1], 999, "NonExistent")
        unload_targets = [target]
        
        with self.assertRaises(ValueError):
            unload(self.initial_state, unload_targets, (8,0))


class EmptyOperationsTest(unittest.TestCase):
    def setUp(self):
        
        self.manifest = utils.parseManifest("test_cases/ShipCase1.txt")
        self.initial_state = State()
        self.initial_state = self.initial_state.init_start_state(self.manifest)

    def test_empty_load(self):
        """Test loading with an empty list of containers"""
        containers_to_load = []  # Empty load list
        
        
        loaded_state, operations = load(self.initial_state, containers_to_load)
        
        
        self.assertEqual(
            self.initial_state.state_representation, 
            loaded_state.state_representation,
            "State should remain unchanged when loading empty list"
        )
        
        
        self.assertEqual(len(operations), 1, "Operations should only contain initial position")
        self.assertEqual(operations[0], [8,0], "Initial position should be [8,0]")

    def test_empty_unload(self):
        """Test unloading with an empty list of target containers"""
        unload_targets = []  
        
        
        unloaded_state, trace, blocking_containers = unload(self.initial_state, unload_targets, (8,0))
        
        
        for row1, row2 in zip(self.initial_state.state_representation, unloaded_state.state_representation):
            for container1, container2 in zip(row1, row2):
                if container1 is None and container2 is None:
                    continue
                self.assertEqual(
                    container1.description,
                    container2.description,
                    "Container descriptions should match"
                )
                self.assertEqual(
                    container1.weight,
                    container2.weight,
                    "Container weights should match"
                )
        
        
        self.assertEqual(len(trace), 0, "Trace should be empty")
        self.assertEqual(len(blocking_containers), 0, "No blocking containers should be found")

    def test_empty_operations_time(self):
        """Test that empty operations don't add unnecessary time"""
        
        initial_time = self.initial_state.time
        
        
        containers_to_load = []
        loaded_state, _ = load(self.initial_state, containers_to_load)
        
        
        self.assertEqual(
            initial_time,
            loaded_state.time,
            "Time should not increase for empty load operation"
        )
        
        
        unload_targets = []
        unloaded_state, _, _ = unload(loaded_state, unload_targets, (8,0))
        
        
        self.assertEqual(
            initial_time,
            unloaded_state.time,
            "Time should not increase for empty unload operation"
            
        )
class EmptyBalanceTest(unittest.TestCase):
    def setUp(self):
        # Initialize with manifest that's basically empty (just NANs in corners)
        self.manifest = utils.parseManifest("test_cases/ShipCase1.txt")  # This has just NAN corners and Cat/Dog
        self.initial_state = State()
        self.initial_state = self.initial_state.init_start_state(self.manifest)
        

    def test_single_container_balance(self):
        """Test balancing with just one container"""
        # Load a single container in an unbalanced position
        containers = [Container([2,1], 100, "Box1")]  # Single container on left side
        
        state = State()
        new_manifest = self.manifest.copy()
        new_manifest.extend(containers)
        state = state.init_start_state(new_manifest)
        
        balancer = ShipBalancer("test_cases/ShipCase1.txt")  # Path doesn't matter as we pass state directly
        optimal_moves, final_state = balancer.balance_ship()
        
        # Should suggest moving container towards center for balance
        self.assertGreater(len(optimal_moves), 0, "Single container should need balancing")


    def get_container_positions(self, state):
        """Helper method to get container positions for comparison"""
        positions = {}
        for row_idx, row in enumerate(state.state_representation):
            for col_idx, container in enumerate(row):
                if container and not container.IsNAN and not container.IsUNUSED:
                    positions[(row_idx, col_idx)] = {
                        'weight': container.weight,
                        'description': container.description
                    }
        return positions

    def test_no_valid_moves_possible(self):
        """Test when no valid moves are possible for balancing"""
        # Create a state where containers can't be moved (e.g., surrounded by NANs)
        containers = [Container([2,1], 1000, "HeavyBox")]  # Very heavy box that can't be balanced
        
        state = State()
        new_manifest = self.manifest.copy()
        new_manifest.extend(containers)
        state = state.init_start_state(new_manifest)
        
        balancer = ShipBalancer("test_cases/ShipCase1.txt")
        optimal_moves, final_state = balancer.balance_ship()
        
        # Should handle the impossible balance case gracefully
        self.assertIsNotNone(final_state, "Should return a final state even if balance is impossible")

class ShipTests(unittest.TestCase):
    def setUp(self):
        self.states = {}
        for case in ["ShipCase2", "ShipCase3", "ShipCase4", "ShipCase5", "SilverQueen"]:
            manifest = utils.parseManifest(f"test_cases/{case}.txt")
            state = State()
            self.states[case] = state.init_start_state(manifest)

    def test_shipcase2(self):
        state = self.states["ShipCase2"]
        target = Container([1,4], 120, "Ram")
        unloaded_state, trace, blocking = unload(state, [target], (8,0))
        self.assertFalse(self.find_container(unloaded_state, "Ram"))
        self.assertTrue(self.find_container(unloaded_state, "Owl"))
        self.assertTrue(self.find_container(unloaded_state, "Dog"))

    def test_shipcase3(self):
        state = self.states["ShipCase3"]
        target = Container([1,1], 10001, "Ewe")
        unloaded_state, trace, blocking = unload(state, [target], (8,0))
        self.assertFalse(self.find_container(unloaded_state, "Ewe"))
        self.assertTrue(self.find_container(unloaded_state, "Cat"))

    def test_shipcase4(self):
        state = self.states["ShipCase4"]
        target = Container([4,5], 2011, "Cow")
        unloaded_state, trace, blocking = unload(state, [target], (8,0))
        self.assertFalse(self.find_container(unloaded_state, "Cow"))
        self.assertTrue(len(blocking) > 0)

    def test_shipcase5(self):
        state = self.states["ShipCase5"]
        target = Container([1,6], 1, "Rat")
        unloaded_state, trace, blocking = unload(state, [target], (8,0))
        self.assertFalse(self.find_container(unloaded_state, "Rat"))
        self.assertTrue(self.find_container(unloaded_state, "Cat"))

    def test_silverqueen(self):
        balancer = ShipBalancer("test_cases/SilverQueen.txt")
        moves, final_state = balancer.balance_ship()
        for move in moves:
            self.assertTrue(0 <= move[0][0] < 8 and 0 <= move[0][1] < 12)
            self.assertTrue(0 <= move[1][0] < 8 and 0 <= move[1][1] < 12)

    def find_container(self, state, name):
        for row in state.state_representation:
            for container in row:
                if container and container.description == name:
                    return True
        return False

    

if __name__ == '__main__':
    unittest.main()