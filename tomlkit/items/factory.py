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
        inline_comment=Comment,
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
        **kwargs
    ):
        loc = locals()
        loc.pop("self")
        loc.pop("kwargs")
        # since child classes are calling super they will be implicitly defining the
        # __class__ variable, remove it if it happens to exist
        # https://docs.python.org/3/reference/datamodel.html#creating-the-class-object
        loc.pop("__class__", None)

        loc.update(kwargs)

        self.set_items(loc)
        self.link_items(loc)

        if loc:
            raise TypeError("got unknown values {}".format(list(loc.keys())))

    def set_items(self, kwargs):
        # store the core items
        self.inline_comment = _check_item(
            "inline_comment", kwargs.pop("inline_comment")
        )
        self.comment = _check_item("comment", kwargs.pop("comment"))
        self.nl = self.newline = _check_item("newline", kwargs.pop("newline"))

        self.key = _check_item("key", kwargs.pop("key"))
        self.hiddenkey = _check_item("hiddenkey", kwargs.pop("hiddenkey"))

        self.bool = self.boolean = _check_item("boolean", kwargs.pop("boolean"))
        self.str = self.string = _check_item("string", kwargs.pop("string"))
        self.datetime = _check_item("datetime", kwargs.pop("datetime"))
        self.date = _check_item("date", kwargs.pop("date"))
        self.time = _check_item("time", kwargs.pop("time"))
        self.int = self.integer = _check_item("integer", kwargs.pop("integer"))
        self.float = _check_item("float", kwargs.pop("float"))
        self.array = _check_item("array", kwargs.pop("array"))
        self.table = _check_item("table", kwargs.pop("table"))

    def link_items(self, kwargs):
        # link items together
        self.array.key = _check_attr(self, kwargs.pop("array_key"))
        self.array.values = _check_attrs(self, kwargs.pop("array_values"))
        self.array.mapping = _check_attr(self, kwargs.pop("array_mapping"))
        self.array.sequence = _check_attr(self, kwargs.pop("array_sequence"))

        self.table.key = _check_attr(self, kwargs.pop("table_key"))
        self.table.values = _check_attrs(self, kwargs.pop("table_values"))
        self.table.mapping = _check_attr(self, kwargs.pop("table_mapping"))
        self.table.sequence = _check_attr(self, kwargs.pop("table_sequence"))


default = TOMLFactory()
