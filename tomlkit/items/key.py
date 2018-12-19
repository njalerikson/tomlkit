# -*- coding: utf-8 -*-
from enum import Enum
from .._compat import PY2, unicode
from .._utils import escape_string
from ..toml_char import TOMLChar
from ._items import _Key

if PY2:
    from functools32 import lru_cache
else:
    from functools import lru_cache


class KeyType(Enum):
    # Bare Key
    BARE = ("",)
    # Basic Key
    BASIC = ('"',)
    # Literal Key
    LITERAL = ("'",)

    @classmethod
    def _missing_(cls, value):
        if value == "":
            return KeyType.BARE
        elif value == '"':
            return KeyType.BASIC
        elif value == "'":
            return KeyType.LITERAL

        super(KeyType, cls)._missing_(value)

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
    def is_bare(self):  # type: () -> bool
        return self is KeyType.BARE

    @lru_cache(maxsize=None)
    def is_basic(self):  # type: () -> bool
        return self is KeyType.BASIC

    @lru_cache(maxsize=None)
    def is_literal(self):  # type: () -> bool
        return self is KeyType.LITERAL


class Key(_Key, unicode):
    """
    A key value.
    """

    def __new__(cls, value, t=None):  # type: (str, KeyType) -> None
        if isinstance(value, cls):
            return value

        value = unicode(value)
        if any(c not in TOMLChar.BARE for c in value):
            # something in key is non-bare char
            t = KeyType(KeyType.BASIC if t is None else t)
            assert t != KeyType.BARE
            value = escape_string(value)
        else:
            # entire key is composed of bare chars
            t = KeyType(KeyType.BARE if t is None else t)

        self = super(Key, cls).__new__(cls, value)
        self._t = t
        return self

    def __flatten__(self):  # type: () -> str
        return [str(self)]

    def __str__(self):  # type: () -> str
        return "{}{}{}".format(self._t.open, super(Key, self).__str__(), self._t.close)

    def __pyobj__(self):  # type: () -> str
        return unicode(self)


HIDDEN_INDEX = -1


# special Key for Array indices, this is a key necessary for the purpose of lookups
# and otherwise handling our values but we do not actually care what this value is
# (it just needs to be unique), nor do we care to see it
class HiddenKey(Key):
    def __new__(cls):  # type: () -> None
        global HIDDEN_INDEX
        HIDDEN_INDEX += 1
        return super(HiddenKey, cls).__new__(cls, HIDDEN_INDEX, KeyType.BARE)

    def __flatten__(self):  # type: () -> str
        return []
