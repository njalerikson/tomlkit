# -*- coding: utf-8 -*-
from ._items import _Value


class Bool(_Value, int):
    """
    A boolean literal.
    """

    def __new__(cls, value):  # type: (bool) -> None
        if isinstance(value, cls):
            return value
        elif isinstance(value, bool):
            pass
        else:
            raise TypeError("Cannot convert {} to {}".format(value, cls.__name__))

        return super(Bool, cls).__new__(cls, value)

    def __flatten__(self):  # type: () -> str
        return [str(self)]

    def __str__(self):  # type: () -> str
        return "true" if self else "false"

    def __pyobj__(self):  # type: () -> str
        return bool(self)
