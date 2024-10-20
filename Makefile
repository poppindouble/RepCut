
base_dir=$(abspath .)

design_dir=$(base_dir)/designs
weighted_dir=$(base_dir)/weighted/essent-verilator-testbed
unweighted_dir=$(base_dir)/unweighted/essent-verilator-testbed
script_dir=$(base_dir)/data_analysis/essent-verilator-testbed


CXX ?= clang++-14
LINK ?= clang++-14
AR ?= llvm-ar-14


ROCKET_WORK_DIR=$(design_dir)/rocket-chip/emulator
ROCKET_GEN_DIR=$(ROCKET_WORK_DIR)/generated-src

BOOM_WORK_DIR=$(design_dir)/boom-standalone/verisim
BOOM_GEN_DIR=$(BOOM_WORK_DIR)/generated-src


DESIGN_ROCKET_SHORTNAME = \
	rocket21-1c \
	rocket21-2c \
	rocket21-4c \


DESIGN_ROCKET_CONFIG_rocket21-1c=freechips.rocketchip.system.DefaultConfig
DESIGN_ROCKET_CONFIG_rocket21-2c=freechips.rocketchip.system.DualCoreConfig
DESIGN_ROCKET_CONFIG_rocket21-4c=freechips.rocketchip.system.QuadCoreConfig

DESIGN_BOOM_SHORTNAME = \
	boom21-4small \
	boom21-4large \
	boom21-4mega \
	boom21-2small \
	boom21-2large \
	boom21-2mega \
	boom21-small \
	boom21-large \
	boom21-mega \


DESIGN_BOOM_CONFIG_boom21-small=SmallBoomConfig
DESIGN_BOOM_CONFIG_boom21-2small=DualSmallBoomConfig
DESIGN_BOOM_CONFIG_boom21-4small=QuadSmallBoomConfig
DESIGN_BOOM_CONFIG_boom21-large=LargeBoomConfig
DESIGN_BOOM_CONFIG_boom21-2large=DualLargeBoomConfig
DESIGN_BOOM_CONFIG_boom21-4large=QuadLargeBoomConfig
DESIGN_BOOM_CONFIG_boom21-mega=MegaBoomConfig
DESIGN_BOOM_CONFIG_boom21-2mega=DualMegaBoomConfig
DESIGN_BOOM_CONFIG_boom21-4mega=QuadMegaBoomConfig



MAKE_VARIABLES = CXX=$(CXX) LINK=$(LINK) AR=$(AR)

# Compiles Rocket chip FIRRTL file
DESIGN_COMPILE_ROCKET_TARGETS = $(addprefix firrtl_,$(DESIGN_ROCKET_SHORTNAME))

${DESIGN_COMPILE_ROCKET_TARGETS}: firrtl_%:
# Make firrtl. RISCV can point to any directory. it's not used
	cd $(ROCKET_WORK_DIR) && make RISCV=$(base_dir) $(ROCKET_GEN_DIR)/$(DESIGN_ROCKET_CONFIG_$*).fir CONFIG=$(DESIGN_ROCKET_CONFIG_$*)
# Compress
	cd $(ROCKET_GEN_DIR) && tar -cvzf $*-firrtl.tar.gz ./$(DESIGN_ROCKET_CONFIG_$*).fir
# Copy to workspace
	cp $(ROCKET_GEN_DIR)/$*-firrtl.tar.gz $(weighted_dir)/$*/firrtl.tar.gz
	cp $(ROCKET_GEN_DIR)/$*-firrtl.tar.gz $(unweighted_dir)/$*/firrtl.tar.gz
	cp $(ROCKET_GEN_DIR)/$(DESIGN_ROCKET_CONFIG_$*).plusArgs $(weighted_dir)/$*/
	cp $(ROCKET_GEN_DIR)/$(DESIGN_ROCKET_CONFIG_$*).plusArgs $(unweighted_dir)/$*/


# Compiles BOOM FIRRTL file
DESIGN_COMPILE_BOOM_TARGETS = $(addprefix firrtl_,$(DESIGN_BOOM_SHORTNAME))

