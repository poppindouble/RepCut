
import bench
import plot_config

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

emulatorGenerators = ['essent', 'essent_no-weight', 'verilator', 'verilator_pgo2']


def plot_sim_speed(dat, showPlot, print_data = False):
    # colors = plot_config.pick_colors(10)

    title_fontsize = 10
    ylabel_fontsize = 10
    xlabel_fontsize = 10
    ticklabel_fontsize = 10
    legend_fontsize = 10


    colors = [
        plot_config.simulator_colors[gen] for gen in emulatorGenerators
    ]

    max_speed = {}

    def draw_subfigure(ax, plot_x, plot_y):
        for i, gen in enumerate(emulatorGenerators):
            plot_dataset = ''
            if len(plot_config.plot_layout[plot_y]) > plot_x:
                plot_dataset = plot_config.plot_layout[plot_y][plot_x]
            if len(plot_dataset) == 0:
                print("Empty dataset")
                exit(-1)

            def get_sim_speed(nThreads):
                baseline_gen = bench.emulatorGenerators_baseline[gen]
                avg_time = dict(dat.runtime_data[gen][plot_dataset])[nThreads]
                cycle_cnt = dat.cycle_count_data[baseline_gen][plot_dataset][nThreads]
                return cycle_cnt / avg_time / 1000

            x_dat = bench.parallelThreads
            y_dat = list(map(get_sim_speed, x_dat))
            max_speed[gen] = max(y_dat)

            if print_data:
                str_dat = ", ".join(map(lambda x: "%st: %.2fKHz" % x, zip(x_dat, y_dat)))
                print("%s, %s, %s" % (gen, plot_dataset, str_dat))
            
            ax.plot(x_dat, y_dat, '-', label = plot_config.generator_pretty_name[gen], marker = plot_config.generator_markers[gen], color=colors[i], zorder=len(emulatorGenerators) - i)
        if print_data:
            print("max speed: e: %.2fKHz, v: %.2fKHz, essent vs verilator: %.2fx" % (max_speed['essent'], max_speed['verilator'], max_speed['essent']/max_speed['verilator']))
            print('')

    # plot_config.plot_framework(draw_subfigure, 
    # y_max=[155, 105, 67, 52], 
    # y_major_step=[30, 20, 10, 10],
    # y_minor_step=[6, 4, 2, 2],
    # x_major_step = 8,
    # showPlot = showPlot, x_text="# of Cores", y_text='Speed (KHz)', y_text_pos = (-17, 16), hasLinear=False, savePlotFile='sim_speed.pdf', legend_pos=[(2, 3)],legend_loc='upper right', custom_figsize=(7, 5.6), legend_fontsize=8)



    x_max = 50
    y_max=[155, 108, 67, 55]
    y_major_step=[30, 20, 10, 10]
    y_minor_step=[6, 4, 2, 2]
    x_major_step = 8
    x_minor_step = 1
    x_text="# of Cores"
    y_text='Speed (KHz)'
    y_text_pos = (-20, 16)

    savePlotFile='sim_speed.pdf'

    layout = plot_config.plot_layout

    x_labels_all = plot_config.plot_x_labels
    y_labels_all = plot_config.plot_y_labels


    n_plots_x = max(map(lambda x: len(x), layout))
    n_plots_y = len(layout)

    figsize=(6, 5)

    

    figs, axes=plt.subplots(nrows=n_plots_y,ncols=n_plots_x,figsize=figsize)

    legend_cursor = 0


    for plot_x in range(0, n_plots_x):
        for plot_y in range(0, n_plots_y):

            x_major_ticks_top=np.arange(0, x_max, x_major_step)
            x_minor_ticks_top=np.arange(0, x_max, x_minor_step)

            if y_max.__class__ == list:
                y_major_ticks_top=np.arange(0, y_max[plot_y], y_major_step[plot_y])
                y_minor_ticks_top=np.arange(0, y_max[plot_y], y_minor_step[plot_y])
                linear_line_pos = min(x_max, y_max[plot_y]) - 4
            else:
                y_major_ticks_top=np.arange(0, y_max, y_major_step)
                y_minor_ticks_top=np.arange(0, y_max, y_minor_step)
                linear_line_pos = min(x_max, y_max) - 4
            
            draw_subfigure(axes[plot_y, plot_x], plot_x, plot_y)

            axes[plot_y, plot_x].tick_params(axis='both', which='major', labelsize=ticklabel_fontsize)

            axes[plot_y, plot_x].set_xticks(x_major_ticks_top)
            axes[plot_y, plot_x].set_yticks(y_major_ticks_top)
            axes[plot_y, plot_x].set_xticks(x_minor_ticks_top,minor=True)
            axes[plot_y, plot_x].set_yticks(y_minor_ticks_top,minor=True)
            axes[plot_y, plot_x].grid(which="major",alpha=0.2, linestyle = 'dashed')
            axes[plot_y, plot_x].grid(which="minor",alpha=0, linestyle = 'dotted')


            if plot_y == 0:
                axes[plot_y, plot_x].set_title(x_labels_all[plot_x], fontsize = title_fontsize)

            # if plot_y == n_plots_y - 1:
            #     # axes[plot_y, plot_x].set_xlabel('# of Cores')
            #     axes[plot_y, plot_x].set_xlabel(x_labels_all[plot_x])

            # if plot_x == 0:
            #     # axes[plot_y, plot_x].set_ylabel('Speedup')
            #     axes[plot_y, plot_x].set_ylabel(y_labels_all[plot_y])



            
            y_label = y_labels_all[plot_y]
            if len(y_text) > 0:
                # y_label = y_label + '\n' + y_text
                axes[plot_y, plot_x].set_ylabel(y_text, style='italic', fontsize = ylabel_fontsize)
                axes[plot_y, plot_x].set_xlabel(x_text, style='italic', fontsize = xlabel_fontsize)

                #
                if plot_x == 0:
                    y_pox_x, y_pos_y = y_text_pos
                    y_pos_y = y_max[plot_y] / 100 * y_pos_y

                    axes[plot_y, plot_x].text(y_pox_x, y_pos_y, y_label, rotation=90, fontsize = ylabel_fontsize)
            else:
                # No y label     
                axes[plot_y, plot_x].set_ylabel(y_label, fontsize = ylabel_fontsize)
                axes[plot_y, plot_x].set_xlabel(x_text, fontsize = xlabel_fontsize)


            axes[plot_y, plot_x].set_xlim(0, x_max)

            if y_max.__class__ == list:
                axes[plot_y, plot_x].set_ylim(0, y_max[plot_y])
            else:
                axes[plot_y, plot_x].set_ylim(0, y_max)


            axes[plot_y, plot_x].tick_params(axis='both', which='major', labelsize=9)

            # if legend_pos == 'all':
            #     axes[plot_y, plot_x].legend(loc=legend_loc, fontsize=legend_fontsize)
            # else:
            #     for legend_pos_x, legend_pos_y in legend_pos:
            #         if legend_pos_x == plot_x and legend_pos_y == plot_y:
            #             axes[plot_y, plot_x].legend(loc=legend_loc, fontsize=legend_fontsize)
            legend_max_items = 2
            if plot_x == 2:
                if plot_y == 2:
                    # legend 1
                    proxy_list = []

                    for i in range(0, legend_max_items):
                        gen_i = legend_cursor
                        if gen_i >= len(emulatorGenerators):
                            break

                        gen = emulatorGenerators[gen_i]
                        proxy = mpl.lines.Line2D([], [], color=colors[gen_i], marker=plot_config.generator_markers[gen], label=plot_config.generator_pretty_name[gen])

                        proxy_list.append(proxy)
                        legend_cursor += 1

                    axes[plot_y, plot_x].legend(handles = proxy_list, loc="upper right", fontsize=legend_fontsize)
                if plot_y == 3:
                    proxy_list = []

                    for i in range(0, legend_max_items):
                        gen_i = legend_cursor
                        if gen_i >= len(emulatorGenerators):
                            break

                        gen = emulatorGenerators[gen_i]
                        proxy = mpl.lines.Line2D([], [], color=colors[gen_i], marker=plot_config.generator_markers[gen], label=plot_config.generator_pretty_name[gen])

                        proxy_list.append(proxy)
                        legend_cursor += 1

                    axes[plot_y, plot_x].legend(handles = proxy_list, loc="upper right", fontsize=legend_fontsize)

                    # gen_i = 2
                    # gen = emulatorGenerators[gen_i]
                    # proxy_1 = mpl.lines.Line2D([], [], color=colors[gen_i], marker=plot_config.generator_markers[gen], label=plot_config.generator_pretty_name[gen])


                    # gen_i = 3
                    # gen = emulatorGenerators[gen_i]
                    # proxy_2 = mpl.lines.Line2D([], [], color=colors[gen_i], marker=plot_config.generator_markers[gen], label=plot_config.generator_pretty_name[gen])

                    # axes[plot_y, plot_x].legend(handles = [proxy_1, proxy_2], loc="upper right", fontsize=legend_fontsize)

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

    plot_sim_speed(dat, showPlot = True, print_data = True)
