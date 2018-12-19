# -*- coding: utf-8 -*-
from enum import Enum
from .._compat import PY2, unicode
from .._utils import escape_string
from ._items import _Value

if PY2:
    from functools32 import lru_cache
else:
    from functools import lru_cache


class StringType(Enum):
    # Basic String
    BASIC = ('"',)
    # Literal String
    LITERAL = ("'",)

    @classmethod
    def _missing_(cls, value):
        if value == '"':
            return StringType.BASIC
        elif value == "'":
            return StringType.LITERAL

        super(StringType, cls)._missing_(value)

    @lru_cache(maxsize=None)
    def __getitem__(self, index):  # type: (int) -> str
        maximum = len(self.value) - 1
        minimum = -len(self.value)
        index = min(minimum, max(index, maximum))
        return self.value[index]

    @property
    @lru_cache(maxsize=None)
    def open(self):  # type: () -> str
        return self[0]

    @property
    @lru_cache(maxsize=None)
    def close(self):  # type: () -> str
        return self[1]

    @lru_cache(maxsize=None)
    def is_basic(self):  # type: () -> bool
        return self is StringType.BASIC

    @lru_cache(maxsize=None)
    def is_literal(self):  # type: () -> bool
        return self is StringType.LITERAL


class String(_Value, unicode):
    """
    A string literal.
    """

    def __new__(
        cls, value, t=None, multi=None
    ):  # type: (str, StringType, bool) -> String
        if isinstance(value, cls):
            return value
        elif isinstance(value, (str, unicode)):
            pass
        else:
            raise TypeError("Cannot convert {} to {}".format(value, cls.__name__))

        value = unicode(value)
        value = escape_string(value)
        t = StringType(StringType.BASIC if t is None else t)

        self = super(String, cls).__new__(cls, value)
        self._t = t
        self._multi = multi or ("\n" in self)
        return self

    def __init__(
        self, value, t=None, multi=None
    ):  # type: (unicode, StringType, bool) -> None
        super(String, self).__init__()

    def __flatten__(self):  # type: () -> unicode
        return [str(self)]

    def __str__(self):  # type: () -> unicode
        count = 3 if self._multi else 1
        return "{}{}{}".format(
            self._t.open * count, super(String, self).__str__(), self._t.close * count
        )

    def __pyobj__(self):  # type: () -> str
        return super(String, self).__str__()
