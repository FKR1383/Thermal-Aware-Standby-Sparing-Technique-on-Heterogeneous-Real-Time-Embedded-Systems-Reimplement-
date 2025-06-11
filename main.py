from DAG import DAG
import sys

def run(n, parallelism_mode):
    task_names = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"] # TODO: will be completed using MiBench task names

    dag = DAG(n, parallelism_mode, task_set=task_names)
    dag.create_DAG()

    print(dag)

    dag.draw_dag()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <n> <parallelism mode>")
        sys.exit(1)
    
    n = int(sys.argv[1])
    parallelism_mode = sys.argv[2]
    run(n, parallelism_mode)

