class ParseErrorMixin:
    """
    This error occurs when the parser encounters a syntax error
    in the TOML being parsed. The error references the line and
    location within the line where the error was encountered.
    """

    def __init__(
        self, line, col, idx, message=None
    ):  # type: (int, int, Optional[str]) -> None
        if message is None:
            message = "parse error"

        message = "{} (line {} column {} char {})".format(message, line, col, idx)

        if isinstance(self, _ParseError):
            return super(ParseErrorMixin, self).__init__(message=message)
        super(ParseErrorMixin, self).__init__(message)


class _ParseError(ValueError):
    def __init__(self, message):
        super(_ParseError, self).__init__(message)


class MixedArrayTypesError(_ParseError):
    """
    An array was found that had two or more element types.
    """

    def __init__(self, message=None):  # type: (str) -> None
        if message is None:
            message = "mixed types found in array"

        super(MixedArrayTypesError, self).__init__(message)


class LeadingZeroError(_ParseError):
    """
    A numeric has invalid leading zeros.
    """

    def __init__(self, message=None):  # type: (str) -> None
        if message is None:
            message = "cannot have leading zeros"

        super(LeadingZeroError, self).__init__(message)


class DuplicateKeyError(_ParseError):
    """
    A key has occurred more than once.
    """

    def __init__(self, key=None, message=None):  # type: (str) -> None
        if message is None:
            if key is None:
                message = "cannot set the same key multiple times"
            else:
                message = "cannot set the same key {} multiple times".format(key)

        super(DuplicateKeyError, self).__init__(message)


class UnexpectedCharError(_ParseError):
    """
    An unexpected character was found during parsing.
    """

    def __init__(self, char=None, message=None):  # type: (str) -> None
        if message is None:
            if char is None:
                message = "unexpected character"
            else:
                message = "unexpected character {}".format(repr(char))

        super(UnexpectedCharError, self).__init__(message)


class EmptyKeyError(_ParseError):
    """
    An empty key was found during parsing.
    """

    def __init__(self, message=None):  # type: (str) -> None
        if message is None:
            message = "empty key"

        super(EmptyKeyError, self).__init__(message)


class EmptyTableNameError(_ParseError):
    """
    An empty table name was found during parsing.
    """

    def __init__(self, message=None):  # type: (str) -> None
        if message is None:
            message = "empty table name"

        super(EmptyTableNameError, self).__init__(message)


class InvalidCharInStringError(_ParseError):
    """
    The string being parsed contains an invalid character.
    """

    def __init__(self, char=None, message=None):  # type: (str) -> None
        if message is None:
            if char is None:
                message = "invalid character in string"
            else:
                message = "invalid character {} in string".format(repr(char))

        super(InvalidCharInStringError, self).__init__(message)


class UnexpectedEofError(_ParseError):
    """
    The TOML being parsed ended before the end of a statement.
    """

    def __init__(self, message=None):  # type: (str) -> None
        if message is None:
            message = "unexpected end of file"

        super(UnexpectedEofError, self).__init__(message)
