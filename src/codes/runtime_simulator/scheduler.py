import math
import random

from codes.runtime_simulator.input.DFVS_levels import *
from codes.offline_simulator.scheduler.TASS import plot_schedule

LAMBDA0 = 1e-6 
D = 0.15       # 28nm tech
V_MAX = max(HI_core_level[i][0] for i in range(len(HI_core_level)))

def lambda_vi(voltage):
    return LAMBDA0 * (10 ** ((V_MAX - voltage) / D))


def reliability(task_time, voltage):
    lam = lambda_vi(voltage)
    return math.exp(-lam * task_time)
    return 0.5


def runtime_scheduling(system_restored):
    max_time = 0
    for hi_core, lo_core in system_restored.core_pairs:
        for _, _, end in hi_core.scheduling:
            max_time = max(max_time, end)
        for _, _, end in lo_core.scheduling:
            max_time = max(max_time, end)

    finished_tasks = set()
    failed_tasks = set()

    for current_time in range(max_time + 1):
        for hi_core, lo_core in system_restored.core_pairs:
            # HI Core
            for task, start, end in hi_core.scheduling:
                if start == current_time:
                    duration = (end - start) # converting ms to s

                    voltage = V_MAX

                    r = reliability(duration, voltage)
                    success = random.random() < r


                    if success:
                        finished_tasks.add(task.id)
                    else:
                        failed_tasks.add(task.id)
                        print(f"❌ Task {task.id} FAILED on HI Core")

            # LO Core
            for task, start, end in lo_core.scheduling:
                if task.id in finished_tasks:
                    lo_core.scheduling.remove((task, start, end))

    
    plot_schedule(system_restored)
