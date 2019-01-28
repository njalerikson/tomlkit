# -*- coding: utf-8 -*-
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
datetime = default.datetime
date = default.date
time = default.time
int = integer = default.integer
float = default.float
array = default.array
table = default.table

toml = default.toml
dumps = default.dumps
