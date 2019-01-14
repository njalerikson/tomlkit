# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import math
import pickle
import pytest
from textwrap import dedent

from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta

# from tomlkit import inline_table
from tomlkit import loads, dumps, flatten, toml
from tomlkit._compat import PY2

# from tomlkit.exceptions import NonExistentKey
# from tomlkit.items import InlineTable
from tomlkit.items import Key, KeyType
from tomlkit.items import Bool
from tomlkit.items import String, StringType
from tomlkit.items import DateTime, Date, Time, Integer, Float
from tomlkit.items import Table, Array

# from tomlkit.items import item
# from tomlkit.parser import Parser


def test_key_comparison():
    k = Key("foo")

    assert k == Key("foo")
    assert k == "foo"
    assert k != "bar"
    assert k != 5


def test_items_can_be_appended_to_and_removed_from_a_table():
    content = "[table]"

    doc = loads(content)
    table = doc["table"]

    assert isinstance(table, Table)
    assert table.complexity is True
    assert flatten(table) == ""

    table["foo"] = String("bar", StringType.BASIC)

    assert flatten(table) == dedent(
        """\
        foo = "bar"
        """
    )

    table["baz"] = 34

    assert flatten(table) == dedent(
        """\
        foo = "bar"
        baz = 34
        """
    )

    table["baz"].comment = "Integer"

    assert flatten(table) == dedent(
        """\
        foo = "bar"
        baz = 34  # Integer
        """
    )

    del table["baz"]

    assert flatten(table) == dedent(
        """\
        foo = "bar"
        """
    )

    del table["foo"]

    assert flatten(table) == ""

    with pytest.raises(KeyError):
        del table["foo"]


def test_items_can_be_appended_to_and_removed_from_an_inline_table():
    content = "table = {}"

    doc = loads(content)
    table = doc["table"]

    assert isinstance(table, Table)
    assert table.complexity is False
    assert flatten(table) == "{}"

    table["foo"] = String("bar", StringType.BASIC)

    assert flatten(table) == '{foo = "bar"}'

    table["baz"] = 34

    assert flatten(table) == '{foo = "bar", baz = 34}'

    table["baz"].comment = "Integer"

    assert flatten(table) == dedent(
        """\
        foo = "bar"
        baz = 34  # Integer
        """
    )

    del table["baz"]

    assert flatten(table) == '{foo = "bar"}'

    del table["foo"]

    assert flatten(table) == "{}"

    with pytest.raises(KeyError):
        del table["foo"]


def test_inf_and_nan_are_supported(example):
    content = example("0.5.0")

    doc = loads(content)

    assert doc["sf1"] == float("inf")
    assert doc["sf2"] == float("inf")
    assert doc["sf3"] == float("-inf")

    assert math.isnan(doc["sf4"])
    assert math.isnan(doc["sf5"])
    assert math.isnan(doc["sf6"])


def test_hex_octal_and_bin_integers_are_supported(example):
    content = example("0.5.0")

    doc = loads(content)

    assert doc["hex1"] == 3735928559
    assert doc["hex2"] == 3735928559
    assert doc["hex3"] == 3735928559

    assert doc["oct1"] == 342391
    assert doc["oct2"] == 493

    assert doc["bin1"] == 214


def test_key_automatically_sets_proper_string_type_if_not_bare():
    key = Key("foo.bar")

    assert key._t == KeyType.BASIC


