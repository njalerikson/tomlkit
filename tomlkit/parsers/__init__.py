# -*- coding: utf-8 -*-
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

loads = default.loads
parse = default.parse
