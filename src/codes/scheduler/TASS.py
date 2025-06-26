from codes.dag_creator.DAG import DAG
from codes.dag_creator.task import Task
from codes.scheduler.system import System
from codes.scheduler.core import Core

def TASS_algorithm(system, dag):
    stack = []
    remaining = set(dag.tasks)
    all_children = {
        task.id: set(child.id for child in task.children) for task in dag.tasks
    }

    # Find tasks that have no children (leaf tasks in the remaining DAG)
    while remaining:
        leaves = [t for t in remaining if not any(child in remaining for child in t.children)]
        if not leaves:
            break
        leaf = max(leaves, key=lambda t: t.deadline)
        stack.append(leaf)
        remaining.remove(leaf)

    while stack:
        task = stack.pop()
        C_hp, C_lp = system.get_best_core_pair()

        # === Primary Scheduling ===
        preds = task.parents

        k = max((
            max(system.get_finish_times_for_task(p.id), default=0)
            for p in preds
        ), default=0)

        t = k
        t_free = None
        while t <= task.deadline - task.wcet_HI:
            t_free = C_hp.find_first_free_time_slot_after(t, task.wcet_HI)
            if system.check_TSP(t_free, task.wcet_HI, task.peak_power_value_HI, 'HI'):
                C_hp.schedule(task, t_free, task.wcet_HI)
                break
            t += 1

        if t > task.deadline - task.wcet_HI:
            return False # UNSCHEDULABLE!

        finish_primary = t_free + task.wcet_HI

        # === Backup Scheduling ===
        t = finish_primary
        while True:
            t_free = C_lp.find_first_free_time_slot_after(t, task.wcet_LO)
            if system.check_TSP(t_free, task.wcet_LO, task.peak_power_value_LO, 'LO'):
                C_lp.schedule(task, t_free, task.wcet_LO)
                break
            t += 1

    return True # SCHEDULABLE!