
import bench
import plot_config

emulatorGenerators = ['essent', 'essent_no-weight', 'verilator', 'verilator_pgo2']


plot_layout = plot_config.plot_layout_4by3

plot_y_labels = plot_config.plot_y_labels_4by3
plot_x_labels = plot_config.plot_x_labels_4by3


def plot_speedup_4by3(dat, showPlot, print_data = False):

    colors = [
        plot_config.simulator_colors[gen] for gen in emulatorGenerators
    ]

    def draw_subfigure(ax, plot_x, plot_y):
        for i, gen in enumerate(emulatorGenerators):
            plot_dataset = ''
            if len(plot_layout[plot_y]) > plot_x:
                plot_dataset = plot_layout[plot_y][plot_x]
            if len(plot_dataset) == 0:
                print("Empty dataset")
                exit(-1)
            line_data = dat.speedup_data[gen][plot_dataset]

            if print_data:
                str_dat = ", ".join(map(lambda x: "%st: %.2fx" % x, line_data))
                print("%s, %s, %s" % (gen, plot_dataset, str_dat))

                max_speedup = max(map(lambda x: x[1], line_data))
                print("%s, %s, max: %.2fx" % (gen, plot_dataset, max_speedup))

            x_dat = list(map(lambda x: x[0], line_data))
            y_dat = list(map(lambda x: x[1], line_data))
            ax.plot(x_dat, y_dat, '-', label = plot_config.generator_pretty_name[gen], marker = plot_config.generator_markers[gen], color=colors[i], zorder=len(emulatorGenerators) - i)


    y_max = [18, 22, 38]

    plot_config.plot_framework(draw_subfigure, showPlot = showPlot, y_max = y_max, y_major_step = [4, 4, 4], x_major_step = 8, y_minor_step = [1, 1, 1], grid_height_ratio = y_max, x_text="# of Parallel Threads", legend_pos=[(0, 2)], legend_loc = 'upper right', savePlotFile='speedup_4by3.pdf', custom_figsize=(11, 5), custom_layout=plot_layout, custom_plot_x_labels=plot_x_labels, custom_plot_y_labels=plot_y_labels, legend_fontsize='medium')



if __name__ == '__main__':
    import bench
    from data_parser import DataParser, deserialize_pickle_z

    # load data
    dat = deserialize_pickle_z("parsed_data.pickle.z")

    plot_speedup_4by3(dat, showPlot = True, print_data = True)
