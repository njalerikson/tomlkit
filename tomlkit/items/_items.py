# -*- coding: utf-8 -*-
from .._compat import unicode


class _Item:
    def __flatten__(self):  # type: () -> str
        raise NotImplementedError

    def __repr__(self):  # type: () -> str
        return "<{} {}>".format(self.__class__.__name__, self)

    def __pyobj__(self):
        raise NotImplementedError

    # Pickling methods

    # def _getstate(self, protocol=3):
    #     raise NotImplementedError()

    # def __reduce__(self):
    #     return self.__reduce_ex__(2)

    # def __reduce_ex__(self, protocol):
    #     return self.__class__, self._getstate(protocol)


class _Key(_Item):
    pass


class Comment(_Item, unicode):
    pass

    def __new__(cls, comment):  # type: (str) -> Comment
        if isinstance(comment, cls):
            return comment

        is_none = comment is None
        if comment:
            comment = unicode(comment)

            # strip leading/trailing spaces
            comment = comment.strip()

            # string leading comment hash/spaces
            comment = comment.lstrip("#")
            comment = comment.lstrip()
        else:
            comment = ""

        self = super(Comment, cls).__new__(cls, comment)
        self._bool = not is_none

        return self

    def __init__(self, comment):  # type: (str) -> None
        return super(Comment, self).__init__()

    def apply(self, other):  # type: (str) -> str
        if self:
            return other + "  # " + self
        return other

    def __flatten__(self):
        if self:
            return ["# " + self]
        return []

    def __bool__(self):
        return self._bool


blank = Comment(None)


class _Trivia(_Item):
    def comment():
        def fget(self):  # type: () -> Comment
            try:
                return self._comment
            except AttributeError:
                return blank

        def fset(self, value):  # type: (str) -> None
            self._comment = Comment(value)

        return locals()

    comment = property(**comment())


class _Value(_Trivia):
    @property
    def _derived_complexity(self):
        return bool(self.comment)

    @property
    def _complexity(self):
        return self._derived_complexity

    @property
    def complexity(self):
        return self._complexity


class _Container(_Trivia):
    @property
    def _derived_complexity(self):
        raise NotImplementedError

    def complexity():
        def fget(self):
            raise NotImplementedError

        def fset(self, value):
            raise NotImplementedError

        def fdel(self):
            raise NotImplementedError

        return locals()

    complexity = property(**complexity())

    # _handle = ???
    # _handle_local = ???
    # _handle_root = ???
