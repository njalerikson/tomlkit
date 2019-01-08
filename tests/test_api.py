import json
import pytest
from textwrap import dedent

from datetime import date
from datetime import datetime
from datetime import time

from tomlkit import dumps, loads, flatten, toml
from tomlkit import parsers
from tomlkit.exceptions import MixedArrayTypesError
from tomlkit.exceptions import UnexpectedCharError
from tomlkit.exceptions import InvalidCharInStringError
from tomlkit.items import Array
from tomlkit.items import Bool
from tomlkit.items import Date
from tomlkit.items import DateTime
from tomlkit.items import Float
from tomlkit.items import Integer
from tomlkit.items import Key
from tomlkit.items import Table
from tomlkit.items import Time


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date, time)):
        return obj.isoformat()

    raise TypeError("Type {} not serializable".format(type(obj)))


@pytest.mark.parametrize(
    "example_name",
    [
        "example",
        "fruit",
        "hard",
        "sections_with_same_start",
        "pyproject",
        "0.5.0",
        "test",
        "newline_in_strings",
        "preserve_quotes_in_string",
        "string_slash_whitespace_newline",
    ],
)
def test_parse_can_parse_valid_toml_files(example, example_name):
    assert isinstance(loads(example(example_name)), Table)


@pytest.mark.parametrize("example_name", ["0.5.0", "pyproject"])
def test_parsed_document_are_properly_json_representable(
    example, json_example, example_name
):
    doc = json.loads(json.dumps(loads(example(example_name)), default=json_serial))
    json_doc = json.loads(json_example(example_name))

    assert doc == json_doc


@pytest.mark.parametrize(
    "example_name,error",
    [
        ("section_with_trailing_characters", UnexpectedCharError),
        ("key_value_with_trailing_chars", UnexpectedCharError),
        ("array_with_invalid_chars", UnexpectedCharError),
        ("mixed_array_types", MixedArrayTypesError),
        ("invalid_number", UnexpectedCharError),
        ("invalid_date", UnexpectedCharError),
        ("invalid_time", UnexpectedCharError),
        ("invalid_datetime", UnexpectedCharError),
        ("trailing_comma", UnexpectedCharError),
        ("newline_in_singleline_string", InvalidCharInStringError),
        ("string_slash_whitespace_char", InvalidCharInStringError),
        ("array_no_comma", UnexpectedCharError),
        ("array_duplicate_comma", UnexpectedCharError),
        ("array_leading_comma", UnexpectedCharError),
        ("inline_table_no_comma", UnexpectedCharError),
        ("inline_table_duplicate_comma", UnexpectedCharError),
        ("inline_table_leading_comma", UnexpectedCharError),
        ("inline_table_trailing_comma", UnexpectedCharError),
    ],
)
def test_parse_raises_errors_for_invalid_toml_files(
    invalid_example, error, example_name
):
    with pytest.raises(error):
        loads(invalid_example(example_name))


@pytest.mark.parametrize(
    "example_name",
    [
        "example",
        "fruit",
        "hard",
        "sections_with_same_start",
        "pyproject",
        "0.5.0",
        "test",
    ],
)
def test_original_string_and_dumped_string_are_equal(example, example_name):
    content = example(example_name)
    parsed = loads(content)

    assert content == dumps(parsed)


def test_a_raw_dict_can_be_dumped():
    s = dumps({"foo": "bar"})

    assert s == dedent(
        """\
        foo = "bar"
        """
    )


def test_integer():
    i = parsers.numdate.parse("34")

    assert isinstance(i, Integer)


def test_float():
    f = parsers.numdate.parse("34.56")

    assert isinstance(f, Float)


def test_boolean():
    b = parsers.boolean.parse("true")

    assert isinstance(b, Bool)


def test_date():
    dt = parsers.numdate.parse("1979-05-13")

    assert isinstance(dt, Date)


def test_time():
    dt = parsers.numdate.parse("12:34:56")

    assert isinstance(dt, Time)


def test_datetime():
    dt = parsers.numdate.parse("1979-05-13T12:34:56")

    assert isinstance(dt, DateTime)


def test_array():
    a = parsers.array.parse("[1,2, 3]")

    assert isinstance(a, Array)


def test_table():
    t = parsers.table.parse(
        dedent(
            """\
        a = 1
        b = 2
        """
        )
    )

    assert isinstance(t, Table)

    t = parsers.table.parse(
        dedent(
            """\
        a = 1
        b = 2

        [foo]
        c = 3
        """
        )
    )

    assert isinstance(t, Table)


def test_inline_table():
    t = parsers.inlinetable.parse("{a = 1, b = 2}")

    assert isinstance(t, Table)


def test_aot():
    t = parsers.table.parse(
        dedent(
            """\
        [[foo]]
        a = 1

        [[foo]]
        b = 2

        [[foo]]
        c = 3
        """
        )
    )

    assert isinstance(t, Table)
    assert isinstance(t["foo"], Array)
    assert t["foo"].type == Table


def test_key():
    k = parsers.key.parse("foo")

    assert isinstance(k, Key)

    ks = parsers.keys.parse("foo.bar.baz =")

    assert isinstance(ks, tuple)
    assert all(isinstance(k, Key) for k in ks)


def test_string():
    s = parsers.string.parse("'foo \"'")

    assert s == 'foo "'
    assert flatten(s) == "'foo \\\"'"

    s = parsers.string.parse('"foo \'"')

    assert s == "foo '"
    assert flatten(s) == '"foo \\\'"'


def test_item_dict_to_table():
    t = toml({"foo": {"bar": "baz"}})

    assert t == {"foo": {"bar": "baz"}}

    assert flatten(t) == dedent(
        """\
        foo = {bar = "baz"}
        """
    )
    t["foo"].complexity = True
    assert flatten(t) == dedent(
        """\
        [foo]
        bar = "baz"
        """
    )
