# -*- coding: utf-8 -*-
from .._utils import _escaped, chars
from ..exceptions import InvalidCharInStringError, UnexpectedCharError


def parse_word(word, src):
    # only keep parsing for special float if the characters match the style
    # try consuming rest of chars in style
    for c in word:
        src.consume(c, min=1, max=1)

    return word


def parse_escaped(src, multi):
    if multi and src.current in chars.ws:
        # When the last non-whitespace character on a line is
        # a \, it will be trimmed along with all whitespace
        # (including newlines) up to the next non-whitespace
        # character or closing delimiter.
        # """\
        #     hello \
        #     world"""
        tmp = ""
        while src.current in chars.ws:
            tmp += src.current
            # consume the whitespace, EOF here is an issue
            # (middle of string)
            src.inc(exception=True)
            continue

        # the escape followed by whitespace must have a newline
        # before any other chars
        if "\n" not in tmp:
            raise src.parse_error(InvalidCharInStringError(src.current))

        return ""

    # special escape chars
    if src.current in _escaped:
        char = _escaped[src.current]

        # consume this char, EOF here is an issue (middle of string)
        src.inc(exception=True)

        return char

    # unicode
    if src.current in "uU":
        count = 8 if src.current == "U" else 4

        # consume this char, EOF here is an issue (middle of unicode, middle of string)
        src.inc(exception=True)

        mark = src.idx
        src.consume(chars.hex, min=count, max=count)
        return chr(int(src[mark : src.idx], 16))

    raise src.parse_error(InvalidCharInStringError(src.current))


def parse_string(style, src, multi=True):
    mark = src._idx

    # consume opening quotes
    open_count = src.consume(style.open, min=1, max=3 if multi else 1)

    # opened and closed string, return early
    if open_count == 2:
        return "", style, False

    multi = open_count == 3

    # A newline immediately following the opening delimiter will be trimmed.
    if multi and src.current == "\n":
        # consume the newline, EOF here is an issue (middle of string)
        src.inc(exception=True)

    value = ""
    escaped = False  # whether the previous key was ESCAPE
    while True:
        if not multi and src.current in "\r\n":
            # single line cannot have actual newline characters
            raise src.parse_error(InvalidCharInStringError(src.current))
        elif not escaped and src.current == style.close:
            # try to process current as a closing delim
            close_count = src.consume(style.close, min=1, max=open_count)
            if close_count != open_count:
                # not a triple quote, leave in result as is
                value += style.close * close_count
                continue

            return value, style, multi, src[mark : src._idx]
        elif style.is_basic() and escaped:
            # attempt to parse the current char as an escaped value, an exception
            # is raised if this fails
            value += parse_escaped(src, multi)

            # no longer escaped
            escaped = False
        elif style.is_basic() and src.current in "\\":
            # the next char is being escaped
            escaped = True

            # consume this char, EOF here is an issue (middle of string)
            src.inc(exception=True)
        else:
            # this is either a literal string where we keep everything as is,
            # or this is not a special escaped char in a basic string
            value += src.current

            # consume this char, EOF here is an issue (middle of string)
            src.inc(exception=True)


def consume_nl(src):
    if src.consume(chars.nl, max=1) == 0 and not src.end():
        raise src.parse_error(UnexpectedCharError(src.current))
