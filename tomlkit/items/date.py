# -*- coding: utf-8 -*-
import datetime as dt
from ._items import _Item
from ._trivia import _Value


def check_raw(value, raw):
    if raw is not None:
        return raw

    return value.isoformat()


class Date(_Value, dt.date):
    __slots__ = ["_raw"]

    def __new__(cls, value, _raw=None):  # type: (date, str) -> Date
        if isinstance(value, cls):
            return value
        elif not isinstance(value, _Item) and isinstance(value, dt.date):
            pass
        else:
            raise TypeError("Cannot convert {} to {}".format(value, cls.__name__))

        self = super(Date, cls).__new__(
            cls, year=value.year, month=value.month, day=value.day
        )
        self._raw = _raw = check_raw(self, _raw)
        return self

    def __init__(self, value, _raw=None):  # type: (date, str) -> None
        pass

    @classmethod
    def fromtimestamp(cls, t):  # type: (str) -> Date
        return cls(dt.date.fromtimestamp(t))

    @classmethod
    def today(cls):  # type: () -> Date
        return cls(dt.date.today())

    @classmethod
    def fromordinal(cls, n):  # type: (int) -> Date
        return cls(dt.date.fromordinal(n))

    @classmethod
    def fromisoformat(cls, date_string):  # type: (str) -> Date
        return cls(dt.date.fromisoformat(date_string))

    def replace(self, year=None, month=None, day=None):  # type: (int, int, int) -> Date
        if year is None:
            year = self.year
        if month is None:
            month = self.month
        if day is None:
            day = self.day
        return self.__class__(dt.date(year, month, day))

    def __pyobj__(self):  # type: () -> date
        return dt.date(self.year, self.month, self.day)

    __hiddenobj__ = __pyobj__
