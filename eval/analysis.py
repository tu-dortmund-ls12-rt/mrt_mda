"""Analysis applied in the evaluation.
Assumptions:
- LET
- periodic"""
import itertools
import math
from cechain import CEChain
import timeit


#####
# Help functions for LET communication
#####

def let_we(job):
    """Write-event of job under LET."""
    return job.task.rel.phase + job.task.rel.period * job.number + job.task.dl.dl


def let_re(job):
    """Read-event of job under LET."""
    return job.task.rel.phase + job.task.rel.period * job.number


def let_re_geq(time, task):
    """Number of earliest job with read-event of (task) at or after (time)."""
    return math.ceil((time - task.rel.phase) / task.rel.period)  # TODO int()


def let_we_leq(time, task):
    """Number of latest job with write-event of (task) at or before (time)."""
    return math.floor((time - task.rel.phase - task.dl.dl) / task.rel.period)  # TODO int()


#####
# Job chain definition
#####
class Job:
    """A job."""

    def __init__(self, task=None, number=None):
        """Create (number)-th job of a task (task).
        Assumption: number starts at 0. (0=first job)"""
        self.task = task
        self.number = number

    def __str__(self):
        return f"({self.task}, {self.number})"


class JobChain(list):
    """A chain of jobs."""

    def __init__(self, *jobs):
        """Create a job chain with jobs *jobs."""
        super().__init__(jobs)

    def __str__(self, no_braces=False):
        return '[ ' + ' -> '.join([str(j) for j in self]) + ' ]'

    def ell(self):
        """length of a job chain"""
        return let_we(self[-1]) - let_re(self[0])


class FwJobChain(JobChain):
    """Immediate forward job chain."""

    def __init__(self, ce_chain, number):
        """Create (number)-th immediate forward job chain. (under LET)"""
        self.number = number  # number of forward job chain

        if len(ce_chain) == 0:
            super().__init__()
            return

        # first job
        job_lst = [Job(ce_chain[0], number)]

        # next jobs
        for tsk in ce_chain[1:]:
            # find next job
            next_job_number = let_re_geq(let_we(job_lst[-1]), tsk)

            # add job to chain
            job_lst.append(Job(tsk, next_job_number))

        # Make job chain
        super().__init__(*job_lst)


class BwJobChain(JobChain):
    """Immediate backward job chain."""

    def __init__(self, ce_chain, number):
        """Create (number)-th immediate backward job chain. (under LET)"""
        self.number = number  # number of backward job chain

        if len(ce_chain) == 0:
            super().__init__()
            return

        # last job
        job_lst = [Job(ce_chain[-1], number)]

        # previous jobs jobs
        for tsk in ce_chain[0:-1][::-1]:  # backwards except the last
            # find previous job
            previous_job_number = let_we_leq(let_re(job_lst[0]), tsk)

            # add job to chain
            job_lst.insert(0, Job(tsk, previous_job_number))

        # Make job chain
        super().__init__(*job_lst)

        # check if complete
        self.complete = (job_lst[0].number >= 0)


#####
# Standard LET analysis
#####
class AugmJobChain():
    """An augmented job chain."""

    def __init__(self, ext_act, job_chain, actuation, base_ce_chain=None):
        """Create an augmented job chain."""
        self.ext_act = ext_act
        self.job_chain = job_chain
        self.actuation = actuation
        self.base_ce_chain = base_ce_chain

    def __str__(self):
        entries = [str(self.ext_act), self.job_chain.__str__(no_braces=True), str(self.actuation)]
        return '[ ' + ' / '.join(entries) + ' ]'

    def ell(self):
        """Length of the chain, more precisely l() function from the paper."""
        return self.actuation - self.ext_act

    def ellstar(self):
        """Reduced length of the chain, more precisely l^*() function from the paper."""
        return self.job_chain.ell()

    def valid(self):
        """Returns True if augmented job chain is valid."""
        ce_chain = self.base_ce_chain
        # maximal first read-event
        max_first_re = max(let_re(Job(tsk, 0)) for tsk in ce_chain)

        # number of external activity
        number_ext_act = let_re_geq(self.ext_act, ce_chain[0])

        # check valid condition
        return let_re(Job(ce_chain[0], number_ext_act + 1)) > max_first_re


