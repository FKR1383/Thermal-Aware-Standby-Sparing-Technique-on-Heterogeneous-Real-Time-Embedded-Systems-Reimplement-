import os
import re
import math


CORE_TYPE = input("Enter core type (a7/a15): ").strip().lower()

def read_mcpat_output(filename="output.txt"):
    if not os.path.exists(filename):
        print(f"❌ File {filename} not found.")
        return []
    with open(filename, "r") as f:
        return f.readlines()

def extract_t_chip(lines):
    for line in lines:
        if "Technology" in line:
            parts = line.split()
            for p in parts:
                if p.isdigit():
                    tech = int(p)
                    return {90:0.00020,45:0.00015,32:0.00013,28:0.00015,14:0.00010,7:0.00007}.get(tech,0.00015)
    return 0.00015

def extract_base_proc_freq(lines):
    for line in lines:
        if "Core clock Rate" in line:
            m = re.search(r'(\d+)', line)
            if m:
                return int(m.group(1)) * 1e6
    return 3e9


# نام‌های بلوک‌ها
STANDARD_NAMES = [
    "L2",
    "Icache", "Dcache",
    "Bpred_0",
    "DTB_0",
    "FPAdd_0", "FPAdd_1",
    "FPReg_0", "FPReg_1", "FPReg_2", "FPReg_3",
    "FPMul_0", "FPMul_1",
    "FPMap_0", "FPMap_1",
    "IntMap", "IntQ",
    "IntReg_0", "IntReg_1",
    "IntExec", "FPQ", "LdStQ",
    "ITB_0"
]

def read_mcpat_output(filename="output.txt"):
    with open(filename, "r") as f:
        return f.readlines()

def find_area(lines, key):
    for i, line in enumerate(lines):
        if key in line and "Area" in line:
            m = re.search(r'Area\s*=\s*([\d\.]+)\s*mm', lines[i])
            if m:
                return float(m.group(1)) * 1e-6
    return 0.000001

def build_ptrace(lines, blocks, ptrace_file="power.ptrace", cycles=100):
    power_map = {}

    def get_block_power(block_name):
        # توی output.txt دنبال بلوک بگرد
        for i, line in enumerate(lines):
            if block_name in line:
                # Peak Dynamic رو بگیر
                if "Peak Dynamic" in lines[i+1]:
                    m = re.search(r'([\d\.]+)', lines[i+1])
                    if m:
                        return float(m.group(1))
                # اگر نبود، جمع بقیه توان‌ها
                total = 0.0
                for j in range(1, 5):
                    if i+j < len(lines):
                        m = re.search(r'([\d\.]+)', lines[i+j])
                        if m:
                            total += float(m.group(1))
                return total
        return 0.05  # مقدار پیش‌فرض

    # توان هر بلوک رو پیدا کن
    for block in blocks:
        if "FPReg" in block:
            power_map[block] = get_block_power("Floating Point RF") / 4.0
        elif "IntReg" in block:
            power_map[block] = get_block_power("Integer RF") / 2.0
        elif "FPAdd" in block or "FPMul" in block or "FPMap" in block:
            power_map[block] = get_block_power("Floating Point Units (FPUs)") / 2.0
        elif "Bpred" in block:
            power_map[block] = (get_block_power("Global Predictor") +
                                get_block_power("L1_Local Predictor") +
                                get_block_power("L2_Local Predictor")) / 3.0
        else:
            power_map[block] = get_block_power(block)

    # نوشتن ptrace
    with open(ptrace_file, "w") as f:
        f.write("\t".join(blocks) + "\n")
        row = "\t".join([f"{power_map[b]:.3f}" for b in blocks])
        for _ in range(cycles):
            f.write(row + "\n")

    print(f"✅ Power trace created: {ptrace_file}")


