import sys

from codes.dag_creator.DAG import DAG
from codes.dag_creator.task import Task
from codes.scheduler.system import System
from codes.scheduler.core import Core
from codes.scheduler.TASS import TASS_algorithm, plot_schedule

def run(task_dag_file, k):
    with open(task_dag_file, "r") as f:
        json_str = f.read()

    dag = DAG.from_json(json_str)
    system = System(dag, k)
    result = TASS_algorithm(system=system, dag=dag)
    if result:
        print("Scheduling Done!")
        for i, (hi_core, lo_core) in enumerate(system.core_pairs):
            print(f"🟦 Core Pair {i+1}:")

            print(f"  🔹 HI Core:")
            for task, start, end in sorted(hi_core.scheduling, key=lambda x: x[1]):
                print(f"    Task {task.task_name} (ID={task.id}): {start} → {end}")

            print(f"  🔸 LO Core:")
            for task, start, end in sorted(lo_core.scheduling, key=lambda x: x[1]):
                print(f"    Task {task.task_name} (ID={task.id}): {start} → {end}")

            print()

            plot_schedule(system=system)
    else:
        print("Tasks are unschedulable!")


    
    
if __name__ == "__main__":
    k = int(sys.argv[1]) # number of core pairs
    TASK_DAG_FILE = 'inputs/dag.json'
    run(TASK_DAG_FILE, k)