class FwAugmJobChain(AugmJobChain):
    """An immediate forward augmented job chain"""

    def __init__(self, ce_chain, number):
        """Create the (number)-th immediate forward augmented job chain."""
        ext_act = let_re(Job(ce_chain[0], number))
        job_chain = FwJobChain(ce_chain, number + 1)
        actuation = let_we(job_chain[-1])

        super().__init__(ext_act, job_chain, actuation, base_ce_chain=ce_chain)


class BwAugmJobChain(AugmJobChain):
    """An immediate backward augmented job chain"""

    def __init__(self, ce_chain, number):
        """Create the (number)-th immediate backward augmented job chain."""
        actuation = let_we(Job(ce_chain[-1], number))
        job_chain = BwJobChain(ce_chain, number - 1)
        ext_act = let_re(job_chain[0])

        super().__init__(ext_act, job_chain, actuation, base_ce_chain=ce_chain)

        self.complete = job_chain.complete


def other_mrt(chain, add_mrrt=False):
    """Method to compute MRT by looking at all valid immediate forward augmented job chains."""
    # find analysis interval
    analysis_end = 2 * chain.hyperperiod() + chain.max_phase()

    # construct forward chains
    fw_augm_jcs = []
    for number in itertools.count(start=0):
        fw = FwAugmJobChain(chain, number)
        if fw.ext_act <= analysis_end:
            fw_augm_jcs.append(fw)
        else:
            break

    if add_mrrt:  # return tuple of mrt and mrrt
        return (max([fac.ell() for fac in fw_augm_jcs if fac.valid()]),  # mrt
                max([fac.ellstar() for fac in fw_augm_jcs if fac.valid()]))  # mrrt
    else:  # return only mrt
        return max([fac.ell() for fac in fw_augm_jcs if fac.valid()])  # mrt


def other_mda(chain, add_mrda=False):
    """Method to compute MDA by looking at all valid, complete immediate backward augmented job chains."""
    # find analysis interval
    analysis_end = 2 * chain.hyperperiod() + chain.max_phase()

    # construct backward chains
    bw_augm_jcs = []
    for number in itertools.count(start=0):
        bw = BwAugmJobChain(chain, number)
        if bw.ext_act <= analysis_end:
            bw_augm_jcs.append(bw)
        else:
            break

    if add_mrda:  # return tuple of mda and mrda
        return (max([bac.ell() for bac in bw_augm_jcs if bac.complete and bac.valid()]),  # mda
                max([bac.ellstar() for bac in bw_augm_jcs if bac.complete and bac.valid()]))  # mrda
    else:  # return only mrt
        return max([bac.ell() for bac in bw_augm_jcs if bac.complete and bac.valid()])  # mda


#####
# Our analysis
#####
class PartitionedJobChain():
    """A partitioned job chain."""

    def __init__(self, part, chain, number):
        """Create a partitioned job chain.
            - part = where is the partioning
            - chain = cause-effect chain
            - number = which chain"""
        assert 0 <= part < len(chain), "part is out of possible interval"
        self.bw = BwJobChain(chain[:part + 1], number)
        self.fw = FwJobChain(chain[part:], number + 1)  # forward job chain part
        self.complete = self.bw.complete  # complete iff bw chain complete
        self.base_ce_chain = chain

    def __str__(self):
        entries = [self.bw.__str__(no_braces=True), self.fw.__str__(no_braces=True)]
        return '[ ' + ' / '.join(entries) + ' ]'

    def ell(self):
        """Length of the partitioned job chain, more precisely l() function from the paper."""
        return let_we(self.fw[-1]) - let_re(self.bw[0])

    def valid(self):
        """Returns true if the partitioned job chain is valid."""
        ce_chain = self.base_ce_chain
        # maximal first read-event
        max_first_re = max(let_re(Job(tsk, 0)) for tsk in ce_chain)

        # number first job
        number_first_job = self.bw[0].number

        # check valid condition
        return let_re(Job(ce_chain[0], number_first_job + 1)) > max_first_re


