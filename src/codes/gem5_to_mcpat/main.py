import json
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom

def read_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)

def read_stats(stats_path):
    stats = {}
    pattern = re.compile(r'([\w\.\-:]+)\s+([-+]?[0-9]*\.?[0-9]+|nan|inf)')
    with open(stats_path, 'r') as f:
        for line in f:
            match = pattern.match(line.strip())
            if match:
                key, val = match.groups()
                stats[key] = 0.0 if val == 'nan' else float(val)
    return stats

def insert_core_and_directory_params(system_elem, config):
    system = config.get("system", {})
    if "cpus" in system:
        cpu_list = system["cpus"]
        num_cores = len(cpu_list)
    elif "cpu" in system:
        cpu_list = [system["cpu"]]
        num_cores = 1
    else:
        cpu_list = []
        num_cores = 0

    if "l2caches" in system:
        num_l2s = len(system["l2caches"])
        num_l2_dirs = len(system["l2caches"])
    elif "l2cache" in system:
        num_l2s = 1
        num_l2_dirs = 1
    else:
        num_l2s = 0
        num_l2_dirs = 0

    num_l1_dirs = num_cores
    mmu = cpu_list[0].get("mmu", {}) if cpu_list else {}
    private_l2 = 1 if not mmu.get("l2_shared") else 0
    num_l3s = 1 if "l3" in system else 0
    num_nocs = sum(1 for k in system if "membus" in k.lower())
    

    def is_homogeneous(attr):
        values = set()
        for cpu in cpu_list:
            if attr in cpu:
                values.add(str(cpu[attr]))
        return len(values) <= 1

    ET.SubElement(system_elem, "param", name="number_of_cores", value=str(num_cores))
    ET.SubElement(system_elem, "param", name="number_of_L1Directories", value=str(num_l1_dirs))
    ET.SubElement(system_elem, "param", name="number_of_L2Directories", value=str(num_l2_dirs))
    ET.SubElement(system_elem, "param", name="number_of_L2s", value=str(num_l2s))
    ET.SubElement(system_elem, "param", name="Private_L2", value=str(private_l2))
    ET.SubElement(system_elem, "param", name="number_of_L3s", value=str(num_l3s))
    ET.SubElement(system_elem, "param", name="number_of_NoCs", value=str(num_nocs))
    ET.SubElement(system_elem, "param", name="homogeneous_cores", value="1" if is_homogeneous("type") else "0")
    ET.SubElement(system_elem, "param", name="homogeneous_L2s", value="1")
    ET.SubElement(system_elem, "param", name="homogeneous_L1Directories", value="1")
    ET.SubElement(system_elem, "param", name="homogeneous_L2Directories", value="1")
    ET.SubElement(system_elem, "param", name="homogeneous_L3s", value="0")
    ET.SubElement(system_elem, "param", name="homogeneous_ccs", value="1")
    ET.SubElement(system_elem, "param", name="homogeneous_NoCs", value="0")

def insert_general_params(system_elem, tech_node, clockrate):
    ET.SubElement(system_elem, "param", name="core_tech_node", value=str(tech_node))
    ET.SubElement(system_elem, "param", name="target_core_clockrate", value=str(clockrate))
    ET.SubElement(system_elem, "param", name="temperature", value="340")
    ET.SubElement(system_elem, "param", name="interconnect_projection_type", value="1")
    ET.SubElement(system_elem, "param", name="device_type", value="2")
    ET.SubElement(system_elem, "param", name="longer_channel_device", value="1")
    ET.SubElement(system_elem, "param", name="Embedded", value="1")
    ET.SubElement(system_elem, "param", name="opt_clockrate", value="1")
    ET.SubElement(system_elem, "param", name="machine_bits", value="32")
    ET.SubElement(system_elem, "param", name="virtual_address_width", value="32")
    ET.SubElement(system_elem, "param", name="physical_address_width", value="32")
    ET.SubElement(system_elem, "param", name="virtual_memory_page_size", value="4096")

