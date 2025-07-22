from m5.objects import *
from m5.util import addToPath
import m5
import argparse

# از فایل خودت import کن

m5.util.addToPath("../../")

import devices
from common import (
    FSConfig,
    ObjectList,
    Options,
    SysPaths,
)
from common.cores.arm import (
    ex5_big,
    ex5_LITTLE,
)
from devices import (
    AtomicCluster,
    FastmodelCluster,
    KvmCluster,
)
from common.cores.arm.ex5_big import ex5_big, L1I, L1D, L2  # فرض کن این فایل اسمش ex5_big.py باشه

parser = argparse.ArgumentParser()
parser.add_argument("binary", help="Path to ARM binary")
parser.add_argument("args", nargs=argparse.REMAINDER, help="Arguments to the binary")
args = parser.parse_args()

system = System()
system.clk_domain = SrcClockDomain(clock="1GHz", voltage_domain=VoltageDomain())
system.mem_mode = "timing"
system.mem_ranges = [AddrRange("2GiB")]

# CPU
system.cpu = ex5_big(cpu_id=0)
system.cpu.clk_domain = SrcClockDomain(clock="2.0GHz", voltage_domain=VoltageDomain(voltage="0.9995V"))

# کش‌ها
system.cpu.icache = L1I(cpu_side = system.cpu.icache_port)
system.cpu.dcache = L1D(cpu_side = system.cpu.dcache_port)

# L2 و اتصال
system.l2cache = L2()
system.tol2bus = L2XBar()
system.cpu.icache.mem_side = system.tol2bus.cpu_side_ports
system.cpu.dcache.mem_side = system.tol2bus.cpu_side_ports
system.l2cache.cpu_side = system.tol2bus.mem_side_ports

# حافظه
system.membus = SystemXBar()
system.l2cache.mem_side = system.membus.cpu_side_ports

system.system_port = system.membus.cpu_side_ports

system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = LPDDR3_1600_1x32()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# بارگذاری باینری
system.workload = SEWorkload.init_compatible(args.binary)
system.cpu.createInterruptController()

process = Process()
process.cmd = [args.binary] + args.args
system.cpu.workload = process
system.cpu.createThreads()

root = Root(full_system=False, system=system)
m5.instantiate()

print("Starting simulation with ex5_big core (Cortex-A15-like)")
exit_event = m5.simulate()
print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")
