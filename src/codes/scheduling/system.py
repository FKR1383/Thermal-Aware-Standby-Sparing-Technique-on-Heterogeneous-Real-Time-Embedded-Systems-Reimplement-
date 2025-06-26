from core import Core

class System:
    def __init__(self, DAG, k):
        self.DAG = DAG
        self.TSP_LO = None # TSP for all possible number of active cores in 'Low Power Island'
        self.TSP_HI = None # TSP for all possible number of active cores in 'High Power Island'
        self.core_pairs = [(Core('HI'), Core('LO')) for i in range(k)]
    

