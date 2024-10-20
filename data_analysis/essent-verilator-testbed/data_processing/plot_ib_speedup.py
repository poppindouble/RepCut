#!/bin/env python3

import bench
import plot_config
import data_parser
import matplotlib.pyplot as plt

processors_per_socket = 24

single_color = plot_config.pick_colors(4)[1]

line_color = plot_config.common_colors[7]
slow_color = plot_config.common_colors[3]
fast_color = plot_config.common_colors[2]

def plot_ib_speedup(dat, showPlot = False, printData = False, savePlotFile = 'ib_speedup.pdf'):

    figsize = (6, 2.5)


    def get_measured_ib(dataset, nThreads):
        raw_dat = []
        for tid in range(0, nThreads):
            eval_ticks = dat.essent_profile_data[dataset][nThreads][tid][data_parser.EVAL_DONE] - dat.essent_profile_data[dataset][nThreads][tid][data_parser.CYCLE_START]
            raw_dat.append(eval_ticks)
        return plot_config.calculate_ib_factor(raw_dat)


    fig, ax = plt.subplots(figsize = figsize)

    max_ib = 0


    for design in bench.benchmarkProjects:
        # if design in ['rocket21-1c']:
        #     continue
        ib_factors = []
        speedups = []

        design_speedups = dict(dat.speedup_data['essent'][design])

        for nthread in bench.parallelThreads:
            if nthread == 1 or nthread > processors_per_socket:
                continue

            ib = get_measured_ib(design, nthread)
            sp = design_speedups[nthread]
            ideal_speedup = nthread

            ib_factors.append(ib)
            speedups.append(sp / ideal_speedup)

            if printData:
                print("Design: {:}: ib: {:.2f}, speedup {:.2f}x".format(design, ib, sp))

        # data ready
        max_ib = max(max_ib, *ib_factors)

        colors = [fast_color if x >= 1 else slow_color for x in speedups]
        ax.scatter(ib_factors, speedups, label = design, c=colors)

    ax.plot([0, max_ib], [1, 1], '--', color=line_color)
    ax.set_ylabel("Parallelization Efficiency")
    # ax.set_ylabel("Speedup (x)")
    ax.set_xlabel("Imbalance Factor")

    # ax.legend()

    plt.tight_layout()

    if savePlotFile != '':
        plt.savefig(savePlotFile)

    if showPlot:
        plt.show()





if __name__ == '__main__':
    from data_parser import DataParser, deserialize_pickle_z

    # load data
    dat = deserialize_pickle_z("parsed_data.pickle.z")

    table_dat = plot_ib_speedup(dat, True, True)



