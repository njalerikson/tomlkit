# -*- coding: utf-8 -*-
from .parser import _Parser
from .parser import KeyParser, ItemKeysParser, TableKeysParser
from .parser import CommentParser
from .parser import BooleanParser, StringParser, NumDateParser
from .parser import ArrayParser, InlineTableParser, TableParser
from .. import items


def _check_parser(var, parser):
    if issubclass(parser, _Parser):
        return parser()
    err = "expected {} to be a _Parser, not {!r}".format(var, parser)
    raise ValueError(err)


def _check_attr(obj, name):
    try:
        return getattr(obj, name, name)
    except TypeError:
        return name


def _check_attrs(obj, names):
    if names in (None, False):
        return ()
    if not isinstance(names, (tuple, list)):
        names = [names]
    return [_check_attr(obj, name) for name in names]


class TOMLParserFactory:
    def __init__(
        self,
        inline_comment=CommentParser,
        inline_comment_klass=items.comment,
        comment=CommentParser,
        comment_klass=items.comment,
        key=KeyParser,
        key_klass=items.key,
        keys=ItemKeysParser,
        keys_key="key",
        tablekeys=TableKeysParser,
        tablekeys_key="key",
        tablekeys_inline_comment="inline_comment",
        boolean=BooleanParser,
        boolean_klass=items.boolean,
        string=StringParser,
        string_klass=items.string,
        string_multi=True,
        numdate=NumDateParser,
        datetime_klass=items.datetime,
        date_klass=items.date,
        time_klass=items.time,
        integer_klass=items.integer,
        float_klass=items.float,
        array=ArrayParser,
        array_klass=items.array,
        array_inline_comment="inline_comment",
        array_comment="comment",
        array_newline=items.newline,
        array_values=("bool", "str", "numdate"),
        array_mapping="inlinetable",
        array_sequence="array",
        inlinetable=InlineTableParser,
        inlinetable_klass=items.table,
        inlinetable_inline_comment=False,
        inlinetable_comment=False,
        inlinetable_key="keys",
        inlinetable_values=("bool", "str", "numdate"),
        inlinetable_mapping="inlinetable",
        inlinetable_sequence="array",
        table=TableParser,
        table_klass=items.table,
        table_inline_comment="inline_comment",
        table_comment="comment",
        table_newline=items.newline,
        table_key="keys",
        table_tablekey="tablekeys",
        table_values=("bool", "str", "numdate"),
        table_mapping="inlinetable",
        table_sequence="array",
    ):
        # store the core parsers
        self.inline_comment = _check_parser("inline_comment", inline_comment)
        self.comment = _check_parser("comment", comment)

        self.key = _check_parser("key", key)

        self.keys = _check_parser("keys", keys)
        self.tablekeys = _check_parser("tablekeys", tablekeys)

        self.bool = self.boolean = _check_parser("boolean", boolean)
        self.str = self.string = _check_parser("string", string)
        self.numdate = _check_parser("numdate", numdate)
        self.array = _check_parser("array", array)
        self.inlinetable = _check_parser("inlinetable", inlinetable)
        self.table = _check_parser("table", table)

        # link parsers together
        self.inline_comment.klass = inline_comment_klass
        self.comment.klass = comment_klass

        self.key.klass = key_klass

        self.keys.key = _check_attr(self, keys_key)
        self.tablekeys.key = _check_attr(self, tablekeys_key)
        self.tablekeys.inline_comment = _check_attr(self, tablekeys_inline_comment)

        self.boolean.klass = boolean_klass
        self.string.klass = string_klass
        self.string.multi = _check_attr(self, string_multi)
        self.numdate.datetime = datetime_klass
        self.numdate.date = date_klass
        self.numdate.time = time_klass
        self.numdate.integer = integer_klass
        self.numdate.float = float_klass

        self.array.klass = array_klass
        self.array.inline_comment = _check_attr(self, array_inline_comment)
        self.array.comment = _check_attr(self, array_comment)
        self.array.newline = array_newline
        self.array.values = _check_attrs(self, array_values)
        self.array.mapping = _check_attr(self, array_mapping)
        self.array.sequence = _check_attr(self, array_sequence)

        self.inlinetable.klass = inlinetable_klass
        self.inlinetable.inline_comment = _check_attr(self, inlinetable_inline_comment)
        self.inlinetable.comment = _check_attr(self, inlinetable_comment)
        self.inlinetable.key = _check_attr(self, inlinetable_key)
        self.inlinetable.values = _check_attrs(self, inlinetable_values)
        self.inlinetable.mapping = _check_attr(self, inlinetable_mapping)
        self.inlinetable.sequence = _check_attr(self, inlinetable_sequence)

        self.table.klass = table_klass
        self.table.inline_comment = _check_attr(self, table_inline_comment)
        self.table.comment = _check_attr(self, table_comment)
        self.table.newline = table_newline
        self.table.key = _check_attr(self, table_key)
        self.table.tablekey = _check_attr(self, table_tablekey)
        self.table.values = _check_attrs(self, table_values)
        self.table.mapping = _check_attr(self, table_mapping)
        self.table.sequence = _check_attr(self, table_sequence)


default = TOMLParserFactory()
