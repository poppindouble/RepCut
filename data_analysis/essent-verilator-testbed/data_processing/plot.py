
import sys

import bench
from data_parser import DataParser, deserialize_pickle_z


import plot_speedup_4by3
import plot_sim_speed
import plot_replication_cost_4by1
import plot_ib
import plot_ib_4by3
import plot_exec_profile
import plot_cross_socket_speedup
import plot_node_peak_speedup
import plot_ib_speedup


import plot_essent_gantt_combined
import plot_verilator_gantt_combined

import table_design

showPlot = False


if __name__ == '__main__':
    noPGO = True

    options = ['no_pgo', 'with_pgo']
    if sys.argv[1] in options:
        if sys.argv[1] != 'no_pgo':
            noPGO = False
    else:
        print("Error: Please choose from " + str(options))
        exit(-1)

    if noPGO:
        bench.emulatorGenerators = [
            'essent', 
            'essent_no-weight',
            'verilator'
        ]
    
    # load data
    dat = deserialize_pickle_z("parsed_data.pickle.z")



    # Figure 7
    # Output: speedup_4by3.pdf
    if noPGO:
        plot_speedup_4by3.emulatorGenerators = ['essent', 'essent_no-weight', 'verilator']
    plot_speedup_4by3.plot_speedup_4by3(dat, False)


    # Figure 9
    # Output: sim_speed.pdf
    if noPGO:
        plot_sim_speed.emulatorGenerators = ['essent', 'essent_no-weight', 'verilator']
    plot_sim_speed.plot_sim_speed(dat, False)


    # Figure 6
    # Output: replication_cost_4by1.pdf
    plot_replication_cost_4by1.plot_replication_cost_simple(dat, False)

    
    # Figure 13
    # Output: imbalance_4by3.pdf
    plot_ib_4by3.plot_ib_factor_4by3(dat, False)

    # Figure 10
    # Output: cross_socket_speedup_2.pdf
    plot_cross_socket_speedup.plot_cross_socket_speedup(dat, showPlot=False)
    
    # Figure 11
    # Output: exec_profile.pdf
    plot_exec_profile.plot_exec_profile('rocket21-4c', 12, 'boom21-4large', 12)

    # Figure 8
    # Output: peak_speedup_node_count.pdf
    if noPGO:
        plot_node_peak_speedup.emulatorGenerators = ['essent', 'essent_no-weight', 'verilator']
    plot_node_peak_speedup.plot_node_peak_speedup(dat, showPlot=False)

    # Figure 12
    # Output: ib_speedup.pdf
    plot_ib_speedup.plot_ib_speedup(dat, showPlot=False)

    # Figure 2b
    # Output: essent_gantt_heatmap_combined.pdf
    plot_essent_gantt_combined.plot_essent_gantt(dat, showPlot = False, savePlotFile='essent_gantt_heatmap_combined.pdf')

    # Figure 2a
    # Output: verilator_gantt_heatmap_combined.pdf
    plot_verilator_gantt_combined.plot_verilator_gantt(dat, showPlot = False, savePlotFile='verilator_gantt_heatmap_combined.pdf')




