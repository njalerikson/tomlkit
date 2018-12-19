# -*- coding: utf-8 -*-
import string
from abc import ABC, abstractmethod
from collections.abc import Mapping
import datetime as dt
from re import compile as r, VERBOSE

from ..source import Source
from ..exceptions import UnexpectedCharError, LeadingZeroError
from .._compat import timezone
from .._utils import _utc
from ..toml_char import TOMLChar

from ..items import Comment
from ..items import Key, KeyType
from ..items import Bool
from ..items import String, StringType
from ..items import DateTime, Date, Time, Integer, Float
from ..items import Array, Table

from ._utils import parse_word, parse_string


def consume_nl(src):
    if src.consume(TOMLChar.NL) == 0 and not src.end():
        raise src.parse_error(UnexpectedCharError, src.current)


class _Parser(ABC):
    # __klass__ = ???
    __slots__ = []

    def parse(self, src, **kwargs):
        # ensure that the src is a valid Source object
        if not isinstance(src, Source):
            src = Source(src)
            value = self.parse(src, **kwargs)

            # if we didn't consume the entire source then we consider this to be
            # an error
            if not src.end():
                raise src.parse_error(UnexpectedCharError, src.current)

            return value

        # check that the first character is valid
        check = self.__check__(src)
        if check is None:
            raise src.parse_error(UnexpectedCharError, src.current)

        # attempt parsing the remaining value
        with src.state:
            return self.__inst__(check, src, **kwargs)

    @abstractmethod
    def __check__(self, src):
        pass

    def __parse__(self, check, src, **kwargs):
        raise NotImplementedError

    def __inst__(self, check, src, **kwargs):
        return self.__klass__(*self.__parse__(check, src, **kwargs))

    def __assign__(self, parent, key, value):
        if isinstance(parent, Mapping):
            if key in parent:
                raise KeyError(
                    "Cannot set the same key ({}) multiple times.".format(key)
                )

            return parent.setdefault(key, value)
        else:
            parent.append(value)
            return parent[-1]


class _ValueParser(_Parser):
    def __inst__(self, check, src, parent, key, **kwargs):
        value = self.__klass__(*self.__parse__(check, src, **kwargs))
        return self.__assign__(parent, key, value)


class _ContainerParser(_Parser):
    pass


class KeyParser(_Parser):
    __klass__ = Key

    def __check__(self, src):
        if src.current in TOMLChar.BARE:
            return KeyType.BARE
        elif src.current == KeyType.BASIC.open:
            return KeyType.BASIC
        elif src.current == KeyType.LITERAL.open:
            return KeyType.LITERAL

    def __parse__(self, style, src):
        if style.is_bare():
            mark = src.idx
            src.consume(TOMLChar.BARE)
            value = src[mark : src.idx]
        else:
            value, style, _ = parse_string(style, src, multi=False)

        return (value, style)


class _KeysParser(_Parser):
    __slots__ = ["_key"]

    def key():
        def fget(self):
            return self._key

        def fset(self, key):
            if not isinstance(key, _Parser):
                raise TypeError("key must be a _Parser")
            self._key = key

        return locals()

    key = property(**key())

    def __inst__(self, _, src, term):
        keys = []
        first = True
        while src.current != term:
            # leading indent
            src.consume(TOMLChar.SPACES)

            # skip additional parsing if we find a closing bracket
            if src.current == term:
                break

            if not first:
                src.consume(".", min=1, max=1)

            # spacing
            src.consume(TOMLChar.SPACES)

            # key
            keys.append(self.key.parse(src))
            first = False

        return tuple(keys)


class ItemKeysParser(_KeysParser):
    def __check__(self, src):
        return True

    def __inst__(self, _, src):
        key = super(ItemKeysParser, self).__inst__(_, src, "=")

        # consume terminating
        src.consume("=", min=1, max=1)

        return key


