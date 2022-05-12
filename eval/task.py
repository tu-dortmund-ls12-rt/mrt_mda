#!/usr/bin/env python3

# TODO instead of checking each feature individually, better check once after add_features. -> put one _check attribute to features and add things to check to the classes (call with super())

####################
# Task.
####################
class Task:
    """A task."""
    features = ['rel', 'dl', 'ex', 'comm']

    def __init__(self, *feature_objects):
        """Initialize a task instance."""
        # for feat in self.features:
        #     setattr(self, feat, None)
        self.rel = None
        self.dl = None
        self.ex = None
        self.comm = None

        # add features
        self.add_features(*feature_objects)

    def add_features(self, *feature_objects):
        """Add feature objects to the task."""
        # Checks
        for feat_obj in feature_objects:
            if not hasattr(feat_obj, '_name'):
                raise ValueError(f'{feat_obj} has no attribute "_name".')
            if feat_obj._name not in self.features:
                raise ValueError(f'{feat_obj._name} in {feat_obj} is not a possible feature name.')

        # Add objects
        for feat_obj in feature_objects:
            setattr(self, feat_obj._name, feat_obj)
            # set _base_tsk
            if hasattr(feat_obj, '_base_tsk') and feat_obj._base_tsk is None:
                feat_obj._base_tsk = self

    def print(self):
        """Quick print of all features for debugging."""
        print(self)
        for feat in [f for f in self.features if getattr(self, f) is not None]:
            print(feat, getattr(self, feat))

    def utilization(self):
        """Task utilization."""
        return self.ex.wcet / self.rel.miniat


####################
# Task Features.
####################
class TaskFeature:
    """A task feature, which can be added to a task."""
    _properties = []  # properties added to the task feature

    def __str__(self):
        """Convert TaskFeature object to string."""
        return self.__repr__() + ':\t' + ', '.join([f'{prop}={getattr(self, prop)}' for prop in self._properties])


# Task Features: Release Pattern
class ReleasePattern(TaskFeature):
    """Basic release pattern feature."""
    _name = 'rel'  # name of the pattern (and all subpatterns)
    type = None  # distinguish different types (also to check if analyses can be applied)

    _properties = TaskFeature._properties + ['type']  # add type to properties


class Sporadic(ReleasePattern):
    """Sporadic release pattern."""
    type = 'sporadic'  # type of the release pattern

    _properties = ReleasePattern._properties + ['miniat', 'maxiat']  # properties for sporadic release pattern

    def __init__(self, maxiat=None, miniat=None):
        """Create a sporadic release pattern task feature.
        - maxiat = maximum inter-arrival time
        - miniat = minimum inter-arrival time"""
        self.maxiat = maxiat
        self.miniat = miniat

    # maxiat getter and setter
    @property
    def maxiat(self):
        return self._maxiat

    @maxiat.setter
    def maxiat(self, value):
        # Checks
        if value is not None:
            if value < 0:
                raise ValueError(f'Non-negative value expected. Received {value=}.')
            if hasattr(self, '_miniat') and self.miniat is not None and value < self._miniat:
                raise ValueError(f'miniat <= value expected. Received {self._miniat=} > {value=}.')
        self._maxiat = value

    # miniat getter and setter
    @property
    def miniat(self):
        return self._miniat

    @miniat.setter
    def miniat(self, value):
        # Checks
        if value is not None:
            if value < 0:
                raise ValueError(f'Non-negative value expected. Received {value=}.')
            if hasattr(self, '_maxiat') and self._maxiat is not None and value > self._maxiat:
                raise ValueError(f'value <= maxiat expected. Received {value=} > {self._maxiat=}.')
        self._miniat = value


class Periodic(Sporadic):
    """Periodic release pattern."""
    type = 'periodic'  # type of the release pattern

    _properties = Sporadic._properties + ['period', 'phase']  # additional properties for Periodic release pattern

    def __init__(self, period=None, phase=None):
        """Create a sporadic release pattern task feature.
            - period = distance between two job releases
            - phase = first job release"""
        # super
        super().__init__(miniat=period, maxiat=period)

        # set properties for periodic release pattern
        self.period = period
        self.phase = phase

    # period getter and setter
    @property
    def period(self):
        return self._period

    @period.setter
    def period(self, value):
        if value is not None and value < 0:
            raise ValueError(f'Non-negative value expected. Received {value=}.')
        self._period = value


# Task Features: Deadline
class Deadline(TaskFeature):
    """Basic deadline feature."""
    _name = 'dl'  # name of deadline feature
    type = None  # distinguish different types (also to check if analyses can be applied)

    _properties = TaskFeature._properties + ['type']  # add type to properties


class ArbitraryDeadline(Deadline):
    """Arbitrary deadlines."""
    type = 'arbitrary'  # type of the deadline feature
    _properties = Deadline._properties + ['dl']  # add dl to properties

    def __init__(self, dl=None):
        """Create an arbitrary deadline task feature.
            - dl = relative deadline"""
        self.dl = dl


