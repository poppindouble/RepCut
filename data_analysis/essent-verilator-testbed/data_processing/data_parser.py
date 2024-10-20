#!/bin/env python3


import pdb
import re
import os
import sys
import base64
import pickle
import zlib
import json
import copy

import essent_profile_tool
import multiprocessing

import statistics

import bench


events = [
    'CYCLE_START',
    'EVAL_DONE',
    'SYNC_START',
    'SYNC_DONE',
    'CYCLE_DONE'
]

CYCLE_START = 0
EVAL_DONE = 1
SYNC_START = 2
SYNC_DONE = 3
CYCLE_DONE = 4



def serialize_pickle_z(dat, filename):
    with open(filename, 'wb') as f:
        byte_string = pickle.dumps(dat)
        compressed = zlib.compress(byte_string)
        # f.write(b64_enc.decode('utf8'))
        f.write(compressed)

def deserialize_pickle_z(filename):
    with open(filename, 'rb') as f:
        compressed = f.read()
        byte_string = zlib.decompress(compressed)
        obj = pickle.loads(byte_string)

        return obj

def deserialize_pickle_b64(filename):
    with open(filename) as f:
        b64_enc = f.read().encode('utf8')
        pickle_raw = base64.b64decode(b64_enc)
        obj = pickle.loads(pickle_raw)
        
        return obj

essent_profile_tool.CPU_TICK_RATE = bench.CPU_TICK_RATE

# # essent no-weight
# "./log/run_sh_essent_no-weight_${design}_${nThread}t_${iter}.log"
# # essent
# "./log/run_sh_essent_${design}_${nThread}t_${iter}.log"

# # verilator
# "./log/run_sh_verilator_${design}_${nThread}t_${iter}.log"
# # verilator pgo
# "./log/run_sh_verilator_pgo2_${design}_${nThread}t_${iter}.log"


# # essent cross
# "./log/run_sh_essent_cross_socket_${design}_${nThread}t_${iter}.log"
# # essent cross perf
# "./log/run_sh_essent_perf_cross_${design}_${nThread}t_${iter}.log"
# # essent perf
# "./log/run_sh_essent_perf_${design}_${nThread}t_${iter}.log"
# # essent profile
# "essent_profile_data_${design}_${nThread}t.pickle.z"
# # verilator gantt
# "./log/verilator_gantt_${design}_${nThread}t.dat"



def get_log_name(gen, design, nThreads, iteration):
    essent_log = "run_sh_essent_%s_%st_%s.log" % (design, nThreads, iteration)
    essent_no_weight_log = "run_sh_essent_no-weight_%s_%st_%s.log" % (design, nThreads, iteration)
    verilator_log = "run_sh_verilator_%s_%st_%s.log" % (design, nThreads, iteration)
    verilator_pgo_log = "run_sh_verilator_pgo2_%s_%st_%s.log" % (design, nThreads, iteration)

    if gen == 'essent':
        return essent_log
    if gen == 'essent_no-weight':
        return essent_no_weight_log
    if gen == 'verilator':
        return verilator_log
    if gen == 'verilator_pgo2':
        return verilator_pgo_log

    print("Error: Unknow generator %s" % (gen))
    exit(-1)

class DataParser(object):

    def __init__(self) -> None:
        self.log_dir = os.path.abspath(os.getcwd() + '/../log')
        
        self.speedup_data = {}
        self.runtime_data = {}

        self.cross_socket_speedup_data = {}
        self.cross_socket_runtime_data = {}

        self.essent_log_data = {}

        self.cycle_count_data = {}

        self.essent_profile_data = {}

        self.perf_data = {}
        self.cross_socket_perf_data = {}

        self.code_reg_mem_size = {}

        self.verilator_gantt = {}

        # Trace files
        self.accessed_files = []

    @staticmethod
    def parse_run_time_log(filename):
        key = 'elapsed'
        with open(filename) as f:
            file_content = f.read().split('\n')
            # if len(file_content) != 2:
            #     print("Error when parsing file: %s" % (filename))
            #     print(str(file_content))
            #     exit(-1)
            time_list = file_content[0].split(' ')

            for section in time_list:
                if section.find(key) >= 0:
                    # found
                    time_text = section.replace(key, '').strip()
                    time_clock = time_text.split(':')
                    time_sec = 0
                    for index, num in enumerate(reversed(time_clock)):
                        if index == 0:
                            time_sec = float(num)
                        elif index == 1:
                            time_sec += int(num) * 60
                        elif index == 2:
                            time_sec += int(num) * 3600
                        else:
                            print("Error: Unsupported time format: %s" % (time_text))
                            exit(-1)
                    return time_sec
                    

    def parse_run_data(self):