def build_flp(lines, flp_file="floorplan.flp"):
    area_map = {}

    # L2 = مجموع سه بخش
    area_map["L2"] = (find_area(lines, "Second Level Directory") +
                      find_area(lines, "L2") +
                      find_area(lines, "L2_Local Predictor"))

    area_map["Icache"] = find_area(lines, "Instruction Cache")
    area_map["Dcache"] = find_area(lines, "Data Cache")

    # Branch predictor = مجموع سه بخش
    area_map["Bpred_0"] = (find_area(lines, "Global Predictor") +
                           find_area(lines, "L1_Local Predictor") +
                           find_area(lines, "L2_Local Predictor"))

    area_map["DTB_0"] = find_area(lines, "Dtlb")

    # FPUs تقسیم به 2
    fp_area = find_area(lines, "Floating Point Units (FPUs)")
    area_map["FPAdd_0"] = area_map["FPAdd_1"] = fp_area / 2
    area_map["FPMul_0"] = area_map["FPMul_1"] = fp_area / 2
    area_map["FPMap_0"] = area_map["FPMap_1"] = fp_area / 2

    # FP Reg تقسیم به 4
    fpreg_area = find_area(lines, "Floating Point RF")
    for i in range(4):
        area_map[f"FPReg_{i}"] = fpreg_area / 4

    # IntMap از Complex ALUs
    area_map["IntMap"] = find_area(lines, "Complex ALUs")

    # IntReg تقسیم به 2
    intreg_area = find_area(lines, "Integer RF")
    area_map["IntReg_0"] = area_map["IntReg_1"] = intreg_area / 2

    # IntExec از Instruction Window
    area_map["IntExec"] = find_area(lines, "Instruction Window")

    # IntQ از Instruction Scheduler
    area_map["IntQ"] = find_area(lines, "Instruction Scheduler")

    # FPQ از FP Instruction Window
    area_map["FPQ"] = find_area(lines, "FP Instruction Window")

    # LdStQ از StoreQ
    area_map["LdStQ"] = find_area(lines, "StoreQ")

    # ITB_0 از Itlb
    area_map["ITB_0"] = find_area(lines, "Itlb")

    # ساخت فایل floorplan
    total_area = sum(area_map.values())
    max_chip_width = math.sqrt(total_area)
    x_offset = y_offset = row_height = 0.0

    with open(flp_file, "w") as f:
        f.write("#name width height x y\n")
        for name in STANDARD_NAMES:
            area = area_map.get(name, 1e-6)
            width = height = math.sqrt(area)

            if x_offset + width > max_chip_width:
                x_offset = 0.0
                y_offset += row_height
                row_height = 0.0

            f.write(f"{name} {width:.6f} {height:.6f} {x_offset:.6f} {y_offset:.6f}\n")
            x_offset += width
            row_height = max(row_height, height)

    print(f"✅ Floorplan created: {flp_file}")

