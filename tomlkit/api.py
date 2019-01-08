# -*- coding: utf-8 -*-
from .items import toml, pyobj, flatten, dumps
from .parsers import loads, parse


# reads TOML document (str) from filehandle, uses loads
def load(fp, *, base=None):
    # read from file pointer
    s = fp.read()

    # load obj from string
    return loads(s, base=base)


# uses dumps, writes TOML document (str) to filehandle
def dump(obj, fp, *, base=None):
    # dump obj to string
    s = dumps(obj, base=base)

    # write to file pointer
    fp.write(s)
