# -*- coding: utf-8 -*-
from ._items import _Item
from ._trivia import _Value


_FLOATFMT = {False: ("{}", "{:,}"), True: ("{:e}", "{:,e}")}


def check_ksep(ksep):
    return bool(ksep)


def check_scientific(scientific):
    return bool(scientific)


def check_raw(value, ksep, scientific, raw):
    if raw is not None:
        return raw

    return _FLOATFMT[scientific][ksep].format(float(value)).replace(",", "_")


class Float(_Value, float):
    __slots__ = ["_ksep", "_scientific", "_raw"]

    def __new__(
        cls, value, ksep=False, scientific=False, _raw=None
    ):  # type: (float, bool, bool, str) -> Float
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
        self._ksep = ksep = check_ksep(ksep)
        self._scientific = scientific = check_scientific(scientific)
        self._raw = _raw = check_raw(self, ksep, scientific, _raw)
        return self

    def __str__(self):
        return self._raw

    def __pyobj__(self):  # type: () -> float
        return float(self)

    __hiddenobj__ = __pyobj__

    def _getstate(self, protocol=3):
        return (self.__hiddenobj__(), self._ksep, self._scientific, self._raw)