def insert_cycle_stats(system_elem, stats):
    idle_cycles = int(stats.get("system.cpu.idleCycles", 0))
    busy_cycles = int(stats.get("system.cpu.tickCycles", 0))
    total_cycles = idle_cycles + busy_cycles

    ET.SubElement(system_elem, "stat", name="total_cycles", value=str(total_cycles))
    ET.SubElement(system_elem, "stat", name="idle_cycles", value=str(idle_cycles))
    ET.SubElement(system_elem, "stat", name="busy_cycles", value=str(busy_cycles))

def insert_branch_predictor(core_elem, config):
    cpu = config.get("system", {}).get("cpu", {})
    branch_pred = cpu.get("branchPred", {})

    local_entries = branch_pred.get("localPredictorSize", 2048)
    local_bits = branch_pred.get("localCtrBits", 2)
    global_entries = branch_pred.get("globalPredictorSize", 8192)
    global_bits = branch_pred.get("globalCtrBits", 2)
    chooser_entries = branch_pred.get("choicePredictorSize", 1024)
    chooser_bits = branch_pred.get("choiceCtrBits", 3)

    predictor_elem = ET.SubElement(core_elem, "component", id="system.core0.predictor", name="PBT")
    ET.SubElement(predictor_elem, "param", name="local_predictor_size", value=f"{local_entries},{local_bits}")
    ET.SubElement(predictor_elem, "param", name="local_predictor_entries", value=str(local_entries))
    ET.SubElement(predictor_elem, "param", name="global_predictor_entries", value=str(global_entries))
    ET.SubElement(predictor_elem, "param", name="global_predictor_bits", value=str(global_bits))
    ET.SubElement(predictor_elem, "param", name="chooser_predictor_entries", value=str(chooser_entries))
    ET.SubElement(predictor_elem, "param", name="chooser_predictor_bits", value=str(chooser_bits))



