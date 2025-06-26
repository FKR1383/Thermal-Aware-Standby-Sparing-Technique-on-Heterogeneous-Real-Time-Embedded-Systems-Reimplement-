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


