# -*- coding: utf-8 -*-
import datetime as dt
from ._items import _Item
from ._trivia import _Value
from .date import Date
from .time import Time


def check_raw(value, raw):
    if raw is not None:
        return raw

    return value.isoformat(sep=" ")


class DateTime(_Value, dt.datetime):
    __slots__ = ["_raw"]

    def __new__(cls, value, _raw=None):  # type: (datetime) -> DateTime
        if isinstance(value, cls):
            return value
        elif not isinstance(value, _Item) and isinstance(value, dt.datetime):
            pass
        else:
            raise TypeError("Cannot convert {} to {}".format(value, cls.__name__))

        self = super(DateTime, cls).__new__(
            cls,
            year=value.year,
            month=value.month,
            day=value.day,
            hour=value.hour,
            minute=value.minute,
            second=value.second,
            microsecond=value.microsecond,
            tzinfo=value.tzinfo,
            fold=value.fold,
        )
        self._raw = _raw = check_raw(self, _raw)
        return self

    @classmethod
    def fromtimestamp(cls, t, tz=None):  # type: (str, tz) -> DateTime
        return cls(dt.datetime.fromtimestamp(t, tz))

    @classmethod
    def utcfromtimestamp(cls, t):  # type: (str) -> DateTime
        return cls(dt.datetime.utcfromtimestamp(t))

    @classmethod
    def now(cls, tz=None):  # type: (tz) -> DateTime
        return cls(dt.datetime.now(tz))

    @classmethod
    def utcnow(cls):  # type: () -> DateTime
        return cls(dt.datetime.utcnow())

    @classmethod
    def fromordinal(cls, n):  # type: (int) -> DateTime
        return cls(dt.datetime.fromordinal(n))

    @classmethod
    def combine(cls, date, time, tzinfo=None):  # type: (date, time, tzinfo) -> DateTime
        return cls(dt.datetime.combine(date, time, tzinfo))

    @classmethod
    def fromisoformat(cls, date_string):  # type: (str) -> DateTime
        return cls(dt.datetime.fromisoformat(date_string))

    def replace(
        self,
        year=None,
        month=None,
        day=None,
        hour=None,
        minute=None,
        second=None,
        microsecond=None,
        tzinfo=True,
        *,
        fold=None
    ):  # type: (int, int, int, int, int, int, int, tzinfo, int) -> DateTime
        if year is None:
            year = self.year
        if month is None:
            month = self.month
        if day is None:
            day = self.day
        if hour is None:
            hour = self.hour
        if minute is None:
            minute = self.minute
        if second is None:
            second = self.second
        if microsecond is None:
            microsecond = self.microsecond
        if tzinfo is True:
            tzinfo = self.tzinfo
        if fold is None:
            fold = self.fold
        return self.__class__(
            dt.datetime(
                year, month, day, hour, minute, second, microsecond, tzinfo, fold=fold
            )
        )

    def date(self):  # type: () -> Date
        return Date(dt.date(self.year, self.month, self.day))

    def time(self):  # type: () -> Time
        return Time(
            dt.time(
                self.hour, self.minute, self.second, self.microsecond, fold=self.fold
            )
        )

    def __pyobj__(self):  # type: () -> datetime
        return dt.datetime(
            self.year,
            self.month,
            self.day,
            self.hour,
            self.minute,
            self.second,
            self.microsecond,
            self.tzinfo,
            fold=self.fold,
        )

    __hiddenobj__ = __pyobj__
