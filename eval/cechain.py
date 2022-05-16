from taskset import TaskSet


class CEChain(TaskSet):
    """A cause-effect chain."""

    def __init__(self, *args, base_ts=None):
        self.base_ts = base_ts  # base task set (needed for some analyses)
        super().__init__(*args)

    def involved_activation_patterns(self):
        """involved activation patterns"""
        return list(set([tsk.rel.period for tsk in self]))


if __name__ == '__main__':
    from task import Task

    ce = CEChain(Task(), Task(), Task())
    breakpoint()