def insert_instruction_stats(core_elem, stats):
    total = int(stats.get("system.cpu.commitStats0.numInsts", 0))

    int_alu = stats.get("system.cpu.commitStats0.committedInstType::IntAlu", 0)
    int_mul = stats.get("system.cpu.commitStats0.committedInstType::IntMult", 0)
    int_div = stats.get("system.cpu.commitStats0.committedInstType::IntDiv", 0)
    int_total = int(int_alu + int_mul + int_div)

    fp_total = 0
    for key, val in stats.items():
        if key.startswith("system.cpu.commitStats0.committedInstType::Float"):
            fp_total += val
    fp_total = int(fp_total)

    branch_total = int(stats.get("system.cpu.branchPred.committed_0::total", 0))
    branch_miss = int(stats.get("system.cpu.branchPred.mispredicted_0::total", 0))
    load = int(stats.get("system.cpu.fetch2.loadInstructions", 0))
    store = int(stats.get("system.cpu.fetch2.storeInstructions", 0))

    ET.SubElement(core_elem, "stat", name="total_instructions", value=str(total))
    ET.SubElement(core_elem, "stat", name="int_instructions", value=str(int_total))
    ET.SubElement(core_elem, "stat", name="fp_instructions", value=str(fp_total))
    ET.SubElement(core_elem, "stat", name="branch_instructions", value=str(branch_total))
    ET.SubElement(core_elem, "stat", name="branch_mispredictions", value=str(branch_miss))
    ET.SubElement(core_elem, "stat", name="load_instructions", value=str(load))
    ET.SubElement(core_elem, "stat", name="store_instructions", value=str(store))
    ET.SubElement(core_elem, "stat", name="committed_instructions", value=str(total))
    ET.SubElement(core_elem, "stat", name="committed_int_instructions", value=str(int_total))
    ET.SubElement(core_elem, "stat", name="committed_fp_instructions", value=str(fp_total))

    ET.SubElement(core_elem, "stat", name="pipeline_duty_cycle", value="1")

    ET.SubElement(core_elem, "stat", name="rename_reads", value=str(2 * total))
    ET.SubElement(core_elem, "stat", name="rename_writes", value=str(total))
    ET.SubElement(core_elem, "stat", name="fp_rename_reads", value=str(2 * fp_total))
    ET.SubElement(core_elem, "stat", name="fp_rename_writes", value=str(fp_total))

    ET.SubElement(core_elem, "stat", name="inst_window_reads", value=str(total))
    ET.SubElement(core_elem, "stat", name="inst_window_writes", value=str(total))
    ET.SubElement(core_elem, "stat", name="inst_window_wakeup_accesses", value=str(2 * total))

    ET.SubElement(core_elem, "stat", name="fp_inst_window_reads", value=str(fp_total))
    ET.SubElement(core_elem, "stat", name="fp_inst_window_writes", value=str(fp_total))
    ET.SubElement(core_elem, "stat", name="fp_inst_window_wakeup_accesses", value=str(2 * fp_total))

    ET.SubElement(core_elem, "stat", name="int_regfile_reads", value=str(3 * int_total))
    ET.SubElement(core_elem, "stat", name="int_regfile_writes", value=str(int_total))
    ET.SubElement(core_elem, "stat", name="float_regfile_reads", value=str(2 * fp_total))
    ET.SubElement(core_elem, "stat", name="float_regfile_writes", value=str(fp_total))

        
    ialu_accesses = int(stats.get("system.cpu.commitStats0.committedInstType::IntAlu", 0))
    mul_accesses = int(stats.get("system.cpu.commitStats0.committedInstType::IntMult", 0))

    
    fpu_accesses = 0
    for key, val in stats.items():
        if key.startswith("system.cpu.commitStats0.committedInstType::Float") or \
           key.startswith("system.cpu.commitStats0.committedInstType::SimdFloat"):
            fpu_accesses += val
    fpu_accesses = int(fpu_accesses)

    
    ET.SubElement(core_elem, "stat", name="ialu_accesses", value=str(ialu_accesses))
    ET.SubElement(core_elem, "stat", name="mul_accesses", value=str(mul_accesses))
    ET.SubElement(core_elem, "stat", name="fpu_accesses", value=str(fpu_accesses))

    
    ET.SubElement(core_elem, "stat", name="cdb_alu_accesses", value=str(ialu_accesses))
    ET.SubElement(core_elem, "stat", name="cdb_mul_accesses", value=str(mul_accesses))
    ET.SubElement(core_elem, "stat", name="cdb_fpu_accesses", value=str(fpu_accesses))

        
    ET.SubElement(core_elem, "stat", name="IFU_duty_cycle", value="0.9")
    ET.SubElement(core_elem, "stat", name="BR_duty_cycle", value="0.72")  # branch
    ET.SubElement(core_elem, "stat", name="LSU_duty_cycle", value="0.71")
    ET.SubElement(core_elem, "stat", name="MemManU_I_duty_cycle", value="0.9")
    ET.SubElement(core_elem, "stat", name="MemManU_D_duty_cycle", value="0.71")
    ET.SubElement(core_elem, "stat", name="ALU_duty_cycle", value="0.76")
    ET.SubElement(core_elem, "stat", name="MUL_duty_cycle", value="0.82")
    ET.SubElement(core_elem, "stat", name="FPU_duty_cycle", value="0.0")
    ET.SubElement(core_elem, "stat", name="ALU_cdb_duty_cycle", value="0.76")
    ET.SubElement(core_elem, "stat", name="MUL_cdb_duty_cycle", value="0.82")
    ET.SubElement(core_elem, "stat", name="FPU_cdb_duty_cycle", value="0.0")


