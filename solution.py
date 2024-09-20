import search
import numpy as np
import ast

class BAProblem(search.Problem):
    def __init__(self):
        self.initial = None
        self.config = None
        self.berth_size = None
        self.vessels = []

    def load(self, fh):
        N = None
        
        # Read the file line by line
        with open(fh, 'r') as file:
            for line in file:
                line = line.strip()
                
                # Ignore empty lines and comment lines
                if not line or line.startswith('#'):
                    continue
                
                # The first non-comment line should contain S and N
                if self.berth_size is None and N is None:
                    self.berth_size, N = map(int, line.split())
                    continue
                
                # Process the next N lines for vessel details
                if N > 0:
                    vessel_info = list(map(int, line.split()))
                    self.vessels.append(vessel_info)
                    N -= 1

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
            # Extract the vessel's parameters from self (assuming self.vessels exists)
            arrival_time = self.vessels[i][0] # arrivaltime
            processing_time = self.vessels[i][1] # proccessing time
            weight = self.vessels[i][3] # weight
            
            # Calculate the flow time
            flow_time = (mooring_time + processing_time) - arrival_time
            
            # Calculate the weighted flow time for this vessel
            total_cost += flow_time * weight
            print(f"Total Cost: {total_cost}")
        # Return the total cost 
        return total_cost

    def check(self, sol):
        # Creates a list with berth size
        vessels_times = [[] for _ in range(self.berth_size)]
        for i in range(len(sol)):
            # Checks if the mooring time in the output comes before the arrival time
            if sol[i][0] < self.vessels[i][0]:
                # print("Mooring time is less than arrival time")
                return False
            
            # Checks if the last last berth utilized is greater than the berth size
            if sol[i][1]+self.vessels[i][2] > self.berth_size:
                return False
            
            for berth_index in range(self.vessels[i][2]):
                for j in vessels_times[sol[i][1]+berth_index]:
                    if (
                        j != None
                        and
                        (
                        (sol[i][0] >= j[0] and sol[i][0] <= j[1]) 
                        or 
                        (sol[i][0]+self.vessels[i][1]-1 >= j[0] and sol[i][0]+self.vessels[i][1]-1 <= j[1])
                        )
                        or
                        (sol[i][0] <= j[0] and sol[i][0]+self.vessels[i][1]-1 >= j[1])
                        ):
                        return False
                times = [sol[i][0],sol[i][0]+self.vessels[i][1]-1]
                vessels_times[sol[i][1]+berth_index].append(times)
        return True

def main():

    baproblem = BAProblem()
    baproblem.load('Tests\ex100.dat')
    print(baproblem.berth_size)
    print(baproblem.vessels)
    sol = baproblem.load_sol('Tests\ex100.plan')
    print(sol)
    # baproblem.check(baproblem.config, baproblem.sol)
    total_cost = baproblem.cost(sol)
    check_bool = baproblem.check(sol)
    print(check_bool)

    # Print the total cost
    print(f"Total Cost: {total_cost}")
if __name__=='__main__':
    main()