class TableKeysParser(_KeysParser):
    __slots__ = ["_inline_comment"]

    def inline_comment():
        def fget(self):
            return self._inline_comment

        def fset(self, inline_comment):
            if not isinstance(inline_comment, _Parser) and inline_comment is not False:
                raise TypeError("inline_comment must be a _Parser or False")
            self._inline_comment = inline_comment

        return locals()

    inline_comment = property(**inline_comment())

    def __check__(self, src):
        if src.current == "[":
            return True

    def __inst__(self, _, src):
        # consume opening bracket
        open_count = src.consume("[", min=1, max=2)

        key = super(TableKeysParser, self).__inst__(_, src, "]")

        # consume closing bracket
        src.consume("]", min=open_count, max=open_count)

        # consume any spacing/newline
        src.consume(TOMLChar.SPACES)

        # inline comment
        comment = None
        if self.inline_comment:
            try:
                comment = self.inline_comment.parse(src)
            except UnexpectedCharError:
                pass

        # if no inline-comment, consume newline chars
        if not comment:
            consume_nl(src)

        return (
            key,
            open_count == 2,  # this is an AoT key if we have double braces
            comment,
        )


class CommentParser(_Parser):
    __klass__ = Comment

    def __check__(self, src):
        if src.current in "#":
            return True

    def __parse__(self, _, src):
        src.inc(exception=True)  # consume comment hash

        mark = src._idx

        # consume everything until we find newline/EOF
        while src.current not in TOMLChar.NL and src.inc():
            pass

        value = src[mark : src._idx]

        # consume newline chars
        consume_nl(src)

        return (value,)


class BoolParser(_ValueParser):
    __klass__ = Bool

    def __check__(self, src):  # type: (Source) -> bool
        if src.current == "t":
            return True
        elif src.current == "f":
            return False

    def __parse__(self, style, src):  # type: (bool, Source) -> Tuple(bool)
        return (parse_word(style, src),)


class StringParser(_ValueParser):
    __klass__ = String
    __slots__ = ["_multi"]

    def multi():
        def fget(self):
            return self._multi

        def fset(self, multi):
            self._multi = bool(multi)

        return locals()

    multi = property(**multi())

    def __check__(self, src):  # type: (Source) -> StringType
        if src.current == StringType.BASIC.open:
            return StringType.BASIC
        elif src.current == StringType.LITERAL.open:
            return StringType.LITERAL

    def __parse__(self, style, src):
        return parse_string(style, src, self.multi)


