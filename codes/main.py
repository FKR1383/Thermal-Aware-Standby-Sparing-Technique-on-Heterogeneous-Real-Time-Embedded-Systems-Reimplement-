from dag_creator.DAG import DAG
from dag_creator.task import Task

def run(task_dag_file):
    with open(task_dag_file, "r") as f:
        json_str = f.read()

    dag_loaded = DAG.from_json(json_str)
    dag_loaded.draw_dag(True)

    
    

if __name__ == "__main__":
    TASK_DAG_FILE = 'inputs/dag.json'
    run(TASK_DAG_FILE)