class ConstrainedDeadline(ArbitraryDeadline):
    """Constrained deadlines."""
    type = 'constrained'  # type of the deadline feature

    def __init__(self, dl=None, base_tsk=None):
        """Create a constrained deadline task feature.
            - dl = relative deadline,
            - base_tsk = base task (to check if deadline is constrained)."""

        self._base_tsk = base_tsk  # base task

        # super
        super().__init__(dl=dl)  # set deadline

    # dl getter and setter
    @property
    def dl(self):
        return self._dl

    @dl.setter
    def dl(self, value):
        # Checks (only if _base_tsk is already given)
        if (hasattr(self, '_base_tsk') and self._base_tsk is not None and value is not None
                and hasattr(self._base_tsk, 'rel')
                and hasattr(self._base_tsk.rel, 'miniat')):
            if self._base_tsk.rel.miniat < value:
                raise ValueError(f'Expected value <= miniat. Received {value=} > {self._base_tsk.rel.miniat=}.')
        self._dl = value


class ImplicitDeadline(ConstrainedDeadline):
    """Implicit deadlines."""
    type = 'implicit'  # type of the deadline feature

    def __init__(self, base_tsk=None):
        """Create an implicit deadline task feature.
            (all arguments are predefined by the release pattern)"""
        # super
        super().__init__(base_tsk=base_tsk)

    # dl getter and setter
    @property
    def dl(self):
        """Deadline is always the minimum inter-arrival time of a task."""
        if (hasattr(self, '_base_tsk')
                and hasattr(self._base_tsk, 'rel')
                and hasattr(self._base_tsk.rel, 'miniat')):
            return self._base_tsk.rel.miniat
        else:
            return None

    @dl.setter
    def dl(self, value):
        """No setting allowed, just a quick check."""
        if value is not None and self.dl is not None and self.dl != value:
            raise ValueError(f'DL=miniat expected for implicit deadline tasks. Want to set {self.dl=} to {value=}?')
        else:
            pass


# Task Features: Execution Behavior
# TODO add suspension
# TODO this place can also be used to implement tasks with probabilistic execution behavior
class Execution(TaskFeature):
    """Execution time specification."""
    _name = 'ex'  # name of execution time specification feature
    type = None  # distinguish different types (also to check if analyses can be applied)

    _properties = TaskFeature._properties + ['type']  # add type to properties


class BCWCExecution(Execution):
    """Best-case and worst-case execution time."""
    type = 'bcwc'  # type of the execution feature
    _properties = Execution._properties + ['bcet', 'wcet']  # add bcet and wcet to properties

    def __init__(self, bcet=None, wcet=None):
        """Create an implicit deadline task feature.
            - bcet = best-case execution time
            - wcet = worst-case execution time"""
        self.bcet = bcet
        self.wcet = wcet

    # bcet getter and setter
    @property
    def bcet(self):
        return self._bcet

    @bcet.setter
    def bcet(self, value):
        if value is not None:
            if value < 0:
                raise ValueError(f'Non-negative value expected. Received {value=}.')
            if hasattr(self, 'wcet') and self.wcet is not None:
                if self.wcet < value:
                    raise ValueError(f'wcet>=value expected. Received: {self.wcet=}<{value=}.')
        self._bcet = value

    # wcet getter and setter
    @property
    def wcet(self):
        return self._wcet

    @wcet.setter
    def wcet(self, value):
        if value is not None:
            if value < 0:
                raise ValueError(f'Non-negative value expected. Received {value=}.')
            if hasattr(self, 'bcet') and self.bcet is not None:
                if self.bcet > value:
                    raise ValueError(f'bcet<=value expected. Received: {self.bcet=}>{value=}.')
        self._wcet = value


# Task Features: Communication Policy
class Communication(TaskFeature):
    """Communication policy."""
    _name = 'comm'  # name of communication policy feature
    _comm_possibilities = ('implicit', 'LET')  # possible types of the communication feature

    _properties = TaskFeature._properties + ['type']  # type is a property of the communication feature

    def __init__(self, communication_policy, **kwargs):
        """Create an implicit deadline task feature.
            - communication_policy = communication policy of the task (implicit, LET, ...)"""
        if communication_policy not in self._comm_possibilities:
            raise ValueError(
                f'{communication_policy} is not a valid communication policy to choose from.'
                + f'Please choose a policy from the list {self._comm_possibilities}.')

        self.type = communication_policy  # set communication type

    # type getter and setter
    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        if value is not None:
            if value not in self._comm_possibilities:
                raise ValueError(f'{value} is not a valid communication policy to choose from. '
                                 + f'Please choose a policy from the list {self._comm_possibilities}.')
        self._type = value


if __name__ == '__main__':
    """Debugging."""
    tsks = dict()
    tsks['tnone'] = Task()

    tsks['tspor1'] = Task(Sporadic(miniat=100))
    tsks['tspor2'] = Task(Sporadic(miniat=10, maxiat=20))
    tsks['tper1'] = Task(Periodic(period=10))

    tsks['tsporid'] = Task(Sporadic(miniat=100), ImplicitDeadline())  # takes deadline from the miniat
    tsks['tsporcd'] = Task(Sporadic(miniat=100), ConstrainedDeadline(dl=80))

    tsks['timpl'] = Task(Communication('implicit'))
    tsks['tLET'] = Task(Communication('LET'))

    tsks['texec1'] = Task(BCWCExecution(bcet=10, wcet=20))
    tsks['texec2'] = Task(BCWCExecution(wcet=100))

    tsks['texec2'].add_features(Periodic(period=10))
    tsks['texec2'].add_features(Communication(communication_policy='LET'))

    for t in tsks.keys():
        print('\n', t)
        tsks[t].print()

    breakpoint()
