# -*- coding: utf-8 -*-


# flatten TOML object into a string
def flatten(data):
    return "\n".join(data.__flatten__())


# convert TOML object into Python object
def pyobj(data):
    return data.__pyobj__()
