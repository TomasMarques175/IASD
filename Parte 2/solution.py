import search
import numpy as np
import ast
from datetime import datetime

class State:
    def __init__(self, solution):
        self.solution = tuple(solution)  # Tuples are immutable
        self.unique = 0
        for index in range(len(solution)):
            self.unique += (1 + solution[index][0]) * (100 ** index)
            self.unique += (1 + solution[index][1]) * (100 ** (index + len(solution)))
        
        self._hash = hash(self.unique)

    def __eq__(self, other):
        """Overrides the default implementation of equality."""
        return self._hash == other._hash
        #return self.berth_array == other.berth_array and self.vessels_array == other.vessels_array and self.time == other.time

    def __hash__(self):
        """Overrides the default implementation to allow hashing."""
        return self._hash

    def __repr__(self):
        """For debugging purposes, returns a string representation of the state."""
        return "State(berths={self.solution})"

    def __lt__(self, other):
        # Compare states based on time, or some other criteria for PriorityQueue
        return True

class BAProblem(search.Problem):
    def __init__(self):
        # global variables initialization
        self.initial = None
        self.config = None
        self.berth_size = None
        self.vessel_size = None
        self.berths = None
        self.vessels = []
        self.debug_mode = False  # Set this to False to disable debug prints

    def debug_print(self, message):
        """Prints a message if debug_mode is enabled."""
        if self.debug_mode:
            print(message)

    def load(self, fh):
        """Loads a BAP problem from the file object fh.
        It may initialize self.initial here"""

        N = None

        # Read the file line by line
        for line in fh:
            line = line.strip()
            # Ignore empty lines and comment lines
            if not line or line.startswith('#'):
                continue
            
            # The first non-comment line should contain berth size and number of vessels
            if self.berth_size is None and N is None:
                self.berth_size, N = map(int, line.split())
                self.vessel_size = N
                continue

            # Process the next N lines for details on each vessel
            if N > 0:
                vessel_info = list(map(int, line.split()))
                self.vessels.append(vessel_info)
                N -= 1

        # Initialize berths once all vessels have been processed
        self.berths = [[] for _ in range(self.berth_size)]


        # Create a list with (-1,-1) arrays with the size of the vessels
        solution = [[-1, -1] for _ in range(len(self.vessels))]

        # Initial state: convert berths and vessels to tuples for immutability
        self.initial = State(solution)

        self.weights = [row[3] for row in self.vessels]
        vessel_sizes = [vessel[2] for vessel in self.vessels]
        # Find the minimum size
        self.min_vessel_size = min(vessel_sizes)

    def result(self, state, action):
        vessel_index, time, berth_index = action

        solucao = [list(v) for v in state.solution]

        # Atualiza os valores com base na ação
        solucao[vessel_index][1] = berth_index  # Atualiza o indice do berth
        solucao[vessel_index][0] = time         # Atualiza o tempo

        # Retorna um novo objeto State com a solução modificada
        return State(solucao)

    def actions(self, state):
        """Returns the list of actions that can be executed in the given state."""
        action_list = []
        
        # Extract the current state information
        vessels_array = [list(v) for v in state.solution]  # Deep copy to avoid modifying the original state
        #self.debug_print("vessels_array: " + str(vessels_array) + "\n")
        for vessel_index in range(self.vessel_size):
            if vessels_array[vessel_index][1] != -1:  # Vessel already assigned, skip
                continue
            
            
            # Initialize vessel start time with its original value
            start_time = self.vessels[vessel_index][0]

            # Try assigning the vessel to a berth
            while True:
                #self.debug_print("State3: " + str(state.solution) + "\n")
                for berth_index in range(self.berth_size):
                    
                    # Check if this action is valid
                    if self.check_action(vessels_array, (vessel_index, start_time, berth_index)):
                        action_list.append((vessel_index, start_time, berth_index))
                        break  # Stop trying further berths for this vessel
                else:
                    # If no valid berth was found in this iteration, increment the start time
                    start_time += 1
                    continue  # Retry with new start time
                break  # Break the outer while when an action is found

        #self.debug_print("State4: " + str(state.solution) + "\n")
        return tuple(action_list)

    def check_action(self, solution, action):
        vessel_index, time, berth_index = action
        vessel_length = self.vessels[vessel_index][2]  # Get the size of the vessel
        vessel_mooring_time = self.vessels[vessel_index][1]  # Mooring time
        
        # Check if the vessel fits in the berth
        if self.berth_size - berth_index  < vessel_length:
            return False  # Vessel doesn't fit in the berth range

        for placed_vessel_index, (placed_time, placed_berth_index) in enumerate(solution):
            if placed_time == -1:
                continue  # Skip vessels that haven't been placed yet

            # Get the details of the already placed vessel
            placed_vessel_length = self.vessels[placed_vessel_index][2]
            placed_vessel_mooring_time = self.vessels[placed_vessel_index][1]

            # Time overlap check
            if not (time + vessel_mooring_time <= placed_time or placed_time + placed_vessel_mooring_time <= time):
                #print(solution)
                # Berth overlap check
                if not (berth_index + vessel_length <= placed_berth_index or placed_berth_index + placed_vessel_length <= berth_index):
                    # If both time and berth overlap, the action is not feasible
                    return False

        # If no conflicts, and the vessel fits, the action is feasible
        return True

    def goal_test(self, state):
        """Returns True if the state is a goal"""
        solution = state.solution

        for time, birth_index in solution:
            if(time == -1 | birth_index == -1):
                return False
        return True

    def path_cost(self, c, state1, action, state2):
        vessel_index, time, _ = action

        cost = self.weights[vessel_index]*(time-self.vessels[vessel_index][0]+self.vessels[vessel_index][1])
        # Calculate the cost of the action
        total_cost = c + cost
        #print("Total cost2: " + str(total_cost))

        return total_cost

    def solve(self):
        # Call the uniform_cost_search method from the search module
        
        solution_node = search.uniform_cost_search(self)
        # solution_node = search.depth_limited_search(self)

        # Extract the solution (actions) from the solution node
        solution_actions = solution_node.solution()  # This gives the list of actions that led to the goal
        solution = [[-1, -1] for _ in range(self.vessel_size)]
        self.debug_print("Solution actions: " + str(solution_actions) + "\n")

        # Remove the initial value from solution_actions for all arrays
        for action in solution_actions:
            vessel_index, time, berth_index = action
            # Atualiza a solução: o primeiro elemento é o tempo, o segundo é o índice do berço
            solution[vessel_index] = [time, berth_index]
        print(solution)
        self.debug_print("Final solution: " + str(solution) + "\n")
        # Extract the final path cost from the solution node (total weighted flow time)
        total_cost = solution_node.path_cost
        return solution

    def check(self, sol):
        # Creates a list with berth size
        vessels_times = [[] for _ in range(self.berth_size)]
        for i in range(len(sol)):
            # Checks if the mooring time in the output comes before the arrival
            # time
            if sol[i][0] < self.vessels[i][0]:
                return False
            
            # Checks if the last berth utilized by the vessel is greater than 
            # the berth size
            if sol[i][1]+self.vessels[i][2] > self.berth_size:
                return False
            
            # Checks each berth space utilized by the vessel
            # This is done by trying to fill all the birth time spaces
            for berth_index in range(self.vessels[i][2]):
                for j in vessels_times[sol[i][1]+berth_index]:
                    if (
                        # Checks if the berth is empty for all the time spaces
                        j != None
                        and
                        # Checks if the arrival time and departure time 
                        # intersect already ocupied times in this berth
                        (
                            (sol[i][0] >= j[0] and sol[i][0] <= j[1]) 
                            or 
                            (sol[i][0]+self.vessels[i][1]-1 >= j[0] and sol[i][0]+self.vessels[i][1]-1 <= j[1])
                        )
                        or
                        # Checks if the berth is being ocupied from arrival time 
                        # till it departures for this vessel
                        (
                            sol[i][0] <= j[0] and sol[i][0]+self.vessels[i][1]-1 >= j[1])
                        ):
                        return False
                # Updates the ocupied times for this berth space
                times = [sol[i][0],sol[i][0]+self.vessels[i][1]-1]
                vessels_times[sol[i][1]+berth_index].append(times)
        return True

def main():

    start_time = datetime.now()

    baproblem = BAProblem()
    input_file_path = 'Tests/ey109.dat'  # Adjust the path as needed

    try:
        with open(input_file_path, 'r') as file:
            baproblem.load(file)  # Load the data
    except FileNotFoundError:
        print(f"Error: The file '{input_file_path}' was not found.")
        return
    except IOError:
        print(f"Error: Could not read the file '{input_file_path}'. Check permissions.")
        return
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return

    # Proceed to solve the problem
    solution = baproblem.solve()

    # End time
    end_time = datetime.now()

    # Calculate the elapsed time
    elapsed_time = end_time - start_time
    print(f"Execution time: {elapsed_time}\n")


if __name__=='__main__':
    main()