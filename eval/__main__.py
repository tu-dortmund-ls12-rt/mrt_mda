#!/usr/bin/env python3
# Evaluation from the paper achieved with python3 -O eval -s0 -p200 -r1000 -n10000
import statistics

from optparse import OptionParser
import sys

import itertools
import random
import numpy as np
import timeit
from multiprocessing import Pool

import benchmark_WATERS as bench

import analysis as ana
import helpers
import plot

# set seed
random.seed(314159)
np.random.seed(314159)

# output path
path_out = "output/"


# Analysis class
###
# Analysis result class
###
class AnaRes:
    """Result of the analysis."""

    def __init__(
        self,
        chain,
        lat_our=None,
        lat_other=None,
        time_our=None,
        time_other=None,
    ):
        # chain
        self.chain = chain

        # our results
        self.lat_our = lat_our

        # other results
        self.lat_other = lat_other

        # timing
        self.time_our = time_our
        self.time_other = time_other

    def check_equal(self):
        return all(
            [
                self.lat_our == self.lat_other,
            ]
        )

    def speedup(self):
        return self.time_other / self.time_our

    def time_ratio(self):
        return self.time_our / self.time_other

    def num_act_pattern(self):
        return len(self.chain.involved_activation_patterns())


##
# Handle Options
##
number_systems_per_util = (
    10000  # number of taskset and cause-effect chain pairs for each utilization
)
code_switch = 0
processes = 1
repeat_measurement = 100
# options
parser = OptionParser()
parser.add_option(
    "-s",
    "--switch",
    dest="code_switch",
    type="int",
    help="Switch to place SWITCH of the experiment.",
    metavar="SWITCH",
)
parser.add_option(
    "-p",
    "--proc",
    "--processes",
    dest="processes",
    type="int",
    help="Number of simultaneous processes.",
)
parser.add_option(
    "-r",
    "--repeat",
    dest="repeat_measurement",
    type="int",
    help="Repeat the runtime measurement REPEAT times and take the smallest one.",
    metavar="REPEAT",
)
parser.add_option(
    "-n",
    "--number",
    dest="number_systems_per_util",
    type="int",
    help="Number of systems to be created per utilization.",
)

(options, args) = parser.parse_args()

if options.code_switch is not None:
    code_switch = options.code_switch

if options.processes is not None:
    processes = options.processes

if options.repeat_measurement is not None:
    repeat_measurement = options.repeat_measurement

if options.number_systems_per_util is not None:
    number_systems_per_util = options.number_systems_per_util

#####
# Generate tasksets and chains
#####

if code_switch in [0, 1]:
    """TODO"""  # TODO
    tries_before_abortion = 100

    def make_system(tries=None, debug_geq=0):
        """Create a task sets and cause-effect chain."""

        ce = None
        for id in itertools.count():
            if tries is not None and id + 1 > tries:
                raise RuntimeError(
                    f"Cause-effect chain could not be created after {tries + 1} tries."
                )
            ts = bench.gen_taskset_periods(random.randint(50, 100))
            ce = bench.gen_ce_chain(ts)

            if ce is not None:  # break when successful
                break

        if __debug__ and id >= debug_geq:
            print(
                f"Cause-effect chain successfully created after {id} failed attempts."
            )

        # set phases = 0
        for tsk in ce.base_ts:
            tsk.rel.phase = 0

        return ce

    def print_status(id):
        number_systems_per_util / 10
        if (id + 1) % (number_systems_per_util / 20) == 0:
            print(helpers.time_now(), f"== {id + 1} systems created")
        return True

    ces = [
        make_system(tries=tries_before_abortion, debug_geq=5)
        for id in range(number_systems_per_util)
        if print_status(id)
    ]

    # Store
    print(helpers.time_now(), "Store Results")
    helpers.check_or_make_directory(path_out)
    helpers.write_data(path_out + f"ces.pickle", ces)


#####
# Analysis
#####

