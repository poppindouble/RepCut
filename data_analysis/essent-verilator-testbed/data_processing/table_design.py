
import bench
import plot_config





def acquire_table_data(dat):
    ret = []

    for design in plot_config.design_simple_pretty_name.keys():
        design_name = plot_config.design_simple_pretty_name[design]
        valid_ir_count = dat.essent_log_data[design][1]['Valid Nodes']
        edge_count = dat.essent_log_data[design][1]['Edges']
        sink_nodes = dat.essent_log_data[design][2]['Sink Nodes']
        reg_writes = dat.essent_log_data[design][2]['Sink Node Distribution']['essent.ir.RegUpdate']

        ret.append([design_name, valid_ir_count, edge_count, sink_nodes, sink_nodes * 100 / valid_ir_count, reg_writes])

    return ret


def print_table_latex(table):
    title = ['Design', 'IR Nodes', 'Edges', 'Sink Vtx', r'\multicolumn{1}{c}{\textbf{Sink Vtx (\%)}}', 'Reg Writes']

    title_fmt = map(lambda x: "\\textbf{%s}" % (x), title)

    print(r" & ".join(title_fmt) + r" \\")
    print(r"\hline")

    for line in table:
        line_text = r"""%s & %s & %s & %s & %.2f & %s \\""" % tuple(line)
        print(line_text)
        print(r"\hline")


if __name__ == '__main__':
    import bench
    from data_parser import DataParser, deserialize_pickle_z

    # load data
    dat = deserialize_pickle_z("parsed_data.pickle.z")

    table_dat = acquire_table_data(dat)

    print_table_latex(table_dat)


