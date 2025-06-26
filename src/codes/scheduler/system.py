from collections import defaultdict

from codes.scheduler.core import Core

class System:
    def __init__(self, DAG, k):
        self.DAG = DAG
        self.TSP_LO = {0: None, 1: 3, 2: 1} # TSP for all possible number of active cores in 'Low Power Island'
        self.TSP_HI = {0: None, 1: 5, 2: 3} # TSP for all possible number of active cores in 'High Power Island'
        self.core_pairs = [(Core('HI'), Core('LO')) for _ in range(k)]

    def get_best_core_pair(self):
        return min(self.core_pairs, key=lambda pair: pair[0].utilization + pair[1].utilization)
    
    def get_max_active_cores_in_interval(self, t, duration, core_type):
        active_count = defaultdict(int)

        for hi_core, lo_core in self.core_pairs:
            core = hi_core if core_type == 'HI' else lo_core

            for _, start, end in core.scheduling:
                overlap_start = max(t, start)
                overlap_end = min(t + duration, end)

                if overlap_start < overlap_end:
                    for time_point in range(overlap_start, overlap_end):
                        active_count[time_point] += 1

        return max(active_count.values(), default=0)

    def check_TSP(self, t, duration, peak_power, core_type):
        active_cores = self.get_max_active_cores_in_interval(t, duration, core_type)
        if core_type == "HI":
            tsp_constraint = self.TSP_HI[active_cores]
        else:
            tsp_constraint = self.TSP_LO[active_cores]
            
        if tsp_constraint == None or tsp_constraint >= peak_power:
            return True
        return False
    
    def get_finish_times_for_task(self, task_id):
        finish_times = []

        for hi_core, lo_core in self.core_pairs:
            for _, s, e in hi_core.scheduling:
                if _.id == task_id:
                    finish_times.append(e)
            for _, s, e in lo_core.scheduling:
                if _.id == task_id:
                    finish_times.append(e)

        return finish_times
    

