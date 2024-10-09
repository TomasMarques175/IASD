import search
import numpy as np
import ast
from datetime import datetime

class State:
    def __init__(self, berth_array, vessels_array, time):
        self.berth_array = tuple(berth_array)  # Tuples are immutable
        self.vessels_array = tuple(vessels_array)
        self.time = time

        self.unique = time
        for index in range(max(len(berth_array), len(vessels_array))):
            if index < len(berth_array):
                self.unique += berth_array[index]*(100**(index + 1))
            if index < len(vessels_array):
                self.unique += (2 + vessels_array[index])*(100**(index+len(berth_array)+1))

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
        return f"State(berths={self.berth_array}, vessels={self.vessels_array}, time={self.time})"

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

        berth_array = np.zeros(self.berth_size)
        vessels_array = np.zeros(self.vessel_size)
        time = 0

        for i in range(len(vessels_array)):
            if self.vessels[i][0] == time:
                    vessels_array[i] = -1
            else:
                vessels_array[i] = -2

        # Initial state: convert berths and vessels to tuples for immutability
        self.initial = State(berth_array, vessels_array, time)

        self.weights = [row[3] for row in self.vessels]
        vessel_sizes = [vessel[2] for vessel in self.vessels]
        # Find the minimum size
        self.min_vessel_size = min(vessel_sizes)

    ## Parte 2
    def result(self, state, action):
        """
        Updates the state based on the action taken. 
        If vessel_index == -1, it updates based on time.
        Otherwise, it updates based on the specified vessel and berth index.

        Args:
        - state: A tuple containing (berth_array, vessels_array, time).
        - action: A tuple (vessel_index, berth_index).

        Returns:
        - new_state: The updated state after the action is applied.
        """
        berth_array = state.berth_array
        vessels_array = state.vessels_array
        time = state.time
        vessel_index, berth_index = action

        # Create copies of the arrays
        berth_copy = list(berth_array)
        vessel_copy = list(vessels_array)

        if vessel_index == -1:
            # If vessel_index is -1, update the state based on time
            # Remove one from every non-zero value in berth_copy
            for i in range(len(berth_copy)):
                if berth_copy[i] != 0:
                    berth_copy[i] -= 1

            # Update vessel_copy based on time and current values
            for i in range(len(vessel_copy)):
                if vessel_copy[i] == -2:
                    if self.vessels[i][0] == time + 1:
                        vessel_copy[i] = -1
                elif vessel_copy[i] > 0:
                    vessel_copy[i] -= 1
            # Create the new state with updated values
            new_state = State(berth_copy, vessel_copy, time + 1)
        else:
            # If vessel_index is valid, update based on the specified vessel
            # Update the berth array for the specified vessel
            for berth_index_copy in range(self.vessels[vessel_index][2]):
                berth_copy[berth_index_copy + berth_index] = self.vessels[vessel_index][1]

            # Update the vessel array for the specified vessel
            vessel_copy[vessel_index] = self.vessels[vessel_index][1]

            # Create the new state with updated values
            new_state = State(berth_copy, vessel_copy, time)

        return new_state

    def actions(self, state):
        """Returns the list of actions that can be executed in the given state."""
        action_list = []
        # Extract the current state information
        vessels_array= state.vessels_array
        berth_spaces = self.find_berth_spaces(state)

        for vessel_index in range(self.vessel_size):
            if vessels_array[vessel_index] != -1:
                continue
            for berth_index, berth_size in berth_spaces:
                if (berth_size < self.vessels[vessel_index][2]):
                    continue
                for berth_index1 in range(berth_size):
                    if (berth_size - berth_index1) < self.vessels[vessel_index][2]:
                        break
                    new_action = (vessel_index, berth_index + berth_index1)
                    action_list.append(new_action)

        new_action = (-1, 1)
        action_list.append(new_action)

        return tuple(action_list)

    def find_berth_spaces(self, state):
        berth_array = state.berth_array 
        berth_spaces = []
        berth_index = -1
        i = 0
        while i < self.berth_size:
            if berth_array[i] == 0:  # Found an occupied berth
                start_index = i
                count = 0

                # Count contiguous occupied berths
                while i < self.berth_size and berth_array[i] == 0:
                    count += 1
                    i += 1

                # Add the start index and the number of contiguous occupied berths
                berth_spaces.append((start_index, count))
            else:
                i += 1
        return berth_spaces

    def goal_test(self, state):
        """Returns True if the state is a goal"""
        vessels_array = state.vessels_array  
        mask = (np.array(vessels_array) != 0)
        if np.sum(mask) == 0:
            return True
        else:
            return False

    def path_cost(self, c, state1, action, state2):
        vessels_array1 = state1.vessels_array
        time1 = state1.time
        vessels_array2 = state2.vessels_array
        time2 = state2.time
        # Check what vessels left in state2 and create a mask for the one who dind't 
        
        if time1 == time2:
            return c

        mask = (np.array(vessels_array1) != -2) & (np.array(vessels_array1) != 0)
        
        # Calculate the cost of the action
        total_cost = c + np.sum(self.weights*mask)*(time2 - time1)
        #print("Total cost2: " + str(total_cost))
        """ if time1 != time2:
            self.debug_print("Total cost: " + str(total_cost))
            self.debug_print("Mask: " + str(mask))
            self.debug_print("vessel 1: " + str(vessels_array1) + "\nVessel 2:" + str(vessels_array2))
            self.debug_print("Weighted time: " + str(self.weights)) """

        return total_cost

    def solve(self):
        # Call the uniform_cost_search method from the search module
        
        solution_node = search.uniform_cost_search(self)
        # solution_node = search.depth_limited_search(self)

        # Extract the solution (actions) from the solution node
        solution_actions = solution_node.solution()  # This gives the list of actions that led to the goal
        solution = [[-1, -1] for _ in range(self.vessel_size)]

        time=0
        for vessels_index, birth_index in solution_actions:
            if(vessels_index == -1):
                time+=1
            else:
                solution[vessels_index][0]=time
                solution[vessels_index][1]=birth_index

        # Extract the final path cost from the solution node (total weighted flow time)
        total_cost = solution_node.path_cost
        return solution

    ## Parte 1
    def load_sol(self, fhs):
        with open(fhs, 'r') as file:
            # Read the line from the .plan file
            line = file.readline().strip()
            # Convert the string representation of the list to an actual list using ast.literal_eval
            tuple_list = ast.literal_eval(line)
            # Convert each tuple into a NumPy array
            sol = [np.array(t) for t in tuple_list]
        return tuple_list

    def cost(self, sol):
        total_cost = 0
        
        # Iterate through each vessel in the solution
        for i, (mooring_time, _) in enumerate(sol):
            # Extract the vessel's parameters from self
            arrival_time = self.vessels[i][0] # arrival time
            processing_time = self.vessels[i][1] # proccessing time
            weight = self.vessels[i][3] # weight
            
            # Calculate the flow time
            flow_time = (mooring_time + processing_time) - arrival_time
            
            # Calculate the total cost for this vessel and sum it 
            total_cost += flow_time * weight
        # Return the total cost 
        return total_cost

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

    if solution:
        print("\nSolution actions:", solution)
    else:
        print("\nNo solution was found.")

    # End time
    end_time = datetime.now()

    # Calculate the elapsed time
    elapsed_time = end_time - start_time
    print(f"Execution time: {elapsed_time}\n")


if __name__=='__main__':
    main()