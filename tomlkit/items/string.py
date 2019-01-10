# -*- coding: utf-8 -*-
from enum import Enum
from .._compat import PY2, unicode, decode
from .._utils import escape_string
from ._items import _Value
from ._utils import pyobj

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
        index = min(minimum, max(index, maximum))
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


class String(_Value, unicode):
    """
    A string literal.
    """

    def __new__(
        cls, value, t=None, multi=None, _raw=None
    ):  # type: (str, StringType, bool) -> String
        if isinstance(value, cls):
            return value
        elif isinstance(value, (str, unicode)):
            pass
        else:
            raise TypeError("Cannot convert {} to {}".format(value, cls.__name__))

        try:
            t = StringType(t)
        except ValueError:
            t = StringType.lookup(t)

        print(value, t, multi, _raw)

        self = super(String, cls).__new__(cls, value)
        self._t = t
        self._multi = ("\n" in self) if multi is None else bool(multi)
        self._raw = _raw
        return self

    def __init__(
        self, value, t=None, multi=None, _raw=None
    ):  # type: (str, StringType, bool) -> None
        super(String, self).__init__()

    def __flatten__(self):  # type: () -> str
        if self._raw:
            return [self._raw]

        count = 3 if self._multi else 1

        # if BASIC and multiline we need to escape non-newline characters
        # if BASIC and singleline we need to escape all characters

        txt = super(String, self).__str__()
        if self._t is StringType.BASIC:
            # escape_string decodes
            txt = escape_string(txt, nl=not self._multi)
        else:
            txt = decode(txt)

        return ["{}{}{}".format(self._t.open * count, txt, self._t.close * count)]

    def __repr__(self):  # type: () -> str
        return "<{} {}>".format(self.__class__.__name__, self.__flatten__()[0])

    def __pyobj__(self, hidden=False):  # type: (bool) -> str
        return unicode(self)

    def _getstate(self, protocol=3):
        tmp = (pyobj(self, hidden=True), self._t.value, self._multi, self._raw)
        print(*tmp)
        return tmp
