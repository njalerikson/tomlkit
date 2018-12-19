# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest
import datetime as dt
import time
import math

from tomlkit.items import Bool, BoolParser
from tomlkit.items import String, StringParser, StringType
from tomlkit.items import DateTime, Date, Time, Integer, Float, NumDateParser
from tomlkit.items import toml
from tomlkit.exceptions import UnexpectedCharError, LeadingZeroError


def test_bool_obj():
    btrue = Bool(True)
    bfalse = Bool(False)

    assert isinstance(btrue, Bool)
    assert isinstance(btrue, Bool)
    assert issubclass(bool, int) == issubclass(Bool, int)

    assert btrue
    assert not bfalse

    assert Bool(btrue) is btrue
    assert Bool(bfalse) is bfalse
    assert True is bool(btrue)
    assert False is bool(bfalse)

    with pytest.raises(TypeError):
        Bool("string")
    with pytest.raises(TypeError):
        Bool(dt.datetime.now())
    with pytest.raises(TypeError):
        Bool(dt.date.today())
    with pytest.raises(TypeError):
        Bool(dt.datetime.now().time())
    with pytest.raises(TypeError):
        Bool(12)
    with pytest.raises(TypeError):
        Bool(12.34)
    with pytest.raises(TypeError):
        Bool([])
    with pytest.raises(TypeError):
        Bool(())
    with pytest.raises(TypeError):
        Bool({})

    assert toml(btrue) == "true"
    assert toml(bfalse) == "false"


def test_bool_parser():
    parent = {}
    key = "test"
    assert BoolParser.parse("true", parent=parent, key=key) == Bool(True)
    assert parent[key] == Bool(True)

    parent = {}
    key = "test"
    assert BoolParser.parse("false", parent=parent, key=key) == Bool(False)
    assert parent[key] == Bool(False)


def test_string_obj():
    string = String("hello world")

    assert isinstance(string, String)
    assert issubclass(String, str)

    assert string
    assert not String("")

    assert String(string) is string
    assert string == "hello world"

    with pytest.raises(TypeError):
        String(True)
    with pytest.raises(TypeError):
        String(dt.datetime.now())
    with pytest.raises(TypeError):
        String(dt.date.today())
    with pytest.raises(TypeError):
        String(dt.datetime.now().time())
    with pytest.raises(TypeError):
        String(12)
    with pytest.raises(TypeError):
        String(12.34)
    with pytest.raises(TypeError):
        String([])
    with pytest.raises(TypeError):
        String(())
    with pytest.raises(TypeError):
        String({})

    assert string[0] == "h"
    assert string[6] == "w"
    assert string[-1] == "d"
    assert string[-7] == "o"

    assert string[:5] == "hello"
    assert string[6:] == "world"

    assert toml(string) == '"hello world"'


def test_string_parser():
    parent = {}
    key = "test"
    value = String("hello world", StringType.BASIC)
    assert StringParser.parse('"hello world"', parent=parent, key=key) == value
    assert parent[key] == value
    assert parent[key]._t == value._t

    parent = {}
    key = "test"
    value = String("hello world", StringType.LITERAL)
    assert StringParser.parse("'hello world'", parent=parent, key=key) == value
    assert parent[key] == value
    assert parent[key]._t == value._t


def test_datetime_obj():
    stmp = dt.datetime.now()
    obj = DateTime(stmp)

    assert isinstance(obj, DateTime)
    assert issubclass(DateTime, dt.datetime)

    assert DateTime(obj) is obj
    assert obj == stmp

    with pytest.raises(TypeError):
        DateTime(True)
    with pytest.raises(TypeError):
        DateTime("hello")
    with pytest.raises(TypeError):
        DateTime(dt.date.today())
    with pytest.raises(TypeError):
        DateTime(dt.datetime.now().time())
    with pytest.raises(TypeError):
        DateTime(12)
    with pytest.raises(TypeError):
        DateTime(12.34)
    with pytest.raises(TypeError):
        DateTime([])
    with pytest.raises(TypeError):
        DateTime(())
    with pytest.raises(TypeError):
        DateTime({})

    assert toml(obj) == stmp.isoformat(sep=" ")

    assert obj.date() == stmp.date()
    assert obj.time() == stmp.time()

    stmp = time.time()
    assert DateTime.fromtimestamp(stmp) == dt.datetime.fromtimestamp(stmp)
    assert DateTime.utcfromtimestamp(stmp) == dt.datetime.utcfromtimestamp(stmp)
    assert DateTime.now()
    assert DateTime.utcnow()
    stmp = (dt.date.today(), dt.datetime.now().time())
    assert DateTime.combine(*stmp) == dt.datetime.combine(*stmp)
    stmp = 737046
    assert DateTime.fromordinal(stmp) == dt.datetime.fromordinal(stmp)
    stmp = "2018-12-18T09:32:27.029614"
    assert DateTime.fromisoformat(stmp) == dt.datetime.fromisoformat(stmp)

    obj = DateTime.now()
    assert obj.replace(year=2000).year == 2000
    assert obj.replace(month=6).month == 6
    assert obj.replace(day=15).day == 15
    assert obj.replace(hour=8).hour == 8
    assert obj.replace(minute=25).minute == 25
    assert obj.replace(second=38).second == 38
    assert obj.replace(microsecond=38).microsecond == 38
    assert obj.replace(tzinfo=dt.timezone.utc).tzinfo == dt.timezone.utc
    assert obj.replace(fold=1).fold == 1


