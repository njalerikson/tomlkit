# -*- coding: utf-8 -*-
from ._item import _Item
from ._utils import pyobj, flatten
from .factory import default


__all__ = ["toml", "pyobj", "flatten", "dumps"]


# expose default
inline_comment = default.inline_comment
comment = default.comment
nl = newline = default.newline

key = default.key
hiddenkey = default.hiddenkey

bool = boolean = default.boolean
str = string = default.string
date = default.date
time = default.time
datetime = default.datetime
int = integer = default.integer
float = default.float
array = default.array
table = default.table


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
