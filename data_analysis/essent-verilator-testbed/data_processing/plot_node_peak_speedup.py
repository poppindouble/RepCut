#!/bin/env python3

import bench
import plot_config
import matplotlib.pyplot as plt


emulatorGenerators = ['essent', 'essent_no-weight', 'verilator', 'verilator_pgo2']


def get_x_tick_text(num):
    if num < 1000:
        return str(num)
    if num < 1000000:
        return "%sK" % int(num / 1000)
    return "{:.1f}M".format(num / 1000000)

def plot_node_peak_speedup(dat, showPlot = False, printData = False, savePlotFile = 'peak_speedup_node_count.pdf'):

    figsize = (5, 2.1)
    
    colors = [
        plot_config.simulator_colors[gen] for gen in emulatorGenerators
    ]

    fig, ax = plt.subplots(figsize = figsize)

    max_ir_nodes = 0

    for i, gen in enumerate(emulatorGenerators):
        x_dat_raw = []
        y_dat_raw = []
        for design in bench.benchmarkProjects:
            design_firrtl_nodes = dat.essent_log_data[design][1]['Valid Nodes']
            design_speedup = list(map(lambda x: x[1], dat.speedup_data[gen][design]))
            design_peak_speedup = max(design_speedup)

            if printData:
                print("{:}, Design: {:}: FIRRTL IR node: {:,}, Peak speedup {:.2f}x".format(gen, design, design_firrtl_nodes, design_peak_speedup))
            
            x_dat_raw.append(design_firrtl_nodes)
            y_dat_raw.append(design_peak_speedup)
            max_ir_nodes = max(max_ir_nodes, design_firrtl_nodes)
        sorted_data = list(sorted(zip(x_dat_raw, y_dat_raw), key=lambda x: x[0]))
        x_dat = list(map(lambda x:x[0], sorted_data))
        y_dat = list(map(lambda x:x[1], sorted_data))
        # data ready
        ax.plot(x_dat, y_dat, '-', label = plot_config.generator_pretty_name[gen], marker = plot_config.generator_markers[gen], color = colors[i], zorder=len(emulatorGenerators) - i)

    ax.set_ylabel("Peak Speedup (x)")
    ax.set_xlabel("# of FIRRTL Nodes")

    x_step = 200000
    x_tick_count = int(max_ir_nodes / x_step) + 1
    x_ticks = list(range(0, max_ir_nodes + 1, x_step))
    ax.xaxis.set_ticks(x_ticks)
    
    ax_x_labels = [get_x_tick_text(x) for x in x_ticks]
    ax.xaxis.set_ticklabels(ax_x_labels)

    ax.legend(fontsize=8, loc='upper left')

    plt.tight_layout()

    if savePlotFile != '':
        plt.savefig(savePlotFile)

    if showPlot:
        plt.show()





if __name__ == '__main__':
    from data_parser import DataParser, deserialize_pickle_z

    # load data
    dat = deserialize_pickle_z("parsed_data.pickle.z")


    table_dat = plot_node_peak_speedup(dat, True, True)