${DESIGN_COMPILE_BOOM_TARGETS}: firrtl_%:
# Make firrtl. RISCV can point to any directory. it's not used
	cd $(BOOM_WORK_DIR) && make RISCV=$(base_dir) firrtl CONFIG=$(DESIGN_BOOM_CONFIG_$*)
# Compress
	cd $(BOOM_GEN_DIR) && tar -cvzf $*-firrtl.tar.gz ./freechips.rocketchip.system.$(DESIGN_BOOM_CONFIG_$*).fir
# Copy to workspace
	cp $(BOOM_GEN_DIR)/$*-firrtl.tar.gz $(weighted_dir)/$*/firrtl.tar.gz
	cp $(BOOM_GEN_DIR)/$*-firrtl.tar.gz $(unweighted_dir)/$*/firrtl.tar.gz
	cp $(BOOM_GEN_DIR)/freechips.rocketchip.system.$(DESIGN_BOOM_CONFIG_$*).plusArgs $(weighted_dir)/$*/
	cp $(BOOM_GEN_DIR)/freechips.rocketchip.system.$(DESIGN_BOOM_CONFIG_$*).plusArgs $(unweighted_dir)/$*/



# Prepare build directory
env_prepare_weighted:
	$(MAKE) $(MAKE_VARIABLES) -C $(weighted_dir) prepare

env_prepare_unweighted:
	$(MAKE) $(MAKE_VARIABLES) -C $(unweighted_dir) -f Makefile-essent-no-weight prepare


# build RCP emulator
emulator_repcut_weighted: 
	$(MAKE) $(MAKE_VARIABLES) -C $(weighted_dir) emulator_essent

# build RCP emulator (no weight)
emulator_repcut_unweighted: 
	$(MAKE) $(MAKE_VARIABLES) -C $(unweighted_dir) -f Makefile-essent-no-weight emulator_essent


# build Verilator baseline
emulator_verilator: 
	$(MAKE) $(MAKE_VARIABLES) -C $(weighted_dir) emulator_verilator


# build Verilator with profiling
emulator_verilator_prof: 
	$(MAKE) $(MAKE_VARIABLES) -C $(weighted_dir) emulator_verilator_prof


# Build Verilator PGO 1
emulator_verilator_pgo1: 
	$(MAKE) $(MAKE_VARIABLES) -C $(weighted_dir) emulator_verilator_pgo1

# Run Verilator PGO 1
emulator_verilator_pgo1_run: emulator_verilator_pgo1
	@echo Run PGO1 simulators to collect profile data
	cd $(weighted_dir) && bash ./run_verilator_pgo1.sh

# Build Verilator PGO 2
emulator_verilator_pgo2: emulator_verilator_pgo1_run
	$(MAKE) $(MAKE_VARIABLES) -C $(weighted_dir) emulator_verilator_pgo2


# A quick compilation
# Only compiles boom21-2small 1,2,4,6,8 threads
emulator_essent_quick:
	$(MAKE) $(MAKE_VARIABLES) -C $(weighted_dir) compile_essent_boom21-2small_1 compile_essent_boom21-2small_2 compile_essent_boom21-2small_4 compile_essent_boom21-2small_6 compile_essent_boom21-2small_8



# Run 
run_no_pgo:
	cd $(unweighted_dir) && bash ./run_essent_no-weight_only.sh
	cd $(weighted_dir) && bash ./run_essent_only.sh
# Remove following line if you cannot run perf
	cd $(weighted_dir) && bash ./run_essent_cross_socket_perf.sh
	cd $(weighted_dir) && bash ./run_essent_cross_socket.sh
# Remove following line if you cannot run perf
	cd $(weighted_dir) && bash ./run_essent_perf.sh
	cd $(weighted_dir) && bash ./run_essent_profile.sh
	cd $(weighted_dir) && bash ./run_verilator_only.sh
	cd $(weighted_dir) && bash ./run_verilator_profile.sh


run_pgo2:
	cd $(weighted_dir) && bash ./run_verilator_pgo2.sh


