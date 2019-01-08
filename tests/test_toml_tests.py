import json
import pytest
from datetime import datetime

from tomlkit import loads, flatten
from tomlkit._compat import decode
from tomlkit._compat import unicode

# from tomlkit._utils import parse_rfc3339
from tomlkit.exceptions import ParseErrorMixin


def to_bool(s):
    assert s in ["true", "false"]

    return s == "true"


stypes = {
    "string": unicode,
    "bool": to_bool,
    "integer": int,
    "float": float,
    "datetime": datetime.fromisoformat,
}


def untag(value):
    if isinstance(value, list):
        return [untag(i) for i in value]
    elif "type" in value and "value" in value and len(value) == 2:
        if value["type"] in stypes:
            val = decode(value["value"])

            return stypes[value["type"]](val)
        elif value["type"] == "array":
            return [untag(i) for i in value["value"]]
        else:
            raise Exception("Unsupported type {}".format(value["type"]))
    else:
        return {k: untag(v) for k, v in value.items()}


def test_valid_decode(valid_case):
    json_val = untag(json.loads(valid_case["json"]))
    toml_val = loads(valid_case["toml"])

    assert toml_val == json_val
    # assert flatten(toml_val) == valid_case["toml"]


def test_invalid_decode(invalid_decode_case):
    with pytest.raises(ParseErrorMixin):
        loads(invalid_decode_case["toml"])
