import random
from task import Task

class DAG:
    def __init__(self, n, h, task_set):
        self.n = n
        self.h = h
        self.task_set = task_set
        self.tasks = []
        self.levels = []

    def get_parallelism_type(self):
        if 1 <= self.h < self.n/3:
            return "high"
        elif self.n/3 <= self.h < 2*self.n/3:
            return "medium"
        elif 2*self.n/3 <= self.h < self.n:
            return "low"
        else:
            return "INVALID_HEIGHT!"
    
    def create_DAG(self):
        if self.get_parallelism_type() == "INVALID_HEIGHT!":
            print('Bad Height Value! DAG creation failed.')
            return
        
        task_names = random.choices(self.task_set, k=self.n)
        

        levels = [[] for _ in range(self.h)]
        remaining = self.n

        for i in range(self.h):
            if i == self.h - 1:
                count = remaining
            else:
                max_possible = remaining - (self.h - i - 1)
                count = random.randint(1, max_possible)
            levels[i] = [None] * count
            remaining -= count

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
            for parent in self.levels[i]:
                possible_children = [t for level in self.levels[i+1:] for t in level]
                if not possible_children:
                    continue
                num_children = random.randint(1, min(len(possible_children), 3))
                children = random.sample(possible_children, num_children)
                for child in children:
                    parent.add_child(child)
                    child.add_parent(parent)

        for i in range(1, self.h):
            for node in self.levels[i]:
                if not node.parents:
                    possible_parents = [t for level in self.levels[:i] for t in level]
                    parent = random.choice(possible_parents)
                    parent.add_child(node)
                    node.add_parent(parent)

        print("DAG created successfully!")

    def __str__(self):
        output = ""
        for task in self.tasks:
            children_ids = [child.id for child in task.children]
            parent_ids = [parent.id for parent in task.parents]
            output += f"Task ID {task.id} ({task.task_name}) in level {task.level} -> Children: {children_ids}, Parents: {parent_ids}\n"
        return output