def insert_tlbs(core_elem, config, stats):
    cpu = config.get("system", {}).get("cpu", {})
    mmu = cpu.get("mmu", {})

    itb = mmu.get("itb", {})
    itlb_entries = itb.get("indexing_policy", {}).get("num_entries", 0)
    itlb_elem = ET.SubElement(core_elem, "component", id="system.core0.itlb", name="itlb")
    ET.SubElement(itlb_elem, "param", name="number_entries", value=str(itlb_entries))
    ET.SubElement(itlb_elem, "stat", name="total_accesses", value=str(int(stats.get("system.cpu.mmu.itb.accesses", 0))))
    ET.SubElement(itlb_elem, "stat", name="total_misses", value=str(int(stats.get("system.cpu.mmu.itb.misses", 0))))
    ET.SubElement(itlb_elem, "stat", name="conflicts", value="0") 

    dtb = mmu.get("dtb", {})
    dtlb_entries = dtb.get("indexing_policy", {}).get("num_entries", 0)
    dtlb_elem = ET.SubElement(core_elem, "component", id="system.core0.dtlb", name="dtlb")
    ET.SubElement(dtlb_elem, "param", name="number_entries", value=str(dtlb_entries))
    ET.SubElement(dtlb_elem, "stat", name="total_accesses", value=str(int(stats.get("system.cpu.mmu.dtb.accesses", 0))))
    ET.SubElement(dtlb_elem, "stat", name="total_misses", value=str(int(stats.get("system.cpu.mmu.dtb.misses", 0))))
    ET.SubElement(dtlb_elem, "stat", name="conflicts", value="0")


def insert_cache_components(core_elem, config, stats):
    icache_cfg = config["system"]["cpu"]["icache"]
    icache_elem = ET.SubElement(core_elem, "component", id="system.core0.icache", name="icache")

    icache_config = f'{icache_cfg["size"]},{icache_cfg["tags"]["block_size"]},{icache_cfg["assoc"]},1,10,10,32,0'
    ET.SubElement(icache_elem, "param", name="icache_config", value=icache_config)
    ET.SubElement(icache_elem, "param", name="buffer_sizes", value=f'{icache_cfg["mshrs"]}, {icache_cfg["mshrs"]}, {icache_cfg["write_buffers"]},0')

    read_accesses = int(stats.get("system.cpu.icache.ReadReq.accesses::total", 0))
    read_misses = int(stats.get("system.cpu.icache.ReadReq.misses::total", 0))
    ET.SubElement(icache_elem, "stat", name="read_accesses", value=str(read_accesses))
    ET.SubElement(icache_elem, "stat", name="read_misses", value=str(read_misses))
    ET.SubElement(icache_elem, "stat", name="conflicts", value="0")

    dcache_cfg = config["system"]["cpu"]["dcache"]
    dcache_elem = ET.SubElement(core_elem, "component", id="system.core0.dcache", name="dcache")

    dcache_config = f'{dcache_cfg["size"]},{dcache_cfg["tags"]["block_size"]},{dcache_cfg["assoc"]},1,10,10,32,1'
    ET.SubElement(dcache_elem, "param", name="dcache_config", value=dcache_config)
    ET.SubElement(dcache_elem, "param", name="buffer_sizes", value=f'{dcache_cfg["mshrs"]}, {dcache_cfg["mshrs"]}, {dcache_cfg["write_buffers"]}, {dcache_cfg["write_buffers"]}')

    read_accesses = int(stats.get("system.cpu.dcache.ReadReq.accesses::total", 0))
    write_accesses = int(stats.get("system.cpu.dcache.WriteReq.accesses::total", 0))
    read_misses = int(stats.get("system.cpu.dcache.ReadReq.misses::total", 0))
    write_misses = int(stats.get("system.cpu.dcache.WriteReq.misses::total", 0))

    ET.SubElement(dcache_elem, "stat", name="read_accesses", value=str(read_accesses))
    ET.SubElement(dcache_elem, "stat", name="write_accesses", value=str(write_accesses))
    ET.SubElement(dcache_elem, "stat", name="read_misses", value=str(read_misses))
    ET.SubElement(dcache_elem, "stat", name="write_misses", value=str(write_misses))
    ET.SubElement(dcache_elem, "stat", name="conflicts", value="0")

    
