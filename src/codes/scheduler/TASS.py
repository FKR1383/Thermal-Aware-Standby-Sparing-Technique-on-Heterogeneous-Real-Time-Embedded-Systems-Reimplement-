import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
import matplotlib.patches as patches

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

def plot_schedule(system):
    num_core_pairs = len(system.core_pairs)

    # Separate and order cores: first all HI, then all LO
    hi_cores = [(f"HP_C{i+1}", pair[0]) for i, pair in enumerate(system.core_pairs)]
    lo_cores = [(f"LP_C{i+1}", pair[1]) for i, pair in enumerate(system.core_pairs)]
    all_cores = hi_cores + lo_cores

    # Reverse for Gantt chart so HI cores appear first top-down
    gantt_cores = list(reversed(all_cores))

    fig, (gantt_ax, *power_axes) = plt.subplots(1 + len(all_cores), 1,
                                                figsize=(16, 3 + 2.5 * len(all_cores)),
                                                gridspec_kw={'height_ratios': [4] + [2]*len(all_cores)})

    # --- Top: Gantt chart ---
    y_labels = []
    yticks = []
    yt = 0
    max_time = 0

    for label, core in gantt_cores:
        for task, start, end in core.scheduling:
            gantt_ax.add_patch(
                patches.Rectangle((start, yt), end - start, 0.8, facecolor='lightgray', edgecolor='black')
            )
            task_label = f"T{task.id}" if core.type == 'HI' else f"B{task.id}"
            gantt_ax.text(start + (end - start)/2, yt + 0.4, task_label,
                          ha='center', va='center', fontsize=8)
            max_time = max(max_time, end)

        y_labels.append(label)
        yticks.append(yt + 0.4)
        yt += 1

    gantt_ax.set_yticks(yticks)
    gantt_ax.set_yticklabels(y_labels)
    gantt_ax.set_xlim(0, max_time + 10)
    gantt_ax.set_xticks(range(0, max_time + 11, 5))
    gantt_ax.set_ylim(-0.5, yt)
    gantt_ax.set_title("Task Scheduling Timeline")
    gantt_ax.set_xlabel("Time (ms)")
    gantt_ax.set_ylabel("Cores")
    gantt_ax.grid(True, axis='x', linestyle='--', alpha=0.5)

    # --- Power profiles ---
    time_range = list(range(max_time + 1))
    for (label, core), ax in zip(all_cores, power_axes):
        power_profile = [0] * len(time_range)
        constraint = [0] * len(time_range)

        for t in time_range:
            for task, start, end in core.scheduling:
                if start <= t < end:
                    if core.type == 'HI':
                        power_profile[t] = task.peak_power_value_HI or 0
                    else:
                        power_profile[t] = task.peak_power_value_LO or 0
                    break

            if core.type == 'HI':
                constraint_value = system.TSP_HI.get(system.get_max_active_cores_in_interval(t, 1, 'HI'))
                constraint[t] = constraint_value if constraint_value is not None else 0
            else:
                constraint_value = system.TSP_LO.get(system.get_max_active_cores_in_interval(t, 1, 'LO'))
                constraint[t] = constraint_value if constraint_value is not None else 0

        ax.step(time_range, power_profile, label='Power Profile', color='blue', where='post')
        ax.step(time_range, constraint, label='Power Constraint', color='orange', linestyle='--', where='post')

        ax.set_title(label)
        ax.set_ylim(0, max(max(constraint), max(power_profile), 1) + 1)
        ax.set_xlim(0, max_time + 10)
        ax.set_xticks(range(0, max_time + 11, 5))
        ax.set_xlabel("Time (ms)")
        ax.set_ylabel("Power (W)")
        ax.legend(loc='upper right')
        ax.grid(True, axis='x', linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig("schedule_output.png")
