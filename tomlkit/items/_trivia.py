# -*- coding: utf-8 -*-
from ._item import _Item
from ._hidden import Comment, blank


class _TriviaMeta(type):
    def comment():
        def fget(self):
            return self._comment

        def fset(self, value):
            if issubclass(value, Comment):
                raise TypeError("comment must be a _Comment")
            self._comment = value

        return locals()

    comment = property(**comment())


class _Trivia(_Item, metaclass=_TriviaMeta):
    def comment():
        def fget(self):  # type: () -> _Comment
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
