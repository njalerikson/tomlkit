# -*- coding: utf-8 -*-
from ._items import _Item, _Key, _Trivia, _Value, _Container  # noqa: F401
from ._items import Comment  # noqa: F401

from .key import Key  # noqa: F401
from .key import KeyType  # noqa: F401

from .bool import Bool
from .string import String
from .string import StringType  # noqa: F401
from .numdate import DateTime, Date, Time, Integer, Float

from .container import Array, Table

from ._utils import flatten, pyobj


__all__ = ["flatten", "pyobj", "toml"]


# link types together
Array.scalars = (Bool, String, DateTime, Date, Time, Integer, Float)
Table.scalars = (Bool, String, DateTime, Date, Time, Integer, Float)


# convert Python object into TOML object
def toml(data, *, base=None):
    base = Table if base is None else base
    if not issubclass(base, _Item):
        raise TypeError("base must be an _Item")

    return base(data)
