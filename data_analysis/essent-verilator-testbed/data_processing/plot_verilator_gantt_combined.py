
import bench
import plot_config

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt


# idle: 00
# real: 01
# predict: 10
# both: 11
cell_color = [
    # idle
    (255,255,255),
    # Working, unpredicted
    (0x54, 0x66, 0x8e),
    # Predicted, not working
    (0xd8, 0xd8, 0xd8),
    # Predicted, working
    (0x35, 0x39, 0x56)
]

# convert to RGB 0.0~1.0
cell_color = list(map(lambda c: tuple(map(lambda x: float(x / 255), c)), cell_color))

# print(cell_color)

cell_labels = [
    "Idle",
    "Working unpredicted",
    "Predicted, not working",
    "Predicted, working"
]

cell_labels_2way = [
    "NA",
    "Measured",
    "Predicted",
    "NA"
]


plot_layout = plot_config.plot_layout_4by3

plot_y_labels = plot_config.plot_y_labels_4by3
plot_x_labels = plot_config.plot_x_labels_4by3


# legend_bbox_to_anchor = (0.5, -1.28, 1.2, 0.08)
legend_bbox_to_anchor = (0.664, -0.9, 0.78, 0.08)

subplot_adjust = {
    "bottom": 0.24,
    "top": 0.93,
    "left": 0.04,
    "right": 0.97
}

subplot_wspace = 0.11
subplot_hspace = 0.4