def test_array_behaves_like_a_list():
    doc = toml([1, 2], base=Array)

    assert doc == [1, 2]
    assert flatten(doc) == "[1, 2]"

    doc += [3, 4]
    assert doc == [1, 2, 3, 4]
    assert flatten(doc) == dedent(
        """\
        [
            1,
            2,
            3,
            4,
        ]"""
    )

    del doc[2]
    assert doc == [1, 2, 4]
    assert flatten(doc) == "[1, 2, 4]"

    del doc[-1]
    assert doc == [1, 2]
    assert flatten(doc) == "[1, 2]"

    del doc[-2]
    assert doc == [2]
    assert flatten(doc) == "[2]"

    if not PY2:
        doc.clear()
        assert doc == []
        assert flatten(doc) == "[]"

    content = "a = [1, 2] # Comment"

    doc = loads(content)

    assert doc["a"] == [1, 2]
    doc["a"] += [3, 4]
    assert doc["a"] == [1, 2, 3, 4]
    assert flatten(doc) == dedent(
        """\
        a = [
            1,
            2,
            3,
            4,
        ]  # Comment
        """
    )


def test_dicts_are_converted_to_tables():
    doc = toml({"foo": {"bar": "baz"}})

    assert flatten(doc) == dedent(
        """\
        foo = {bar = "baz"}
        """
    )

    doc["foo"].complexity = True

    assert flatten(doc) == dedent(
        """\
        [foo]
        bar = "baz"
        """
    )


def test_dicts_are_converted_to_tables_and_sorted():
    doc = toml({"foo": {"bar": "baz", "abc": 123, "baz": [{"c": 3, "b": 2, "a": 1}]}})

    assert flatten(doc) == dedent(
        """\
        foo = {bar = "baz", abc = 123, baz = [{c = 3, b = 2, a = 1}]}
        """
    )

    doc["foo"].complexity = True

    assert flatten(doc) == dedent(
        """\
        [foo]
        bar = "baz"
        abc = 123
        baz = [{c = 3, b = 2, a = 1}]
        """
    )

    doc["foo", "baz"].complexity = True

    assert flatten(doc) == dedent(
        """\
        [foo]
        bar = "baz"
        abc = 123

        [[foo.baz]]
        c = 3
        b = 2
        a = 1
        """
    )


def test_dicts_with_sub_dicts_are_properly_converted():
    doc = toml({"foo": {"bar": {"string": "baz"}, "int": 34, "float": 3.14}})

    assert flatten(doc) == dedent(
        """\
        foo = {bar = {string = "baz"}, int = 34, float = 3.14}
        """
    )

    doc["foo"].complexity = True

    assert flatten(doc) == dedent(
        """\
        [foo]
        bar = {string = "baz"}
        int = 34
        float = 3.14
        """
    )

    doc["foo", "bar"].complexity = True

    assert flatten(doc) == dedent(
        """\
        [foo]
        int = 34
        float = 3.14

        [foo.bar]
        string = "baz"
        """
    )


def test_item_array_of_dicts_converted_to_aot():
    doc = toml({"foo": [{"bar": "baz"}]})

    assert flatten(doc) == dedent(
        """\
        foo = [{bar = "baz"}]
        """
    )

    doc["foo"].complexity = True

    assert flatten(doc) == dedent(
        """\
        [[foo]]
        bar = "baz"
        """
    )


def test_integers_behave_like_ints():
    doc = toml({"i": 34})

    i = doc["i"]
    assert i == 34
    assert isinstance(i, int) and isinstance(i, Integer)

    ii = i + 1
    assert ii == 35
    assert isinstance(ii, int) and not isinstance(ii, Integer)

    i += 1
    assert i == 35
    assert isinstance(i, int) and not isinstance(i, Integer)

    i = doc["i"]
    ii = i - 1
    assert ii == 33
    assert isinstance(ii, int) and not isinstance(ii, Integer)

    i -= 1
    assert i == 33
    assert isinstance(i, int) and not isinstance(i, Integer)

    assert flatten(doc) == dedent(
        """\
        i = 34
        """
    )

    doc["i"] += 1
    assert doc["i"] == 35
    assert flatten(doc) == dedent(
        """\
        i = 35
        """
    )

    doc["i"] -= 2
    assert doc["i"] == 33
    assert flatten(doc) == dedent(
        """\
        i = 33
        """
    )