# # essent no-weight
# "./log/run_sh_essent_no-weight_${design}_${nThread}t_${iter}.log"
# # essent
# "./log/run_sh_essent_${design}_${nThread}t_${iter}.log"

# # verilator
# "./log/run_sh_verilator_${design}_${nThread}t_${iter}.log"
# # verilator pgo
# "./log/run_sh_verilator_pgo2_${design}_${nThread}t_${iter}.log"


        # Collect runtime
        for gen in bench.emulatorGenerators:
            self.runtime_data[gen] = {}

            for design in bench.benchmarkProjects:

                self.runtime_data[gen][design] = []
                for nThreads in bench.parallelThreads:
                    if nThreads == 1 and gen in bench.emulatorGenerators_no_sequential:
                        continue

                    raw_dat = []

                    for iteration in range(0, bench.iterations):
                        log_name = get_log_name(gen, design, nThreads, iteration)
                        log_path = os.path.join(self.log_dir, log_name)

                        self.accessed_files.append(log_path)
                        exec_time = self.parse_run_time_log(log_path)

                        raw_dat.append(exec_time)

                    avg_time = sum(raw_dat) / len(raw_dat)
                    self.runtime_data[gen][design].append((nThreads, avg_time))

        # Patch baseline
        for gen in bench.emulatorGenerators_no_sequential:
            for design in bench.benchmarkProjects:
                baseline_gen = bench.emulatorGenerators_baseline[gen]
                baseline_info = self.runtime_data[baseline_gen][design][0]
                if baseline_info[0] != 1:
                    print("Error: Unexpected baseline: %s" % str(baseline_info))
                self.runtime_data[gen][design].insert(0, baseline_info)

        # Calculate speedup
        for gen in bench.emulatorGenerators:
            self.speedup_data[gen] = {}
            for design in bench.benchmarkProjects:
                self.speedup_data[gen][design] = []
                
                baseline_info = self.runtime_data[gen][design][0]
                if baseline_info[0] != 1:
                    print("Error: Unexpected baseline: %s" % str(baseline_info))

                seq_exec_time = baseline_info[1]
                
                for nt, exec_time in self.runtime_data[gen][design]:
                    speedup = seq_exec_time / exec_time
                    self.speedup_data[gen][design].append((nt, speedup))



    def parse_essent_cross_socket_data(self):

