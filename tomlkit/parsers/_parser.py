# -*- coding: utf-8 -*-
from collections.abc import Mapping
from ..source import Source
from ..exceptions import UnexpectedCharError, DuplicateKeyError
from ..items._item import _Item


class _Parser:
    __slots__ = ["_klass"]

    def klass():
        def fget(self):
            return self._klass

        def fset(self, value):
            if value in (None, False):
                value = None
            elif not issubclass(value, _Item):
                err = "expected klass to be an _Item, not {!r}".format(value)
                raise ValueError(err)
            self._klass = value

        return locals()

    klass = property(**klass())

    def parse(self, src, **kwargs):
        # ensure that the src is a valid Source object
        if not isinstance(src, Source):
            src = Source(src)
            value = self.parse(src, **kwargs)

            # if we didn't consume the entire source then we consider this to be
            # an error
            if not src.end():
                raise src.parse_error(UnexpectedCharError(src.current))

            return value

        # check that the first character is valid
        check = self.__check__(src)
        if check is None:
            raise src.parse_error(UnexpectedCharError(src.current))

        # attempt parsing the remaining value
        with src.state:
            return self.__inst__(check, src, **kwargs)

    def __check__(self, src):
        raise NotImplementedError

    def __parse__(self, check, src, **kwargs):
        raise NotImplementedError

    def __inst__(self, check, src, **kwargs):
        return self.klass(*self.__parse__(check, src, **kwargs))

    def __assign__(self, parent, key, value):
        if isinstance(parent, Mapping):
            if key in parent:
                raise DuplicateKeyError(key)

            return parent.setdefault(key, value)
        else:
            parent.append(value)
            return parent[-1]
