# -*- coding: utf-8 -*-
import datetime as dt
from ._items import _Item, _Value
from ._utils import pyobj


class DateTime(_Value, dt.datetime):
    """
    A datetime literal.
    """

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
        self._raw = _raw
        return self

    def __flatten__(self):  # type: () -> str
        if self._raw:
            return [self._raw]

        return [self.isoformat(sep=" ")]

    def __pyobj__(self, hidden=False):  # type: (bool) -> datetime
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

    def _getstate(self, protocol=3):
        return (pyobj(self, hidden=True), self._raw)


class Date(_Value, dt.date):
    """
    A date literal.
    """

    def __new__(cls, value, _raw=None):  # type: (date) -> Date
        if isinstance(value, cls):
            return value
        elif not isinstance(value, _Item) and isinstance(value, dt.date):
            pass
        else:
            raise TypeError("Cannot convert {} to {}".format(value, cls.__name__))

        self = super(Date, cls).__new__(
            cls, year=value.year, month=value.month, day=value.day
        )
        self._raw = _raw
        return self

    def __flatten__(self):  # type: () -> str
        if self._raw:
            return [self._raw]

        return [self.isoformat()]

    def __pyobj__(self, hidden=False):  # type: (bool) -> date
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

    def _getstate(self, protocol=3):
        return (pyobj(self, hidden=True), self._raw)


class Time(_Value, dt.time):
    """
    A time literal.
    """

    def __new__(cls, value, _raw=None):  # type: (time) -> Time
        if isinstance(value, cls):
            return value
        elif not isinstance(value, _Item) and isinstance(value, dt.time):
            pass
        else:
            raise TypeError("Cannot convert {} to {}".format(value, cls.__name__))

        self = super(Time, cls).__new__(
            cls,
            hour=value.hour,
            minute=value.minute,
            second=value.second,
            microsecond=value.microsecond,
            tzinfo=value.tzinfo,
            fold=value.fold,
        )
        self._raw = _raw
        return self

    def __flatten__(self):  # type: () -> str
        if self._raw:
            return [self._raw]

        return [self.isoformat()]

    def __pyobj__(self, hidden=False):  # type: (bool) -> time
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

    def _getstate(self, protocol=3):
        return (pyobj(self, hidden=True), self._raw)


_integerfmt = {
    16: ("0x{:x}", "0x{:x}"),
    10: ("{:d}", "{:,}"),
    8: ("0o{:o}", "0o{:o}"),
    2: ("0b{:b}", "0b{:b}"),
}


class Integer(_Value, int):
    """
    An integer literal.
    """

    def ksep():
        def fget(self):
            return self._ksep

        def fset(self, ksep):
            self._ksep = bool(ksep)

        return locals()

    ksep = property(**ksep())

    def base():
        def fget(self):
            return self._base

        def fset(self, base):
            if base not in _integerfmt:
                raise ValueError

            self._base = base

        return locals()

    base = property(**base())

    @property
    def _fmt(self):
        return _integerfmt[self.base]

    def __new__(
        cls, value, ksep=False, base=None, _raw=None
    ):  # type: (int, bool) -> Integer
        if isinstance(value, cls):
            return value
        elif not isinstance(value, _Item) and isinstance(value, int):
            _base = base or 10
            base = None
        elif (
            not isinstance(value, _Item)
            and isinstance(value, str)
            and "." not in value
            and "e" not in value
        ):
            _base = base or 10
        else:
            raise TypeError("Cannot convert {} to {}".format(value, cls.__name__))

        if base is None:
            self = super(Integer, cls).__new__(cls, value)
        else:
            self = super(Integer, cls).__new__(cls, value, base=base)

        # thousands separator (_)
        self.ksep = ksep
        self.base = _base
        self._raw = _raw
        return self

    def __flatten__(self):  # type: () -> str
        if self._raw:
            return [self._raw]

        return [str(self).replace(",", "_")]

    def __str__(self):
        return self._fmt[self._ksep].format(self)

    def __repr__(self):  # type: () -> str
        return "<{} {}>".format(self.__class__.__name__, str(self))

    def __pyobj__(self, hidden=False):  # type: (bool) -> int
        return int(self)

    def _getstate(self, protocol=3):
        return (pyobj(self, hidden=True), self.ksep, self.base, self._raw)


_floatfmt = {False: ("{:f}", "{:,f}"), True: ("{:e}", "{:,e}")}


class Float(_Value, float):
    """
    A float literal.
    """

    def ksep():
        def fget(self):
            return self._ksep

        def fset(self, ksep):
            self._ksep = bool(ksep)

        return locals()

    ksep = property(**ksep())

    def scientific():
        def fget(self):
            return self._scientific

        def fset(self, scientific):
            self._scientific = bool(scientific)

        return locals()

    scientific = property(**scientific())

    @property
    def _fmt(self):
        return _floatfmt[self.scientific]

    def __new__(
        cls, value, ksep=False, scientific=False, _raw=None
    ):  # type: (float, bool) -> Float
        if isinstance(value, cls):
            return value
        elif not isinstance(value, _Item) and isinstance(value, float):
            pass
        elif (
            not isinstance(value, _Item)
            and isinstance(value, str)
            and (
                value.count(".") == 1
                or value.count("e") == 1
                or value.lower() in ["inf", "nan"]
            )
        ):
            pass
        else:
            raise TypeError("Cannot convert {} to {}".format(value, cls.__name__))

        self = super(Float, cls).__new__(cls, value)

        # thousands separator (_)
        self.ksep = ksep
        self.scientific = scientific
        self._raw = _raw
        return self

    def __flatten__(self):  # type: () -> str
        if self._raw:
            return [self._raw]

        return [str(self).replace(",", "_")]

    def __str__(self):
        return self._fmt[self._ksep].format(self)

    def __repr__(self):  # type: () -> str
        return "<{} {}>".format(self.__class__.__name__, str(self))

    def __pyobj__(self, hidden=False):  # type: (bool) -> float
        return float(self)

    def _getstate(self, protocol=3):
        return (pyobj(self, hidden=True), self.ksep, self.scientific, self._raw)
