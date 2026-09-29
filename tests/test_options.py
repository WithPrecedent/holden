"""Tests for `holden.options`."""

from __future__ import annotations

import dataclasses
from typing import Any

import pytest

import holden
from holden import options


@dataclasses.dataclass
class CustomEdges(holden.Edges):
    """Edge list that is used in place of `Edges`."""


def test_get_base() -> None:
    """Tests `get_base`."""
    assert options.get_base('adjacency') is holden.Adjacency
    assert options.get_base('Edges') is holden.Edges
    assert options.get_base('matrix') is holden.Matrix
    assert options.get_base('parallel') is holden.Parallel
    assert options.get_base('serial') is holden.Serial
    with pytest.raises(KeyError, match = 'registered'):
        options.get_base('unknown')


def test_set_base() -> None:
    """Tests that `set_base` changes the class that `Forms` creates."""
    original = options._BASE_EDGES
    try:
        options.set_base('edges', CustomEdges)
        assert options._BASE_EDGES is CustomEdges
        assert options.get_base('edges') is CustomEdges
        result = holden.Forms.transform(
            holden.System.from_edges([('a', 'b')]), 'edges')
        assert type(result) is CustomEdges
        assert holden.System.from_edges([('a', 'b')]).edges.contents == [
            ('a', 'b')]
    finally:
        options.set_base('edges', original)
    assert type(holden.Forms.transform([('a', 'b')], 'adjacency')) is (
        holden.Adjacency)
    assert options._BASE_EDGES is holden.Edges


def test_set_base_validates() -> None:
    """Tests that `set_base` rejects invalid arguments."""
    with pytest.raises(KeyError, match = 'registered'):
        options.set_base('unknown', CustomEdges)
    bad: Any = dict
    with pytest.raises(TypeError, match = 'Composite'):
        options.set_base('edges', bad)
    assert options.get_base('edges') is holden.Edges