def plot_verilator_gantt(dat, showPlot, savePlotFile='verilator_gantt_heatmap_combined.pdf'):

    def draw_subfigure(ax, plot_x, plot_y):
        real_max_tick = 0
        plot_dataset = ''
        if len(plot_layout[plot_y]) > plot_x:
            plot_dataset = plot_layout[plot_y][plot_x]
        if len(plot_dataset) == 0:
            print("Empty dataset")
            exit(-1)
        gantt_data = dat.verilator_gantt[plot_dataset][plot_config.heatmap_nthread]

        max_ticks = gantt_data['ticks']
        real_max_tick = max_ticks
        x_grain = int(max_ticks / plot_config.heatmap_x_resolution) + 1

        heatmap_real = []

        for x in range(0, plot_config.heatmap_x_resolution):
            line = []

            for tid in range(0, plot_config.heatmap_nthread):
                window_start = x_grain * x
                window_end = x_grain * (x + 1)
                window_size = x_grain
                busy_ticks = 0

                for mtask in gantt_data[tid]:
                    mtask_start_tick = mtask['real_begin']
                    mtask_end_tick = mtask['real_end']

                    if mtask_start_tick >= window_end:
                        # out of range. Data is sorted so later data is out of topic
                        break
                    if mtask_end_tick <= window_start:
                        # not started yet
                        continue

                    in_window_end = min(mtask_end_tick, window_end)
                    in_window_start = max(mtask_start_tick, window_start)
                    busy_ticks += (in_window_end - in_window_start)
                    
                rates = busy_ticks / window_size
                line.append(rates)
            heatmap_real.append(line)


        heatmap_predict = []

        for x in range(0, plot_config.heatmap_x_resolution):
            line = []

            for tid in range(0, plot_config.heatmap_nthread):
                window_start = x_grain * x
                window_end = x_grain * (x + 1)
                window_size = x_grain
                busy_ticks = 0

                for mtask in gantt_data[tid]:
                    mtask_start_tick = mtask['predict_begin']
                    mtask_end_tick = mtask['predict_end']

                    if mtask_start_tick >= window_end:
                        # out of range. Data is sorted so later data is out of topic
                        break
                    if mtask_end_tick <= window_start:
                        # not started yet
                        continue

                    in_window_end = min(mtask_end_tick, window_end)
                    in_window_start = max(mtask_start_tick, window_start)
                    busy_ticks += (in_window_end - in_window_start)
                    
                rates = busy_ticks / window_size
                line.append(rates)
            heatmap_predict.append(line)

        heat_map = []

        busy_threshold = 0.5


        line_idx = 0
        for line_real, line_predict in zip(heatmap_real, heatmap_predict):
            heat_map.append([])
            for dp_real, dp_predict in zip(line_real, line_predict):
                color_idx = 0
                if dp_real > busy_threshold:
                    color_idx += 1
                if dp_predict > busy_threshold:
                    color_idx += 2

                color = cell_color[color_idx]
                heat_map[line_idx].append(color)
            line_idx += 1

        heat_map_T = [[] for i in range(0, len(heat_map[0]))]

        for x, line in enumerate(heat_map):
            for y, point in enumerate(line):
                heat_map_T[y].append(point)

        
        ax.imshow(heat_map_T, aspect='auto', interpolation='nearest')

        ax.tick_params(length=2)

        return real_max_tick

        # ax.imshow(np.array(heat_map).T, cmap = colors, aspect='auto')



    y_text="Threads"
    x_text=r"Time ($\mu$s)"

    x_max = plot_config.heatmap_x_resolution
    y_max = plot_config.heatmap_nthread


    figsize = plot_config.fig_size_heatmap


    n_plots_x = max(map(lambda x: len(x), plot_layout))
    n_plots_y = len(plot_layout)



    


    figs, axes=plt.subplots(nrows=n_plots_y,ncols=n_plots_x,figsize=figsize)
    for plot_x in range(0, n_plots_x):
        for plot_y in range(0, n_plots_y):

            
            max_ticks = draw_subfigure(axes[plot_y, plot_x], plot_x, plot_y)


            # Set title
            if plot_y == 0:
                axes[plot_y, plot_x].set_title(plot_x_labels[plot_x], fontsize='small')

            # Set y label
            if plot_x == 0:
                # axes[plot_y, plot_x].set_ylabel(plot_y_labels[plot_y] + "\n" + y_text, fontsize='small')
                axes[plot_y, plot_x].text(-50, 2, plot_y_labels[plot_y], rotation=90, fontsize='small')
                axes[plot_y, plot_x].set_ylabel(y_text, fontsize='small', style='italic')

            # Set x label
            if plot_y == n_plots_y - 1:
                axes[plot_y, plot_x].set_xlabel(x_text, style='italic')


            axes[plot_y, plot_x].set_xlim(0, x_max)
            axes[plot_y, plot_x].set_ylim(-0.5, y_max-0.5)

            # Set x, y tick labels
            x_tick_count = 5
            axes[plot_y, plot_x].xaxis.set_ticks(np.arange(0, plot_config.heatmap_x_resolution + 1, plot_config.heatmap_x_resolution / (x_tick_count-1)))

            ax_x_labels = ["{:.1f}".format(bench.tick_to_us(x * (max_ticks / x_tick_count))) if x != 0 else '0' for x in range(0, x_tick_count)]
            axes[plot_y, plot_x].xaxis.set_ticklabels(ax_x_labels)

            # Set y ticks
            y_tick_count = 3
            axes[plot_y, plot_x].yaxis.set_ticks(np.arange(0, plot_config.heatmap_nthread + 1, plot_config.heatmap_nthread / (y_tick_count-1)))

            # if plot_x != 0 and plot_y != 3:
            axes[plot_y, plot_x].yaxis.set_ticklabels([])

            axes[plot_y, plot_x].tick_params(axis='both', which='major', labelsize=9)


            if plot_y == 2 and plot_x == 1:

                colors = cell_color
        
                # create a patch (proxy artist) for every color 
                patches = [ mpl.patches.Patch(edgecolor='black', facecolor=colors[i], label=cell_labels_2way[i]) for i in [2, 1] ]

                axes[plot_y, plot_x].legend(handles=patches, bbox_to_anchor=legend_bbox_to_anchor, loc='lower left', ncol=2, mode="expand", borderaxespad=0, fontsize='small', handlelength=1)


    plt.tight_layout()
    plt.subplots_adjust(wspace=subplot_wspace, hspace=subplot_hspace, bottom=subplot_adjust['bottom'], top = subplot_adjust['top'], left = subplot_adjust['left'], right = subplot_adjust['right'])

    if savePlotFile != '':
        plt.savefig(savePlotFile)

    if showPlot:
        plt.show()



if __name__ == '__main__':
    import bench
    from data_parser import DataParser, deserialize_pickle_z

    # load data
    dat = deserialize_pickle_z("parsed_data.pickle.z")

    plot_verilator_gantt(dat, showPlot = True, savePlotFile='verilator_gantt_heatmap_combined.pdf')