def insert_btb_component(system_elem, config, stats):
    ET.SubElement(system_elem, "param", name="number_of_BTB", value="1")

    btb_cfg = config["system"]["cpu"]["branchPred"]["btb"]
    capacity = btb_cfg["numEntries"]
    assoc = btb_cfg["btbIndexingPolicy"]["assoc"]

    btb_elem = ET.SubElement(system_elem, "component", id="system.core0.BTB", name="BTB")

    btb_config = f"{capacity},4,{assoc},2,1,1"
    ET.SubElement(btb_elem, "param", name="BTB_config", value=btb_config)

    read_accesses = int(stats.get("system.cpu.branchPred.BTBLookups", 0))
    write_accesses = int(stats.get("system.cpu.branchPred.BTBUpdates", 0))

    ET.SubElement(btb_elem, "stat", name="read_accesses", value=str(read_accesses))
    ET.SubElement(btb_elem, "stat", name="write_accesses", value=str(write_accesses))

def add_L1_L2_directories(root_elem, stats):
    # ---------- L1Directory0 ----------
    l1_dir = ET.SubElement(root_elem, "component",
                           id="system.L1Directory0",
                           name="L1Directory0")

    ET.SubElement(l1_dir, "param", name="Directory_type", value="0")
    ET.SubElement(l1_dir, "param", name="Dir_config", value="2048,1,0,1,4,4,8")
    ET.SubElement(l1_dir, "param", name="buffer_sizes", value="8,8,8,8")
    ET.SubElement(l1_dir, "param", name="clockrate", value="2000")
    ET.SubElement(l1_dir, "param", name="ports", value="1,1,1")
    ET.SubElement(l1_dir, "param", name="device_type", value="2")

    ET.SubElement(l1_dir, "stat", name="read_accesses",
                  value=str(int(stats.get("system.cpu.dcache.overallAccesses::total", 0))))
    ET.SubElement(l1_dir, "stat", name="write_accesses",
                  value=str(int(stats.get("system.cpu.dcache.WriteReq.accesses::total", 0))))
    ET.SubElement(l1_dir, "stat", name="read_misses",
                  value=str(int(stats.get("system.cpu.dcache.overallMisses::total", 0))))
    ET.SubElement(l1_dir, "stat", name="write_misses",
                  value=str(int(stats.get("system.cpu.dcache.WriteReq.misses::total", 0))))
    ET.SubElement(l1_dir, "stat", name="conflicts", value="20")
    ET.SubElement(l1_dir, "stat", name="duty_cycle", value="0.1")

    # ---------- L2Directory0 ----------
    l2_dir = ET.SubElement(root_elem, "component",
                           id="system.L2Directory0",
                           name="L2Directory0")

    ET.SubElement(l2_dir, "param", name="Directory_type", value="1")
    ET.SubElement(l2_dir, "param", name="Dir_config", value="1048576,16,16,1,2,100")
    ET.SubElement(l2_dir, "param", name="buffer_sizes", value="8,8,8,8")
    ET.SubElement(l2_dir, "param", name="clockrate", value="3400")
    ET.SubElement(l2_dir, "param", name="ports", value="1,1,1")
    ET.SubElement(l2_dir, "param", name="device_type", value="0")

    ET.SubElement(l2_dir, "stat", name="read_accesses",
                  value=str(int(stats.get("system.l2cache.overallAccesses::total", 0))))
    ET.SubElement(l2_dir, "stat", name="write_accesses",
                  value=str(int(stats.get("system.l2cache.WritebackClean.accesses::total", 0))))
    ET.SubElement(l2_dir, "stat", name="read_misses",
                  value=str(int(stats.get("system.l2cache.overallMisses::total", 0))))
    ET.SubElement(l2_dir, "stat", name="write_misses",
                  value=str(int(stats.get("system.l2cache.WritebackDirty.hits::total", 0))))
    ET.SubElement(l2_dir, "stat", name="conflicts", value="100")
    ET.SubElement(l2_dir, "stat", name="duty_cycle", value="0.1")

    # ---------- L20 ----------
    l20 = ET.SubElement(root_elem, "component",
                        id="system.L20",
                        name="L20")

    ET.SubElement(l20, "param", name="L2_config", value="1048576,32,8,8,8,23,32,1")
    ET.SubElement(l20, "param", name="buffer_sizes", value="16,16,16,16")
    ET.SubElement(l20, "param", name="clockrate", value="3400")
    ET.SubElement(l20, "param", name="ports", value="1,1,1")
    ET.SubElement(l20, "param", name="device_type", value="0")

    ET.SubElement(l20, "stat", name="read_accesses",
                  value=str(int(stats.get("system.l2cache.demandAccesses::total", 0))))
    ET.SubElement(l20, "stat", name="write_accesses",
                  value=str(int(stats.get("system.l2cache.WritebackClean.accesses::total", 0))))
    ET.SubElement(l20, "stat", name="read_misses",
                  value=str(int(stats.get("system.l2cache.demandMisses::total", 0))))
    ET.SubElement(l20, "stat", name="write_misses",
                  value=str(int(stats.get("system.l2cache.WritebackDirty.hits::total", 0))))
    ET.SubElement(l20, "stat", name="conflicts", value="0")
    ET.SubElement(l20, "stat", name="duty_cycle", value="1.0")



