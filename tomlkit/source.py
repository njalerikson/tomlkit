# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import itertools

from copy import copy
from typing import Optional
from typing import Tuple

from ._compat import PY2
from ._compat import unicode
from ._compat import decode
from .exceptions import UnexpectedEofError
from .exceptions import UnexpectedCharError
from .exceptions import ParseErrorMixin


class _State:
    def __init__(
        self, source, save_marker=False, restore=False
    ):  # type: (_Source, Optional[bool], Optional[bool]) -> None
        self._source = source
        self._save_marker = save_marker
        self.restore = restore

    def __enter__(self):  # type: () -> None
        # Entering this context manager - save the state
        if PY2:
            # Python 2.7 does not allow to directly copy
            # an iterator, so we have to make tees of the original
            # chars iterator.
            self._source._chars, self._chars = itertools.tee(self._source._chars)
        else:
            self._chars = copy(self._source._chars)
        self._idx = self._source._idx
        self._current = self._source._current
        self._marker = self._source._marker

        return self

    def __exit__(self, exception_type, exception_val, trace):
        # Exiting this context manager - restore the prior state
        if self.restore or exception_type:
            self._source._chars = self._chars
            self._source._idx = self._idx
            self._source._current = self._current
            if self._save_marker:
                self._source._marker = self._marker


class _StateHandler:
    """
    State preserver for the Parser.
    """

    def __init__(self, source):  # type: (Source) -> None
        self._source = source
        self._states = []

    def __call__(self, *args, **kwargs):
        return _State(self._source, *args, **kwargs)

    def __enter__(self):  # type: () -> None
        state = self()
        self._states.append(state)
        return state.__enter__()

    def __exit__(self, exception_type, exception_val, trace):
        state = self._states.pop()
        return state.__exit__(exception_type, exception_val, trace)


class Source(unicode):
    __slots__ = ["_chars", "_idx", "_marker", "_current", "_state"]
    EOF = "\0"

    def __new__(cls, value):
        if isinstance(value, cls):
            return value
        return super(Source, cls).__new__(cls, decode(value))

    def __init__(self, _):  # type: (unicode) -> None
        super(Source, self).__init__()

        # Collection of Chars
        self._chars = iter([(i, c) for i, c in enumerate(self)])

        # set by self.inc()
        # self._idx = ???
        # self._current = ???

        # set by self.mark()
        # self._marker = ???

        self._state = _StateHandler(self)

        self.inc()
        self.mark()

    @property
    def state(self):  # type: () -> _StateHandler
        return self._state

    @property
    def idx(self):  # type: () -> int
        return self._idx

    @property
    def current(self):  # type: () -> Char
        return self._current

    @property
    def marker(self):  # type: () -> int
        return self._marker

    def extract(self):  # type: () -> unicode
        """
        Extracts the value between marker and index
        """
        return self[self._marker : self._idx]

    def inc(self, exception=None):  # type: (Optional[ParseError.__class__]) -> bool
        """
        Increments the parser if the end of the input has not been reached.
        Returns whether or not it was able to advance.
        """
        try:
            self._idx, self._current = next(self._chars)

            return True
        except StopIteration:
            self._idx = len(self)
            self._current = self.EOF
            if exception:
                raise self.parse_error(exception)

            return False

    def inc_n(self, n, exception=None):  # type: (int, Exception) -> bool
        """
        Increments the parser by n characters
        if the end of the input has not been reached.
        """
        for _ in range(n):
            if not self.inc(exception=exception):
                return False

        return True

    def consume(self, chars, min=0, max=-1):
        """
        Consume chars until min/max is satisfied is valid.
        """
        count = 0
        while self.current in chars and max != 0:
            min -= 1
            max -= 1
            count += 1
            if not self.inc():
                break

        # failed to consume minimum number of characters
        if min > 0:
            raise self.parse_error(UnexpectedCharError(self.current))

        return count

    def increment(self, iter):
        for i in iter:
            yield i, self.current

            self.inc()

    def start(self):  # type: () -> bool
        """
        Returns True if the parser is at the start of the input.
        """
        return self._idx == 0

    def end(self):  # type: () -> bool
        """
        Returns True if the parser has reached the end of the input.
        """
        return self._current is self.EOF

    def mark(self):  # type: () -> None
        """
        Sets the marker to the index's current position
        """
        self._marker = self._idx

    def parse_error(self, exception=UnexpectedCharError, *args):
        """
        Creates a generic "parse error" at the current position.
        """
        line, col = self._to_linecol()

        # de-construct exception
        if not isinstance(exception, Exception):
            exception = exception(*args)
        args = exception.args
        exception = exception.__class__

        # generate new exception
        class _(ParseErrorMixin, exception):
            pass

        _.__name__ = exception.__name__
        _.__module__ = exception.__module__
        _.__doc__ = exception.__doc__

        return _(line, col, *args)

    def _to_linecol(self):  # type: () -> Tuple[int, int]
        cur = 0
        for i, line in enumerate(self.splitlines()):
            if cur + len(line) + 1 > self.idx:
                return (i + 1, self.idx - cur)

            cur += len(line) + 1

        return len(self.splitlines()), 0