# Run quick compilation_result
run_quick:
	cd $(weighted_dir) && bash ./run_essent_quick.sh


# Measure RDTSC tick rate
$(script_dir)/data_processing/cpu_tick_rate.txt:
	cd $(script_dir)/data_processing/ && $(CXX) time_tick_measure.cpp -o measure_cpu_tick
	$(script_dir)/data_processing/measure_cpu_tick > $(script_dir)/data_processing/cpu_tick_rate.txt

figures_no_pgo: $(script_dir)/data_processing/cpu_tick_rate.txt
	rsync -a $(weighted_dir)/log/* $(script_dir)/log/
	rsync -a $(unweighted_dir)/log/* $(script_dir)/log/
	cd $(script_dir) && python3 ./data_processing/data_parser.py no_pgo
	cd $(script_dir) && python3 ./data_processing/plot.py no_pgo

figures_with_pgo: $(script_dir)/data_processing/cpu_tick_rate.txt
	rsync -a $(weighted_dir)/log/* $(script_dir)/log/
	rsync -a $(unweighted_dir)/log/* $(script_dir)/log/
	cd $(script_dir) && python3 ./data_processing/data_parser.py with_pgo
	cd $(script_dir) && python3 ./data_processing/plot.py with_pgo

result_quick:
	cd $(weighted_dir) && python3 ./print_quick_result.py


.PHONY: design_firrtl $(DESIGN_COMPILE_ROCKET_TARGETS) $(DESIGN_COMPILE_BOOM_TARGETS) firrtl_clean build_clean figure_clean clean env_prepare_weighted env_prepare_unweighted emulator_repcut_unweighted emulator_repcut_weighted emulator_verilator emulator_verilator_prof emulator_verilator_pgo1 emulator_verilator_pgo1_run emulator_verilator_pgo2 emulator_no_pgo prepare run_no_pgo run_pgo2 figures_no_pgo figures_with_pgo emulator_essent_quick run_quick result_quick

design_firrtl: $(DESIGN_COMPILE_ROCKET_TARGETS) $(DESIGN_COMPILE_BOOM_TARGETS)

emulator_no_pgo: emulator_repcut_weighted emulator_verilator emulator_repcut_unweighted emulator_verilator_prof

prepare: env_prepare_unweighted env_prepare_weighted



firrtl_clean:
	-rm -rf $(ROCKET_GEN_DIR)/*
	-rm -rf $(BOOM_GEN_DIR)/*
	-$(foreach design, $(DESIGN_ROCKET_SHORTNAME), rm $(weighted_dir)/$(design)/firrtl.tar.gz; rm $(unweighted_dir)/$(design)/firrtl.tar.gz; )
	-$(foreach design, $(DESIGN_ROCKET_SHORTNAME), rm $(weighted_dir)/$(design)/$(DESIGN_ROCKET_CONFIG_$(design)).plusArgs; rm $(unweighted_dir)/$(design)/$(DESIGN_ROCKET_CONFIG_$(design)).plusArgs;)
	-$(foreach design, $(DESIGN_BOOM_SHORTNAME), rm $(weighted_dir)/$(design)/firrtl.tar.gz; rm $(unweighted_dir)/$(design)/firrtl.tar.gz; )
	-$(foreach design, $(DESIGN_BOOM_SHORTNAME), rm $(weighted_dir)/$(design)/freechips.rocketchip.system.$(DESIGN_BOOM_CONFIG_$(design)).plusArgs; rm $(unweighted_dir)/$(design)/freechips.rocketchip.system.$(DESIGN_BOOM_CONFIG_$(design)).plusArgs;)

build_clean:
	-rm -rf $(weighted_dir)/build
	-rm -rf $(weighted_dir)/log/*
	-rm -rf $(weighted_dir)/emulator/*
	-rm -rf $(unweighted_dir)/build
	-rm -rf $(unweighted_dir)/log/*
	-rm -rf $(unweighted_dir)/emulator/*


figure_clean:
	-rm $(script_dir)/*.pdf
	-rm $(script_dir)/log/*

clean: firrtl_clean build_clean figure_clean