def write_config_file(t_chip, base_proc_freq, init_temp, output_config="hotspot_config.txt"):
    with open(output_config, "w") as f:
        f.write("# HotSpot configuration file\n\n")
        f.write("# thermal model parameters\n\n")

        # chip specs
        f.write("# chip specs\n")
        f.write(f"-t_chip {t_chip:.8f}\n")
        f.write(f"-k_chip 130.0\n")
        f.write(f"-p_chip 1630300\n\n")

        # heat sink specs
        f.write("# heat sink specs\n")
        f.write(f"-c_convec 140.4\n")
        f.write(f"-r_convec 0.1\n")
        f.write(f"-s_sink 0.06\n")
        f.write(f"-t_sink 0.0069\n")
        f.write(f"-k_sink 400.0\n")
        f.write(f"-p_sink 3.55e6\n\n")

        # heat spreader specs
        f.write("# heat spreader specs\n")
        f.write(f"-s_spreader 0.03\n")
        f.write(f"-t_spreader 0.001\n")
        f.write(f"-k_spreader 400.0\n")
        f.write(f"-p_spreader 3.55e6\n\n")

        # interface material specs
        f.write("# interface material specs\n")
        f.write(f"-t_interface 2.0e-05\n")
        f.write(f"-k_interface 4.0\n")
        f.write(f"-p_interface 4.0e6\n\n")

        # secondary path
        f.write("# secondary path\n")
        f.write(f"-model_secondary 0\n")
        f.write(f"-r_convec_sec 50.0\n")
        f.write(f"-c_convec_sec 40.0\n")
        f.write(f"-n_metal 8\n")
        f.write(f"-t_metal 100.0e-6\n")
        f.write(f"-t_c4 0.0001\n")
        f.write(f"-s_c4 20.0e-6\n")
        f.write(f"-n_c4 400\n")
        f.write(f"-s_sub 0.021\n")
        f.write(f"-t_sub 0.001\n")
        f.write(f"-s_solder 0.021\n")
        f.write(f"-t_solder 0.00094\n")
        f.write(f"-s_pcb 0.1\n")
        f.write(f"-t_pcb 0.002\n\n")

        # others
        f.write("# others\n")
        f.write(f"-ambient {init_temp}\n")
        f.write(f"-init_file (null)\n")
        f.write(f"-init_temp {init_temp}\n")
        f.write(f"-steady_file (null)\n")
        f.write(f"-sampling_intvl 0.01\n")
        f.write(f"-base_proc_freq {base_proc_freq}\n")
        f.write(f"-dtm_used 0\n")
        f.write(f"-model_type block\n")
        f.write(f"-leakage_used 0\n")
        f.write(f"-leakage_mode 0\n")
        f.write(f"-package_model_used 0\n")
        f.write(f"-package_config_file package.config\n\n")

        # block model specific
        f.write("# block model specific parameters\n")
        f.write(f"-block_omit_lateral 0\n\n")

        # grid model specific
        f.write("# grid model specific parameters\n")
        f.write(f"-grid_rows 39\n")
        f.write(f"-grid_cols 39\n")
        f.write(f"-grid_layer_file (null)\n")
        f.write(f"-grid_steady_file (null)\n")
        f.write(f"-grid_map_mode avg\n\n")

        # microfluidic cooling parameters
        f.write("# microfluidic cooling parameters\n")
        f.write(f"-use_microfluidic_cooling 0\n")
        f.write(f"-pumping_pressure 52000\n")
        f.write(f"-pump_internal_res 0\n")
        f.write(f"-inlet_temperature 298.15\n")
        f.write(f"-coolant_material water\n")
        f.write(f"-wall_material silicon\n")
        f.write(f"-htc 27132\n\n")

        # floorplanner parameters
        f.write("# floorplanner parameters\n")
        f.write(f"-wrap_l2 1\n")
        f.write(f"-l2_label L2\n")
        f.write(f"-model_rim 0\n")
        f.write(f"-rim_thickness 5e-05\n")
        f.write(f"-compact_ratio 0.005\n")
        f.write(f"-n_orients 300\n")
        f.write(f"-P0 0.99\n")
        f.write(f"-Davg 1\n")
        f.write(f"-Kmoves 7\n")
        f.write(f"-Rcool 0.99\n")
        f.write(f"-Rreject 0.99\n")
        f.write(f"-Nmax 1000\n")
        f.write(f"-lambdaA 5.0e+06\n")
        f.write(f"-lambdaT 1\n")
        f.write(f"-lambdaW 350\n")

    print(f"✅ Config file {output_config} created with full parameters")

def write_example_materials(filename="example.materials"):
    content = """# Format:
#
# material name
# material type (solid or fluid)
# thermal conductivity in W/(m-K)
# volumetric heat capacity in J/(m^3-K)
# dynamic viscosity in Pa-s (fluid only)

silicon
solid
130.0
1630300

water
fluid
0.6069
4172638
8.89e-4

aluminum
solid
237.0
2.422e6
"""
    with open(filename, "w") as f:
        f.write(content)
    print(f"✅ File {filename} created successfully.")




if __name__ == "__main__":
    lines = read_mcpat_output("output.txt")
    if lines:
        t_chip = extract_t_chip(lines)
        base_proc_freq = extract_base_proc_freq(lines)
        init_temp = float(input("Enter initial temperature (K): "))

        write_config_file(t_chip, base_proc_freq, init_temp)
        build_flp(lines)
        build_ptrace(lines, STANDARD_NAMES)
        write_example_materials()