def insert_core_component(system_elem, clockrate, machine_type, stats, config):
    core_elem = ET.SubElement(system_elem, "component", id="system.core0", name="core0")
    ET.SubElement(core_elem, "param", name="clock_rate", value=str(clockrate))
    ET.SubElement(core_elem, "param", name="opt_local", value="0")
    ET.SubElement(core_elem, "param", name="instruction_length", value="32")
    ET.SubElement(core_elem, "param", name="opcode_width", value="7")
    ET.SubElement(core_elem, "param", name="x86", value="0")
    ET.SubElement(core_elem, "param", name="micro_opcode_width", value="8")
    ET.SubElement(core_elem, "param", name="machine_type", value=str(machine_type))
    ET.SubElement(core_elem, "param", name="number_hardware_threads", value="1")
    ET.SubElement(core_elem, "param", name="fetch_width", value="2")
    ET.SubElement(core_elem, "param", name="number_instruction_fetch_ports", value="1")
    ET.SubElement(core_elem, "param", name="decode_width", value="2")
    ET.SubElement(core_elem, "param", name="issue_width", value="4")
    ET.SubElement(core_elem, "param", name="peak_issue_width", value="7")
    ET.SubElement(core_elem, "param", name="commit_width", value="4")
    ET.SubElement(core_elem, "param", name="fp_issue_width", value="1")
    ET.SubElement(core_elem, "param", name="prediction_width", value="1")
    ET.SubElement(core_elem, "param", name="pipelines_per_core", value="1,1")
    ET.SubElement(core_elem, "param", name="pipeline_depth", value="8,8")
    alu_val = "1" if machine_type == 1 else "2"
    fpu_val = "1" if machine_type == 1 else "2"
    ET.SubElement(core_elem, "param", name="ALU_per_core", value=alu_val)
    ET.SubElement(core_elem, "param", name="MUL_per_core", value="1")
    ET.SubElement(core_elem, "param", name="FPU_per_core", value=fpu_val)
    ET.SubElement(core_elem, "param", name="instruction_buffer_size", value="32")
    ET.SubElement(core_elem, "param", name="decoded_stream_buffer_size", value="16")
    ET.SubElement(core_elem, "param", name="instruction_window_scheme", value="0")
    ET.SubElement(core_elem, "param", name="instruction_window_size", value="20")
    ET.SubElement(core_elem, "param", name="fp_instruction_window_size", value="15")
    ET.SubElement(core_elem, "param", name="ROB_size", value="0")
    ET.SubElement(core_elem, "param", name="archi_Regs_IRF_size", value="32")
    ET.SubElement(core_elem, "param", name="archi_Regs_FRF_size", value="32")
    ET.SubElement(core_elem, "param", name="phy_Regs_IRF_size", value="64")
    ET.SubElement(core_elem, "param", name="phy_Regs_FRF_size", value="64")
    ET.SubElement(core_elem, "param", name="rename_scheme", value="0")
    ET.SubElement(core_elem, "param", name="checkpoint_depth", value="1")
    ET.SubElement(core_elem, "param", name="register_windows_size", value="0")
    ET.SubElement(core_elem, "param", name="LSU_order", value="inorder")
    ET.SubElement(core_elem, "param", name="store_buffer_size", value="4")
    ET.SubElement(core_elem, "param", name="load_buffer_size", value="0")
    ET.SubElement(core_elem, "param", name="memory_ports", value="1")
    ET.SubElement(core_elem, "param", name="RAS_size", value="4")
    insert_instruction_stats(core_elem, stats)

    insert_branch_predictor(core_elem, config)
    insert_tlbs(core_elem, config, stats)
    insert_cache_components(core_elem, config, stats)
    insert_btb_component(core_elem, config, stats)

