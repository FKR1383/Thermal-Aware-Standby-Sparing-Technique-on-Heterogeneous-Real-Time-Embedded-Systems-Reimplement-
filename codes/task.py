class Task:
    def __init__(self, id, task_name):
        self.id = id
        self.task_name = task_name
        self.parents = []
        self.children = []
        self.level = None
        # TODO: other arguments will be added. (such as wcet, power comsumption, etc.)
    
    def __str__(self):
        return f"Task {self.task_name}"
    
    def add_parent(self, parent):
        self.parents.append(parent)

    def add_child(self, child):
        self.children.append(child)
    
    