def test_floats_behave_like_floats():
    doc = toml({"f": 34.12})

    f = doc["f"]
    assert f == 34.12
    assert isinstance(f, float) and isinstance(f, Float)

    ff = f + 1
    assert ff == 35.12
    assert isinstance(ff, float) and not isinstance(ff, Float)

    f += 1
    assert f == 35.12
    assert isinstance(f, float) and not isinstance(f, Float)

    f = doc["f"]
    ff = f - 1
    assert ff == 33.12
    assert isinstance(ff, float) and not isinstance(ff, Float)

    f -= 1
    assert f == 33.12
    assert isinstance(f, float) and not isinstance(f, Float)

    assert flatten(doc) == dedent(
        """\
        f = 34.12
        """
    )

    doc["f"] += 1
    assert doc["f"] == 35.12
    assert flatten(doc) == dedent(
        """\
        f = 35.12
        """
    )

    doc["f"] -= 2
    assert doc["f"] == 33.12
    assert flatten(doc) == dedent(
        """\
        f = 33.12
        """
    )


def test_datetimes_behave_like_datetimes():
    doc = toml({"dt": datetime(2018, 7, 22, 12, 34, 56)})

    d = doc["dt"]
    assert d == datetime(2018, 7, 22, 12, 34, 56)
    assert isinstance(d, datetime) and isinstance(d, DateTime)

    dd = d + timedelta(days=1)
    assert dd == datetime(2018, 7, 23, 12, 34, 56)
    assert isinstance(dd, datetime) and not isinstance(dd, DateTime)

    d += timedelta(days=1)
    assert d == datetime(2018, 7, 23, 12, 34, 56)
    assert isinstance(d, datetime) and not isinstance(d, DateTime)

    dd = d - timedelta(days=2)
    assert dd == datetime(2018, 7, 21, 12, 34, 56)
    assert isinstance(dd, datetime) and not isinstance(dd, DateTime)

    d -= timedelta(days=2)
    assert d == datetime(2018, 7, 21, 12, 34, 56)
    assert isinstance(d, datetime) and not isinstance(d, DateTime)

    assert flatten(doc) == dedent(
        """\
        dt = 2018-07-22 12:34:56
        """
    )

    doc["dt"] += timedelta(days=1)
    assert doc["dt"] == datetime(2018, 7, 23, 12, 34, 56)
    assert flatten(doc) == dedent(
        """\
        dt = 2018-07-23 12:34:56
        """
    )

    doc["dt"] -= timedelta(days=2)
    assert doc["dt"] == datetime(2018, 7, 21, 12, 34, 56)
    assert flatten(doc) == dedent(
        """\
        dt = 2018-07-21 12:34:56
        """
    )


def test_dates_behave_like_dates():
    doc = toml({"d": date(2018, 7, 22)})

    d = doc["d"]
    assert d == date(2018, 7, 22)
    assert isinstance(d, date) and isinstance(d, Date)

    dd = d + timedelta(days=1)
    assert dd == date(2018, 7, 23)
    assert isinstance(dd, date) and not isinstance(dd, Date)

    d += timedelta(days=1)
    assert d == date(2018, 7, 23)
    assert isinstance(d, date) and not isinstance(d, Date)

    dd = d - timedelta(days=2)
    assert dd == date(2018, 7, 21)
    assert isinstance(dd, date) and not isinstance(dd, Date)

    d -= timedelta(days=2)
    assert d == date(2018, 7, 21)
    assert isinstance(d, date) and not isinstance(d, Date)

    assert flatten(doc) == dedent(
        """\
        d = 2018-07-22
        """
    )

    doc["d"] += timedelta(days=1)
    assert doc["d"] == datetime(2018, 7, 23)
    assert flatten(doc) == dedent(
        """\
        d = 2018-07-23
        """
    )

    doc["d"] -= timedelta(days=2)
    assert doc["d"] == date(2018, 7, 21)
    assert flatten(doc) == dedent(
        """\
        d = 2018-07-21
        """
    )


