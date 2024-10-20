
import bench
import plot_config

emulatorGenerators = ['essent', 'verilator', 'commercial']




import numpy as np
import matplotlib.pyplot as plt

num_data_pts = len(list(filter(lambda x: x <= 24, bench.parallelThreads)))

def plot_cross_socket_speedup_all(dat, showPlot, print_data = False):
    colors = plot_config.pick_colors(6)

    def draw_subfigure(ax, plot_x, plot_y):
        plot_dataset = ''
        if len(plot_config.plot_layout[plot_y]) > plot_x:
            plot_dataset = plot_config.plot_layout[plot_y][plot_x]
        if len(plot_dataset) == 0:
            print("Empty dataset")
            exit(-1)
        
        line_data_within_socket = dat.speedup_data['essent'][plot_dataset][:num_data_pts]
        line_data_cross_socket = dat.cross_socket_speedup_data['essent'][plot_dataset][:num_data_pts]

        if print_data:
            str_dat = ", ".join(map(lambda x: "%st: %.2fx" % x, line_data_within_socket))
            print("Same socket, %s, %s" % (plot_dataset, str_dat))

            str_dat = ", ".join(map(lambda x: "%st: %.2fx" % x, line_data_cross_socket))
            print("Interleaved, %s, %s" % (plot_dataset, str_dat))

        x_dat = list(map(lambda x: x[0], line_data_within_socket))
        
        y_dat = list(map(lambda x: x[1], line_data_within_socket))
        ax.plot(x_dat, y_dat, '-', label = 'Within Socket', marker = plot_config.socket_markers['within'],color=colors[0])

        y_dat_cross = list(map(lambda x: x[1], line_data_cross_socket))
        ax.plot(x_dat, y_dat_cross, '-', label = 'Cross Socket', marker = plot_config.socket_markers['cross'], color=colors[1])


    plot_config.plot_framework(draw_subfigure, x_max=26, showPlot = showPlot, x_text="# of Parallel Threads", y_text="Speedup (x)", savePlotFile='cross_socket_speedup_all.pdf')


def plot_cross_socket_speedup(dat, showPlot, print_data = False):
    colors = plot_config.pick_colors(5)

    plot_layout = ['boom21-mega', 'boom21-2mega', 'boom21-4mega']
    x_max=26
    y_max=32
    x_major_step=4
    y_major_step=6
    x_minor_step=1
    y_minor_step=1
    x_text = '# of Parallel Threads'
    y_text = 'Speedup (x)'
    savePlotFile='cross_socket_speedup_2.pdf'
    legend_loc='upper left'
    n_plots_x = len(plot_layout)

    figsize = (6, 2.25)
    



    figs, axes=plt.subplots(nrows=1,ncols=n_plots_x,figsize=figsize)
    for plot_x in range(0, n_plots_x):
        
        ax = axes[plot_x]

        x_major_ticks_top=np.arange(0, x_max, x_major_step)
        x_minor_ticks_top=np.arange(0, x_max, x_minor_step)

        y_major_ticks_top=np.arange(0, y_max, y_major_step)
        y_minor_ticks_top=np.arange(0, y_max, y_minor_step)
        linear_line_pos = min(x_max, y_max) - 4



        # draw data
        plot_dataset = plot_layout[plot_x]
        
        line_data_within_socket = dat.speedup_data['essent'][plot_dataset][:num_data_pts]
        line_data_cross_socket = dat.cross_socket_speedup_data['essent'][plot_dataset][:num_data_pts]

        if print_data:
            str_dat = ", ".join(map(lambda x: "%st: %.2fx" % x, line_data_within_socket))
            print("Same Socket, %s, %s" % (plot_dataset, str_dat))

            str_dat = ", ".join(map(lambda x: "%st: %.2fx" % x, line_data_cross_socket))
            print("Interleaved, %s, %s" % (plot_dataset, str_dat))

        x_dat = list(map(lambda x: x[0], line_data_within_socket))
        
        y_dat = list(map(lambda x: x[1], line_data_within_socket))
        ax.plot(x_dat, y_dat, '-', label = 'Same Socket', marker = plot_config.socket_markers['within'], color=colors[0])

        y_dat_cross = list(map(lambda x: x[1], line_data_cross_socket))
        ax.plot(x_dat, y_dat_cross, '-', label = 'Interleaved', marker = plot_config.socket_markers['cross'], color=colors[1])

        ax.tick_params(axis='both', which='major', labelsize=9)



        ax.set_xticks(x_major_ticks_top)
        ax.set_yticks(y_major_ticks_top)
        ax.set_xticks(x_minor_ticks_top,minor=True)
        ax.set_yticks(y_minor_ticks_top,minor=True)
        ax.grid(which="major",alpha=0.2, linestyle = 'dashed')
        ax.grid(which="minor",alpha=0, linestyle = 'dotted')

        ax.plot([1, linear_line_pos], [1, linear_line_pos], 'r--')


            
        ax.set_title(plot_config.design_simple_pretty_name[plot_dataset])


        ax.set_xlabel(x_text)
        ax.set_ylabel(y_text)


        ax.set_xlim(0, x_max)
        ax.set_ylim(0, y_max)


        ax.tick_params(axis='both', which='major', labelsize=10)

        if plot_x == 0:
            ax.legend(loc=legend_loc)

        ax.label_outer()

    plt.tight_layout()
    # plt.subplots_adjust(wspace=0.03, hspace=0.03)

    if savePlotFile != '':
        plt.savefig(savePlotFile)

    if showPlot:
        plt.show()

if __name__ == '__main__':
    import bench
    from data_parser import DataParser, deserialize_pickle_z

    # load data
    dat = deserialize_pickle_z("parsed_data.pickle.z")

    plot_cross_socket_speedup(dat, showPlot = True, print_data = True)
    # plot_cross_socket_speedup_all(dat, showPlot = True, print_data = True)
