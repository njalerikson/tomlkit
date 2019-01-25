# -*- coding: utf-8 -*-
from ._item import _Item
from ._key import _Key  # noqa: F401
from ._hidden import Comment, Newline
from ._trivia import _Trivia, _Value, _Container  # noqa: F401

from .key import Key, HiddenKey
from .key import KeyType  # noqa: F401

from .boolean import Boolean
from .string import String
from .string import StringType  # noqa: F401
from .date import Date
from .time import Time
from .datetime import DateTime
from .integer import Integer
from .float import Float

from .container import ArrayFactory, TableFactory

from ._utils import pyobj, flatten


__all__ = ["toml", "pyobj", "flatten", "dumps"]


# link types together
comment = Comment
nl = newline = Newline

key = Key
hiddenkey = HiddenKey

bool = boolean = Boolean
str = string = String
date = Date
time = Time
datetime = DateTime
int = integer = Integer
float = Float

array = ArrayFactory()
table = TableFactory()

array.key = hiddenkey
array.values = (boolean, string, datetime, date, time, integer, float)
array.mapping = table
array.sequence = array

table.key = key
table.values = (boolean, string, datetime, date, time, integer, float)
table.mapping = table
table.sequence = array


# converts Python object into TOML object
def toml(data=None, *, base=None):
    base = table if base is None else base
    try:
        if not issubclass(base, _Item):
            raise TypeError
    except TypeError:
        raise TypeError("base must be an _Item")
    else:
        return base({} if data is None else data)


# converts TOML object (using a base node) into TOML document (str)
def dumps(obj, **kwargs):
    # ensure data is valid according to base
    data = toml(obj, **kwargs)

    # flatten data into string
    return flatten(data)
