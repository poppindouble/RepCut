
import bench
import plot_config
import data_parser

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

emulatorGenerators = ['essent', 'verilator', 'commercial']

def plot_ib_factor_4by3(dat, showPlot, print_data = False):

    x_max = 25
    x_major_step = 4
    x_minor_step = 1
    y_max = 0.78
    y_major_step = 0.3
    y_minor_step = 0.06


    title_fontsize = 9
    ylabel_fontsize = 9
    xlabel_fontsize = 9
    ticklabel_fontsize = 9
    legend_fontsize = 9

    colors = plot_config.pick_colors(3)

    ib_source_markers = {
        'KaHyPar': '.',
        'Partition': 'v',
        'Measured': '*'
    }

    plot_layout = plot_config.plot_layout_4by3

    def draw_subfigure(ax, plot_x, plot_y):

        plot_dataset = ''
        if len(plot_layout[plot_y]) > plot_x:
            plot_dataset = plot_layout[plot_y][plot_x]
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
        line_exclude = ax.plot(x_dat, y_dat, '-', label = 'Excluding Replication', marker = ib_source_markers['KaHyPar'], color=colors[0])

        y_dat = list(map(lambda x: get_partition_ib(plot_dataset, x), x_dat))
        line_include = ax.plot(x_dat, y_dat, '-', label = 'Including Replication', marker = ib_source_markers['Partition'], color=colors[1])

        y_dat = list(map(lambda x: get_measured_ib(plot_dataset, x), x_dat))
        line_measured = ax.plot(x_dat, y_dat, '-', label = 'Measured', marker = ib_source_markers['Measured'], color=colors[2])

        if print_data:
            str_dat = ", ".join(map(lambda x: "%st: %.2f" % x, zip(x_dat, y_dat)))
            print("%s, %s" % (plot_dataset, str_dat))

        if plot_y == 2:
            if plot_x == 0:
                proxy_exclude = mpl.lines.Line2D([], [], color=colors[0], marker=ib_source_markers['KaHyPar'], label='Excluding Replication')
                ax.legend(handles = [proxy_exclude], fontsize = legend_fontsize, bbox_to_anchor = (0.2, -0.5, 1.2, 0.2))
            if plot_x == 1:
                proxy_include = mpl.lines.Line2D([], [], color=colors[1], marker=ib_source_markers['Partition'], label='Including Replication')
                ax.legend(handles = [proxy_include], fontsize = legend_fontsize, bbox_to_anchor = (0.2, -0.5, 1.2, 0.2))
            if plot_x == 2:
                proxy_measured = mpl.lines.Line2D([], [], color=colors[2], marker=ib_source_markers['Measured'], label='Measured Imbalance')
                ax.legend(handles = [proxy_measured], fontsize = legend_fontsize, bbox_to_anchor = (0.2, -0.5, 1.2, 0.2))





    
    layout = plot_layout

    x_labels_all = plot_config.plot_x_labels_4by3
    y_labels_all = plot_config.plot_y_labels_4by3

    n_plots_x = max(map(lambda x: len(x), layout))
    n_plots_y = len(layout)

    figsize = (11, 2.5)



    x_text="# of Cores"
    savePlotFile='imbalance_4by3.pdf'


    figs, axes=plt.subplots(nrows=n_plots_y,ncols=n_plots_x,figsize=figsize)


    for plot_x in range(0, n_plots_x):
        for plot_y in range(0, n_plots_y):

            x_major_ticks_top=np.arange(0, x_max, x_major_step)
            x_minor_ticks_top=np.arange(0, x_max, x_minor_step)

            y_major_ticks_top=np.arange(0, y_max, y_major_step)
            y_minor_ticks_top=np.arange(0, y_max, y_minor_step)
            linear_line_pos = min(x_max, y_max) - 4
            
            draw_subfigure(axes[plot_y, plot_x], plot_x, plot_y)

            axes[plot_y, plot_x].set_xticks(x_major_ticks_top)
            axes[plot_y, plot_x].set_yticks(y_major_ticks_top)
            axes[plot_y, plot_x].set_xticks(x_minor_ticks_top,minor=True)
            axes[plot_y, plot_x].set_yticks(y_minor_ticks_top,minor=True)
            axes[plot_y, plot_x].grid(which="major",alpha=0.2, linestyle = 'dashed')
            axes[plot_y, plot_x].grid(which="minor",alpha=0, linestyle = 'dotted')


            if plot_y == 0:
                axes[plot_y, plot_x].set_title(x_labels_all[plot_x], fontsize = title_fontsize)


            
            y_label = y_labels_all[plot_y]

            axes[plot_y, plot_x].set_ylabel(y_label, fontsize = ylabel_fontsize)
            axes[plot_y, plot_x].set_xlabel(x_text, fontsize = xlabel_fontsize)


            axes[plot_y, plot_x].set_xlim(0, x_max)

            if y_max.__class__ == list:
                axes[plot_y, plot_x].set_ylim(0, y_max[plot_y])
            else:
                axes[plot_y, plot_x].set_ylim(0, y_max)


            axes[plot_y, plot_x].tick_params(axis='both', which='major', labelsize=ticklabel_fontsize)



            axes[plot_y, plot_x].label_outer()

    plt.tight_layout()
    plt.subplots_adjust(wspace=0.03, hspace=0.03)

    if savePlotFile != '':
        plt.savefig(savePlotFile)

    if showPlot:
        plt.show()

if __name__ == '__main__':
    import bench
    from data_parser import DataParser, deserialize_pickle_z

    # load data
    dat = deserialize_pickle_z("parsed_data.pickle.z")

    plot_ib_factor_4by3(dat, showPlot = True, print_data=True)


