# Low Power Design Project: Thermal-Aware Standby-Sparing on Heterogeneous Real-Time Embedded Systems

## Overview
This project implements the **Thermal-Aware Standby-Sparing (TASS)** technique on heterogeneous real-time embedded systems. The approach focuses on improving **fault tolerance** and **thermal safety** while minimizing overall power consumption. Using a combination of **big (high-performance)** and **LITTLE (low-power)** cores, tasks are scheduled with both primary and spare execution to ensure deadline satisfaction under thermal and reliability constraints.

## Key Features
- **Standby-Sparing Scheduling**: Primary tasks execute on high-performance cores, while spare tasks are mapped to low-power cores to ensure reliability.
- **Thermal-Aware Design (TSP)**: Applies the Thermal Safe Power (TSP) constraint to limit the maximum peak power per cluster of cores.
- **Task Graph Modeling**: Generates task sets from MiBench benchmarks, modeled as Directed Acyclic Graphs (DAGs).
- **Offline Scheduler (TASS)**: Uses a Latest Deadline First (LDF)-based algorithm to schedule tasks while respecting thermal limits.
- **Runtime Scheduling**: Provides fault tolerance by executing backup tasks only if primary tasks fail.
- **Simulation Flow**: Integrates GEM5, McPAT, HotSpot, and QUILT simulators for WCET, power, and thermal profiling.

## Project Steps
1. **Task Graph Creation**: Generate DAG-based task sets using MiBench benchmarks.  
2. **Task Profiling**: Measure WCET and peak power on ARM Cortex-A7 (LITTLE) and Cortex-A15 (big) cores using GEM5.  
3. **Thermal Safe Power (TSP) Analysis**: Define safe peak power thresholds for both core types.  
4. **Offline Scheduling (TASS)**: Implement an LDF-based offline scheduler that respects task dependencies and TSP.  
5. **Simulation Tools**:  
   - GEM5 → WCET extraction  
   - McPAT → Power estimation  
   - HotSpot → Thermal simulation  
   - QUILT → Floorplan visualization  
6. **Runtime Scheduling**: Evaluate reliability and energy reduction by enabling Dynamic Power Management (DPM) on backup tasks.  
7. **Results Analysis**: Compare energy, peak power, and reliability metrics with and without the TASS approach.  

## Tools and Technologies
- **Python**: Task graph generation, schedulers, and simulation scripts.  
- **GEM5**: For WCET profiling on ARM Cortex-A7 and Cortex-A15.  
- **McPAT**: For detailed power estimation.  
- **HotSpot**: For thermal modeling and hotspot detection.  
- **QUILT**: For floorplan visualization.  
- **MiBench**: Benchmark suite used to generate realistic task graphs.  

## Results
- **Thermal Safety**: Ensured that system peak power never exceeded the TSP threshold.  
- **Fault Tolerance**: Achieved high reliability through spare execution while reducing backup task execution with DPM.  
- **Energy Efficiency**: Reduced overall power consumption by avoiding unnecessary execution of spare tasks.  
- **Reliability**: Primary tasks had a low probability of failure, and backup tasks successfully guaranteed deadlines when failures occurred.  


## Conclusion
This project demonstrates how a **thermal-aware standby-sparing approach** can improve both **reliability** and **thermal management** in heterogeneous embedded systems. By combining TSP constraints, fault-tolerant scheduling, and runtime optimization, the system achieves reduced peak power, high reliability, and better thermal stability.

For detailed implementation and source code, see the repository.
