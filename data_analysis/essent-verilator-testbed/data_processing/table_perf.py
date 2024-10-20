#!/bin/env python3

import bench
import plot_config

def get_analysis_data(log_dat, real_dat, design, nthread, event):
    perf_dat = real_dat[design][nthread]
    if event == 'IPC':
        nInst = perf_dat['instructions']
        nCycles = perf_dat['cycles']
        return "{:.2f}".format(nInst / nCycles)
    
    if event == 'Extra Inst':
        if nthread == 1:
            return "-"
        baseline_inst = log_dat.perf_data['essent'][design][1]['instructions']
        nInst = perf_dat['instructions']
        extra_inst_percentage = (nInst - baseline_inst) * 100 / baseline_inst
        return "{:.2f}\\%".format(extra_inst_percentage)

    if event == 'Replication':
        if nthread == 1:
            return "-"
        
        weight_rep_cost = log_dat.essent_log_data[design][nthread]['weight_replication_cost']
        return "{:.2f}\\%".format(weight_rep_cost)

    if event == 'branch miss rate':
        nBranch = perf_dat['branches']
        nBranchMisses = perf_dat['branch-misses']

        branchMissRate = nBranchMisses * 100 / nBranch

        return "{:.2f}\\%".format(branchMissRate)

def print_table_latex(log_dat, config, events):


    table_width = 2 + len(config)

    print(r"\begin{tabular}{l|l|%s}" % ("|".join(['r' for i in range(0, len(config))])))
    print(r"\hline")



    title = [r'\multicolumn{2}{c|}{\textbf{Perf Event}}']

    for design, numa_type, nthread in config:
        if nthread == 1:
            name = '1 Thread'
        else:
            name = '%s Threads' % (nthread)
        title.append(name)

    title_fmt = map(lambda x:"\\textbf{%s}" % (x), title[1:])

    print(title[0] + r" & " + r" & ".join(title_fmt) + r" \\")


    title_2 = [r'\multicolumn{2}{c|}{}']
    for design, numa_type, nthread in config:
        name = "\\textbf{%s}" % ("Interleaved" if numa_type == 'cross' else "Same")
        title_2.append(name)
    print(r" & ".join(title_2) + r" \\")


    print(r"\hline")
    print(r"\hline")


    cline_start = 2
    cline_max = table_width

    
    
    for category in events.keys():
        is_first_line = True
        num_of_rows = len(events[category])

        for event_id, event in enumerate(events[category]):
            dat = []
            for design, numa_type, nthread in config:

                if numa_type == 'cross':
                    real_dat = log_dat.cross_socket_perf_data['essent']
                else:
                    real_dat = log_dat.perf_data['essent']


                if category != 'Analysis':
                    event_num = real_dat[design][nthread][event]
                    fmt_str = "{:,}M".format(int(event_num / 1000000)) if isinstance(event_num, int) else "{:.2f}s".format(event_num)
                else:
                    fmt_str = get_analysis_data(log_dat, real_dat, design, nthread, event)
                
                dat.append(fmt_str)
            
            # Write latex
            head_cell = ''
            if is_first_line:
                head_cell = r"\multirow{%s}{*}{\rotatebox[origin=c]{90}{%s}}" % (num_of_rows, category)

            event_name = plot_config.event_pretty_name[event]
            print(" & ".join([head_cell, event_name, *dat]) + r" \\")
            if event_id != num_of_rows - 1:
                print(r"\cline{%s-%s}" % (cline_start, cline_max))
            else:
                print(r"\hline")
            is_first_line = False

    # Analysis
    # IPC, replication, extra instruction,cache miss rate, ...

    print(r"\end{tabular}")





plot_perf_events = {
    "Cache": [
        "L1-icache-load-misses",
        "L1-dcache-load-misses", 
        "L1-dcache-loads", 
        "L1-dcache-stores", 
        "l2_rqsts.code_rd_miss",
        "l2_rqsts.code_rd_hit",
        "l2_rqsts.pf_miss",
        "l2_rqsts.pf_hit",
        "l2_rqsts.all_demand_miss", 
        "l2_rqsts.all_demand_data_rd", 
        "l2_rqsts.miss",

        "LLC-load-misses",
        "LLC-loads",
        "LLC-store-misses",
        "LLC-stores",

        # "llc_misses.mem_read",
        # "llc_misses.mem_write",
        # "unc_m_rpq_inserts",
        # "unc_m_rpq_occupancy",
        # "unc_m_tagchk.hit",
        # "unc_m_tagchk.miss_clean",
        # "unc_m_tagchk.miss_dirty",
        # "unc_m_wpq_inserts", 
        # "unc_m_wpq_occupancy",
    ],

    "Branch": [
        "instructions",
        "branch-misses", 
        "branches",
        # "baclears.any", 
        # "br_inst_retired.all_branches", 
        # "br_misp_retired.all_branches", 
        # "br_inst_retired.conditional", 
        # "br_misp_retired.conditional", 
        # "br_inst_retired.near_call", 
        # "br_misp_retired.near_call", 
    ],

    "Pipeline": [
        # "lsd.uops",
        "topdown-fetch-bubbles", 
        # "topdown-recovery-bubbles", 
        # "dsb2mite_switches.penalty_cycles", 
        "icache_16b.ifdata_stall", 
        "icache_64b.iftag_stall", 

        # Decode path. Decode is not bottleneck
        # "idq.dsb_cycles", 
        # "idq.mite_cycles", 
        # "idq.all_dsb_cycles_any_uops", 
        # "idq.all_mite_cycles_any_uops", 
        # "int_misc.clear_resteer_cycles",
    ],

    "Misc": [
        "time_total",
        "time_user"
    ],

    "Analysis": [
        'IPC',
        'branch miss rate',
        'Extra Inst',
        'Replication',
    ]
}




if __name__ == '__main__':
    from data_parser import DataParser, deserialize_pickle_z

    # load data
    dat = deserialize_pickle_z("parsed_data.pickle.z")

    columns = [
        ('boom21-4mega', 'local', 1),
        ('boom21-4mega', 'local', 4),
        ('boom21-4mega', 'local', 8),
        ('boom21-4mega', 'local', 16),
        ('boom21-4mega', 'local', 24),


        ('boom21-4mega', 'cross', 4),
        ('boom21-4mega', 'cross', 8),
        ('boom21-4mega', 'cross', 16),
        ('boom21-4mega', 'cross', 24),
        # ('boom21-4mega', 'cross', 32),
        ('boom21-4mega', 'cross', 48),
    ]

    table_dat = print_table_latex(dat, columns, events = plot_perf_events)



