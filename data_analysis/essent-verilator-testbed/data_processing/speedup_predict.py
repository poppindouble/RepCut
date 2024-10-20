#!/bin/env python3


import bench
import plot_config

from data_parser import DataParser, deserialize_pickle_z
CPU_TICK_RATE = 2394620000


def predict_speedup(log_dat, design, nthread):
    if nthread == 1:
        return 1.0

    def get_measured_ib(dataset, nThreads):
        raw_dat = []
        for tid in range(0, nThreads):
            raw_dat.append(dat.essent_profile_data[dataset][nThreads][tid]['eval'])
        return plot_config.calculate_ib_factor(raw_dat)

    ib_facor = get_measured_ib(design, nthread)

    run_time = dict(dat.runtime_data['essent'][design])
    time_1t = run_time[1]
    time_nt = run_time[nthread]
    nCycles = dat.cycle_count_data['essent'][design][nthread]



    replication_cost = dat.essent_log_data[design][nthread]['weight_replication_cost']

    sequential_ticks = -1
    parallel_work = 0
    total_eval_ticks = 0
    for i in range(0, nthread):
        barrier_ticks = dat.essent_profile_data[design][nthread][i]['barrier']
        sync_ticks = dat.essent_profile_data[design][nthread][i]['sync']
        last_ticks = dat.essent_profile_data[design][nthread][i]['last']
        eval_ticks = dat.essent_profile_data[design][nthread][i]['eval']

        total_eval_ticks += eval_ticks

        measured_seq_work = dat.essent_profile_data[design][nthread][i]['barrier']
        measured_seq_work += dat.essent_profile_data[design][nthread][i]['sync']
        measured_seq_work += dat.essent_profile_data[design][nthread][i]['last']
        parallel_work = max(parallel_work, dat.essent_profile_data[design][nthread][i]['eval'])

        if sequential_ticks == -1:
            sequential_ticks = measured_seq_work
        else:
            sequential_ticks = min(sequential_ticks, measured_seq_work)
    
    cycle_time = time_nt / nCycles
    # measured_seq_time = (sequential_ticks / (sequential_ticks + parallel_work)) * cycle_time


    total_seq_eval_ticks = time_1t * CPU_TICK_RATE
    total_par_eval_ticks = total_eval_ticks * nCycles

    eval_speedup = total_seq_eval_ticks / total_par_eval_ticks



    # try to predict
    original_cycle_ticks = total_seq_eval_ticks / nCycles

    real_work = 1 * (1 + replication_cost/100)
    avg_work = real_work / nthread
    peak_thread_work = avg_work * (1 + ib_facor)

    peak_thread_exec_ticks = ((total_seq_eval_ticks / nCycles) * peak_thread_work) / eval_speedup

    peak_thread_cycle_ticks = peak_thread_exec_ticks + sequential_ticks


    predicted_speedup = original_cycle_ticks / peak_thread_cycle_ticks

    return predicted_speedup




if __name__ == '__main__':
    dat = deserialize_pickle_z("parsed_data.pickle.z")


    for design in bench.benchmarkProjects:
        # if design != 'boom21-4mega':
        #     continue
        design_speedups = dict(dat.speedup_data['essent'][design])
        for nthread in bench.parallelThreads:
            if nthread > 24:
                continue
            predicted_sp = predict_speedup(dat, design, nthread)
            real_speedup = design_speedups[nthread]

            stat = "{0:>14}, {1:>3} threads, predicted speedup: {2:>5.2f}x, real {3:>5.2f}x".format(design, nthread, predicted_sp, real_speedup)

            print(stat)