# -*- coding: utf-8 -*-
from .items import flatten, pyobj, toml
from .parsers import loads


def dumps(obj, *, base=None):
    # ensure data is valid according to base
    data = toml(obj, base=base)

    # flatten data into string
    return flatten(data)


def dump(obj, fp, *, base=None):
    # dump obj to string
    s = dumps(obj, base=base)

    # write to file pointer
    fp.write(s)


def load(fp, *, base=None):
    # read from file pointer
    s = fp.read()

    # load obj from string
    return loads(s, base=base)
