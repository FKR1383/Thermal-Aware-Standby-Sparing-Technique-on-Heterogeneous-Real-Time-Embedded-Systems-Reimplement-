import sys
from dag_creator.DAG import DAG
from dag_creator.task import Task
from scheduling.system import System
from scheduling.core import Core
from scheduling.TASS import TASS_algorithm

def run(task_dag_file, k):
    with open(task_dag_file, "r") as f:
        json_str = f.read()

    dag = DAG.from_json(json_str)
    system = System(dag, k)
    TASS_algorithm(system=system, dag=dag)


    
    
if __name__ == "__main__":
    k = int(sys.argv[1]) # number of core pairs
    TASK_DAG_FILE = 'inputs/dag.json'
    run(TASK_DAG_FILE, k)
