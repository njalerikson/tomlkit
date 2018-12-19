# -*- coding: utf-8 -*-
from .parser import _Parser
from .parser import KeyParser, ItemKeysParser, TableKeysParser
from .parser import CommentParser
from .parser import BoolParser, StringParser, NumDateParser
from .parser import ArrayParser, InlineTableParser, TableParser


__all__ = ["loads"]


# link parsers together
inline_comment = comment = CommentParser()

key = KeyParser()

keys = ItemKeysParser()
keys.key = key
tablekeys = TableKeysParser()
tablekeys.key = key
tablekeys.inline_comment = inline_comment

boolean = BoolParser()
string = StringParser()
string.multi = True
numdate = NumDateParser()
numdate.datetime = True
numdate.date = True
numdate.time = True
numdate.integer = True
numdate.float = True
array = ArrayParser()
array.inline_comment = inline_comment
array.comment = comment
inlinetable = InlineTableParser()
inlinetable.key = keys
inlinetable.inline_comment = False
inlinetable.comment = False

table = TableParser()
table.tablekey = tablekeys
table.key = keys
table.inline_comment = inline_comment
table.comment = comment

array.values = [boolean, string, numdate, array, inlinetable]
inlinetable.values = [boolean, string, numdate, array, inlinetable]
table.values = [boolean, string, numdate, array, inlinetable]


# parse string as TOML object
def loads(src, *, base=None):
    base = table if base is None else base
    if not isinstance(base, _Parser):
        raise TypeError("base must be a _Parser")

    return base.parse(src)
