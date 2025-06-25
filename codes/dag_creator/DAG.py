import random
import math
from task import Task
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import numpy as np


class DAG:
    def __init__(self, n, parallelism_mode, task_set):
        self.n = n
        self.parallelism_mode = parallelism_mode
        self.h = self.get_h_range_for_parallelism_mode() # assigning random height according to parallelism mode
        self.task_set = task_set
        self.tasks = []
        self.levels = []

    def get_h_range_for_parallelism_mode(self):
        if self.parallelism_mode == "high":
            start = 1
            end = math.ceil(self.n / 3) - 1
            return random.randint(start, end)
        
        elif self.parallelism_mode == "medium":
            start = math.ceil(self.n / 3)    
            end = math.ceil(2*self.n / 3) - 1
            return random.randint(start, end)
        
        elif self.parallelism_mode == "low":
            start = math.ceil(2 * self.n / 3)  
            end = self.n - 1                   
            return random.randint(start, end)

    def get_parallelism_type(self):
        if 1 <= self.h < self.n/3:
            return "high"
        elif self.n/3 <= self.h < 2*self.n/3:
            return "medium"
        elif 2*self.n/3 <= self.h < self.n:
            return "low"
        else:
            return "INVALID_HEIGHT!"
    
    def create_DAG(self, edge_prob=0.2):
        if self.get_parallelism_type() == "INVALID_HEIGHT!":
            print('Bad Height Value! DAG creation failed.')
            return

        task_names = random.choices(self.task_set, k=self.n)

        parts = [1] * self.h
        remaining = self.n - self.h

        for _ in range(remaining):
            parts[random.randint(0, self.h - 1)] += 1

        random.shuffle(parts)

        
        levels = [[None] * count for count in parts]
        self.levels = levels

        task_id = 0
        for level in range(self.h):
            for i in range(len(self.levels[level])):
                task = Task(task_id, task_names[task_id])
                self.levels[level][i] = task
                task.level = level
                self.tasks.append(task)
                task_id += 1

        for i in range(self.h - 1):
            for j in range(i + 1, self.h):
                for parent in self.levels[i]:
                    for child in self.levels[j]:
                        if random.random() < edge_prob:
                            parent.add_child(child)
                            child.add_parent(parent)

        for i in range(1, self.h):
            for node in self.levels[i]:
                has_direct_parent = any(parent.level == i - 1 for parent in node.parents)
                if not has_direct_parent:
                    parent = random.choice(self.levels[i - 1])
                    parent.add_child(node)
                    node.add_parent(parent)

        print("DAG created successfully using layrprob method!")

    def __str__(self):
        output = ""
        for task in self.tasks:
            children_ids = [child.id for child in task.children]
            parent_ids = [parent.id for parent in task.parents]
            output += f"Task ID {task.id} ({task.task_name}) in level {task.level} -> Children: {children_ids}, Parents: {parent_ids}\n"
        return output
    


    def draw_dag(self, show_task_names):
        G = nx.DiGraph()

        pos = {} 
        labels = {} 

        
        for level_index, level in enumerate(self.levels):
            for node_index, task in enumerate(level):
                G.add_node(task.id)
                pos[task.id] = (node_index, -level_index)  
                if show_task_names:
                    labels[task.id] = f"{task.task_name}\n{task.id}"
                else:
                    labels[task.id] = f"{task.id}"

        
        for task in self.tasks:
            for child in task.children:
                G.add_edge(task.id, child.id)

        plt.figure(figsize=(12, 6))
        nx.draw(G, pos, with_labels=True, labels=labels, node_size=1500,
                node_color='lightblue', arrows=True, arrowsize=20, font_size=10)

        plt.title("DAG Visualization")
        plt.axis('off')
        plt.tight_layout()
        plt.show()