# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from textwrap import dedent

from tomlkit import toml, flatten, loads
from tomlkit.items import String
from tomlkit._utils import _utc


def test_build_example(example):
    content = example("example")

    doc = toml()
    doc.comments.append("This is a TOML document. Boom.")
    doc["title"] = "TOML Example"

    owner = doc.setdefault("owner", {})
    owner["name"] = "Tom Preston-Werner"
    owner["organization"] = "GitHub"
    owner["bio"] = String(
        "GitHub Cofounder & CEO\nLikes tater tots and beer.", multi=False
    )
    owner["dob"] = datetime.datetime(1979, 5, 27, 7, 32, tzinfo=_utc)
    owner["dob"].comment = "First class dates? Why not?"

    database = doc.setdefault("database", {})
    database["server"] = "192.168.1.1"
    database["ports"] = [8001, 8001, 8002]
    database["connection_max"] = 5000
    database["enabled"] = True

    servers = doc.setdefault("servers", {})
    servers.explicit = True  # force the empty table to display

    alpha = servers.setdefault("alpha", {})
    alpha.head_comments.append(
        "You can indent as you please. Tabs or spaces. TOML don't care."
    )
    alpha.complexity = True  # force Table
    alpha["ip"] = "10.0.0.1"
    alpha["dc"] = "eqdc10"

    beta = servers.setdefault("beta", {})
    beta.complexity = True  # force Table
    beta["ip"] = "10.0.0.2"
    beta["dc"] = "eqdc10"
    beta["country"] = "中国"
    beta["country"].comment = "This should be parsed as UTF-8"

    clients = doc.setdefault("clients", {})
    clients["data"] = [["gamma", "delta"], [1, 2]]
    clients["data"].comment = "just an update to make sure parsers support it"
    clients.comments.append("Line breaks are OK when inside arrays")
    clients["hosts"] = ["alpha", "omega"]

    product = doc.setdefault("products", [])
    product.complexity = True  # force AoT

    product.append({})
    product[0].head_comments.append("Products")
    product[0, "name"] = "Hammer"
    product[0, "sku"] = 738594937

    product.append({})
    product[1, "name"] = "Nail"
    product[1, "sku"] = 284758393
    product[1, "color"] = "gray"

    assert flatten(doc) == content


def test_add_remove():
    content = ""

    doc = loads(content)
    doc["foo"] = "bar"

    assert flatten(doc) == dedent(
        """\
        foo = "bar"
        """
    )

    del doc["foo"]

    assert flatten(doc) == ""


def test_append_table_after_multiple_indices():
    content = """
    [packages]
    foo = "*"

    [settings]
    enable = false

    [packages.bar]
    version = "*"
    """

    doc = loads(content)
    doc["foobar"] = {"name": "John"}
