# -*- coding: utf-8 -*-
from ._parser import _Parser
from .factory import default


__all__ = ["loads", "parse"]


# expose default
inline_comment = default.inline_comment
comment = default.comment

key = default.key

keys = default.keys
tablekeys = default.tablekeys

bool = boolean = default.boolean
str = string = default.string
numdate = default.numdate
array = default.array
inlinetable = default.inlinetable
table = default.table


# converts TOML document (str) into TOML object
def loads(src, *, base=None):
    base = table if base is None else base
    if not isinstance(base, _Parser):
        raise TypeError("base must be a _Parser")

    return base.parse(src)


parse = loads
