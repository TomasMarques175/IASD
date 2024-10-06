import search
import numpy as np
import ast

class BAProblem(search.Problem):
    def __init__(self):
        # global variables initialization
        self.initial = None
        self.config = None
        self.berth_size = None
        self.vessel_size = None
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
        berth_array[2]=1
        vessels_array = np.zeros(self.vessel_size)
        time = 0

        for i in range(len(vessels_array)):
            if self.vessels[i][0] == time:
                    vessels_array[i] = -1
            else:
                vessels_array[i] = -2

        # Initial state: convert berths and vessels to tuples for immutability
        self.initial = tuple((tuple(berth_array), tuple(vessels_array), time))

        self.weights = [row[3] for row in self.vessels]


    ## Parte 2
    def result(self, state, action):
        """Returns the new state resulting from applying the given action to the current state."""
        return action


    def actions(self, state):
        print("State: ", state)
        """Returns the list of actions that can be executed in the given state."""
        action_list = []
        # Extract the current state information
        berth_array, vessels_array, time = state
        
        # Calculate the cost of the action

        berth_spaces = self.find_berth_spaces(state)

        for berth_index, berth_size in berth_spaces:
            print("berth_index: ", berth_index)
            print("berth_size: ", berth_size)
            for berth_index in range(berth_size):
                print("\tberth_index: ", berth_index)
                for vessel_index in range(self.vessel_size):
                    print("\t\tvessel_index: ", vessel_index)
                    vessel_copy = list(vessels_array)
                    if vessel_copy[vessel_index] != -1:
                        continue
                    if (berth_size - berth_index) >= self.vessels[vessel_index][2]:
                        # Create a new state based on the action
                        # Actualizes the vessel array with a possible vessel mooring
                        berth_copy = list(berth_array)
                        for berth_index_copy in range(berth_size - berth_index):
                            print("\t\t\tberth_copy[berth_index_copy]: ", berth_copy[berth_index_copy])
                            print("\t\t\tself.vessels[vessel_index][1]: ", self.vessels[vessel_index][1])
                            berth_copy[berth_index_copy] = self.vessels[vessel_index][1]
                        vessel_copy[vessel_index] = self.vessels[vessel_index][1]
                        new_state = tuple((tuple(berth_copy), tuple(vessel_copy), time))
                        action_list.append(new_state)
                        print("\t\tNew State: ", new_state)

        berth_copy = list(berth_array)
        vessel_copy = list(vessels_array)
        # Remove one in every value of berth_copy
        for i in range(len(berth_copy)):
            if berth_copy[i] != 0:
                berth_copy[i] -= 1

        for i in range(len(vessel_copy)):
            if vessel_copy[i] == -2:
                if self.vessels[i][0] == time + 1:
                    vessel_copy[i] = -1
            elif vessel_copy[i] > 0:
                vessel_copy[i] -= 1
        
        new_state = tuple((tuple(berth_copy), tuple(vessel_copy), time+1))
        action_list.append(new_state)
        print("New State: ", new_state)
        return tuple(action_list)


    # comentar
    def find_berth_spaces(self, state):
        berth_array, vessels_array, time = state
        berth_spaces = []
        berth_index = -1
        print("Berth Array: ", berth_array)
        for i in range(self.berth_size):
            if berth_array[i] == 0 and berth_index == -1:
                berth_index = i
            if berth_array[i] != 0 and berth_index != -1:
                berth_spaces.append((berth_index, i - berth_index))
                berth_index = -1
            if berth_array[i] == 0 and i == self.berth_size - 1:
                if  berth_index != -1:
                    berth_spaces.append((berth_index, i - berth_index + 1))
                    berth_index = -1
                else:
                    berth_spaces.append((i, 1))

        print("Berth Spaces: ", berth_spaces)
        return berth_spaces


    def goal_test(self, state):
        print("Entrou no goal_test\n")
        print("State: ", state)
        berth_array, vessels_array, time = state
        mask = (np.array(vessels_array) != 0)
        if np.sum(mask) == 0:
            return True
        else:
            return False


    def path_cost(self, c, state1, action, state2):
        print("Entrou no path_cost\n")
        berth_array1, vessels_array1, time1 = state1
        berth_array2, vessels_array2, time2 = state2
        # Check what vessels left in state2 and create a mask for the one who dind't 
        # Search for 2's in an array
        mask = (np.array(vessels_array2) != -2) & (np.array(vessels_array2) != 0)
        # Calculate the cost of the action
        weighted_time = np.sum(self.weights*mask)*(time2 - time1)
        return c + weighted_time


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
        solution_actions = solution_node.solution()  # This gives the list of actions that led to the goal
        solution = [[0, 0] for _ in range(self.vessel_size)]
        # Print the solution actions (how vessels were scheduled)
        print("\nSolution Actions: ", solution_actions)
        for berth_array, vessels_array, time in solution_actions:
            if (berth_copy == None):
                berth_copy = berth_array
                vessels_copy = vessels_array
            for j in range(self.berth_size):
                if (berth_copy[i] != berth_array[i]) and berth_copy[i] == 0:
                    for i in range(len(vessels_array)):
                        #checkar se colocou um vessel nesta ação
                        if (vessels_copy[i] != vessels_array[i]) and vessels_copy[i] == -1:
                                vessels_array[i] = -1
                                solution[i][0]=j
                                solution[i][1]=time
                                continue




        # Extract the final path cost from the solution node (total weighted flow time)
        total_cost = solution_node.path_cost
        print("\nTotal Cost (Weighted Flow Time): ", total_cost)

        # Return the final path based on the solution given by the algorithm
        #TODO: This is just a placeholder, replace with the actual solution
        
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