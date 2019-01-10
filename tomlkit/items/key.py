# -*- coding: utf-8 -*-
from enum import Enum
from .._compat import PY2, unicode, decode
from .._utils import escape_string, chars
from ._items import _Key
from ._utils import pyobj

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
        if t in chars.bare:
            return KeyType.BARE
        elif t == KeyType.BASIC.open:
            return KeyType.BASIC
        elif t == KeyType.LITERAL.open:
            return KeyType.LITERAL


class Key(_Key, unicode):
    __slots__ = ["_t"]

    def __new__(cls, value, t=None):  # type: (str, KeyType) -> None
        if isinstance(value, cls):
            return value

        value = unicode(value)
        if any(c not in chars.bare for c in value):
            # something in key is non-bare char
            if t is None:
                t = KeyType.BASIC
            else:
                try:
                    t = KeyType(t)
                except ValueError:
                    t = KeyType.lookup(t)
            assert t != KeyType.BARE
        else:
            # entire key is composed of bare chars
            if t is None:
                t = KeyType.BARE
            else:
                try:
                    t = KeyType(t)
                except ValueError:
                    t = KeyType.lookup(t)

        self = super(Key, cls).__new__(cls, value)
        self._t = t
        return self

    def __flatten__(self):  # type: () -> str
        # if BASIC we need to escape all characters

        txt = super(Key, self).__str__()
        if self._t is KeyType.BASIC:
            # escape_string decodes
            txt = escape_string(txt, nl=True)
        else:
            txt = decode(txt)

        return ["{}{}{}".format(self._t.open, txt, self._t.close)]

    def __repr__(self):  # type: () -> str
        return "<{} {}>".format(self.__class__.__name__, self.__flatten__()[0])

    def __pyobj__(self, hidden=False):  # type: (bool) -> str
        return unicode(self)

    def _getstate(self, protocol=3):
        return (pyobj(self, hidden=True), self._t.value)


HIDDEN_INDEX = -1


# special Key for Array indices, this is a key necessary for the purpose of lookups
# and otherwise handling our values but we do not actually care what this value is
# (it just needs to be unique), nor do we care to see it
class HiddenKey(Key):
    __slots__ = []  # must include __slots__ otherwise we become __dict__

    def __new__(cls):  # type: () -> None
        global HIDDEN_INDEX
        HIDDEN_INDEX += 1
        return super(HiddenKey, cls).__new__(cls, HIDDEN_INDEX, KeyType.BARE)

    def __flatten__(self):  # type: () -> str
        return []

    def __repr__(self):  # type: () -> str
        txt = super(Key, self).__str__()
        return "<{} {}>".format(self.__class__.__name__, txt)

    def _getstate(self, protocol=3):
        return ()
