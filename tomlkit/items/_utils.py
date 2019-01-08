# -*- coding: utf-8 -*-


# converts TOML object (use as is) into TOML document (str)
def flatten(data):
    return "\n".join(data.__flatten__())


# converts TOML object into Python object
def pyobj(data):
    return data.__pyobj__()