class NumDateParser(_ValueParser):
    def datetime():
        def fget(self):
            return self._datetime

        def fset(self, datetime):
            self._datetime = bool(datetime)

        return locals()

    datetime = property(**datetime())

    def date():
        def fget(self):
            return self._date

        def fset(self, date):
            self._date = bool(date)

        return locals()

    date = property(**date())

    def time():
        def fget(self):
            return self._time

        def fset(self, time):
            self._time = bool(time)

        return locals()

    time = property(**time())

    def integer():
        def fget(self):
            return self._integer

        def fset(self, integer):
            self._integer = bool(integer)

        return locals()

    integer = property(**integer())

    def float():
        def fget(self):
            return self._float

        def fset(self, float):
            self._float = bool(float)

        return locals()

    float = property(**float())

    def __check__(self, src):
        if (
            src.current in "+-"  # signed
            or src.current == "i"  # inf
            or src.current == "n"  # nan
            or src.current in string.digits
        ):
            return True

    def _get_sign(self, src):  # type: (Parser) -> str
        # if the current char is a sign, consume it
        sign = ""
        if src.current in "+-":
            sign = src.current

            # consume this sign, EOF here is problematic as it would be a bare sign
            src.inc(exception=True)

        return sign

    def _parse_offset(self, src):
        mark = src.idx

        # sign
        sign = self._get_sign(src)

        # hour
        _mark = src.idx
        if src.current in "01":
            src.inc(exception=True)
            src.consume(string.digits, min=1, max=1)
        elif src.current in "2":
            src.inc(exception=True)
            src.consume("0123", min=1, max=1)
        else:
            raise src.parse_error(UnexpectedCharError, src.current)
        hour = int(src[_mark : src.idx])

        # delimiter [:]
        src.consume(":", min=1, max=1)

        # minute
        _mark = src.idx
        if src.current in "012345":
            src.inc(exception=True)
            src.consume(string.digits, min=1, max=1)
        else:
            raise src.parse_error(UnexpectedCharError, src.current)
        minute = int(src[_mark : src.idx])

        seconds = hour * 3600 + minute * 60
        offset = dt.timedelta(seconds=seconds)
        if sign == "-":
            offset = -offset

        return timezone(offset, src[mark : src.idx])

    def _parse_datetime(self, year, month, day, src):
        # delimiter [T ] (already tested for)
        src.inc(exception=True)

        # hour
        mark = src.idx
        if src.current in "01":
            src.inc(exception=True)
            src.consume(string.digits, min=1, max=1)
        elif src.current in "2":
            src.inc(exception=True)
            src.consume("0123", min=1, max=1)
        else:
            raise src.parse_error(UnexpectedCharError, src.current)

        value = self._parse_time(mark, src)
        hour = value.hour
        minute = value.minute
        second = value.second
        microsecond = value.microsecond

        # delimiter [Z] or timezone
        tzinfo = {}
        if src.current in "Z":
            src.inc()
            tzinfo = {"tzinfo": _utc}
        elif src.current in "+-":
            tzinfo = {"tzinfo": self._parse_offset(src)}

        return dt.datetime(
            year, month, day, hour, minute, second, microsecond, **tzinfo
        )

    def _parse_date(self, mark, src):
        # year (already consumed)
        year = int(src[mark : src.idx])

        # delimiter [-] (already tested for)
        src.inc(exception=True)

        # month
        _mark = src.idx
        if src.current in "0":
            src.inc(exception=True)
            src.consume("123456789", min=1, max=1)
        elif src.current in "1":
            src.inc(exception=True)
            src.consume("012", min=1, max=1)
        else:
            raise src.parse_error(UnexpectedCharError, src.current)
        month = int(src[_mark : src.idx])

        # delimiter [-]
        src.consume("-", min=1, max=1)

        # day
        _mark = src.idx
        if src.current in "0":
            src.inc(exception=True)
            src.consume("123456789", min=1, max=1)
        elif src.current in "12":
            src.inc(exception=True)
            src.consume(string.digits, min=1, max=1)
        elif src.current in "3":
            src.inc(exception=True)
            src.consume("01", min=1, max=1)
        else:
            raise src.parse_error(UnexpectedCharError, src.current)
        day = int(src[_mark : src.idx])

        if self.datetime and src.current in "T ":
            with src.state:
                return self._parse_datetime(year, month, day, src)

        if self.date:
            return dt.date(year, month, day)

        raise src.parse_error(UnexpectedCharError, src.current)

    def _parse_time(self, mark, src):
        # hour - parsed prior to getting here, extract
        raw = src[mark : src.idx]
        hour = int(raw)
        if len(raw) != 2 or hour > 23:
            raise src.parse_error(UnexpectedCharError, src.current)

        # delimiter [:]
        src.consume(":", min=1, max=1)

        # minute
        _mark = src.idx
        if src.current in "012345":
            src.inc(exception=True)
            src.consume(string.digits, min=1, max=1)
        else:
            raise src.parse_error(UnexpectedCharError, src.current)
        minute = int(src[_mark : src.idx])

        # delimiter [:]
        src.consume(":", min=1, max=1)

        # second
        _mark = src.idx
        if src.current in "012345":
            src.inc(exception=True)
            src.consume(string.digits, min=1, max=1)
        # Python's datetime/time doesn't handle RFC3339 leap seconds
        # elif src.current in "6":
        #     src.inc(exception=True)
        #     src.consume("0", min=1, max=1)
        else:
            raise src.parse_error(UnexpectedCharError, src.current)
        second = int(src[_mark : src.idx])

        # microsecond
        microsecond = 0
        if src.current == ".":
            src.inc(exception=True)
            _mark = src.idx
            src.consume(string.digits, min=1, max=6)
            microsecond = int("{:<06s}".format(src[_mark : src.idx]))

        return dt.time(hour, minute, second, microsecond)

    _RE_UNDERSCORE = r(
        r"""
        (?<=
            [{digits}]
        )
        _
        (?=
            [{digits}]
        )
        """.format(
            digits=string.digits
        ),
        flags=VERBOSE,
    )

    def _parse_integer(self, sign, mark, src):
        # get the raw number
        raw = src[mark : src.idx]

        # underscores must be surrounded by digits so only replace those,
        # the rest will remain and cause failures
        # (Python doesn't like _ in integers/floats)
        clean = self._RE_UNDERSCORE.sub("", raw)

        # use thousands separator
        ksep = clean != raw

        return int(sign + clean), ksep

    def _parse_float(self, sign, mark, src):
        # get the raw number
        raw = src[mark : src.idx]

        # underscores must be surrounded by digits so only replace those,
        # the rest will remain and cause failures
        # (Python doesn't like _ in integers/floats)
        clean = self._RE_UNDERSCORE.sub("", raw)

        # use thousands separator
        ksep = clean != raw

        return float(sign + clean), ksep

    def _parse_underscore(self, src):
        src.consume(string.digits, min=1)

        # if the next character is _ we will consume it and expect a digit to follow
        if src.current == "_":
            src.inc(exception=True)

            self._parse_underscore(src)

    def __parse__(self, _, src):
        sign = self._get_sign(src)

        # inf
        if self.float and src.current == "i":
            return (float(sign + parse_word("inf", src)),)

        # nan
        if self.float and src.current == "n":
            return (float(sign + parse_word("nan", src)),)

        # mark the start of the number
        mark = src.idx

        # consume as many valid characters as possible
        src.consume(string.digits, min=1)

        # datetime or date
        if (self.datetime or self.date) and not sign and src.current == "-":
            return (self._parse_date(mark, src),)

        # time
        if self.time and not sign and src.current == ":":
            return (self._parse_time(mark, src),)

        # float or integer
        decimal = euler = False

        # _ allowed between digits
        if src.current == "_":
            src.inc(exception=True)

            # we got digit(s) followed by an underscore, we must have more digits
            # (possibly more underscores)
            self._parse_underscore(src)

        # check for leading zero
        raw = src[mark : src.idx]
        if len(raw) > 1 and raw.startswith("0"):
            raise src.parse_error(LeadingZeroError)

        # decimal
        if self.float and src.current == ".":
            decimal = True

            # consume this char, EOF here is problematic (middle of number)
            src.inc(exception=True)

            # consume as many valid characters as possible (at least one)
            self._parse_underscore(src)

        # euler
        if self.float and src.current in "eE":
            euler = True

            # consume this char, EOF here is problematic (middle of number)
            src.inc(exception=True)

            # there may (or may not) be a sign here, consume it
            self._get_sign(src)

            # consume as many valid characters as possible (at least one)
            self._parse_underscore(src)

        # float
        if self.float and (decimal or euler):
            return self._parse_float(sign, mark, src)

        # integer
        if self.integer:
            return self._parse_integer(sign, mark, src)

        raise src.parse_error(UnexpectedCharError, src.current)

    def __inst__(self, check, src, parent, key, **kwargs):
        value, *args = self.__parse__(check, src, **kwargs)
        if isinstance(value, dt.datetime):
            value = DateTime(value, *args)
        elif isinstance(value, dt.date):
            value = Date(value, *args)
        elif isinstance(value, dt.time):
            value = Time(value, *args)
        elif isinstance(value, int):
            value = Integer(value, *args)
        else:
            value = Float(value, *args)
        return self.__assign__(parent, key, value)


