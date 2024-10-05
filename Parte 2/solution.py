import search
import numpy as np
import ast

class BAProblem(search.Problem):
    def __init__(self):
        # global variables initialization
        self.initial = []
        self.config = None
        self.berth_size = None
        self.vessels = []

    ## Parte 2
    def result(self, state, action):
        """Returns the state that results from executing the given action
        in the given state"""
        # TODO: Implement this
        pass

    def actions(self, state):
        """Returns the list of actions that can be executed in the given
        state"""
        # TODO: Implement this

        # Ideia: Para um dado navio ver se ele pode ser alocado em todos os seus berços possíveis
        # Para isso, é necessário verificar se o berço está disponível para o navio em um dado tempo
        # Se estiver disponível, adicionar a ação à lista de ações disponíveis com todos os barcos que 
        # chegam depois desse tempo de processamento e todos os que chegaram antes e ainda n foram processados



        # state contains the current schedule (which berths are occupied at what times)
        available_actions = []
        berths = state['berths']  # Berth availability list
        vessels = state['remaining_vessels']  # Vessels to be scheduled

        for vessel in vessels:
            a_v = vessel['arrival_time']
            p_v = vessel['processing_time']
            s_v = vessel['size']

            for berth_index in range(len(berths)):
                # Check if the berth has enough contiguous free sections for the vessel size
                for start_time in range(a_v, max_time):
                    if berth_is_available(berth_index, start_time, p_v, s_v, berths):
                        # If the berth is available, add this as a valid action
                        available_actions.append((berth_index, start_time))
    
        return available_actions
    
    def goal_test(self, state):
        """Returns True if the state is a goal"""
        # TODO: Implement this
        pass
    
    def path_cost(self, c, state1, action, state2):
        """Returns the cost of a path that arrives at state2 from state1
        via action, assuming cost c to get up to state1"""
        print("c: ", c)
        print("state1: ", state1)
        print("precessing time: ", state1[2], "\n")
        # If the arrival time of the vessel in state2 is greater than the sum of the cost and the processing time of the vessel in state1
        if state2[0] > c + state1[1]:
            return state2[0]
        # Else, return the sum of the cost and the processing time of the vessel in state1
        else:
            return c + state1[1]
    
    def solve(self):
        """Calls the uninformed search algorithm chosen.
        Returns a solution using the specified format"""
        
        # Call the uniform_cost_search method from the search module
        solution = search.uniform_cost_search(self)
        print("\nSolution: ", solution)
        print("\nCost: ", self.cost(solution))
        return solution


    ## Parte 1
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
                continue
            
            arrival_time = None
            # Process the next N lines for details on each vessel
            if N > 0:
                vessel_info = list(map(int, line.split()))
                self.vessels.append(vessel_info)
                if arrival_time is None or arrival_time > vessel_info[0]:
                    self.initial.append(vessel_info)
                N -= 1

            """ # Initial state: all berths are empty, and all vessels are unscheduled
            self.initial_state = {
                'berths': self.berths,  # List of empty berths
                'remaining_vessels': self.vessels  # All vessels are unscheduled
            } """


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
    baproblem.load('Tests\ex100.dat')
    print(baproblem.berth_size)
    print(baproblem.vessels)
    print(baproblem.initial)
    baproblem.solve()


if __name__=='__main__':
    main()