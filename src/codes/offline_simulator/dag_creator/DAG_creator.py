from codes.offline_simulator.dag_creator.DAG import DAG
import sys

def run(n, parallelism_mode, show_task_names):
    task_names = ["Basicmath", "Bitcount", "CRC32", "Dijkstra", "FFT", "Jpeg", "Patricia", "Qsort", "SHA", "String search", "Susan"] # Completed: will be completed using MiBench task names

    dag = DAG(n, parallelism_mode, task_set=task_names)
    dag.create_DAG()

    print(dag)

    dag.draw_dag(show_task_names)

    print('------------------------------------------')

    print('DO YOU WANT TO SAVE THIS DAG INTO JSON FILE? (y/n)')

    answer = input()
    if answer == 'y':
        json_data = dag.to_json()
        with open("output/dag.json", "w") as f:
            f.write(json_data)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python DAG_creator.py <n> <parallelism mode including 'high', 'medium' and 'low'> <show task names y/n>")
        print("Example: python DAG_creator.py 30 high n")
        sys.exit(1)
    
    n = int(sys.argv[1])
    parallelism_mode = sys.argv[2]
    show_task_names = True if sys.argv[3] == 'y' else False 
    run(n, parallelism_mode, show_task_names)