# # essent cross
# "./log/run_sh_essent_cross_socket_${design}_${nThread}t_${iter}.log"

        # Collect runtime
        gen = 'essent'
        
        self.cross_socket_runtime_data[gen] = {}

        for design in bench.benchmarkProjects_cross_socket:

            self.cross_socket_runtime_data[gen][design] = []
            for nThreads in bench.parallelThreads_cross_socket:
                if nThreads == 1:
                    continue

                raw_dat = []

                for iteration in range(0, bench.iterations):
                    log_name = 'run_sh_essent_cross_socket_%s_%st_%s.log' % (design, nThreads, iteration)
                    log_path = os.path.join(self.log_dir, log_name)

                    self.accessed_files.append(log_path)
                    exec_time = self.parse_run_time_log(log_path)

                    raw_dat.append(exec_time)

                avg_time = sum(raw_dat) / len(raw_dat)
                self.cross_socket_runtime_data[gen][design].append((nThreads, avg_time))

            # Patch baseline
            baseline_info = self.runtime_data[gen][design][0]
            if baseline_info[0] != 1:
                print("Error: Unexpected baseline: %s" % str(baseline_info))
            self.cross_socket_runtime_data[gen][design].insert(0, baseline_info)

        # Calculate speedup

        self.cross_socket_speedup_data[gen] = {}
        for design in bench.benchmarkProjects_cross_socket:
            self.cross_socket_speedup_data[gen][design] = []
            
            baseline_info = self.runtime_data[gen][design][0]
            if baseline_info[0] != 1:
                print("Error: Unexpected baseline: %s" % str(baseline_info))

            seq_exec_time = baseline_info[1]
            
            for nt, exec_time in self.cross_socket_runtime_data[gen][design]:
                speedup = seq_exec_time / exec_time
                self.cross_socket_speedup_data[gen][design].append((nt, speedup))



    # def add_placeholder_commercial(self):
    #     self.speedup_data['commercial'] = {}
    #     self.runtime_data['commercial'] = {}
    #     self.cycle_count_data['commercial'] = {}
    #     for line_name, line_data in self.run_data_raw['essent'].items():
    #         self.speedup_data['commercial'][line_name] = list(map(lambda x: (x[0], 1), line_data.items()))
    #         self.runtime_data['commercial'][line_name] = list(map(lambda x: (x[0], 1), line_data.items()))

    #         self.cycle_count_data['commercial'][line_name] = {}
    #         for nThreads in bench.parallelThreads:
    #             self.cycle_count_data['commercial'][line_name][nThreads] = 1


    @staticmethod
    def _parse_essent_log(filename):
        check_stat_token = "Starting Transform essent.passes.CheckStatistics"
        stat_found = False

        sink_node_dist_start_line = """*****Sink Node Distribution*****"""
        sink_node_dist_end_line = """*****End Sink Node Distribution*****"""
        sink_node_dist_found = False
        
        ret = {}
        firrtl_irs = {}
        kahypar_info = {}
        part_info = {}
        sink_node_dist = {}
        sink_nodes = 0
        n_stmts_design = 0
        n_stmts_all = 0
        weight_design = 0
        weight_replicate = 0

        with open(filename) as f:
            for eachline in f:
                line = eachline.strip()

                # KaHyPar partition size
                if len(re.findall("\|part\s+\d+\s+\|\s+=\s+\d+\s+w\(\s+\d+\s+\)\s+=\s+\d+", line)) > 0:
                    dat = re.findall("\d+", line)
                    part_id, part_size, _, part_weight = dat
                    kahypar_info[int(part_id)] = int(part_weight)

                # Sink nodes
                if len(re.findall("^Found \d+ sink nodes$", line)) > 0:
                    sink_nodes = int(re.findall("\d+", line)[0])

                # Sink node distribution
                if line.find(sink_node_dist_start_line) >= 0:
                    sink_node_dist_found = True
                elif line.find(sink_node_dist_end_line) >= 0:
                    sink_node_dist_found = False
                elif sink_node_dist_found:
                    k, v = line.split(":")
                    sink_node_dist[k.strip()] = int(v.strip())

                # FIRRTL IR
                if line.find(check_stat_token) > 0:
                    stat_found = True
                elif line.find('-------------------------------------------------------') >= 0:
                    stat_found = False
                if stat_found:
                    if len(line.split(":")) == 2:
                        # print(line)
                        k, v = line.split(":")
                        firrtl_irs[k.strip()] = int(v.strip())

                # partition info
                if len(re.findall("Pid: \d+, part size: \d+, part weight: \d+", line)) > 0:
                    # found
                    pid, stmts, weight = re.findall("\d+", line)
                    part_info[int(pid)] = {"stmts": int(stmts), "weight": int(weight)}

                # graph info
                if len(re.findall("Total node count is \d+, original statement graph has \d+ valid nodes", line)) > 0:
                    n_stmts_all, n_stmts_design = re.findall("\d+", line)
                    n_stmts_all = int(n_stmts_all)
                    n_stmts_design = int(n_stmts_design)

                if len(re.findall("Total node weight \(whole design\) is \d+", line)) > 0:
                    weight_design = int(re.findall("\d+", line)[0])

                if len(re.findall("Duplication weight cost: \d+", line)) > 0:
                    weight_replicate = int(re.findall("\d+", line)[0])

                if len(re.findall("Graph has \d+ nodes \(\d+ valid\) and \d+ edges", line)) > 0:
                    nodes, valid_nodes, edges = re.findall("\d+", line)
                    ret['IR Nodes'] = int(nodes)
                    ret['Valid Nodes'] = int(valid_nodes)
                    ret['Edges'] = int(edges)
                    

        # Firrtl ir, before flatten
        ret["FIRRTL IR"] = firrtl_irs
        ret['Sink Nodes'] = sink_nodes
        ret['Sink Node Distribution'] = sink_node_dist
        ret["Partitions"] = part_info
        ret['stmts_design'] = n_stmts_design
        ret['stmts_replication'] = n_stmts_all - n_stmts_design
        ret['weight_design'] = weight_design
        ret['weight_replication'] = weight_replicate
        ret['KaHyPar Weight'] = kahypar_info

        if weight_design != 0:
            ret['stmts_replication_cost'] = (n_stmts_all - n_stmts_design) * 100 / n_stmts_design
            ret['weight_replication_cost'] = weight_replicate * 100 / weight_design

        return ret

    def parse_essent_log(self):
        for design in bench.benchmarkProjects:
            self.essent_log_data[design] = {}
            for nthread in bench.parallelThreads:
                log_filename = "essent_%s_%st.log" % (design, nthread)
                log_file_path = os.path.join(self.log_dir, log_filename)

                if not os.path.exists(log_file_path):
                    print("Warning: log file [%s] does not exist" % (log_file_path))
                    exit(-1)

                self.accessed_files.append(log_file_path)
                self.essent_log_data[design][nthread] = self._parse_essent_log(log_file_path)


    def parse_emulator_log(self):
        for gen in bench.emulatorGenerators:
            if gen != 'essent':
                continue
            self.cycle_count_data[gen] = {}
            for design in bench.benchmarkProjects:
                self.cycle_count_data[gen][design] = {}
                for nthread in bench.parallelThreads:
                    log_filename = "run_%s-%s-%st-0_stdout.log" % (gen, design, nthread)
                    log_file_path = os.path.join(self.log_dir, log_filename)

                    if not os.path.exists(log_file_path):
                        print("Warning: log file [%s] does not exist" % (log_file_path))
                        exit(-1)

                    # Completed after 1439263 cycles
                    self.accessed_files.append(log_file_path)
                    cycle_count = 0
                    with open(log_file_path) as f:
                        for line in f:
                            if len(re.findall("Completed after \d+ cycles", line)) > 0:
                                cycle_count = int(re.findall("\d+", line)[0])

                    self.cycle_count_data[gen][design][nthread] = cycle_count
            for gen in bench.emulatorGenerators:
                if gen != 'essent':
                    # copy cycle count from ESSENT. They should be same
                    self.cycle_count_data[gen] = copy.deepcopy(self.cycle_count_data['essent'])

    @staticmethod
    def _parse_essent_profile_log(filename):

        print("Working on file [%s]" % filename)
        dat = deserialize_pickle_z(filename)

        def drop_extreme(d):
            min_val = min(d)
            mean = statistics.mean(d)

            cleanned = list(filter(lambda x: x < (mean - min_val) * 2 + min_val, d))

            return cleanned

        record_cycles = dat['Profile Cycles']
        nthreads = dat['nThreads']

        events = [
            CYCLE_START,
            EVAL_DONE,
            SYNC_START,
            SYNC_DONE,
            CYCLE_DONE
        ]


        ret = {i: {
            CYCLE_START: [],
            EVAL_DONE: [],
            SYNC_START: [],
            SYNC_DONE: [],
            CYCLE_DONE: []
        } for i in range(0, nthreads)}

        for cycle, cycle_data in enumerate(zip(*[dat[i] for i in range(0, nthreads)])):
            cycle_start_tick = cycle_data[0][CYCLE_START]

            for tid in range(0, nthreads):
                cycle_start_tick = min(cycle_start_tick, cycle_data[tid][CYCLE_START])
            
            for tid in range(0, nthreads):
                for ev in events:
                    d = cycle_data[tid][ev] - cycle_start_tick
                    ret[tid][ev].append(d)

        
        for tid in range(0, nthreads):
            for ev in events:
                ret[tid][ev] = statistics.mean(drop_extreme(ret[tid][ev]))

        return ret


    def parse_essent_profile_log(self):
        # don't store raw data in memory

        task_files = []
        task_config = []
        for design in bench.benchmarkProjects:
            self.essent_profile_data[design] = {}

            for nThread in bench.parallelThreads_profile:
                if nThread == 1:
                    continue

                profile_filename = "essent_profile_data_%s_%st.pickle.z" % (design, nThread)
                profile_file_path = os.path.join(self.log_dir, profile_filename)


                if not os.path.exists(profile_file_path):
                    print("Warning: log file [%s] does not exist" % (profile_file_path))
                    exit(-1)

                task_files.append(profile_file_path)
                task_config.append((design, nThread))

        cpu_count = min(int(os.cpu_count() / 2), 16)
        pool = multiprocessing.Pool(cpu_count)

        parsed = pool.map(self._parse_essent_profile_log, task_files)

        for cfg, result in zip(task_config, parsed):
            design, nThread = cfg

            self.essent_profile_data[design][nThread] = result

        pool.close()
        pool.join()
        self.accessed_files.extend(task_files)


    @staticmethod
    def _parse_essent_perf_log(log_file_path):
        ret = {}
        with open(log_file_path) as f:
            found_perf = False

            for line in f:
                if len(line.strip()) == 0:
                    continue

                if found_perf:
                    # Split by space and drop empty string
                    split_line = list(filter(lambda x: len(x) > 0, re.split("\s+", line)))
                    num, event = split_line[:2]

                    if event in bench.perf_events:
                        # found a perf event
                        ret[event] = int(num.replace(',', ''))
                    elif event == 'seconds':
                        # time
                        key = ''
                        if split_line[2] == 'time':
                            # total time
                            key = 'time_total'
                        elif split_line[2] == 'user':
                            key = 'time_user'
                        elif split_line[2] == 'sys':
                            key = 'time_sys'
                        else:
                            print("Error: unknow exec time")
                            print(line)
                            exit(-1)
                        ret[key] = float(num.replace(',', ''))
                    else:
                        print("Error: unknow event")
                        print(line)
                        exit(-1)
                if line.find("Performance counter stats for") >= 0:
                    found_perf = True


        return ret

    def parse_essent_perf_log(self):
        self.perf_data['essent'] = {}
        perf_events = bench.perf_events


        for design in bench.benchmarkProjects_perf:
            self.perf_data['essent'][design] = {}
            for nthread in bench.parallelThreads:
                log_filename = "run_sh_essent_perf_%s_%st_0.log" % (design, nthread)
                log_file_path = os.path.join(self.log_dir, log_filename)

                if not os.path.exists(log_file_path):
                    print("Warning: log file [%s] does not exist" % (log_file_path))
                    continue

                self.accessed_files.append(log_file_path)
                self.perf_data['essent'][design][nthread] = self._parse_essent_perf_log(log_file_path)

    def parse_cross_socket_essent_perf_log(self):
        self.cross_socket_perf_data['essent'] = {}
        perf_events = bench.perf_events


        for design in bench.benchmarkProjects_perf:
            self.cross_socket_perf_data['essent'][design] = {}
            for nthread in bench.parallelThreads:
                if nthread == 1:
                    continue
                log_filename = "run_sh_essent_perf_cross_%s_%st_0.log" % (design, nthread)
                log_file_path = os.path.join(self.log_dir, log_filename)

                if not os.path.exists(log_file_path):
                    print("Warning: log file [%s] does not exist" % (log_file_path))
                    continue

                self.accessed_files.append(log_file_path)
                self.cross_socket_perf_data['essent'][design][nthread] = self._parse_essent_perf_log(log_file_path)

    # def parse_code_size(self):
    #     dat_file_path = os.path.join(self.log_dir, "code_mem_size.json")
    #     self.accessed_files.append(dat_file_path)
    #     with open(dat_file_path) as f:
    #         self.code_reg_mem_size = json.loads(f.read())

    @staticmethod
    def _parseVerilatorGantt(filename):
        ret = {}
        with open(filename) as f:

            current_thread = -1
            current_thread_mtasks = []

            begin_tick = 0
            predict_begin_tick = 0
            mtask_id = 0
            cpu_id = 0

            for _lineno, line in enumerate(f):
                lineno = _lineno + 1

                if line.find("VLPROFPROC") >= 0:
                    # dont care
                    continue
                
                if line.find("VLPROFTHREAD") >= 0:
                    thread_id = int(re.findall("\d+", line)[0])
                    if len(current_thread_mtasks) != 0:
                        ret[current_thread] = current_thread_mtasks
                        current_thread_mtasks = []
                    current_thread = thread_id
                elif line.find("VLPROFEXEC") >= 0:
                    # A new mtask
                    split_line = line.split(" ")
                    if split_line[1] == 'MTASK_BEGIN':
                        begin_tick, mtask_id, predict_begin_tick, cpu_id = list(map(lambda x: int(x), re.findall("\d+", line)))

                    if split_line[1] == 'MTASK_END':
                        end_tick, end_mtask_id, predict_cost_tick = list(map(lambda x: int(x), re.findall("\d+", line)))

                        if end_mtask_id != mtask_id:
                            print("Error: mtask overlapping observed at line %s" % (lineno))
                            exit(-1)

                        current_thread_mtasks.append({
                            "mtask_id" : mtask_id,
                            "predict_begin": predict_begin_tick,
                            "predict_end": predict_begin_tick + predict_cost_tick,
                            "real_begin": begin_tick,
                            "real_end": end_tick
                        })
                elif line.find("VLPROF stat ticks") >= 0:
                    total_ticks = int(re.findall("\d+", line)[0])
                    ret['ticks'] = total_ticks
        return ret

    def parse_verilator_gantt(self):
        self.verilator_gantt = {}
        
        for design in bench.benchmarkProjects:
            self.verilator_gantt[design] = {}
            for nthread in bench.parallelThreads_profile:
                if nthread == 1:
                    continue
                log_filename = "verilator_gantt_%s_%st.dat" % (design, nthread)
                log_file_path = os.path.join(self.log_dir, log_filename)

                if not os.path.exists(log_file_path):
                    print("Warning: log file [%s] does not exist" % (log_file_path))
                    exit(-1)

                self.accessed_files.append(log_file_path)
                self.verilator_gantt[design][nthread] = self._parseVerilatorGantt(log_file_path)
    



