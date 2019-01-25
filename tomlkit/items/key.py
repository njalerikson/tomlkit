# -*- coding: utf-8 -*-
from enum import Enum
from .._compat import PY2, unicode, decode
from .._utils import escape_string, chars
from ._item import _Item
from ._key import _Key

if PY2:
    from functools32 import lru_cache
else:
    from functools import lru_cache


_open_close = {0: ("",), 1: ('"',), 2: ("'",)}


class KeyType(Enum):
    # Bare Key
    BARE = 0
    # Basic Key
    BASIC = 1
    # Literal Key
    LITERAL = 2

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
    def is_bare(self):  # type: () -> bool
        return self is KeyType.BARE

    @lru_cache(maxsize=None)
    def is_basic(self):  # type: () -> bool
        return self is KeyType.BASIC

    @lru_cache(maxsize=None)
    def is_literal(self):  # type: () -> bool
        return self is KeyType.LITERAL

    @staticmethod
    @lru_cache(maxsize=None)
    def lookup(t):  # type: () -> bool
        # we will receive a single char to lookup, cannot match with KeyType.BARE.open
        if t in chars.bare:
            return KeyType.BARE
        elif t == KeyType.BASIC.open:
            return KeyType.BASIC
        elif t == KeyType.LITERAL.open:
            return KeyType.LITERAL


def check_t(value, t):
    if any(c not in chars.bare for c in value):
        # something in key is non-bare char
        if t is None:
            return KeyType.BASIC

        try:
            t = KeyType(t)
        except ValueError:
            t = KeyType.lookup(t)

        assert t != KeyType.BARE
        return t
    else:
        # entire key is composed of bare chars
        if t is None:
            return KeyType.BARE

        try:
            return KeyType(t)
        except ValueError:
            return KeyType.lookup(t)


def check_raw(value, t, raw):
    if raw is not None:
        return raw

    if t is KeyType.BASIC:
        # escape_string decodes
        txt = escape_string(value, nl=True)
    else:
        txt = decode(value)
    return "{}{}{}".format(t.open, txt, t.close)


class Key(_Key, unicode):
    __slots__ = ["_t", "_raw"]

    def __new__(cls, value, t=None, _raw=None):  # type: (str, KeyType, str) -> Key
        if isinstance(value, cls):
            return value
        elif not isinstance(value, _Item) and isinstance(value, (str, unicode)):
            pass
        else:
            raise TypeError("Cannot convert {} to {}".format(value, cls.__name__))

        self = super(Key, cls).__new__(cls, value)
        self._t = t = check_t(self, t)
        self._raw = _raw = check_raw(self, t, _raw)
        return self

    def __init__(self, value, t=None, _raw=None):  # type: (str, KeyType, str) -> None
        pass

    def __pyobj__(self):  # type: () -> str
        return unicode(self)

    __hiddenobj__ = __pyobj__

    def _getstate(self, protocol=3):
        return (self.__hiddenobj__(), self._t, self._raw)


HIDDEN_INDEX = -1


# special Key for Array indices, this is a key necessary for the purpose of lookups
# and otherwise handling our values but we do not actually care what this value is
# (it just needs to be unique), nor do we care to see it
class HiddenKey(_Key, unicode):
    __slots__ = ["_raw"]

    def __new__(cls):  # type: () -> HiddenKey
        global HIDDEN_INDEX
        HIDDEN_INDEX += 1
        _raw = unicode(HIDDEN_INDEX)

        self = super(HiddenKey, cls).__new__(cls, _raw)
        self._raw = _raw
        return self

    def __flatten__(self):  # type: () -> list
        return []

    def _getstate(self, protocol=3):
        return ()