class _ValueParser(_ContainerParser):
    __slots__ = ["_values", "_inline_comment", "_comment"]

    def values():
        def fget(self):
            return self._values

        def fset(self, values):
            values = list(values)
            if any(not isinstance(v, _Parser) for v in values):
                raise TypeError("values must be a list of _Parser")
            self._values = values

        return locals()

    values = property(**values())

    def inline_comment():
        def fget(self):
            return self._inline_comment

        def fset(self, inline_comment):
            if not isinstance(inline_comment, _Parser) and inline_comment is not False:
                raise TypeError("inline_comment must be a _Parser or False")
            self._inline_comment = inline_comment

        return locals()

    inline_comment = property(**inline_comment())

    def comment():
        def fget(self):
            return self._comment

        def fset(self, comment):
            if not isinstance(comment, _Parser) and comment is not False:
                raise TypeError("comment must be a _Parser or False")
            self._comment = comment

        return locals()

    comment = property(**comment())

    def __inst__(self, src, parent, key):
        for parser in self.values:
            check = parser.__check__(src)
            if check is None:
                continue

            with src.state:
                return parser.__inst__(check, src, parent, key)

        raise src.parse_error(UnexpectedCharError, src.current)


class _ItemParser(_ValueParser):
    __slots__ = ["_key"]

    def key():
        def fget(self):
            return self._key

        def fset(self, key):
            if not isinstance(key, _Parser):
                raise TypeError("key must be a _Parser")
            self._key = key

        return locals()

    key = property(**key())

    def __inst__(self, src, parent):
        # key
        key = self.key.parse(src)

        # spacing
        src.consume(TOMLChar.SPACES)

        # value
        value = super(_ItemParser, self).__inst__(src, parent, key)

        # spacing
        src.consume(TOMLChar.SPACES)

        # inline comment
        if self.inline_comment:
            try:
                value.comment = self.inline_comment.parse(src)
            except UnexpectedCharError:
                pass

        return key, value


