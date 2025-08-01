from codes.runtime_simulator.json_handler import *
from codes.runtime_simulator.input.DFVS_levels import *
from codes.runtime_simulator.scheduler import *

def run():
    system_restored = import_system_from_json("input/system_scheduled.json")

    LO_voltage_frequency_levels = LO_core_level
    HI_voltage_frequency_levels = HI_core_level

    runtime_scheduling(system_restored)




if __name__ == "__main__":
    run()
