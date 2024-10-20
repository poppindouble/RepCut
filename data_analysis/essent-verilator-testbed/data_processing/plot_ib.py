
import bench
import plot_config
import data_parser

emulatorGenerators = ['essent', 'verilator', 'commercial']

def plot_ib_factor(dat, showPlot, print_data = False):
    colors = plot_config.pick_colors(3)

    ib_source_markers = {
        'KaHyPar': '.',
        'Partition': 'v',
        'Measured': '*'
    }

    def draw_subfigure(ax, plot_x, plot_y):

        plot_dataset = ''
        if len(plot_config.plot_layout[plot_y]) > plot_x:
            plot_dataset = plot_config.plot_layout[plot_y][plot_x]
        if len(plot_dataset) == 0:
            print("Empty dataset")
            exit(-1)

        x_dat = bench.parallelThreads_profile[1:]

        def get_kahypar_ib(dataset, nThreads):
            raw_dat = []
            for tid in range(0, nThreads):
                raw_dat.append(dat.essent_log_data[dataset][nThreads]['KaHyPar Weight'][tid])
            return plot_config.calculate_ib_factor(raw_dat)

        def get_partition_ib(dataset, nThreads):
            raw_dat = []
            for tid in range(0, nThreads):
                raw_dat.append(dat.essent_log_data[dataset][nThreads]["Partitions"][tid]['weight'])
            return plot_config.calculate_ib_factor(raw_dat)

        def get_measured_ib(dataset, nThreads):
            raw_dat = []
            for tid in range(0, nThreads):
                eval_ticks = dat.essent_profile_data[dataset][nThreads][tid][data_parser.EVAL_DONE] - dat.essent_profile_data[dataset][nThreads][tid][data_parser.CYCLE_START]
                raw_dat.append(eval_ticks)
            return plot_config.calculate_ib_factor(raw_dat)

        # After KaHyPar: Exclude Replication
        y_dat = list(map(lambda x: get_kahypar_ib(plot_dataset, x), x_dat))
        ax.plot(x_dat, y_dat, '-', label = 'Excluding Replication', marker = ib_source_markers['KaHyPar'], color=colors[0])

        y_dat = list(map(lambda x: get_partition_ib(plot_dataset, x), x_dat))
        ax.plot(x_dat, y_dat, '-', label = 'Including Replication', marker = ib_source_markers['Partition'], color=colors[1])

        y_dat = list(map(lambda x: get_measured_ib(plot_dataset, x), x_dat))
        ax.plot(x_dat, y_dat, '-', label = 'Measured', marker = ib_source_markers['Measured'], color=colors[2])

        if print_data:
            str_dat = ", ".join(map(lambda x: "%st: %.2f" % x, zip(x_dat, y_dat)))
            print("%s, %s" % (plot_dataset, str_dat))




    # plot_config.plot_framework(draw_subfigure, y_max = 1.2, y_major_step=0.2, y_minor_step=0.05, showPlot = showPlot, hasLinear = False, x_text="# of Cores", y_text="Imbalance Factor", savePlotFile='imbalance.pdf')


    plot_config.plot_framework(draw_subfigure, y_max = 0.88, y_major_step=0.2, y_minor_step=0.05, x_max = 25, showPlot = showPlot, hasLinear = False, x_text="# of Cores", savePlotFile='imbalance.pdf', legend_fontsize=8, custom_figsize=(6, 5), legend_pos=[(2, 3)])

    

if __name__ == '__main__':
    import bench
    from data_parser import DataParser, deserialize_pickle_z

    # load data
    dat = deserialize_pickle_z("parsed_data.pickle.z")

    plot_ib_factor(dat, showPlot = True, print_data=True)


