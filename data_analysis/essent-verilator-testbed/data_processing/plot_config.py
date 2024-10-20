import bench

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

plot_bar_projects = [
    'rocket21-1c',
    'rocket21-2c',
    'rocket21-4c',
    'boom21-small',
    'boom21-2small',
    'boom21-4small',
    'boom21-large',
    'boom21-2large',
    'boom21-4large',
    'boom21-mega',
    'boom21-2mega',
    'boom21-4mega',
]

plot_layout = [
    ['rocket21-1c', 'rocket21-2c', 'rocket21-4c'],
    ['boom21-small', 'boom21-2small', 'boom21-4small'],
    ['boom21-large', 'boom21-2large', 'boom21-4large'],
    ['boom21-mega', 'boom21-2mega', 'boom21-4mega']
]

plot_x_labels = ['1 Core', '2 Cores', '4 Cores']
plot_y_labels = ['Rocket Chip', 'Small BOOM', 'Large BOOM', 'Mega BOOM']


plot_layout_4by3 = [
    ['rocket21-1c', 'boom21-small', 'boom21-large', 'boom21-mega'], 
    ['rocket21-2c', 'boom21-2small', 'boom21-2large', 'boom21-2mega'], 
    ['rocket21-4c', 'boom21-4small', 'boom21-4large', 'boom21-4mega'], 
]

plot_y_labels_4by3 = ['1 Core', '2 Cores', '4 Cores']
plot_x_labels_4by3 = ['Rocket Chip', 'Small BOOM', 'Large BOOM', 'Mega BOOM']


# plot_layout = [
#     ['rocket21-1c', 'boom21-small', 'boom21-large', 'boom21-mega'], 
#     ['rocket21-2c', 'boom21-2small', 'boom21-2large', 'boom21-2mega'], 
#     ['rocket21-4c', 'boom21-4small', 'boom21-4large', 'boom21-4mega'], 
# ]

# plot_y_labels = ['1 Core Design', '2 Cores Design', '4 Cores Design']
# plot_x_labels = ['Rocket Chip', 'Small BOOM', 'Large BOOM', 'Mega BOOM']

design_pretty_name = {
    'rocket21-1c'   : 'RocketChip, 1 Core',
    'rocket21-2c'   : 'RocketChip, 2 Cores',
    'rocket21-4c'   : 'RocketChip, 4 Cores',
    'boom21-small'  : 'BOOM, SmallBoomConfig, 1 Core',
    'boom21-2small' : 'BOOM, SmallBoomConfig, 2 Cores',
    'boom21-4small' : 'BOOM, SmallBoomConfig, 4 Cores',
    'boom21-large'  : 'BOOM, LargeBoomConfig, 1 Core',
    'boom21-2large' : 'BOOM, LargeBoomConfig, 2 Cores',
    'boom21-4large' : 'BOOM, LargeBoomConfig, 4 Cores',
    'boom21-mega'   : 'BOOM, MegaBoomConfig, 1 Core',
    'boom21-2mega'  : 'BOOM, MegaBoomConfig, 2 Cores',
    'boom21-4mega'  : 'BOOM, MegaBoomConfig, 4 Cores',
}


design_simple_pretty_name = {
    'rocket21-1c'   : 'RocketChip-1C',
    'rocket21-2c'   : 'RocketChip-2C',
    'rocket21-4c'   : 'RocketChip-4C',
    'boom21-small'  : 'SmallBOOM-1C',
    'boom21-2small' : 'SmallBOOM-2C',
    'boom21-4small' : 'SmallBOOM-4C',
    'boom21-large'  : 'LargeBOOM-1C',
    'boom21-2large' : 'LargeBOOM-2C',
    'boom21-4large' : 'LargeBOOM-4C',
    'boom21-mega'   : 'MegaBOOM-1C',
    'boom21-2mega'  : 'MegaBOOM-2C',
    'boom21-4mega'  : 'MegaBOOM-4C',
}

design_tiny_pretty_name = {
    'rocket21-1c'   : 'RocketChip-1C',
    'rocket21-2c'   : 'RocketChip-2C',
    'rocket21-4c'   : 'RocketChip-4C',
    'boom21-small'  : 'SmallBOOM-1C',
    'boom21-2small' : 'SmallBOOM-2C',
    'boom21-4small' : 'SmallBOOM-4C',
    'boom21-large'  : 'LargeBOOM-1C',
    'boom21-2large' : 'LargeBOOM-2C',
    'boom21-4large' : 'LargeBOOM-4C',
    'boom21-mega'   : 'MegaBOOM-1C',
    'boom21-2mega'  : 'MegaBOOM-2C',
    'boom21-4mega'  : 'MegaBOOM-4C',
}