def test_times_behave_like_times():
    doc = toml({"t": time(12, 34, 56)})

    t = doc["t"]
    assert t == time(12, 34, 56)
    assert flatten(t) == "12:34:56"

    assert flatten(doc) == dedent(
        """\
        t = 12:34:56
        """
    )


def test_strings_behave_like_strs():
    doc = toml({"s": "foo"})

    s = doc["s"]
    assert s == "foo"
    assert isinstance(s, str) and isinstance(s, String)

    ss = s + " bar"
    assert ss == "foo bar"
    assert isinstance(ss, str) and not isinstance(ss, String)

    s += " bar"
    assert s == "foo bar"
    assert isinstance(s, str) and not isinstance(s, String)

    assert flatten(doc) == dedent(
        """\
        s = "foo"
        """
    )

    doc["s"] += " bar"
    assert doc["s"] == "foo bar"
    assert flatten(doc) == dedent(
        """\
        s = "foo bar"
        """
    )

    doc["s"] += " é"
    assert doc["s"] == "foo bar é"
    assert flatten(doc) == dedent(
        """\
        s = "foo bar é"
        """
    )


def test_tables_behave_like_dicts():
    doc = toml({"foo": "bar"})

    assert flatten(doc) == dedent(
        """\
        foo = "bar"
        """
    )

    doc.update({"bar": "baz"})

    assert flatten(doc) == dedent(
        """\
        foo = "bar"
        bar = "baz"
        """
    )

    doc.update({"bar": "boom"})

    assert flatten(doc) == dedent(
        """\
        foo = "bar"
        bar = "boom"
        """
    )


def test_items_are_pickable():
    n = Integer(12)

    s = pickle.dumps(n)
    assert flatten(pickle.loads(s)) == "12"

    n = Float(12.34)

    s = pickle.dumps(n)
    assert flatten(pickle.loads(s)) == "12.34"

    n = Bool(True)

    s = pickle.dumps(n)
    assert flatten(pickle.loads(s)) == "true"

    n = DateTime(datetime(2018, 10, 11, 12, 34, 56, 123456))

    s = pickle.dumps(n)
    assert flatten(pickle.loads(s)) == "2018-10-11 12:34:56.123456"

    n = Date(date(2018, 10, 11))

    s = pickle.dumps(n)
    assert flatten(pickle.loads(s)) == "2018-10-11"

    n = Time(time(12, 34, 56, 123456))

    s = pickle.dumps(n)
    assert flatten(pickle.loads(s)) == "12:34:56.123456"

    n = Array([1, 2, 3])

    s = pickle.dumps(n)
    assert flatten(pickle.loads(s)) == "[1, 2, 3]"

    n = Table({"foo": "bar"})

    s = pickle.dumps(n)
    assert flatten(pickle.loads(s)) == dedent(
        """\
        foo = "bar"
        """
    )

    n = Table()
    n["foo"] = {"bar": "baz"}

    s = pickle.dumps(n)
    assert flatten(pickle.loads(s)) == dedent(
        """\
        foo = {bar = "baz"}
        """
    )

    n = String("foo")

    s = pickle.dumps(n)
    assert flatten(pickle.loads(s)) == '"foo"'

    n = Table()
    n["foo"] = [{"bar": "baz"}]

    s = pickle.dumps(n)
    assert flatten(pickle.loads(s)) == dedent(
        """\
        foo = [{bar = "baz"}]
        """
    )


# def test_trim_comments_when_building_inline_table():
#     table = inline_table()
#     row = parse('foo = "bar"  # Comment')
#     table.update(row)
#     assert flatten(table) == '{foo = "bar"}'
#     value = item("foobaz")
#     value.comment("Another comment")
#     table.append("baz", value)
#     assert "# Another comment" not in flatten(table)
