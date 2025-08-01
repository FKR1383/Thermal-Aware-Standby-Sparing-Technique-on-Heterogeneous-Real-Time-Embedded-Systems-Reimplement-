import json
from codes.offline_simulator.scheduler.core import Core
from codes.offline_simulator.scheduler.system import System
from codes.offline_simulator.dag_creator.DAG import DAG
from codes.offline_simulator.dag_creator.task import Task


def import_system_from_json(filename="input/system_full.json"):
    with open(filename, "r") as f:
        data = json.load(f)

    dag = DAG.from_json(json.dumps(data["DAG"]))

    k = len(data["core_pairs"])
    system = System(dag, k)
    system.TSP_LO = {int(k): v for k, v in data["TSP_LO"].items()}
    system.TSP_HI = {int(k): v for k, v in data["TSP_HI"].items()}

    task_map = {task.id: task for task in dag.tasks}

    for i, (hi_core, lo_core) in enumerate(system.core_pairs):
        core_pair_data = data["core_pairs"][i]

        restore_core_from_dict(hi_core, core_pair_data["HI_core"], task_map)

        restore_core_from_dict(lo_core, core_pair_data["LO_core"], task_map)

    return system


def restore_core_from_dict(core, core_data, task_map):
    core.type = core_data["type"]
    core.utilization = core_data["utilization"]
    core.voltage_frequency_values = core_data["voltage_frequency_values"]

    core.scheduling = []
    for t_data in core_data["scheduling"]:
        task = task_map[t_data["task_id"]]
        start = t_data["start"]
        end = t_data["end"]
        core.scheduling.append((task, start, end))

    core.calculate_utilization()