ir_pretty_name = {
    "essent.ir.MemWrite" : "MemWrite",
    "firrtl.ir.Stop" : "Stop",
    "firrtl.ir.Print" : "Print",
    "essent.ir.RegUpdate" : "RegUpdate",
    "firrtl.ir.Connect" : "Connect",
}

def rgbToStringColor(rgb):
    hex_str = "".join(map(lambda x: "%02X" % (x), rgb))
    return r"#" + hex_str

common_colors_rgb = [
    (16, 70, 128),
    (49, 124, 183),
    (109, 173, 209),
    (182, 215, 232),
    (233, 241, 244),
    (251, 227, 213),
    (246, 178, 147),
    (220, 109, 87),
    (183, 34, 48),
    (109, 1, 31)
]

common_colors = list(map(rgbToStringColor, common_colors_rgb))

def pick_colors(num_of_colors):
    # print("%s colors requested" % num_of_colors)
    if num_of_colors > len(common_colors):
        print("Error: Cannot return satisfied num of colors")
        exit(-1)

    ret = []

    for i in range(0, num_of_colors):
        idx = int(len(common_colors) * i / num_of_colors)
        ret.append(common_colors[idx])
    return ret

simulator_colors = {
    "essent": common_colors[0],
    'verilator': common_colors[-2],
    "essent_no-weight": common_colors[2],
    'verilator_pgo2': common_colors[-4]
}


bar_chart_colors = [
    'coral',
    'bisque',
    'lawngreen',
    'aqua',
    'slategrey',
    'violet'
]

event_pretty_name = {
    "L1-icache-load-misses"             : "L1-icache-load-misses",
    "l2_rqsts.code_rd_hit"              : "l2\_rqsts.code\_rd\_hit",
    "l2_rqsts.code_rd_miss"             : "l2\_rqsts.code\_rd\_miss",
    "l2_rqsts.miss"                     : "l2\_rqsts.miss",
    "l2_rqsts.pf_hit"                   : "l2\_rqsts.pf\_hit",
    "l2_rqsts.pf_miss"                  : "l2\_rqsts.pf\_miss",
    "instructions"                      : "instructions",
    "branches"                          : "branches",
    "branch-misses"                     : "branch-misses",
    "baclears.any"                      : "baclears.any",
    "br_inst_retired.all_branches"      : "br\_inst\_retired.all\_branches",
    "br_misp_retired.all_branches"      : "br\_misp\_retired.all\_branches",
    "br_inst_retired.conditional"       : "br\_inst\_retired.conditional",
    "br_misp_retired.conditional"       : "br\_misp\_retired.conditional",
    "br_inst_retired.near_call"         : "br\_inst\_retired.near\_call",
    "br_misp_retired.near_call"         : "br\_misp\_retired.near\_call",
    "lsd.uops"                          : "lsd.uops",
    "topdown-fetch-bubbles"             : "topdown-fetch-bubbles",
    "topdown-recovery-bubbles"          : "topdown-recovery-bubbles",
    "dsb2mite_switches.penalty_cycles"  : "dsb2mite\_switches.penalty\_cycles",
    "icache_16b.ifdata_stall"           : "icache\_16b.ifdata\_stall",
    "icache_64b.iftag_stall"            : "icache\_64b.iftag\_stall",
    "idq.dsb_cycles"                    : "idq.dsb\_cycles",
    "idq.mite_cycles"                   : "idq.mite\_cycles",
    "idq.all_dsb_cycles_any_uops"       : "idq.all\_dsb\_cycles\_any\_uops",
    "idq.all_mite_cycles_any_uops"      : "idq.all\_mite\_cycles\_any\_uops",
    "int_misc.clear_resteer_cycles"     : "int\_misc.clear\_resteer\_cycles",
    "L1-dcache-load-misses"             : "L1-dcache-load-misses",
    "L1-dcache-loads"                   : "L1-dcache-loads",
    "L1-dcache-stores"                  : "L1-dcache-stores",
    "l2_rqsts.all_demand_data_rd"       : "l2\_rqsts.all\_demand\_data\_rd",
    "l2_rqsts.all_demand_miss"          : "l2\_rqsts.all\_demand\_miss",
    "mem_load_retired.l1_hit"           : "mem\_load\_retired.l1\_hit",
    "mem_load_retired.l1_miss"          : "mem\_load\_retired.l1\_miss",
    "mem_load_retired.l2_hit"           : "mem\_load\_retired.l2\_hit",
    "mem_load_retired.l2_miss"          : "mem\_load\_retired.l2\_miss",

    "time_total"                        : "Wall Clock Time",
    "time_user"                         : "CPU Time",
    "time_sys"                          : "OS Time",


    "LLC-load-misses"                   : "LLC-load-misses",
    "LLC-loads"                         : "LLC-loads",
    "LLC-store-misses"                  : "LLC-store-misses",
    "LLC-stores"                        : "LLC-stores",

    "llc_misses.mem_read"               : "llc\_misses.mem\_read",
    "llc_misses.mem_write"              : "llc\_misses.mem\_write",
    "unc_m_rpq_inserts"                 : "unc\_m\_rpq\_inserts",
    "unc_m_rpq_occupancy"               : "unc\_m\_rpq\_occupancy",
    "unc_m_tagchk.hit"                  : "unc\_m\_tagchk.hit",
    "unc_m_tagchk.miss_clean"           : "unc\_m\_tagchk.miss\_clean",
    "unc_m_tagchk.miss_dirty"           : "unc\_m\_tagchk.miss\_dirty",
    "unc_m_wpq_inserts"                 : "unc\_m\_wpq\_inserts", 
    "unc_m_wpq_occupancy"               : "unc\_m\_wpq\_occupancy",

    "IPC"                               : "IPC",
    "Extra Inst"                        : "Extra Instructions (vs. 1 thread)",
    "Replication"                       : "Replication Cost",
    'branch miss rate'                  : "Branch Miss Rate"
}



