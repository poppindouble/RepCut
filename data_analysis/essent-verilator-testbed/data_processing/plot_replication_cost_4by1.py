
import bench
import plot_config

emulatorGenerators = ['essent', 'verilator', 'commercial']



import plot_config
from data_parser import DataParser, deserialize_pickle_z
import statistics

import matplotlib.pyplot as plt

def plot_replication_cost_simple(dat, showPlot, savePlotFile='replication_cost_4by1.pdf', print_data = False):

    cost_metric = 'weight'
    colors = plot_config.pick_colors(3)

    plot_layout = {
        "RocketChip": {
            1: "rocket21-1c",
            2: "rocket21-2c",
            4: "rocket21-4c"
        },
        "SmallBoom": {
            1: "boom21-small",
            2: "boom21-2small",
            4: "boom21-4small"
        },
        "LargeBoom": {
            1: "boom21-large",
            2: "boom21-2large",
            4: "boom21-4large"
        },
        "MegaBoom": {
            1: "boom21-mega",
            2: "boom21-2mega",
            4: "boom21-4mega"
        },
    }

    design_markers = {
        1: '.',
        2: 'v',
        4: '*'
    }

    figsize = (11, 2)
    y_max = 30

    fig, axes = plt.subplots(nrows=1, ncols=4, figsize=figsize, sharex=True, sharey=True)

    x_dat = bench.parallelThreads[1:]

    for pos in range(0, 4):
        ax = axes[pos]

        chip_name = list(plot_layout.keys())[pos]

        for i, nCores in enumerate(plot_layout[chip_name].keys()):
            design_name = plot_layout[chip_name][nCores]      

            # y_dat = list(map(lambda x: dat.essent_log_data[design_name][x]['stmts_replication_cost'], x_dat))
            # ax.plot(x_dat, y_dat, '-', label = '%s Core(s)' % (nCores), marker = design_markers[nCores])

            y_dat = list(map(lambda x: dat.essent_log_data[design_name][x]['weight_replication_cost'], x_dat))
            ax.plot(x_dat, y_dat, '-', label = '%s Core(s)' % (nCores), marker = design_markers[nCores], color=colors[i])

            if print_data:
                str_dat = ", ".join(map(lambda x: ("%st: %.2f" % x) + "%", zip(x_dat, y_dat)))
                print("%s, %s" % (design_name, str_dat))

        if pos == 0:
            ax.set_ylabel("Replication Cost (%)")
            ax.set_ylim(0, y_max)


        ax.set_xlabel("# of Parallel Threads")
        ax.set_xlim(0, 50)

        ax.set_title(chip_name)

        if pos == 3:
            ax.legend(loc='upper left', fontsize = 9)
    plt.tight_layout()

    if savePlotFile != '':
        plt.savefig(savePlotFile)

    if showPlot:
        plt.show()



if __name__ == '__main__':
    import bench
    from data_parser import DataParser, deserialize_pickle_z

    # load data
    dat = deserialize_pickle_z("parsed_data.pickle.z")

    # plot_replication_cost(dat, showPlot = True)
    plot_replication_cost_simple(dat, showPlot = True, print_data=True)


