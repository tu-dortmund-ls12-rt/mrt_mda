"""Analysis applied in the evaluation.
Assumptions:
- LET
- periodic"""
import itertools
import math


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
        """Length of the chain, more precisely l() function from the paper. """
        return self.actuation - self.ext_act

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


def other_mrt(chain):
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

    return max([fac.ell() for fac in fw_augm_jcs if fac.valid()])


def other_mda(chain):
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

    return max([bac.ell() for bac in bw_augm_jcs if bac.complete and bac.valid()])


#####
# Our analysis
#####
def our_mda(chain):
    pass


def compute_mrt(mda):
    pass


def compute_mrrt(mrt):
    pass


def compute_mrda(mda):
    pass


if __name__ == '__main__':
    """Debug"""
    debug_switch = 2

    import benchmark_WATERS as bw

    ce = None
    while ce is None:
        ts = bw.gen_taskset(0.7)
        ce = bw.gen_ce_chain(ts)
    for tsk in ts:
        tsk.rel.phase = 0

    if debug_switch in [0, 1]:

        fcs = [FwJobChain(ce, nmb) for nmb in range(10)]
        bcs = [BwJobChain(ce, nmb) for nmb in range(10)]

        facs = [FwAugmJobChain(ce, nmb) for nmb in range(10)]
        bacs = [BwAugmJobChain(ce, nmb) for nmb in range(10)]

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

        print('\nCE Chain:')
        ce.print_tasks()

    if debug_switch in [0, 2]:
        print('MRT other:', other_mrt(ce))
        print('MDA other:', other_mda(ce))

        print('\nCE Chain:')
        ce.print_tasks()

    breakpoint()