# Marker: The available marker styles that can be used,
# “’.’“           point marker
# “’,’“           pixel marker
# “’o’“          circle marker
# “’v’“          triangle_down marker
# “’^’“          triangle_up marker
# “'<‘“          triangle_left marker
# “’>’“          triangle_right marker
# “’1’“          tri_down marker
# “’2’“          tri_up marker
# “’3’“          tri_left marker
# “’4’“          tri_right marker
# “’s’“          square marker
# “’p’“          pentagon marker
# “’*’“          star marker
# “’h’“          hexagon1 marker
# “’H’“         hexagon2 marker
# “’+’“          plus marker
# “’x’“          x marker
# “’D’“         diamond marker
# “’d’“          thin_diamond marker
# “’|’“           vline marker
# “’_’“          hline marker

generator_markers = {
    'essent': '.',
    'verilator': 'v',
    'essent_no-weight': '*',
    'verilator_pgo2': 'h',
}

generator_pretty_name = {
    'essent': 'RepCut',
    'essent_no-weight': 'RepCut UW',
    'verilator': 'Verilator',
    'verilator_pgo2': 'Verilator PGO'
}



socket_markers = {
    'within': '.',
    'cross': 'v'
}

# fig_size_speedup = (14, 7)
fig_size_speedup = (9, 8)
fig_size_heatmap = (10, 2.6)
fig_size_bar = (10, 6)


heatmap_nthread = 18
heatmap_x_resolution = 300
heatmap_color = mpl.colormaps['Blues']


def calculate_ib_factor(dat):
    avg = sum(dat) / len(dat)
    max_dat = max(dat)
    return (max_dat - avg) / avg



def plot_multiple_bar(dat, width, ylabel, savePlotFile='', showPlot=False, colors = None, legend_loc='upper left', customize_figsize = None):


    line_dat = {}
    line_key = list(dat.keys())
    datasets = []
    dataset_color = {}
    color_id = 0
    colors = colors if colors is not None else bar_chart_colors

    for value in dat.values():
        for d in value.keys():
            if d not in datasets:
                datasets.append(d)
                dataset_color[d] = colors[color_id]
                color_id += 1



    for dataset in datasets:
        line = []
        for x_item in line_key:
            line.append(dat[x_item][dataset])
        line_dat[dataset] = line

    if customize_figsize is None:
        figsize = fig_size_bar
    else:
        figsize = customize_figsize

    figs, ax = plt.subplots(figsize = figsize)

    lines = []
    labels = []

    prev_data = None
    for dataset in datasets:
        current_data = line_dat[dataset]
        if prev_data is None:
            line = ax.bar(line_key, current_data, width, label=dataset, color=dataset_color[dataset])
            prev_data = current_data
        else:
            line = ax.bar(line_key, current_data, width, bottom=prev_data, label=dataset, color=dataset_color[dataset])
            prev_data = list(map(lambda x: sum(x), zip(prev_data, current_data)))

        lines.append(line)
        labels.append(dataset)

    ax.set_ylabel(ylabel)
    ax.set_xticks(line_key, line_key)

    ax.legend(reversed(lines), reversed(labels), loc=legend_loc)

    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()

    if savePlotFile != '':
        plt.savefig(savePlotFile)

    if showPlot:
        plt.show()