if code_switch in [0, 2]:
    """Run analysis for the experiments (E2E Latency only)."""

    # Load data
    print(helpers.time_now(), "Load data")
    ces = helpers.load_data(path_out + f"ces.pickle")

    # do experiments
    print(helpers.time_now(), "Start our analysis")
    with Pool(processes) as p:
        our_results = p.starmap(
            ana.our_all_lat_only, zip(ces, itertools.repeat(repeat_measurement))
        )

    print(helpers.time_now(), "Start other analysis")
    with Pool(processes) as p:
        other_results = p.starmap(
            ana.other_all_lat_only, zip(ces, itertools.repeat(repeat_measurement))
        )

    assert (
        len(ces) == len(our_results) == len(other_results)
    ), "length of results and of ce chains does not coincide"

    # match into analysis objects
    print(helpers.time_now(), "Match analysis objects")
    ana_results = []
    for ce, our, other in zip(ces, our_results, other_results):
        ana_results.append(
            AnaRes(
                ce,
                lat_our=our['lat'],
                lat_other=other['lat'],
                time_our=our["time"],
                time_other=other["time"],
            )
        )

    # Store
    print(helpers.time_now(), "Store Results")
    helpers.check_or_make_directory(path_out)
    helpers.write_data(path_out + f"ana_results.pickle", ana_results)

#####
# Evaluation
#####

if code_switch in [0, 3]:
    """TODO"""  # TODO

    # Load data
    ana_results = helpers.load_data(path_out + f"ana_results.pickle")

    # Check if all analyzed values coincide
    if all([a.check_equal() for a in ana_results]):
        print("All measured values are equal.")
    else:
        print("Some values do not coincide!")
        breakpoint()

    # draw speedup over activation patterns
    different_activations = sorted(list(set(a.num_act_pattern() for a in ana_results)))
    speedups = [
        [a.speedup() for a in ana_results if a.num_act_pattern() == act]
        for act in different_activations
    ]  # speedups ordered by activation
    time_ratios = [
        [a.time_ratio() for a in ana_results if a.num_act_pattern() == act]
        for act in different_activations
    ]  # speedups ordered by activation

    assert sum(len(sp) for sp in speedups) == len(
        ana_results
    ), "number of speedups and number of analysis results does not coincide"

    plot.boxplot(
        speedups,
        path_out + "speedup.pdf",
        xticks=different_activations,
        xaxis_label="involved activation patterns",
        yaxis_label="speedup",
    )
    plot.boxplot(
        time_ratios,
        path_out + "time_ratios.pdf",
        xticks=different_activations,
        xaxis_label="involved activation patterns",
        yaxis_label="time_ratio",
    )

    # # speedups but 2 tasks per chains extra
    # speedups2 = [[a.speedup() for a in ana_results if a.num_act_pattern() == act and len(a.chain) <= 2] for act in
    #              different_activations]
    # speedups3 = [[a.speedup() for a in ana_results if a.num_act_pattern() == act and len(a.chain) > 2] for act in
    #              different_activations]
    #
    # for sp2, sp3, act in zip(speedups2, speedups3, different_activations):
    #     plot.histogram([sp2, sp3], path_out + f"histogram_{act}.pdf", yscale='log')

    for sp, act in zip(speedups, different_activations):
        plot.histogram(sp, path_out + f"histogram_{act}.pdf", yscale="log")

    # print min, max, median,
    import statistics

    report_string = []
    for sp, act in zip(speedups, different_activations):
        report_string.append(
            f"=== Number of involved activation patterns: {act}, Sample contains {len(sp)} values"
            + f"\nSpeedups: \n- min={min(sp):.2f}\n- median={statistics.median(sp):.2f}"
            + f"\n- mean={statistics.mean(sp):.2f}\n- max={max(sp):.2f}"
            f"\n- speedup < 1.0 in {len([s for s in sp if s < 1])} cases"
        )
    report_string = "\n\n".join(report_string)
    print(report_string)

    with open(path_out + "results.txt", "w") as f:
        f.write(report_string)

quit()
