#!/bin/env python3

import os

import plot_config
from data_parser import DataParser, deserialize_pickle_z
import essent_profile_tool
import data_parser

import bench

import statistics

import matplotlib.pyplot as plt

essent_profile_tool.CPU_TICK_RATE = bench.CPU_TICK_RATE

dataset_name = {
    'start': 'Start Barrier',
    'eval': "Eval Stage",
    'barrier': "Eval Barrier",
    "sync": "Sync Stage",
    "last": "Sync Barrier"
}

CYCLE_START = 0
EVAL_DONE = 1
SYNC_START = 2
SYNC_DONE = 3
CYCLE_DONE = 4


profile_cycles = 1000000

legend_pretty_lable_dict = {
    'start': "Global Update Barrier (Last)",
    "eval": "Evaluation Phase",
    "barrier": "Evaluation Barrier",
    "sync": "Global Update Phase",
    "last": "Global Update Barrier"
}


def get_ib(dat):
    eval_ticks = list(map(lambda x: x[data_parser.EVAL_DONE] - x[data_parser.CYCLE_START], dat.values()))
    return plot_config.calculate_ib_factor(eval_ticks)

def reshape_data(d, rate = 4):
    eval_ticks = list(map(lambda x: x[1] - x[0], d))
    min_val = min(eval_ticks)
    avg_val = statistics.mean(eval_ticks)
    # Why allow user to adjust this?
    # To make matplotlib happy as ylim of violin plot is not adjustable
    max_threshold = (avg_val - min_val) * rate + min_val

    return list(filter(lambda x: x < max_threshold, eval_ticks))