class InlineTableParser(_ItemParser):
    __klass__ = Table

    def __check__(self, src):
        if src.current == "{":
            return True

    def __inst__(self, src, parent, key):
        src.inc(exception=True)  # consume opening bracket

        tbl = self.__assign__(parent, key, {})
        first = True
        while src.current != "}":
            # leading indent
            src.consume(TOMLChar.SPACES)

            # skip additional parsing if we find a closing bracket
            if src.current == "}":
                break

            if not first:
                src.consume(",", min=1, max=1)

            # spacing
            src.consume(TOMLChar.SPACES)

            # key-value
            super(InlineTableParser, self).__inst__(src, tbl)
            first = False

        src.inc()  # consume closing bracket

        return tbl


class TableParser(_ItemParser):
    __klass__ = Table
    __slots__ = ["_tablekey"]

    def tablekey():
        def fget(self):
            return self._tablekey

        def fset(self, tablekey):
            if not isinstance(tablekey, _Parser):
                raise TypeError("tablekey must be a _Parser")
            self._tablekey = tablekey

        return locals()

    tablekey = property(**tablekey())

    def __check__(self, src):
        return True

    def _get_table(self, src, tbl):
        while src.current not in "[\0":
            # leading indent
            src.consume(TOMLChar.WS)

            # skip additional parsing if we find a closing bracket
            if src.current in "[\0":
                break

            if self.comment:
                try:
                    tbl.comments.append(self.comment.parse(src))
                    continue
                except UnexpectedCharError:
                    pass

            # key-value
            _, value = super(TableParser, self).__inst__(src, tbl)

            # if no inline-comment, consume newline chars
            if not value.comment:
                consume_nl(src)

    def __inst__(self, _, src):
        inst = self.__klass__()
        inst.complex = True
        self._get_table(src, inst)

        while src.current != "\0":
            # get key
            key, aot, comment = self.tablekey.parse(src)

            # if the open_count is one, we are looking at a normal Table which needs
            # to be inserted directly into inst, if the open_count is two, we are
            # looking at an array of Tables where the current Table needs to be
            # inserted into the array (and if the array doesn't exist yet it needs to
            # be created)
            if aot:
                arr = inst.setdefault(key, [])
                arr.append({})
                tbl = arr[-1]
            else:
                tbl = inst.setdefault(key, {})
            if comment:
                tbl.comment = comment
            tbl.complex = True

            self._get_table(src, tbl)

        return inst


class ArrayParser(_ValueParser):
    __klass__ = Array

    def __check__(self, src):
        if src.current == "[":
            return True

    def __inst__(self, _, src, parent, key):
        src.inc(exception=True)  # consume opening bracket

        arr = self.__assign__(parent, key, [])
        previous_is_value = False
        while src.current != "]":
            # leading indent
            src.consume(TOMLChar.WS)

            # skip additional parsing if we find a closing bracket
            if src.current == "]":
                break

            # comment
            if self.comment:
                try:
                    arr.comments.append(self.comment.parse(src))
                    continue
                except UnexpectedCharError:
                    pass

            if previous_is_value:
                src.consume(",", min=1, max=1)
                previous_is_value = False
            else:
                # value
                value = super(ArrayParser, self).__inst__(src, arr, key)

                # spacing
                src.consume(TOMLChar.SPACES)

                if src.consume(",", max=1) == 1:
                    previous_is_value = False

                    # spacing
                    src.consume(TOMLChar.SPACES)
                else:
                    previous_is_value = True

                # inline comment
                if self.inline_comment:
                    try:
                        value.comment = self.inline_comment.parse(src)
                    except UnexpectedCharError:
                        pass

        src.inc()  # consume closing bracket

        return arr