def test_date_obj():
    stmp = dt.date.today()
    obj = Date(stmp)

    assert isinstance(obj, Date)
    assert issubclass(Date, dt.date)

    assert Date(obj) is obj
    assert obj == stmp

    with pytest.raises(TypeError):
        Date(True)
    with pytest.raises(TypeError):
        Date("hello")
    # with pytest.raises(TypeError):
    #     Date(dt.datetime.now())
    with pytest.raises(TypeError):
        Date(dt.datetime.now().time())
    with pytest.raises(TypeError):
        Date(12)
    with pytest.raises(TypeError):
        Date(12.34)
    with pytest.raises(TypeError):
        Date([])
    with pytest.raises(TypeError):
        Date(())
    with pytest.raises(TypeError):
        Date({})

    assert toml(obj) == stmp.isoformat()

    stmp = time.time()
    assert Date.fromtimestamp(stmp) == dt.date.fromtimestamp(stmp)
    assert Date.today()
    stmp = 737046
    assert Date.fromordinal(stmp) == dt.date.fromordinal(stmp)
    stmp = "2018-12-18"
    assert Date.fromisoformat(stmp) == dt.date.fromisoformat(stmp)

    obj = Date.today()
    assert obj.replace(year=2000).year == 2000
    assert obj.replace(month=6).month == 6
    assert obj.replace(day=15).day == 15


def test_time_obj():
    stmp = dt.datetime.now().time()
    obj = Time(stmp)

    assert isinstance(obj, Time)
    assert issubclass(Time, dt.time)

    assert Time(obj) is obj
    assert obj == stmp

    with pytest.raises(TypeError):
        Time(True)
    with pytest.raises(TypeError):
        Time("hello")
    with pytest.raises(TypeError):
        Time(dt.datetime.now())
    with pytest.raises(TypeError):
        Time(dt.date.today())
    with pytest.raises(TypeError):
        Time(12)
    with pytest.raises(TypeError):
        Time(12.34)
    with pytest.raises(TypeError):
        Time([])
    with pytest.raises(TypeError):
        Time(())
    with pytest.raises(TypeError):
        Time({})

    assert toml(obj) == stmp.isoformat()

    stmp = "09:32:27.029614"
    assert Time.fromisoformat(stmp) == dt.time.fromisoformat(stmp)

    obj = Time(dt.datetime.now().time())
    assert obj.replace(hour=8).hour == 8
    assert obj.replace(minute=25).minute == 25
    assert obj.replace(second=38).second == 38
    assert obj.replace(microsecond=38).microsecond == 38
    assert obj.replace(tzinfo=dt.timezone.utc).tzinfo == dt.timezone.utc
    assert obj.replace(fold=1).fold == 1


def test_integer_obj():
    integer = Integer(12)

    assert isinstance(integer, Integer)

    assert Integer(integer) is integer

    # with pytest.raises(TypeError):
    #     Integer(True)
    with pytest.raises(TypeError):
        Integer("hllo.world")
    with pytest.raises(TypeError):
        Integer("hlloeworld")
    with pytest.raises(ValueError):
        Integer("hllo world")
    with pytest.raises(TypeError):
        Integer(dt.datetime.now())
    with pytest.raises(TypeError):
        Integer(dt.date.today())
    with pytest.raises(TypeError):
        Integer(dt.datetime.now().time())
    with pytest.raises(TypeError):
        Integer(12.34)
    with pytest.raises(TypeError):
        Integer([])
    with pytest.raises(TypeError):
        Integer(())
    with pytest.raises(TypeError):
        Integer({})

    assert integer == 12

    assert issubclass(Integer, int)

    assert toml(integer) == "12"
    assert toml(Integer(12345, ksep=True)) == "12_345"


