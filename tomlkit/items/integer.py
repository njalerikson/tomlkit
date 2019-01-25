# -*- coding: utf-8 -*-
from ._item import _Item
from ._trivia import _Value


_INTEGERFMT = {
    16: ("0x{:x}", "0x{:x}"),
    10: ("{:d}", "{:,}"),
    8: ("0o{:o}", "0o{:o}"),
    2: ("0b{:b}", "0b{:b}"),
}


def check_ksep(ksep):
    return bool(ksep)


def check_base(base):
    if base not in _INTEGERFMT:
        raise ValueError

    return base


def check_raw(value, ksep, base, raw):
    if raw is not None:
        return raw

    return _INTEGERFMT[base][ksep].format(int(value)).replace(",", "_")


class Integer(_Value, int):
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
        self._ksep = ksep = check_ksep(ksep)
        self._base = _base = check_base(_base)
        self._raw = _raw = check_raw(self, ksep, _base, _raw)
        return self

    def __str__(self):
        return self._raw

    def __pyobj__(self):  # type: () -> int
        return int(self)

    __hiddenobj__ = __pyobj__

    def _getstate(self, protocol=3):
        return (self.__hiddenobj__(), self._ksep, self._base, self._raw)
