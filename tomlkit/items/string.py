# -*- coding: utf-8 -*-
from enum import Enum
from .._compat import PY2, unicode, decode
from .._utils import escape_string
from ._item import _Item
from ._trivia import _Value

if PY2:
    from functools32 import lru_cache
else:
    from functools import lru_cache


_open_close = {0: ('"',), 1: ("'",)}


class StringType(Enum):
    # Basic String
    BASIC = 0
    # Literal String
    LITERAL = 1

    @lru_cache(maxsize=None)
    def __getitem__(self, index):  # type: (int) -> str
        OC = _open_close[self.value]

        maximum = len(OC) - 1
        minimum = -len(OC)
        index = max(minimum, min(index, maximum))
        return OC[index]

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

    @staticmethod
    @lru_cache(maxsize=None)
    def lookup(t):  # type: () -> bool
        if t == StringType.BASIC.open:
            return StringType.BASIC
        elif t == StringType.LITERAL.open:
            return StringType.LITERAL


def check_t(t):
    if t is None:
        return StringType.BASIC

    try:
        return StringType(t)
    except ValueError:
        return StringType.lookup(t)


def check_multi(value, multi):
    if multi is not None:
        return bool(multi)

    return "\n" in value


def check_raw(value, t, multi, raw):
    if raw is not None:
        return raw

    count = 3 if multi else 1

    if t is StringType.BASIC:
        # escape_string decodes
        txt = escape_string(value, nl=not multi)
    else:
        txt = decode(value)
    return "{}{}{}".format(t.open * count, txt, t.close * count)


class String(_Value, unicode):
    __slots__ = ["_t", "_multi", "_raw"]

    def __new__(
        cls, value, t=None, multi=None, _raw=None
    ):  # type: (str, StringType, bool, str) -> String
        if isinstance(value, cls):
            return value
        elif not isinstance(value, _Item) and isinstance(value, (str, unicode)):
            pass
        else:
            raise TypeError("Cannot convert {} to {}".format(value, cls.__name__))

        self = super(String, cls).__new__(cls, value)
        self._t = t = check_t(t)
        self._multi = multi = check_multi(self, multi)
        self._raw = _raw = check_raw(self, t, multi, _raw)
        return self

    def __init__(
        self, value, t=None, multi=None, _raw=None
    ):  # type: (str, StringType, bool, str) -> None
        pass

    def __pyobj__(self):  # type: () -> str
        return unicode(self)

    __hiddenobj__ = __pyobj__

    def _getstate(self, protocol=3):
        return (self.__hiddenobj__(), self._t, self._multi, self._raw)
