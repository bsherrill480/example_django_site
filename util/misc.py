from typing import Callable


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


def get_unique_str_fn() -> Callable[[], str]:
    """
    :return: Callable. Takes no arguments, returns a different string each call.
    e.g.
    c = get_unique_str_fn()
    c()  # '1'
    c()  # '2'
    c()  # '3'
    ...
    """
    return _CounterStr()
