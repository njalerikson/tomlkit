# -*- coding: utf-8 -*-
import datetime as dt
from ._item import _Item
from ._trivia import _Value


def check_raw(value, raw):
    if raw is not None:
        return raw

    return value.isoformat()


class Time(_Value, dt.time):
    __slots__ = ["_raw"]

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
        self._raw = _raw = check_raw(self, _raw)
        return self

    @classmethod
    def fromisoformat(cls, time_string):  # type: (str) -> Time
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
    ):  # type: (int, int, int, int, tzinfo, int) -> Time
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

    def __pyobj__(self):  # type: () -> time
        return dt.time(
            self.hour,
            self.minute,
            self.second,
            self.microsecond,
            self.tzinfo,
            fold=self.fold,
        )

    __hiddenobj__ = __pyobj__
