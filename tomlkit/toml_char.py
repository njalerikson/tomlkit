import string

from ._compat import PY2
from ._compat import unicode

if PY2:
    from functools32 import lru_cache
else:
    from functools import lru_cache


class TOMLChar(unicode):
    def __init__(self, c):
        super(TOMLChar, self).__init__()
        if len(self) > 1:
            raise ValueError("A TOML character must be of length 1")


tests = {
    "BARE": string.ascii_letters + string.digits + "-_",
    "NUM": string.digits + "+-_.e",
    "SPACES": " \t",
    "NL": "\r\n",
    "WS": " \t\r\n",
    "SEP": "= \t",
}

for tk, tv in tests.items():

    def _(tv):
        @lru_cache(maxsize=None)
        def _(self):  # type: () -> bool
            return self in tv

        return _

    setattr(TOMLChar, tk, tv)
    setattr(TOMLChar, "is_{}".format(tk.lower()), _(tv))
