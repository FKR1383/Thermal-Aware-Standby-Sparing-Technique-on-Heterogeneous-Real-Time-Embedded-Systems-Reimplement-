class Task:
    def __init__(self, id, task_name):
        self.id = id
        self.task_name = task_name
        self.parents = []
        self.children = []
        self.level = None
        self.deadline = None # we will set this (I don't know how :) ) -- one value
        self.wcet_LO = None # assigned automatically according to the task name -- per voltage/frequency value
        self.wcet_HI = None # assigned automatically according to the task name -- per voltage/frequency value
        self.power_value = None # assigned automatically according to the task name -- per voltage/frequency value
        # TODO: other arguments will be added. (such as wcet, power comsumption, etc.)
    
    def __str__(self):
        return f"Task {self.task_name}"
    
    def add_parent(self, parent):
        self.parents.append(parent)

    def add_child(self, child):
        self.children.append(child)


    def to_dict(self):
        return {
            "id": self.id,
            "task_name": self.task_name,
            "level": self.level,
            "deadline": self.deadline,
            "wcet_LO": self.wcet_LO,
            "wcet_HI": self.wcet_HI,
            "power_value": self.power_value,
            "parents": [p.id for p in self.parents],
            "children": [c.id for c in self.children]
        }

    @staticmethod
    def from_dict(data, task_map):
        task = Task(data["id"], data["task_name"])
        task.level = data["level"]
        task.deadline = data["deadline"]
        task.wcet_LO = data["wcet_LO"]
        task.wcet_HI = data["wcet_HI"]
        task.power_value = data["power_value"]
        task_map[task.id] = task
        return task