def our_mda(chain: CEChain) -> float:
    """Compute maximum data age as in our paper using result X # TODO add definition/equation
    """
    # construct first complete backward chain
    fw0 = FwJobChain(chain, 0)  # first forward chain
    bw_first = BwJobChain(chain, fw0[-1].number)

    # find analysis interval
    analysis_end = 2 * chain.hyperperiod() + chain.max_phase()

    # choose point for partitioning
    number_jobs_to_consider = [(analysis_end - tsk.rel.phase) / tsk.rel.period for tsk in chain]
    part = number_jobs_to_consider.index(min(number_jobs_to_consider))  # choose part such that number of jobs minimized

    # construct partitioned chains
    part_chains = []
    for number in itertools.count(start=0):
        pc = PartitionedJobChain(part, chain, number)
        if let_re(pc.bw[0]) <= analysis_end:
            part_chains.append(pc)
        else:
            break

    return max([pc.ell() for pc in part_chains if pc.complete and pc.valid()])


def our_mrt(chain: CEChain, mda: float = None) -> float:
    """Compute maximum reaction time using the result X # TODO add result
    """
    if mda is None:  # Comptue MDA if not given
        mda = our_mda(chain)

    # find first valid 1-partitioned chain
    max_first_re = max(let_re(Job(tsk, 0)) for tsk in chain)
    for number in itertools.count(start=0):
        if let_re(Job(chain[0], number + 1)) > max_first_re:
            break
    first_valid = PartitionedJobChain(0, chain, number)

    return max(mda, first_valid.ell())


def compute_mrrt(chain: CEChain, mrt: float = None) -> float:
    """Compute MRRT using the result from X # TODO add result
    Assumption: LET communication
    """
    if mrt is None:  # Compute MRT if not given
        mrt = our_mrt(chain)

    # difference between MRT and MRRT under LET is one period of the first task
    mrrt = mrt - chain[0].rel.period

    return mrrt


def compute_mrda(chain: CEChain, mda: float = None) -> float:
    """Compute MRDA using the result from X # TODO add result
        Assumption: LET communication
        """
    if mda is None:  # Compute MRT if not given
        mda = our_mda(chain)

    # difference between MRT and MRRT under LET is one period of the last task
    mrda = mda - chain[-1].rel.period

    return mrda


#####
# For our analysis:
#####


def our_all(ce, repeat=10):
    """Return list of MDA, MRDA, MRT, and MRRT results for our analysis, plus a timer value."""

    def analyses(ce):
        res_our_mda = our_mda(ce)
        res_our_mrt = our_mrt(ce, res_our_mda)
        return {'mda': res_our_mda,
                'mrda': compute_mrda(ce, res_our_mda),
                'mrt': res_our_mrt,
                'mrrt': compute_mrrt(ce, res_our_mrt)}

    # our analysis
    result = analyses(ce)

    # timing
    result['time'] = min(timeit.repeat(lambda: analyses(ce), repeat=repeat, number=1))

    return result


def other_all(ce, repeat=10):
    """Return list of MDA, MRDA, MRT, and MRRT results for other analysis, plus a timer value."""

    def analyses(ce):
        res_other_mda_mrda = other_mda(ce, add_mrda=True)
        res_other_mrt_mrrt = other_mrt(ce, add_mrrt=True)
        return {'mda': res_other_mda_mrda[0],
                'mrda': res_other_mda_mrda[1],
                'mrt': res_other_mrt_mrrt[0],
                'mrrt': res_other_mrt_mrrt[1]}

    # other analysis
    result = analyses(ce)

    # timing
    result['time'] = min(timeit.repeat(lambda: analyses(ce), repeat=repeat, number=1))

    return result