def insert_noc_mc_components(system_elem, stats):
    # ---------- NoC0 ----------
    noc = ET.SubElement(system_elem, "component", id="system.NoC0", name="noc0")
    ET.SubElement(noc, "param", name="clockrate", value="1000")
    ET.SubElement(noc, "param", name="type", value="0")
    ET.SubElement(noc, "param", name="horizontal_nodes", value="1")
    ET.SubElement(noc, "param", name="vertical_nodes", value="1")
    ET.SubElement(noc, "param", name="has_global_link", value="0")
    ET.SubElement(noc, "param", name="link_throughput", value="1")
    ET.SubElement(noc, "param", name="link_latency", value="1")
    ET.SubElement(noc, "param", name="input_ports", value="1")
    ET.SubElement(noc, "param", name="output_ports", value="1")
    ET.SubElement(noc, "param", name="flit_bits", value="64")
    ET.SubElement(noc, "param", name="chip_coverage", value="1")
    ET.SubElement(noc, "param", name="link_routing_over_percentage", value="0.5")

    total_accesses = int(stats.get("system.membus.pktCount::total", 0))
    duty_cycle = round(
        stats.get("system.tol2bus.reqLayer0.occupancy", 0) /
        stats.get("system.mem_ctrl.dram.power_state.pwrStateResidencyTicks::UNDEFINED", 1),
        2
    )
    ET.SubElement(noc, "stat", name="total_accesses", value=str(total_accesses))
    ET.SubElement(noc, "stat", name="duty_cycle", value=str(duty_cycle))

    # ---------- Memory Controller ----------
    mc = ET.SubElement(system_elem, "component", id="system.mc", name="mc")
    ET.SubElement(mc, "param", name="type", value="1")
    ET.SubElement(mc, "param", name="mc_clock", value="400")
    ET.SubElement(mc, "param", name="peak_transfer_rate", value="6400")
    ET.SubElement(mc, "param", name="block_size", value="64")
    ET.SubElement(mc, "param", name="number_mcs", value="1")
    ET.SubElement(mc, "param", name="memory_channels_per_mc", value="1")
    ET.SubElement(mc, "param", name="number_ranks", value="1")
    ET.SubElement(mc, "param", name="req_window_size_per_channel", value="32")
    ET.SubElement(mc, "param", name="IO_buffer_size_per_channel", value="32")
    ET.SubElement(mc, "param", name="databus_width", value="128")
    ET.SubElement(mc, "param", name="addressbus_width", value="51")

    reads = int(stats.get("system.mem_ctrl.readReqs", 0))
    writes = int(stats.get("system.mem_ctrl.writeReqs", 0))
    ET.SubElement(mc, "stat", name="memory_accesses", value=str(reads + writes))
    ET.SubElement(mc, "stat", name="memory_reads", value=str(reads))
    ET.SubElement(mc, "stat", name="memory_writes", value=str(writes))


