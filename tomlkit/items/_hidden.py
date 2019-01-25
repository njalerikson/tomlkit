# -*- coding: utf-8 -*-
from .._compat import unicode
from ._item import _Item


class _Hidden(_Item):
    pass


class Comment(_Hidden, unicode):
    def __new__(cls, comment):  # type: (str) -> Comment
        if isinstance(comment, cls):
            return comment

        is_none = comment is None
        if comment:
            comment = unicode(comment)

            # strip leading/trailing spaces
            comment = comment.strip()

            if not comment.startswith("#"):
                comment = "# " + comment
        else:
            comment = ""

        self = super(Comment, cls).__new__(cls, comment)
        self._bool = not is_none

        return self

    def __init__(self, comment):  # type: (str) -> None
        super(Comment, self).__init__()

    def apply(self, other):  # type: (str) -> str
        if self:
            return other + "  " + self
        return other

    def __flatten__(self):  # type: () -> list
        if self:
            return [unicode(self)]
        return []

    def __bool__(self):
        return self._bool

    def __repr__(self):  # type: () -> str
        return "<{} {}>".format(self.__class__.__name__, self)

    def _getstate(self, protocol=3):
        if not self:
            return (None,)
        return (unicode(self),)


blank = Comment(None)


class Newline(_Hidden, unicode):
    def __new__(cls, ws=1):  # type: (str) -> Newline
        if isinstance(ws, cls):
            return ws

        count = ws if isinstance(ws, int) else str(ws).count("\n")

        self = super(Newline, cls).__new__(cls, "\n")
        self._count = max(1, count)
        return self

    def __init__(self, ws=1):  # type: (str) -> None
        return super(Newline, self).__init__()

    def __flatten__(self):  # type: () -> list
        return [""] * self._count

    def __repr__(self):  # type: () -> str
        return "<{} {}>".format(self.__class__.__name__, self._count)

    def _getstate(self, protocol=3):
        return (self._count,)