def test_float_obj():
    flt = Float(12.34)

    assert isinstance(flt, Float)

    assert Float(flt) is flt

    with pytest.raises(TypeError):
        Float(True)
    with pytest.raises(ValueError):
        Float("hllo.world")
    with pytest.raises(ValueError):
        Float("hlloeworld")
    with pytest.raises(TypeError):
        Float("hllo world")
    with pytest.raises(TypeError):
        Float(dt.datetime.now())
    with pytest.raises(TypeError):
        Float(dt.date.today())
    with pytest.raises(TypeError):
        Float(dt.datetime.now().time())
    with pytest.raises(TypeError):
        Float(12)
    with pytest.raises(TypeError):
        Float([])
    with pytest.raises(TypeError):
        Float(())
    with pytest.raises(TypeError):
        Float({})

    assert flt == 12.34

    assert issubclass(Float, float)

    assert toml(flt) == "12.34"
    assert toml(Float(12345.67, ksep=True)) == "12_345.67"


def test_datetime_parser():
    for raw, stmp in [
        (
            "2018-12-18T09:32:27.029614",
            dt.datetime.fromisoformat("2018-12-18T09:32:27.029614"),
        ),
        (
            "2018-12-18T22:32:27.029614",
            dt.datetime.fromisoformat("2018-12-18T22:32:27.029614"),
        ),
        (
            "2018-12-18T09:32:27.029614Z",
            dt.datetime.fromisoformat("2018-12-18T09:32:27.029614-00:00"),
        ),
        (
            "2018-12-18T09:32:27.029614-06:30",
            dt.datetime.fromisoformat("2018-12-18T09:32:27.029614-06:30"),
        ),
        (
            "2018-12-18T09:32:27.029614-23:30",
            dt.datetime.fromisoformat("2018-12-18T09:32:27.029614-23:30"),
        ),
    ]:
        parent = {}
        key = "test"
        obj = DateTime(stmp)
        assert NumDateParser.parse(raw, parent=parent, key=key) == obj
        assert parent[key] == obj

    for raw in [
        "2018-12-18T09:32:27.029614-33:30",
        "2018-12-18T09:32:27.029614-06:99",
        "2018-12-18T43:32:27.029614",
    ]:
        with pytest.raises(UnexpectedCharError):
            NumDateParser.parse(raw, parent={}, key="test")


def test_date_parser():
    for raw in ["2018-12-18", "2018-06-18", "2018-12-08", "2018-12-30"]:
        parent = {}
        key = "test"
        stmp = dt.date.fromisoformat(raw)
        obj = Date(stmp)
        assert NumDateParser.parse(raw, parent=parent, key=key) == obj
        assert parent[key] == obj

    for raw in ["2018-22-18", "2018-12-33", "2018-12-41"]:
        with pytest.raises(UnexpectedCharError):
            NumDateParser.parse(raw, parent={}, key="test")


def test_time_parser():
    for raw in ["09:32:27.029614", "22:32:27.029614"]:
        parent = {}
        key = "test"
        stmp = dt.time.fromisoformat(raw)
        obj = Time(stmp)
        assert NumDateParser.parse(raw, parent=parent, key=key) == obj
        assert parent[key] == obj

    for raw in [
        "42:32:27.029614",
        "22:72:27.029614",
        "222:72:27.029614",
        "22:32:60.029614",
    ]:
        with pytest.raises(UnexpectedCharError):
            NumDateParser.parse(raw, parent={}, key="test")


def test_integer_parser():
    for raw in ["12", "+12", "-12", "1234", "1_234", "1_2_3_4"]:
        parent = {}
        key = "test"
        obj = Integer(raw)
        assert NumDateParser.parse(raw, parent=parent, key=key) == obj
        assert parent[key] == obj

    for raw, exc in [("nonint", UnexpectedCharError), ("01", LeadingZeroError)]:
        with pytest.raises(exc):
            NumDateParser.parse(raw, parent={}, key="test")


def test_float_parser():
    for raw in [
        "12.34",
        "+12.34",
        "-12.34",
        "12e34",
        "12e+34",
        "12e-34",
        "+12e34",
        "+12e+34",
        "+12e-34",
        "-12e34",
        "-12e+34",
        "-12e-34",
        "1234.56",
        "1_234.56",
        "1_2_3_4.5_6",
    ]:
        parent = {}
        key = "test"
        obj = Float(raw)
        assert NumDateParser.parse(raw, parent=parent, key=key) == obj
        assert parent[key] == obj

    math.isinf(NumDateParser.parse("inf", parent={}, key="test"))
    math.isnan(NumDateParser.parse("nan", parent={}, key="test"))

    for raw, exc in [("nonfloat", UnexpectedCharError), ("01.23", LeadingZeroError)]:
        with pytest.raises(exc):
            NumDateParser.parse(raw, parent={}, key="test")
