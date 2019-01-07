from datetime import timedelta
from .._compat import decode
from .._compat import timezone
from . import chars

_utc = timezone(timedelta(), "UTC")

_escaped = {"b": "\b", "t": "\t", "n": "\n", "f": "\f", "r": "\r", '"': '"', "\\": "\\"}
_escapes_wnl = {v: "\\" + k for k, v in _escaped.items()}
_escapes_wonl = dict(_escapes_wnl)
_escapes_wonl["\n"] = "\n"


def escape_string(s, nl=True):
    s = decode(s)

    res = []
    start = 0

    def flush():
        if start != i:
            res.append(s[start:i])

        return i + 1

    escapes = _escapes_wnl if nl else _escapes_wonl

    i = 0
    while i < len(s):
        c = s[i]
        if c in escapes:
            start = flush()
            res.append(escapes[c])
            i += 1
            continue

        c = ord(c)
        if c < 0x20:
            start = flush()
            res.append("\\u%04x" % c)
            i += 1
            continue

        i += 1

    flush()

    return "".join(res)
