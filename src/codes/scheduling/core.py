class Core:
    def __init__(self, type):
        self.voltage_frequency_values = []
        self.utilization = 0
        self.type = type # high power ('HI') or low power ('LO')
        self.scheduling = [] # 3-tuple including (task, start time, end time)

    def find_first_free_time_slot_after(self, k):
        pass

    def calculate_utilization(self):
        self.utilization = 0
        pass


