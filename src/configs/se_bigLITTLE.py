from m5.objects import *
from m5.util import addToPath
import argparse
import m5

# مسیر فایل‌های تعریف هسته‌ها
addToPath("../../")

# فقط از exynos‌ها استفاده می‌کنیم
from common.cores.arm import ex5_big, ex5_LITTLE

parser = argparse.ArgumentParser(description="Run Exynos core in SE mode")
parser.add_argument("--cpu-type", choices=["big", "little"], default="little", help="Choose core type")
parser.add_argument("binary", help="Path to ARM binary")
parser.add_argument("args", nargs=argparse.REMAINDER, help="Arguments to pass to binary")
args = parser.parse_args()

# تعریف سیستم
system = System()
system.mem_mode = "timing"
system.mem_ranges = [AddrRange("2GiB")]

# clk_domain عمومی برای اجزای غیر CPU (مثل mem)
system.clk_domain = SrcClockDomain(clock="1GHz", voltage_domain=VoltageDomain())
system.membus = SystemXBar()
system.system_port = system.membus.cpu_side_ports

# انتخاب CPU و کش‌ها
if args.cpu_type == "big":
    print("Using ex5_big (Cortex-A15-like)")
    system.cpu = ex5_big.ex5_big(cpu_id=0)
    system.cpu.clk_domain = SrcClockDomain(clock="2GHz", voltage_domain=VoltageDomain(voltage="0.9995V"))
    L1I = ex5_big.L1I
    L1D = ex5_big.L1D
    L2 = ex5_big.L2
else:
    print("Using ex5_LITTLE (Cortex-A7-like)")
    system.cpu = ex5_LITTLE.ex5_LITTLE(cpu_id=0)
    system.cpu.clk_domain = SrcClockDomain(clock="1.4GHz", voltage_domain=VoltageDomain(voltage="0.93V"))
    L1I = ex5_LITTLE.L1I
    L1D = ex5_LITTLE.L1D
    L2 = ex5_LITTLE.L2

# کش‌های L1
system.cpu.icache = L1I(cpu_side=system.cpu.icache_port)
system.cpu.dcache = L1D(cpu_side=system.cpu.dcache_port)

# کش L2
system.l2cache = L2()
system.tol2bus = L2XBar()
system.cpu.icache.mem_side = system.tol2bus.cpu_side_ports
system.cpu.dcache.mem_side = system.tol2bus.cpu_side_ports
system.l2cache.cpu_side = system.tol2bus.mem_side_ports
system.l2cache.mem_side = system.membus.cpu_side_ports

# حافظه اصلی
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = LPDDR3_1600_1x32()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# بارگذاری باینری در SE-mode
system.workload = SEWorkload.init_compatible(args.binary)
process = Process()
process.cmd = [args.binary] + args.args
system.cpu.workload = process
system.cpu.createThreads()
system.cpu.createInterruptController()

# آماده‌سازی و اجرا
root = Root(full_system=False, system=system)
m5.instantiate()
print(f"\n[INFO] Starting simulation with {args.cpu_type.upper()} core")
exit_event = m5.simulate()
print(f"[EXIT] Reason: {exit_event.getCause()} @ Tick: {m5.curTick()}")
