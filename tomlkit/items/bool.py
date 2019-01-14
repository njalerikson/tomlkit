# -*- coding: utf-8 -*-
from ._items import _Item
from ._trivia import _Value


def check_raw(value, raw):
    if raw is not None:
        return raw

    return "true" if value else "false"


class Bool(_Value, int):
    def __new__(cls, value, _raw=None):  # type: (bool, str) -> Bool
        if isinstance(value, cls):
            return value
        elif not isinstance(value, _Item) and isinstance(value, bool):
            pass
        else:
            raise TypeError("Cannot convert {} to {}".format(value, cls.__name__))

        self = super(Bool, cls).__new__(cls, value)
        self._raw = _raw = check_raw(self, _raw)
        return self

    def __init__(self, value, _raw=None):  # type: (bool, str) -> None
        pass

    def __str__(self):  # type: () -> str
        return self._raw

    def __pyobj__(self):  # type: () -> bool
        return bool(self)

    __hiddenobj__ = __pyobj__
