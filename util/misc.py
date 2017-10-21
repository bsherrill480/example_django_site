class _Counter:
    def __init__(self):
        self._count = 0

    def __call__(self):
        to_return = self._count
        self._count += 1
        return to_return


class _CounterStr(_Counter):
    def __call__(self):
        count = super(_CounterStr, self).__call__()
        return str(count)


def get_unique_str_fn():
    return _CounterStr()