def insert_niu_pcie_flashc_components(system_elem):
    # ---------- NIU ----------
    niu = ET.SubElement(system_elem, "component", id="system.niu", name="niu")
    ET.SubElement(niu, "param", name="type", value="0")            # high performance
    ET.SubElement(niu, "param", name="clockrate", value="350")
    ET.SubElement(niu, "param", name="vdd", value="0")
    ET.SubElement(niu, "param", name="power_gating_vcc", value="-1")
    ET.SubElement(niu, "param", name="number_units", value="0")
    ET.SubElement(niu, "stat", name="duty_cycle", value="1.0")
    ET.SubElement(niu, "stat", name="total_load_perc", value="0.7")

    # ---------- PCIe ----------
    pcie = ET.SubElement(system_elem, "component", id="system.pcie", name="pcie")
    ET.SubElement(pcie, "param", name="type", value="0")           # high performance
    ET.SubElement(pcie, "param", name="withPHY", value="1")
    ET.SubElement(pcie, "param", name="clockrate", value="350")
    ET.SubElement(pcie, "param", name="vdd", value="0")
    ET.SubElement(pcie, "param", name="power_gating_vcc", value="-1")
    ET.SubElement(pcie, "param", name="number_units", value="0")
    ET.SubElement(pcie, "param", name="num_channels", value="8")
    ET.SubElement(pcie, "stat", name="duty_cycle", value="1.0")
    ET.SubElement(pcie, "stat", name="total_load_perc", value="0.7")

    # ---------- Flash Controller ----------
    flashc = ET.SubElement(system_elem, "component", id="system.flashc", name="flashc")
    ET.SubElement(flashc, "param", name="number_flashcs", value="0")
    ET.SubElement(flashc, "param", name="type", value="1")         # low power
    ET.SubElement(flashc, "param", name="withPHY", value="1")
    ET.SubElement(flashc, "param", name="peak_transfer_rate", value="200")
    ET.SubElement(flashc, "param", name="vdd", value="0")
    ET.SubElement(flashc, "param", name="power_gating_vcc", value="-1")
    ET.SubElement(flashc, "stat", name="duty_cycle", value="1.0")
    ET.SubElement(flashc, "stat", name="total_load_perc", value="0.7")


    


def create_base_xml(config, stats, tech_node, clockrate, machine_type):
    root_comp = ET.Element("component", id="root", name="root")
    system = config.get("system", {})
    system_elem = ET.SubElement(root_comp, "component", id=system.get("path", "system"), name=system.get("name", "system"))
    insert_core_and_directory_params(system_elem, config)
    insert_general_params(system_elem, tech_node, clockrate)
    insert_cycle_stats(system_elem, stats)
    insert_core_component(system_elem, clockrate, machine_type, stats, config)
    add_L1_L2_directories(system_elem, stats)
    insert_noc_mc_components(system_elem, stats)
    insert_niu_pcie_flashc_components(system_elem)
    return ET.ElementTree(root_comp)

def prettify_xml(tree):
    rough_string = ET.tostring(tree.getroot(), 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def write_xml(tree, output_path):
    pretty = prettify_xml(tree)
    with open(output_path, 'w') as f:
        f.write(pretty)
    print(f"✅ XML saved to {output_path}")

def main():
    config = read_config("files/config.json")
    stats = read_stats("files/stats.txt")
    print("🔧 Config & stats loaded.")
    tech_node = input("📥 Enter core technology node (nm): ").strip()
    clockrate = input("📥 Enter target core clockrate (MHz): ").strip()
    machine_type_str = input("📥 Enter CPU model (a7 / a15): ").strip().lower()
    machine_type = 1 if machine_type_str == "a7" else 0
    tree = create_base_xml(config, stats, tech_node, clockrate, machine_type)
    write_xml(tree, "infile.xml")

if __name__ == "__main__":
    main()
