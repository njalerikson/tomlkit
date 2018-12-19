# -*- coding: utf-8 -*-
import datetime as dt
from ._items import _Value


class NumDate(_Value):
    pass


class DateTime(NumDate, dt.datetime):
    """
    A datetime literal.
    """

    def __new__(cls, value):  # type: (datetime) -> DateTime
        if isinstance(value, cls):
            return value
        elif isinstance(value, dt.datetime):
            pass
        else:
            raise TypeError("Cannot convert {} to {}".format(value, cls.__name__))

        return super(DateTime, cls).__new__(
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

    def __flatten__(self):  # type: () -> str
        return [self.isoformat(sep=" ")]

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

    @classmethod
    def fromtimestamp(cls, t, tz=None):
        return cls(dt.datetime.fromtimestamp(t, tz))

    @classmethod
    def utcfromtimestamp(cls, t):
        return cls(dt.datetime.utcfromtimestamp(t))

    @classmethod
    def now(cls, tz=None):
        return cls(dt.datetime.now(tz))

    @classmethod
    def utcnow(cls):
        return cls(dt.datetime.utcnow())

    @classmethod
    def fromordinal(cls, n):
        return cls(dt.datetime.fromordinal(n))

    @classmethod
    def combine(cls, date, time, tzinfo=None):
        return cls(dt.datetime.combine(date, time, tzinfo))

    @classmethod
    def fromisoformat(cls, date_string):
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
    ):
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

    def date(self):
        return Date(dt.date(self.year, self.month, self.day))

    def time(self):
        return Time(
            dt.time(
                self.hour, self.minute, self.second, self.microsecond, fold=self.fold
            )
        )


class Date(NumDate, dt.date):
    """
    A date literal.
    """

    def __new__(cls, value):  # type: (date) -> Date
        if isinstance(value, cls):
            return value
        elif not isinstance(value, dt.date):
            raise TypeError("Cannot convert {} to {}".format(value, cls.__name__))

        return super(Date, cls).__new__(
            cls, year=value.year, month=value.month, day=value.day
        )

    def __flatten__(self):  # type: () -> str
        return [self.isoformat()]

    def __pyobj__(self):  # type: () -> date
        return dt.date(self.year, self.month, self.day)

    @classmethod
    def fromtimestamp(cls, t):
        return cls(dt.date.fromtimestamp(t))

    @classmethod
    def today(cls):
        return cls(dt.date.today())

    @classmethod
    def fromordinal(cls, n):
        return cls(dt.date.fromordinal(n))

    @classmethod
    def fromisoformat(cls, date_string):
        return cls(dt.date.fromisoformat(date_string))

    def replace(self, year=None, month=None, day=None):
        if year is None:
            year = self.year
        if month is None:
            month = self.month
        if day is None:
            day = self.day
        return self.__class__(dt.date(year, month, day))


class Time(NumDate, dt.time):
    """
    A time literal.
    """

    def __new__(cls, value):  # type: (time) -> Time
        if isinstance(value, cls):
            return value
        elif not isinstance(value, dt.time):
            raise TypeError("Cannot convert {} to {}".format(value, cls.__name__))

        return super(Time, cls).__new__(
            cls,
            hour=value.hour,
            minute=value.minute,
            second=value.second,
            microsecond=value.microsecond,
            tzinfo=value.tzinfo,
            fold=value.fold,
        )

    def __flatten__(self):  # type: () -> str
        return [self.isoformat()]

    def __pyobj__(self):  # type: () -> time
        return dt.time(
            self.hour,
            self.minute,
            self.second,
            self.microsecond,
            self.tzinfo,
            fold=self.fold,
        )

    @classmethod
    def fromisoformat(cls, time_string):
        return cls(dt.time.fromisoformat(time_string))

    def replace(
        self,
        hour=None,
        minute=None,
        second=None,
        microsecond=None,
        tzinfo=True,
        *,
        fold=None
    ):
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
            dt.time(hour, minute, second, microsecond, tzinfo, fold=fold)
        )


class Integer(NumDate, int):
    """
    An integer literal.
    """

    def __new__(cls, value, ksep=False):  # type: (int, bool) -> Integer
        if isinstance(value, cls):
            return value
        elif isinstance(value, int):
            pass
        elif isinstance(value, str) and "." not in value and "e" not in value:
            pass
        else:
            raise TypeError("Cannot convert {} to {}".format(value, cls.__name__))

        self = super(Integer, cls).__new__(cls, value)

        # thousands separator (_)
        self._ksep = ksep

        return self

    def __flatten__(self):  # type: () -> str
        if self._ksep:
            return ["{:,}".format(self).replace(",", "_")]
        return [str(self)]

    def __pyobj__(self):  # type: () -> datetime
        return int(self)


class Float(NumDate, float):
    """
    A float literal.
    """

    def __new__(cls, value, ksep=False):  # type: (float, bool) -> Float
        if isinstance(value, cls):
            return value
        elif isinstance(value, float):
            pass
        elif isinstance(value, str) and (
            value.count(".") == 1
            or value.count("e") == 1
            or value.lower() in ["inf", "nan"]
        ):
            pass
        else:
            raise TypeError("Cannot convert {} to {}".format(value, cls.__name__))

        self = super(Float, cls).__new__(cls, value)

        # thousands separator (_)
        self._ksep = ksep

        return self

    def __flatten__(self):  # type: () -> str
        if self._ksep:
            return ["{:,}".format(self).replace(",", "_")]
        return [str(self)]

    def __pyobj__(self):  # type: () -> datetime
        return float(self)