def plot_exec_profile(bench1_name, bench1_threads, bench2_name, bench2_threads, log_dir='./log', savePlotFile='exec_profile.pdf', showPlot = False):
    colors = plot_config.pick_colors(6)
    figsize = (5.5 ,3.7)

    profile_name_template = "essent_profile_data_%s_%st.pickle.z"
    bench1_profile_file = os.path.join(log_dir, profile_name_template % (bench1_name, bench1_threads))
    bench2_profile_file = os.path.join(log_dir, profile_name_template % (bench2_name, bench2_threads))

    bench1_profile_data = deserialize_pickle_z(bench1_profile_file)
    bench2_profile_data = deserialize_pickle_z(bench2_profile_file)

    dat = deserialize_pickle_z("parsed_data.pickle.z")

    bench1_violin_data = [reshape_data(bench1_profile_data[n], 5) for n in range(0, bench1_threads)]
    bench2_violin_data = [reshape_data(bench2_profile_data[n], 3) for n in range(0, bench2_threads)]

    bench1_average_data = dat.essent_profile_data[bench1_name][bench1_threads]
    bench2_average_data = dat.essent_profile_data[bench2_name][bench2_threads]

    bench1_eval_ticks = [(bench1_average_data[nt][data_parser.EVAL_DONE]) for nt in range(0, bench1_threads)]
    bench2_eval_ticks = [(bench2_average_data[nt][data_parser.EVAL_DONE]) for nt in range(0, bench2_threads)]

    bench1_thread_seq = list(map(lambda x: x[0], sorted(enumerate(bench1_eval_ticks), key=lambda x: x[1])))

    bench2_thread_seq = list(map(lambda x: x[0], sorted(enumerate(bench2_eval_ticks), key=lambda x: x[1])))

    bench1_max_avg_ticks = max(map(max, bench1_average_data.values()))
    bench2_max_avg_ticks = max(map(max, bench2_average_data.values()))
    bench1_max_violin_ticks = max(map(max, bench1_violin_data))
    bench2_max_violin_ticks = max(map(max, bench2_violin_data))
    bench1_max_ticks = max(bench1_max_avg_ticks, bench1_max_violin_ticks)
    bench2_max_ticks = max(bench2_max_avg_ticks, bench2_max_violin_ticks)

    violin_dat = [bench1_violin_data, bench2_violin_data]
    average_dat = [bench1_average_data, bench2_average_data]
    max_ticks = [bench1_max_ticks, bench2_max_ticks]
    design_name = [bench1_name, bench2_name]
    design_nthreads = [bench1_threads, bench2_threads]

    thread_sequence = [bench1_thread_seq, bench2_thread_seq]


    width = 0.3
    plot_label = [['a', 'b'], ['c', 'd']]
    title_fontsize = 9
    ylabel_fontsize = 9
    xlabel_fontsize = 9

    ticklabel_fontsize = 9
    legend_font_size = 9

    y_label = "RDTSC Ticks"
    x_label = "Thread ID"


    fig, axes = plt.subplots(nrows = 2, ncols = 2, figsize = figsize, gridspec_kw = {'width_ratios': [2, 3], 'height_ratios': [1.4, 3]})

    for plot_x in range(0, 2):
        for plot_y in range(0, 2):
            ax = axes[plot_y, plot_x]
            p_label = plot_label[plot_y][ plot_x]

            if plot_x == 0:
                # Violin plot
                violin_dat_raw_seq = violin_dat[plot_y]
                thread_seq = thread_sequence[plot_y]
                violin_dat_adj_seq = [violin_dat_raw_seq[i] for i in thread_seq]
                ax.violinplot(violin_dat_adj_seq, widths = 0.5, showmeans = True, showmedians=False, showextrema=False)


                ax.set_ylabel(y_label, fontsize = ylabel_fontsize)
                ax.set_ylim(0, max_ticks[plot_y])
                
                y_tick_labels = [str(int(x / 1000)) + 'K' if x != 0 else '0' for x in ax.get_yticks().tolist()]
                ax.set_yticklabels(y_tick_labels, fontsize=ticklabel_fontsize, rotation=90, va='center')

                labels = [str(n) if n & 1 == 0 else '' for n in range(0, design_nthreads[plot_y])]

                ax.xaxis.set_tick_params(direction='out')
                ax.xaxis.set_ticks_position('bottom')
                ax.set_xticks(range(1, len(labels) + 1), labels=labels, fontsize=ticklabel_fontsize)
                # ax.set_xticklabels([])
                ax.set_xlim(0.25, len(labels) + 0.75)
                ax.set_xlabel(x_label, fontsize = xlabel_fontsize)

                total_data_cnt = design_nthreads[plot_y] * profile_cycles
                remaing_data_cnt = sum(map(len, violin_dat[plot_y]))
                remaining_percentage = remaing_data_cnt * 100 / total_data_cnt
                pretty_design_name = plot_config.design_simple_pretty_name[design_name[plot_y]]

                ax.set_title(p_label + ') Eval, %s, %.2f' % (pretty_design_name, remaining_percentage) + r"% of data", fontsize=title_fontsize)
            elif plot_x == 1:
                # bar plot 
                plot_dat_raw = average_dat[plot_y]
                thread_seq = thread_sequence[plot_y]


                plot_dat = {k: [] for k in dataset_name.keys()}


                for tid in thread_seq:
                    cycle_start = plot_dat_raw[tid][data_parser.CYCLE_START]
                    eval_done = plot_dat_raw[tid][data_parser.EVAL_DONE]
                    sync_start = plot_dat_raw[tid][data_parser.SYNC_START]
                    sync_done = plot_dat_raw[tid][data_parser.SYNC_DONE]
                    cycle_done = plot_dat_raw[tid][data_parser.CYCLE_DONE]

                    plot_dat['start'].append(cycle_start)
                    plot_dat['eval'].append(eval_done - cycle_start)
                    plot_dat['barrier'].append(sync_start - eval_done)
                    plot_dat['sync'].append(sync_done - sync_start)
                    plot_dat['last'].append(cycle_done - sync_done)

                legend_lines = []
                legend_labels = []


                prev_data = None
                for i, k in enumerate(plot_dat.keys()):
                    current_data = plot_dat[k]
                    if prev_data is None:
                        line = ax.bar(range(0, design_nthreads[plot_y]), current_data, width,label=k, color = colors[i])
                        prev_data = current_data
                    else:
                        line = ax.bar(range(0, design_nthreads[plot_y]), current_data, width,label=k, color = colors[i], bottom=prev_data)
                        prev_data = list(map(lambda x: sum(x), zip(prev_data, current_data)))
                    legend_lines.append(line)
                    legend_labels.append(legend_pretty_lable_dict[k])
                
                ax.set_ylabel(y_label, fontsize = ylabel_fontsize)
                ax.set_ylim(0, max_ticks[plot_y])
                y_tick_labels = [str(int(x / 1000)) + 'K' if x != 0 else '0' for x in ax.get_yticks().tolist()]
                ax.set_yticklabels(y_tick_labels, fontsize=ticklabel_fontsize, rotation=90, va='center')

                labels = [str(n) if n & 1 == 0 else '' for n in range(0, design_nthreads[plot_y])]
                ax.set_xticks(range(0, design_nthreads[plot_y]), labels=labels, fontsize=ticklabel_fontsize)
                # ax.set_xticklabels([])
                ax.set_xlabel(x_label, fontsize = xlabel_fontsize)

                ib_factor = get_ib(plot_dat_raw)

                pretty_design_name = plot_config.design_simple_pretty_name[design_name[plot_y]]
                ax.set_title(p_label + ') %s, ib_factor = %.2f' % (pretty_design_name, ib_factor), fontsize=title_fontsize)

                if plot_y == 1:
                    ax.legend(reversed(legend_lines), reversed(legend_labels), loc='lower right', fontsize=legend_font_size)


                
            else:
                print("No more figures")
                exit(-1)

    # plt.tight_layout()

    plt.subplots_adjust(left=0.08,
                    bottom=0.11,
                    right=0.99,
                    top=0.94,
                    wspace=0.23,
                    hspace=0.5)

    if savePlotFile != '':
        plt.savefig(savePlotFile)

    if showPlot:
        plt.show()

if __name__ == '__main__':
    plot_exec_profile('rocket21-4c', 12, 'boom21-4mega', 12, showPlot=True)
