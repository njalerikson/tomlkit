# -*- coding: utf-8 -*-
from .parser import _Parser
from .parser import KeyParser, ItemKeysParser, TableKeysParser
from .parser import CommentParser
from .parser import BooleanParser, StringParser, NumDateParser
from .parser import ArrayParser, InlineTableParser, TableParser
from .. import items


__all__ = ["loads", "parse"]


# link parsers together
inline_comment = comment = CommentParser()

key = KeyParser()

keys = ItemKeysParser()
keys.key = key
tablekeys = TableKeysParser()
tablekeys.key = key
tablekeys.inline_comment = inline_comment

bool = boolean = BooleanParser()
str = string = StringParser()
string.multi = True
numdate = NumDateParser()
numdate.datetime = True
numdate.date = True
numdate.time = True
numdate.integer = True
numdate.float = True

array = ArrayParser()
inlinetable = InlineTableParser()
table = TableParser()

array.__klass__ = items.array
array.inline_comment = inline_comment
array.comment = comment
array.values = (boolean, string, numdate)
array.mapping = inlinetable
array.sequence = array

inlinetable.__klass__ = items.table
inlinetable.inline_comment = False
inlinetable.comment = False
inlinetable.key = keys
inlinetable.values = (boolean, string, numdate)
inlinetable.mapping = inlinetable
inlinetable.sequence = array

table.__klass__ = items.table
table.inline_comment = inline_comment
table.comment = comment
table.key = keys
table.tablekey = tablekeys
table.values = (boolean, string, numdate)
table.mapping = inlinetable
table.sequence = array


# converts TOML document (str) into TOML object
def loads(src, *, base=None):
    base = table if base is None else base
    if not isinstance(base, _Parser):
        raise TypeError("base must be a _Parser")

    return base.parse(src)


parse = loads
