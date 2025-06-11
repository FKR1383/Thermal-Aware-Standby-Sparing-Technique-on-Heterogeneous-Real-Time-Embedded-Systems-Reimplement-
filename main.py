from DAG import DAG
import sys

def run(n, h):
    task_names = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"] # TODO: will be completed using MiBench task names

    dag = DAG(n, h, task_set=task_names)
    dag.create_DAG()

    print(dag)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <n> <h>")
        sys.exit(1)
    
    n = int(sys.argv[1])
    h = int(sys.argv[2])
    run(n, h)

