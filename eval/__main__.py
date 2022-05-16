#!/usr/bin/env python3
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

# set seed
random.seed(314159)
np.random.seed(314159)

# output path
path_out = 'output/'


# Analysis class
###
# Analysis result class
###
class AnaRes:
    """Result of the analysis."""

    def __init__(self, chain,
                 mrt_our=None, mrrt_our=None, mda_our=None, mrda_our=None,
                 mrt_other=None, mrrt_other=None, mda_other=None, mrda_other=None,
                 time_our=None, time_other=None):
        # chain
        self.chain = chain

        # our results
        self.mrt_our = mrt_our
        self.mrrt_our = mrrt_our
        self.mda_our = mda_our
        self.mrda_our = mrda_our

        # other results
        self.mrt_other = mrt_other
        self.mrrt_other = mrrt_other
        self.mda_other = mda_other
        self.mrda_other = mrda_other

        # timing
        self.time_our = time_our
        self.time_other = time_other

    def check_equal(self):
        return all([
            self.mrt_our == self.mrt_other,
            self.mrrt_our == self.mrrt_other,
            self.mda_our == self.mda_other,
            self.mrda_our == self.mrda_other
        ])

    def speedup(self):
        return self.time_other / self.time_our

    def num_act_pattern(self):
        return len(self.chain.involved_activation_patterns())


##
# Handle Options
##
# options
parser = OptionParser()
parser.add_option("-s", "--switch", dest="code_switch", type='int', help="Switch to place SWITCH of the experiment.",
                  metavar="SWITCH")
parser.add_option("-p", "--proc", "--processes", dest="processes", type='int', help="Number of simultaneous processes.")

(options, args) = parser.parse_args()

if options.code_switch is not None:
    code_switch = options.code_switch

if options.processes is not None:
    processes = options.processes

#####
# Generate tasksets and chains
#####

if code_switch in [0, 1]:
    """TODO """  # TODO
    utils = [0.5, 0.6, 0.7, 0.8, 0.9]  # utilization for the experiments
    tries_before_abortion = 100  # tries before aborted
    number_systems_per_util = 10  # number of taskset and cause-effect chain pairs for each utilization


    def make_system(util, tries=None):
        """Create a task sets and cause-effect chain."""
        ce = None
        for id in itertools.count():
            if tries is not None and id + 1 > tries:
                raise RuntimeError(f"Cause-effect chain could not be created for {util=} after {tries + 1} tries.")
            ts = bench.gen_taskset(util)
            ce = bench.gen_ce_chain(ts)

            if ce is not None:  # break when successful
                break

        if id > 0:
            print(f"Cause-effect chain for {util=} successfully created after {id} failed attempts.")

        # set phases = 0
        for tsk in ce.base_ts:
            tsk.rel.phase = 0

        return ce


    ces = []
    for ut in utils:
        ces.extend([make_system(ut, tries_before_abortion) for _ in range(number_systems_per_util)])

    # Store
    helpers.check_or_make_directory(path_out)
    helpers.write_data(path_out + f"ces.pickle", ces)

#####
# Analysis
#####

if code_switch in [0, 2]:
    """TODO """  # TODO

    # Load data
    ces = helpers.load_data(path_out + f"ces.pickle")

    # do experiments
    with Pool(processes) as p:
        our_results = p.map(ana.our_all, ces)
        other_results = p.map(ana.other_all, ces)

    assert len(ces) == len(our_results) == len(other_results), "length of results and of ce chains does not coincide"

    # match into analysis objects
    ana_results = []
    for ce, our, other in zip(ces, our_results, other_results):
        ana_results.append(AnaRes(
            ce,
            mrt_our=our['mrt'], mrrt_our=our['mrrt'],
            mda_our=our['mda'], mrda_our=our['mrda'],
            mrt_other=other['mrt'], mrrt_other=other['mrrt'],
            mda_other=other['mda'], mrda_other=other['mrda'],
            time_our=our['time'], time_other=other['time']
        ))

    # Store
    helpers.check_or_make_directory(path_out)
    helpers.write_data(path_out + f"ana_results.pickle", ana_results)

quit()
