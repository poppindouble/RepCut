#!/usr/bin/env python3


import os
import re
import time
import json
import logging
import subprocess


# benchmarks = ['dhrystone.riscv']

emulatorGenerators = [
    'essent', 
    'essent_no-weight',
    'verilator',
    'verilator_pgo2'
]

emulatorGenerators_no_sequential = [
    'essent_no-weight',
    'verilator_pgo2'
]

emulatorGenerators_baseline = {
    'essent': 'essent',
    'verilator': 'verilator',
    'essent_no-weight': 'essent',
    'verilator_pgo2': 'verilator'
}

benchmarkProjects_cross_socket = [
    'boom21-mega',
    'boom21-2mega',
    'boom21-4mega'
]

benchmarkProjects_perf = [
    'boom21-4mega'
]

benchmarkProjects = [
    'rocket21-1c',
    'rocket21-2c',
    'rocket21-4c',
    'boom21-small',
    'boom21-large',
    'boom21-mega',
    'boom21-2small',
    'boom21-2large',
    'boom21-2mega',
    'boom21-4small',
    'boom21-4large',
    'boom21-4mega',
]
# This machine has 2 sockets, each socket has 24 physical core
parallelThreads = [1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 32, 48]

parallelThreads_profile = [1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24]

parallelThreads_cross_socket = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24]
iterations = 1

perf_events = [
    "cycles",

    "L1-icache-load-misses",
    "l2_rqsts.code_rd_hit",
    "l2_rqsts.code_rd_miss",
    "l2_rqsts.miss",
    "l2_rqsts.pf_hit",
    "l2_rqsts.pf_miss",
    "LLC-load-misses",
    "LLC-loads",
    "LLC-store-misses",
    "LLC-stores",

    # # [read requests to memory controller. Derived from unc_m_cas_count.rd. Unit: uncore_imc]
    # "llc_misses.mem_read",
    # # [write requests to memory controller. Derived from unc_m_cas_count.wr. Unit: uncore_imc]
    # "llc_misses.mem_write",

    # # [Read Pending Queue Allocations. Unit: uncore_imc]
    # "unc_m_rpq_inserts",
    # # [Read Pending Queue Occupancy. Unit: uncore_imc]
    # "unc_m_rpq_occupancy",
    # # [All hits to Near Memory(DRAM cache) in Memory Mode. Unit: uncore_imc]
    # "unc_m_tagchk.hit",
    # # [All Clean line misses to Near Memory(DRAM cache) in Memory Mode. Unit: uncore_imc]
    # "unc_m_tagchk.miss_clean",
    # # [All dirty line misses to Near Memory(DRAM cache) in Memory Mode. Unit: uncore_imc]
    # "unc_m_tagchk.miss_dirty",
    # # [Write Pending Queue Allocations. Unit: uncore_imc]
    # "unc_m_wpq_inserts", 
    # # [Write Pending Queue Occupancy. Unit: uncore_imc]
    # "unc_m_wpq_occupancy",
    

    "instructions",
    "branches",
    "branch-misses", 
    # Counts the total number when the front end is resteered, mainly when the BPU cannot provide a correct prediction and this is corrected by other branch handling mechanisms at the front end
    # "baclears.any", 
    # All (macro) branch instructions retired Spec update: SKL091
    # "br_inst_retired.all_branches", 
    # All mispredicted macro branch instructions retired
    # "br_misp_retired.all_branches", 
    # Conditional branch instructions retired Spec update: SKL091 (Precise event)
    # "br_inst_retired.conditional", 
    # Mispredicted conditional branch instructions retired (Precise event)
    # "br_misp_retired.conditional", 
    # Direct and indirect near call instructions retired Spec update: SKL091 (Precise event)
    # "br_inst_retired.near_call", 
    # Mispredicted direct and indirect near call instructions retired (Precise event)
    # "br_misp_retired.near_call", 

    # Number of Uops delivered by the LSD
    # "lsd.uops",

    # "cycle_activity.stalls_total",
    # "cycle_activity.stalls_mem_any",
    # "resource_stalls.any",

    # [Cycles when Reservation Station (RS) is empty for the thread]
    # "rs_events.empty_cycles",
    
    # [Counts end of periods where the Reservation Station (RS) was empty. Could be useful to precisely locate Frontend Latency Bound issues]
    # "rs_events.empty_end",
       

    # Pipeline gaps in the frontend
    "topdown-fetch-bubbles", 
    # Pipeline gaps during recovery from misspeculation
    # "topdown-recovery-bubbles", 
    # Decode Stream Buffer (DSB)-to-MITE switch true penalty cycles
    # "dsb2mite_switches.penalty_cycles", 
    # Cycles where a code fetch is stalled due to L1 instruction cache miss
    "icache_16b.ifdata_stall", 
    # Instruction fetch tag lookups that hit in the instruction cache (L1I). Counts at 64-byte cache-line granularity
    "icache_64b.iftag_stall", 

    # Cycles when uops are being delivered to Instruction Decode Queue (IDQ) from Decode Stream Buffer (DSB) path
    # "idq.dsb_cycles", 
    # Cycles when uops are being delivered to Instruction Decode Queue (IDQ) from MITE path
    # "idq.mite_cycles", 
    # Cycles Decode Stream Buffer (DSB) is delivering any Uop
    # "idq.all_dsb_cycles_any_uops", 
    # Cycles MITE is delivering any Uop
    # "idq.all_mite_cycles_any_uops", 
    # Cycles the issue-stage is waiting for front-end to fetch from resteered path following branch misprediction or machine clear events
    # "int_misc.clear_resteer_cycles",

    "L1-dcache-load-misses", 
    "L1-dcache-loads", 
    "L1-dcache-stores", 
    "l2_rqsts.all_demand_data_rd", 
    "l2_rqsts.all_demand_miss", 
    # "mem_load_retired.l1_hit", 
    # "mem_load_retired.l1_miss", 
    # "mem_load_retired.l2_hit", 
    # "mem_load_retired.l2_miss"
]

