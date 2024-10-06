import search
import numpy as np
import ast
###xdazasd
class BAProblem(search.Problem):
    def __init__(self):
        # global variables initialization
        self.initial = None
        self.config = None
        self.berth_size = None
        self.berths = None
        self.vessels = []

    def load(self, fh):
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
                print(self.berth_size)
                print(N)
                continue
            
            # Process the next N lines for details on each vessel
            if N > 0:
                vessel_info = list(map(int, line.split()))
                self.vessels.append(vessel_info)
                N -= 1

        # Initialize berths once all vessels have been processed
        self.berths = [[] for _ in range(self.berth_size)]

        # Initial state: convert berths and vessels to tuples for immutability
        self.initial = self.hashable_state((tuple(map(tuple, self.berths)), tuple(self.vessels)))


    def hashable_state(self, state):
        """Convert state to a hashable representation."""
        berths, vessels = state
        # Convert lists to tuples
        return (tuple(map(tuple, berths)), tuple(map(tuple, vessels)))  # Convert to hashable tuples


    ## Parte 2
    def result(self, state, action):
        """Returns the new state resulting from applying the given action to the current state."""
        berths, vessels = state  # Unpack the state tuple
        new_berths = [list(berth) for berth in berths]  # Deep copy of berth availability
        new_vessels = list(vessels)  # Deep copy of remaining vessels

        if action[0] == "process":
            berth_index, start_time, vessel_index = action[1], action[2], action[3]
            
            vessel = new_vessels[vessel_index]
            processing_time = vessel[1]
            size = vessel[2]
            
            for i in range(size):
                new_berths[berth_index + i].append((start_time, start_time + processing_time))
            
            new_vessels.pop(vessel_index)  # Remove the scheduled vessel
        
        elif action[0] == "wait":
            # No changes to the state if the vessel is waiting
            pass
        
        # Return new state as a tuple
        return self.hashable_state((tuple(map(tuple, new_berths)), tuple(new_vessels)))


    def actions(self, state):
        """Returns the list of actions that can be executed in the given state."""
        available_actions = []
        berths, vessels = state  # Unpack the state tuple
        vessels = list(vessels)  # Convert to a mutable list

        # Iterate through each unscheduled vessel
        for vessel_index, vessel in enumerate(vessels):
            arrival_time, processing_time, size = vessel[0], vessel[1], vessel[2]

            # Check all possible start times from the vessel's arrival time
            for start_time in range(arrival_time, 100):  # Assuming 100 is the max time limit
                # Try to assign the vessel to the required contiguous berths
                for berth_index in range(self.berth_size - size + 1):  # Ensure enough contiguous berths
                    if self.berth_is_available(berth_index, start_time, processing_time, size, berths):
                        # If available, add the "process" action
                        available_actions.append(("process", berth_index, start_time, vessel_index))

            # If no "process" action is available, we can only "wait"
            if not any(action[0] == "process" and action[3] == vessel_index for action in available_actions):
                available_actions.append(("wait", vessel_index))
        print("Available actions: ", available_actions)
        return available_actions


    def berth_is_available(self, berth_index, start_time, processing_time, size, berths):
        #print("Entrou no berth_is_available\n")
        # Check if all berths from berth_index to berth_index + size - 1 are free
        for i in range(size):
            berth = berths[berth_index + i]
            # Check for overlaps with existing scheduled vessels
            for occupied_time in berth:
                if start_time < occupied_time[1] and start_time + processing_time > occupied_time[0]:
                    return False  # There is an overlap, so this berth is not available
        return True  # All berths are available


    def goal_test(self, state):
        print("Entrou no goal_test\n")
        """Returns True if all vessels have been scheduled."""
        _, vessels = state  # Unpack the state tuple
        print("Number of vessels: ", len(vessels))
        print("Vessels: ", vessels)
        return len(vessels) == 0  # True if no remaining vessels


    def path_cost(self, c, state1, action, state2):
        #print("Entrou no path_cost\n")
        """Calculate the cost of the path from state1 to state2 via action."""
        new_cost = c
        if action[0] == "process":
            berth_index, start_time, vessel_index = action[1], action[2], action[3]
            
            vessel = state2[1][vessel_index]  # Access vessels from the new state tuple
            arrival_time = vessel[0]
            processing_time = vessel[1]
            weight = vessel[3]
            
            departure_time = start_time + processing_time
            flow_time = departure_time - arrival_time
            weighted_flow_time = flow_time * weight
            
            new_cost += weighted_flow_time
        
        return new_cost


    def solve(self):
        print("Entrou no solve\n")
        """Calls the uniform_cost_search method from the search module.
        Returns a solution using the specified format."""
        
        # Call the uniform_cost_search method from the search module
        solution_node = search.uniform_cost_search(self)
        
        # Check if a solution was found
        if solution_node is None:
            print("No solution found.")
            return None

        # Extract the solution (actions) from the solution node
        solution = solution_node.solution()  # This gives the list of actions that led to the goal
        
        # Print the solution actions (how vessels were scheduled)
        print("\nSolution Actions: ", solution)
        
        # Extract the final path cost from the solution node (total weighted flow time)
        total_cost = solution_node.path_cost
        print("\nTotal Cost (Weighted Flow Time): ", total_cost)
        
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
    baproblem = BAProblem()
    input_file_path = 'Tests/ey100.dat'  # Adjust the path as needed

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


if __name__=='__main__':
    main()