def plot_framework(subfigure_callback, x_max=50, y_max=38, x_major_step=4, y_major_step=4, x_minor_step=1, y_minor_step=1, grid_height_ratio = None, hasLinear=True, x_text = '', y_text = '', y_text_pos = (0, 0), showPlot = False, savePlotFile = '', legend_loc='upper left', legend_fontsize = 'small', legend_pos = 'all', custom_figsize = None, custom_layout = None, custom_plot_x_labels = None, custom_plot_y_labels = None):

    if custom_layout is None:
        layout = plot_layout
    else:
        layout = custom_layout

    if custom_plot_x_labels is None:
        x_labels_all = plot_x_labels
    else:
        x_labels_all = custom_plot_x_labels

    if custom_plot_y_labels is None:
        y_labels_all = plot_y_labels
    else:
        y_labels_all = custom_plot_y_labels

    n_plots_x = max(map(lambda x: len(x), layout))
    n_plots_y = len(layout)

    if custom_figsize is None:
        figsize = fig_size_speedup
    else:
        figsize = custom_figsize


    

    if grid_height_ratio is None:
        figs, axes=plt.subplots(nrows=n_plots_y,ncols=n_plots_x,figsize=figsize)
    else:
        print(grid_height_ratio)
        figs, axes=plt.subplots(nrows=n_plots_y,ncols=n_plots_x,figsize=figsize, gridspec_kw={'height_ratios': grid_height_ratio})
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
            
            subfigure_callback(axes[plot_y, plot_x], plot_x, plot_y)

            axes[plot_y, plot_x].set_xticks(x_major_ticks_top)
            axes[plot_y, plot_x].set_yticks(y_major_ticks_top)
            axes[plot_y, plot_x].set_xticks(x_minor_ticks_top,minor=True)
            axes[plot_y, plot_x].set_yticks(y_minor_ticks_top,minor=True)
            axes[plot_y, plot_x].grid(which="major",alpha=0.2, linestyle = 'dashed')
            axes[plot_y, plot_x].grid(which="minor",alpha=0, linestyle = 'dotted')

            if hasLinear:
                axes[plot_y, plot_x].plot([1, linear_line_pos], [1, linear_line_pos], 'r--')
            # axes[plot_y, plot_x].annotate('linear', xy=(linear_line_pos, linear_line_pos), xytext=(linear_line_pos + 1, linear_line_pos))

            if plot_y == 0:
                axes[plot_y, plot_x].set_title(x_labels_all[plot_x])

            # if plot_y == n_plots_y - 1:
            #     # axes[plot_y, plot_x].set_xlabel('# of Cores')
            #     axes[plot_y, plot_x].set_xlabel(x_labels_all[plot_x])

            # if plot_x == 0:
            #     # axes[plot_y, plot_x].set_ylabel('Speedup')
            #     axes[plot_y, plot_x].set_ylabel(y_labels_all[plot_y])



            
            y_label = y_labels_all[plot_y]
            if len(y_text) > 0:
                # y_label = y_label + '\n' + y_text
                axes[plot_y, plot_x].set_ylabel(y_text, style='italic')
                axes[plot_y, plot_x].set_xlabel(x_text, style='italic')

                #
                if plot_x == 0:
                    y_pox_x, y_pos_y = y_text_pos
                    y_pos_y = y_max[plot_y] / 100 * y_pos_y

                    axes[plot_y, plot_x].text(y_pox_x, y_pos_y, y_label, rotation=90)
            else:
                # No y label     
                axes[plot_y, plot_x].set_ylabel(y_label)
                axes[plot_y, plot_x].set_xlabel(x_text)


            axes[plot_y, plot_x].set_xlim(0, x_max)

            if y_max.__class__ == list:
                axes[plot_y, plot_x].set_ylim(0, y_max[plot_y])
            else:
                axes[plot_y, plot_x].set_ylim(0, y_max)


            axes[plot_y, plot_x].tick_params(axis='both', which='major', labelsize=9)

            if legend_pos == 'all':
                axes[plot_y, plot_x].legend(loc=legend_loc, fontsize=legend_fontsize)
            else:
                for legend_pos_x, legend_pos_y in legend_pos:
                    if legend_pos_x == plot_x and legend_pos_y == plot_y:
                        axes[plot_y, plot_x].legend(loc=legend_loc, fontsize=legend_fontsize)

            axes[plot_y, plot_x].label_outer()

    plt.tight_layout()
    plt.subplots_adjust(wspace=0.03, hspace=0.03)

    if savePlotFile != '':
        plt.savefig(savePlotFile)

    if showPlot:
        plt.show()
