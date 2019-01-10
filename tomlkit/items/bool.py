# -*- coding: utf-8 -*-
from ._items import _Item, _Value
from ._utils import pyobj


class Bool(_Value, int):
    """
    A boolean literal.
    """

    def __new__(cls, value, _raw=None):  # type: (bool) -> None
        if isinstance(value, cls):
            return value
        elif not isinstance(value, _Item) and isinstance(value, bool):
            pass
        else:
            raise TypeError("Cannot convert {} to {}".format(value, cls.__name__))

        self = super(Bool, cls).__new__(cls, value)
        self._raw = _raw
        return self

    def __flatten__(self):  # type: () -> str
        if self._raw:
            return [self._raw]

        return [str(self)]

    def __str__(self):  # type: () -> str
        return "true" if self else "false"

    def __pyobj__(self, hidden=False):  # type: (bool) -> bool
        return bool(self)

    def _getstate(self, protocol=3):
        return (pyobj(self, hidden=True), self._raw)
