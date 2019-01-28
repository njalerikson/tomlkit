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
        items=items,
        inline_comment=CommentParser,
        comment=CommentParser,
        key=KeyParser,
        keys=ItemKeysParser,
        keys_key="key",
        tablekeys=TableKeysParser,
        tablekeys_key="key",
        tablekeys_inline_comment="inline_comment",
        boolean=BooleanParser,
        string=StringParser,
        string_multi=True,
        numdate=NumDateParser,
        array=ArrayParser,
        array_inline_comment="inline_comment",
        array_comment="comment",
        array_values=("bool", "str", "numdate"),
        array_mapping="inlinetable",
        array_sequence="array",
        inlinetable=InlineTableParser,
        inlinetable_inline_comment=False,
        inlinetable_comment=False,
        inlinetable_key="keys",
        inlinetable_values=("bool", "str", "numdate"),
        inlinetable_mapping="inlinetable",
        inlinetable_sequence="array",
        table=TableParser,
        table_inline_comment="inline_comment",
        table_comment="comment",
        table_key="keys",
        table_tablekey="tablekeys",
        table_values=("bool", "str", "numdate"),
        table_mapping="inlinetable",
        table_sequence="array",
        **kwargs,
    ):
        loc = locals()
        loc.pop("self")
        loc.pop("items")
        loc.pop("kwargs")
        loc.update(kwargs)

        # since child classes are calling super they will be implicitly defining the
        # __class__ variable, remove it if it happens to exist
        # https://docs.python.org/3/reference/datamodel.html#creating-the-class-object
        loc.pop("__class__", None)

        self.set_parsers(loc)
        self.link_parsers(loc)

        if loc:
            raise TypeError("got unknown values {}".format(list(loc.keys())))

        self.set_items(items)

    def set_parsers(self, kwargs):
        # store the core parsers
        self.inline_comment = _check_parser(
            "inline_comment", kwargs.pop("inline_comment")
        )
        self.comment = _check_parser("comment", kwargs.pop("comment"))

        self.key = _check_parser("key", kwargs.pop("key"))

        self.keys = _check_parser("keys", kwargs.pop("keys"))
        self.tablekeys = _check_parser("tablekeys", kwargs.pop("tablekeys"))

        self.bool = self.boolean = _check_parser("boolean", kwargs.pop("boolean"))
        self.str = self.string = _check_parser("string", kwargs.pop("string"))
        self.numdate = _check_parser("numdate", kwargs.pop("numdate"))
        self.array = _check_parser("array", kwargs.pop("array"))
        self.inlinetable = _check_parser("inlinetable", kwargs.pop("inlinetable"))
        self.table = _check_parser("table", kwargs.pop("table"))

    def link_parsers(self, kwargs):
        # link parsers together
        self.keys.key = _check_attr(self, kwargs.pop("keys_key"))
        self.tablekeys.key = _check_attr(self, kwargs.pop("tablekeys_key"))
        self.tablekeys.inline_comment = _check_attr(
            self, kwargs.pop("tablekeys_inline_comment")
        )

        self.string.multi = _check_attr(self, kwargs.pop("string_multi"))

        self.array.inline_comment = _check_attr(
            self, kwargs.pop("array_inline_comment")
        )
        self.array.comment = _check_attr(self, kwargs.pop("array_comment"))
        self.array.values = _check_attrs(self, kwargs.pop("array_values"))
        self.array.mapping = _check_attr(self, kwargs.pop("array_mapping"))
        self.array.sequence = _check_attr(self, kwargs.pop("array_sequence"))

        self.inlinetable.inline_comment = _check_attr(
            self, kwargs.pop("inlinetable_inline_comment")
        )
        self.inlinetable.comment = _check_attr(self, kwargs.pop("inlinetable_comment"))
        self.inlinetable.key = _check_attr(self, kwargs.pop("inlinetable_key"))
        self.inlinetable.values = _check_attrs(self, kwargs.pop("inlinetable_values"))
        self.inlinetable.mapping = _check_attr(self, kwargs.pop("inlinetable_mapping"))
        self.inlinetable.sequence = _check_attr(
            self, kwargs.pop("inlinetable_sequence")
        )

        self.table.inline_comment = _check_attr(
            self, kwargs.pop("table_inline_comment")
        )
        self.table.comment = _check_attr(self, kwargs.pop("table_comment"))
        self.table.key = _check_attr(self, kwargs.pop("table_key"))
        self.table.tablekey = _check_attr(self, kwargs.pop("table_tablekey"))
        self.table.values = _check_attrs(self, kwargs.pop("table_values"))
        self.table.mapping = _check_attr(self, kwargs.pop("table_mapping"))
        self.table.sequence = _check_attr(self, kwargs.pop("table_sequence"))

    def set_items(self, items):
        # link items to parsers
        self.inline_comment.klass = items.inline_comment
        self.comment.klass = items.comment

        self.key.klass = items.key

        self.boolean.klass = items.boolean
        self.string.klass = items.string
        self.numdate.datetime = items.datetime
        self.numdate.date = items.date
        self.numdate.time = items.time
        self.numdate.integer = items.integer
        self.numdate.float = items.float

        self.array.klass = items.array
        self.array.newline = items.newline
        self.inlinetable.klass = items.table
        self.table.klass = items.table
        self.table.newline = items.newline


default = TOMLParserFactory()