if __name__ == '__main__':
    """Debug"""
    debug_switch = 6

    import benchmark_WATERS as bw


    def make_ce_test():
        ce = None
        while ce is None:
            ts = bw.gen_taskset(0.7)
            ce = bw.gen_ce_chain(ts)
        for tsk in ts:
            tsk.rel.phase = 0
        return ce, ts


    if debug_switch in [0, 1]:
        ce, ts = make_ce_test()

        fcs = [FwJobChain(ce, nmb) for nmb in range(10)]
        bcs = [BwJobChain(ce, nmb) for nmb in range(10)]

        facs = [FwAugmJobChain(ce, nmb) for nmb in range(10)]
        bacs = [BwAugmJobChain(ce, nmb) for nmb in range(10)]

        pc0 = [PartitionedJobChain(0, ce, nmb) for nmb in range(10)]
        pc1 = [PartitionedJobChain(1, ce, nmb) for nmb in range(10)]
        pcL = [PartitionedJobChain(len(ce) - 1, ce, nmb) for nmb in range(10)]

        print('\nForward job chains:')
        for fc in fcs:
            print(fc)

        print('\nForward augmented job chains:')
        for fac in facs:
            print(fac, fac.valid())

        print('\nBackward job chains:')
        for bc in bcs:
            print(bc, bc.complete)

        print('\nBackward augmented job chains:')
        for bac in bacs:
            print(bac, bac.complete, bac.valid())

        print('\n0 partitioned job chains:')
        for pc in pc0:
            print(pc, pc.complete, pc.valid())

        print('\n1 partitioned job chains:')
        for pc in pc1:
            print(pc, pc.complete, pc.valid())

        print('\nL partitioned job chains:')
        for pc in pcL:
            print(pc, pc.complete, pc.valid())

        print('\nCE Chain:')
        ce.print_tasks()

    if debug_switch in [0, 2]:
        ce, ts = make_ce_test()
        print('MRT other:', other_mrt(ce))
        print('MDA other:', other_mda(ce))

        print('MDA our:', our_mda(ce))

        print('\nCE Chain:')
        ce.print_tasks()

    if debug_switch in [0, 3]:
        ce_tests = [make_ce_test()[0] for _ in range(10)]

        for id, ce in enumerate(ce_tests):
            print('\n', id)
            print('other:', other_mda(ce, add_mrda=True), other_mrt(ce, add_mrrt=True))
            o_mda = our_mda(ce)
            o_mrt = our_mrt(ce, o_mda)
            print('our:', o_mda, compute_mrda(ce, o_mda), o_mrt, compute_mrrt(ce, o_mrt))

    if debug_switch in [0, 4]:
        range_number = 1000
        for id in range(range_number):
            # test sample
            ce, _ = make_ce_test()

            # other analysis
            res_other = [*other_mda(ce, add_mrda=True), *other_mrt(ce, add_mrrt=True)]
            # our analysis
            res_our_mda = our_mda(ce)
            res_our_mrt = our_mrt(ce, res_our_mda)
            res_our = [res_our_mda, compute_mrda(ce, res_our_mda), res_our_mrt, compute_mrrt(ce, res_our_mrt)]
            # compare values
            if not all([x == y for x, y in zip(res_other, res_our)]):
                print('not equal')
                breakpoint()
            if (id + 1) % (range_number / 10) == 0:
                print(id + 1, "already checked")

    if debug_switch in [0, 5]:  # Test timing behavior
        import timeit


        def our_all(ce):
            # our analysis
            res_our_mda = our_mda(ce)
            res_our_mrt = our_mrt(ce, res_our_mda)
            return [res_our_mda, compute_mrda(ce, res_our_mda), res_our_mrt, compute_mrrt(ce, res_our_mrt)]


        def other_all(ce):
            return [*other_mda(ce, add_mrda=True), *other_mrt(ce, add_mrrt=True)]


        def time(fct, ce):
            start = timeit.default_timer()
            fct(ce)
            end = timeit.default_timer()
            return end - start


        ce_tests = [make_ce_test()[0] for _ in range(10)]

        for ce in ce_tests:
            print(ce, ce.involved_activation_patterns())
            print('our', timeour := timeit.timeit(lambda: our_all(ce), number=10))
            print('our2', timeour2 := time(our_all, ce))
            print('other', timeother := timeit.timeit(lambda: other_all(ce), number=10))
            print('other2', timeother2 := time(other_all, ce))
            print('speedup:', timeother / timeour, timeother2 / timeour2)

    if debug_switch in [0, 6]:
        ce_tests = [make_ce_test()[0] for _ in range(10)]
        for ce in ce_tests:
            print(ce, our_all(ce), other_all(ce))

    breakpoint()
