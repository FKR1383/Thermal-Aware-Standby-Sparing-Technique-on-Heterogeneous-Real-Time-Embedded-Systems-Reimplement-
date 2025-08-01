class Core:
    def __init__(self, type):
        self.voltage_frequency_values = []
        self.utilization = 0
        self.type = type # high power ('HI') or low power ('LO')
        self.scheduling = [] # 3-tuple including (task, start time, end time)

    def find_first_free_time_slot_after(self, k, duration):
        t = k
        while True:
            if all(not (start <= t < end or start < t + duration <= end) for _, start, end in self.scheduling):
                return t
            t += 1

    def calculate_utilization(self):
        total_time = sum(end - start for _, start, end in self.scheduling) # sum of active periods of the core
        self.utilization = total_time

    def schedule(self, task, start_time, duration):
        self.scheduling.append((task, start_time, start_time + duration))
        self.calculate_utilization()

    def core_to_dict(self):
        return {
            "type": self.type,
            "utilization": self.utilization,
            "voltage_frequency_values": self.voltage_frequency_values,
            "scheduling": [
                {
                    "task_id": task.id,
                    "task_name": task.task_name,
                    "start": start,
                    "end": end,
                    "wcet": getattr(task, "wcet_HI", None) if self.type == "HI" else getattr(task, "wcet_LO", None) ,
                    "deadline": getattr(task, "deadline", None),
                    "parents": [p.id for p in getattr(task, "parents", [])],
                    "children": [c.id for c in getattr(task, "children", [])],
                    "level": getattr(task, "level", None)
                }
                for task, start, end in self.scheduling
            ]
        }


