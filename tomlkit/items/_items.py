# -*- coding: utf-8 -*-
from six import with_metaclass
from abc import ABCMeta
from .._compat import unicode


class _Item(with_metaclass(ABCMeta)):
    """
    An item within a TOML document.
    """

    def __flatten__(self):  # type: () -> str
        raise NotImplementedError

    def __repr__(self):  # type: () -> unicode
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
    def __new__(cls, comment):  # type: (unicode) -> Comment
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
        self.__bool = not is_none

        return self

    def __init__(self, comment):  # type: (unicode) -> None
        return super(Comment, self).__init__()

    def apply(self, other):  # type: (unicode) -> unicode
        if self:
            return other + "  # " + self
        return other

    def __flatten__(self):
        if self:
            return ["# " + self]
        return []

    def __bool__(self):
        return self.__bool


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
    def complex(self):
        return bool(self.comment)


class _Container(_Trivia):
    pass