CPU_TICK_RATE = 2394620000

def get_cpu_tick_rate():
    file_path = os.path.split(os.path.realpath(__file__))[0]
    tick_rate_file_name = "cpu_tick_rate.txt"

    tick_rate_file = os.path.join(file_path, tick_rate_file_name)
    with open(tick_rate_file) as f:
        for line in f:
            # only first line
            CPU_TICK_RATE = int(re.findall("\d+", line)[0])
            print("Find CPU tick rate at " + str(CPU_TICK_RATE))

get_cpu_tick_rate()

def tick_to_us(ticks):
    return ticks * 1000 * 1000 / CPU_TICK_RATE



# * Instruction fetch (most important)
# L1-icache-load-misses,l2_rqsts.code_rd_hit,l2_rqsts.code_rd_miss,l2_rqsts.miss,l2_rqsts.pf_hit,l2_rqsts.pf_miss

# * Branches (next most important)
# branches,branch-misses,baclears.any,br_inst_retired.all_branches,br_misp_retired.all_branches,br_inst_retired.conditional,br_misp_retired.conditional,br_inst_retired.near_call,br_misp_retired.near_call, baclears.any

# * Decoding (lower importance)
# topdown-fetch-bubbles,topdown-recovery-bubbles,dsb2mite_switches.penalty_cycles,icache_16b.ifdata_stall,icache_64b.iftag_stall,idq.dsb_cycles,idq.mite_cycles,idq.all_dsb_cycles_any_uops,idq.all_mite_cycles_any_uops,int_misc.clear_resteer_cycles

# * Data flow (least important)
# L1-dcache-load-misses,L1-dcache-loads,L1-dcache-stores,l2_rqsts.all_demand_data_rd,l2_rqsts.all_demand_miss,mem_load_retired.l1_hit,mem_load_retired.l1_miss,mem_load_retired.l2_hit,mem_load_retired.l2_miss




