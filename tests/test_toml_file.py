import io
import os

from tomlkit import load, dump
from tomlkit import items


def test_toml_file(example):
    original_content = example("example")

    toml_file = os.path.join(os.path.dirname(__file__), "examples", "example.toml")
    with open(toml_file) as fh:
        content = load(fh)

    assert isinstance(content, items.table)
    assert content["owner"]["organization"] == "GitHub"

    with open(toml_file, "w") as fh:
        dump(content, fh)

    try:
        with io.open(toml_file, encoding="utf-8") as fh:
            assert original_content == fh.read()
    finally:
        with io.open(toml_file, "w", encoding="utf-8") as fh:
            assert fh.write(original_content)
