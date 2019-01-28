# -*- coding: utf-8 -*-
from ._item import _Item
from ._itemfactory import _ItemFactory

from ._hidden import Comment, Newline

from .key import Key, HiddenKey

from .boolean import Boolean
from .string import String
from .date import Date
from .time import Time
from .datetime import DateTime
from .integer import Integer
from .float import Float

from .container import ArrayFactory, TableFactory


def _check_item(var, item):
    if issubclass(item, _Item):
        return item
    if issubclass(item, _ItemFactory):
        return item()
    err = "expected {} to be an _Item or a _ItemFactory, not {!r}".format(var, item)
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


class TOMLFactory:
    def __init__(
        self,
        comment=Comment,
        newline=Newline,
        key=Key,
        hiddenkey=HiddenKey,
        boolean=Boolean,
        string=String,
        datetime=DateTime,
        date=Date,
        time=Time,
        integer=Integer,
        float=Float,
        array=ArrayFactory,
        array_key="hiddenkey",
        array_values=("bool", "str", "datetime", "date", "time", "int", "float"),
        array_mapping="table",
        array_sequence="array",
        table=TableFactory,
        table_key="key",
        table_values=("bool", "str", "datetime", "date", "time", "int", "float"),
        table_mapping="table",
        table_sequence="array",
    ):
        # store the core items
        self.comment = _check_item("comment", comment)
        self.nl = self.newline = _check_item("newline", newline)

        self.key = _check_item("key", key)
        self.hiddenkey = _check_item("hiddenkey", hiddenkey)

        self.bool = self.boolean = _check_item("boolean", boolean)
        self.str = self.string = _check_item("string", string)
        self.datetime = _check_item("datetime", datetime)
        self.date = _check_item("date", date)
        self.time = _check_item("time", time)
        self.int = self.integer = _check_item("integer", integer)
        self.float = _check_item("float", float)
        self.array = _check_item("array", array)
        self.table = _check_item("table", table)

        # link items together
        self.array.key = _check_attr(self, array_key)
        self.array.values = _check_attrs(self, array_values)
        self.array.mapping = _check_attr(self, array_mapping)
        self.array.sequence = _check_attr(self, array_sequence)

        self.table.key = _check_attr(self, table_key)
        self.table.values = _check_attrs(self, table_values)
        self.table.mapping = _check_attr(self, table_mapping)
        self.table.sequence = _check_attr(self, table_sequence)


default = TOMLFactory()
