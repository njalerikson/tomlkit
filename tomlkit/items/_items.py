# -*- coding: utf-8 -*-
class _Item:
    def __flatten__(self):  # type: () -> str
        return [self._raw]

    def __repr__(self):  # type: () -> str
        return "<{} {}>".format(self.__class__.__name__, self._raw)

    def __pyobj__(self, hidden=False):
        raise NotImplementedError(self.__class__)

    __hiddenobj__ = __pyobj__

    # Pickling methods

    def _getstate(self, protocol=3):
        return (self.__hiddenobj__(), self._raw)

    def __reduce__(self):
        return self.__reduce_ex__(2)

    def __reduce_ex__(self, protocol):
        return self.__class__, self._getstate(protocol)