if __name__ == '__main__':
    noPGO = True

    options = ['no_pgo', 'with_pgo']
    if sys.argv[1] in options:
        if sys.argv[1] != 'no_pgo':
            noPGO = False
    else:
        print("Error: Please choose from " + str(options))
        exit(-1)

    if noPGO:
        bench.emulatorGenerators = [
            'essent', 
            'essent_no-weight',
            'verilator'
        ]

        bench.emulatorGenerators_no_sequential = [
            'essent_no-weight',
        ]

    dat = DataParser()
    dat.log_dir = os.path.abspath('./log/')

    dat.parse_verilator_gantt()

    dat.parse_run_data()
    dat.parse_essent_perf_log()
    dat.parse_essent_cross_socket_data()
    dat.parse_emulator_log()
    dat.parse_essent_log()
    dat.parse_cross_socket_essent_perf_log()

    # dat.parse_code_size()

    # This is slow
    dat.parse_essent_profile_log()


    serialize_pickle_z(dat, "parsed_data.pickle.z")

    # log_dir_files = os.listdir(dat.log_dir)
    # for log_file in log_dir_files:
    #     log_file_path = os.path.join(dat.log_dir, log_file)
    #     if log_file_path not in dat.accessed_files:
    #         print("mv ./log/%s ./unused_log/%s" % (log_file, log_file))