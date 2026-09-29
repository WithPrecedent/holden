"""Tests for `holden.utilities`."""

from __future__ import annotations

import collections
import dataclasses
import pathlib

import pytest

from holden import utilities


@dataclasses.dataclass
class Named:
    """Class with a `name` attribute."""

    name: str = 'label'


class Plain:
    """Class without a `name` attribute."""


class CamelCase:
    """Class with a camel case name."""


def test_iterify() -> None:
    """Tests `_iterify`."""
    assert list(utilities._iterify(None)) == []
    assert list(utilities._iterify('abc')) == ['abc']
    assert list(utilities._iterify(b'abc')) == [b'abc']
    assert list(utilities._iterify([1, 2])) == [1, 2]
    assert list(utilities._iterify(5)) == [5]
    assert list(utilities._iterify({'a': 1})) == ['a']


def test_listify() -> None:
    """Tests `_listify`."""
    assert utilities._listify(None) == []
    assert utilities._listify('abc') == ['abc']
    assert utilities._listify(5) == [5]
    assert utilities._listify([1, 2]) == [1, 2]
    assert utilities._listify((1, 2)) == [1, 2]
    assert utilities._listify({1}) == [1]
    assert utilities._listify(frozenset({1})) == [1]
    assert utilities._listify(collections.deque([1, 2])) == [1, 2]
    original = [1, 2]
    assert utilities._listify(original) is not original


def test_namify() -> None:
    """Tests `_namify`."""
    assert utilities._namify('text') == 'text'
    assert utilities._namify(Named()) == 'label'
    assert utilities._namify(Named) == 'named'
    assert utilities._namify(Plain()) == 'plain'
    assert utilities._namify(CamelCase()) == 'camel_case'
    assert utilities._namify(Named(name = 'other')) == 'other'
    assert utilities._namify(utilities._snakify) == '_snakify'
    assert utilities._namify(3, default = 'x') == 'int'


def test_pathlibify(tmp_path: pathlib.Path) -> None:
    """Tests `_pathlibify`."""
    assert utilities._pathlibify(str(tmp_path)) == tmp_path
    assert utilities._pathlibify(tmp_path) is tmp_path
    with pytest.raises(TypeError):
        utilities._pathlibify(5)  # type: ignore[arg-type]


def test_rawify() -> None:
    """Tests `_rawify`."""
    class Stored:
        contents = [1, 2]

    class Labelled:
        contents = [[0]]
        labels = ['a']

    raw = {'a': set()}
    assert utilities._rawify(raw) is raw
    assert utilities._rawify('text') == 'text'
    assert utilities._rawify(5) == 5
    assert utilities._rawify(Stored()) == [1, 2]
    assert utilities._rawify(Labelled()) == ([[0]], ['a'])


def test_snakify() -> None:
    """Tests `_snakify`."""
    assert utilities._snakify('Adjacency') == 'adjacency'
    assert utilities._snakify('CamelCase') == 'camel_case'
    assert utilities._snakify('HTTPServer') == 'http_server'
    assert utilities._snakify('already_snake') == 'already_snake'


def test_stabilize() -> None:
    """Tests `_stabilize`."""
    assert utilities._stabilize({'b', 'a', 'c'}) == ['a', 'b', 'c']
    assert utilities._stabilize([3, 1, 2]) == [1, 2, 3]
    assert utilities._stabilize([]) == []


def test_typify() -> None:
    """Tests `_typify`."""
    assert utilities._typify('1') == 1
    assert utilities._typify('1.5') == 1.5
    assert utilities._typify('true') is True
    assert utilities._typify('Yes') is True
    assert utilities._typify('false') is False
    assert utilities._typify('no') is False
    assert utilities._typify('1, 2.5, yes, word') == [1, 2.5, True, 'word']
    assert utilities._typify('word') == 'word'
    assert utilities._typify(5) == 5
    assert utilities._typify(['a']) == ['a']


def test_windowify() -> None:
    """Tests `_windowify`."""
    assert list(utilities._windowify([1, 2, 3], 2)) == [(1, 2), (2, 3)]
    assert list(utilities._windowify([1, 2, 3], 3)) == [(1, 2, 3)]
    assert list(utilities._windowify([1, 2, 3, 4, 5], 2, step = 2)) == [
        (1, 2), (3, 4), (5, None)]
    assert list(utilities._windowify([1], 3, fill_value = 0)) == [(1, 0, 0)]
    assert list(utilities._windowify([1, 2], 0)) == [()]
    assert list(utilities._windowify([], 2)) == []
    with pytest.raises(ValueError, match = 'length'):
        list(utilities._windowify([1], -1))
    with pytest.raises(ValueError, match = 'step'):
        list(utilities._windowify([1], 1, step = 0))
