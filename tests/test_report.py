"""Tests for `holden.report`."""

from __future__ import annotations

import pytest

import holden
from holden import report


def test_adjacency(adjacency: dict[str, set[str]]) -> None:
    """Tests `get_roots_adjacency` and `get_endpoints_adjacency`."""
    assert report.get_roots_adjacency(adjacency) == ['a', 'c']
    assert report.get_endpoints_adjacency(adjacency) == ['b', 'e']
    assert report.get_roots_adjacency({}) == []
    assert report.get_endpoints_adjacency({}) == []
    system = holden.System(adjacency)
    assert report.get_roots_adjacency(system) == ['a', 'c']
    assert report.get_endpoints_adjacency(system) == ['b', 'e']


def test_adjacency_special_cases() -> None:
    """Tests isolated nodes, cycles, and nodes that are not keys."""
    assert report.get_roots_adjacency({'a': set()}) == ['a']
    assert report.get_endpoints_adjacency({'a': set()}) == ['a']
    assert report.get_roots_adjacency({'a': {'b'}, 'b': {'a'}}) == []
    assert report.get_endpoints_adjacency({'a': {'b'}, 'b': {'a'}}) == []
    unlisted = {'a': {'b', 'c'}}
    assert report.get_roots_adjacency(unlisted) == ['a']
    assert report.get_endpoints_adjacency(unlisted) == ['b', 'c']


def test_edges(edges: list[tuple[str, str]]) -> None:
    """Tests `get_roots_edges` and `get_endpoints_edges`."""
    assert report.get_roots_edges(edges) == ['a', 'c']
    assert report.get_endpoints_edges(edges) == ['b', 'e']
    assert report.get_roots_edges([]) == []
    assert report.get_roots_edges(holden.Edges(edges)) == ['a', 'c']


def test_matrix(matrix: tuple[list[list[int]], list[str]]) -> None:
    """Tests `get_roots_matrix` and `get_endpoints_matrix`."""
    assert report.get_roots_matrix(matrix) == ['a', 'c']
    assert report.get_endpoints_matrix(matrix) == ['b', 'e']
    assert report.get_roots_matrix(
        holden.Matrix(matrix[0], matrix[1])) == ['a', 'c']


def test_parallel() -> None:
    """Tests `get_roots_parallel` and `get_endpoints_parallel`."""
    paths = [['a', 'b'], ['a', 'd', 'e'], ['c', 'd', 'e']]
    assert report.get_roots_parallel(paths) == ['a', 'c']
    assert report.get_endpoints_parallel(paths) == ['b', 'e']
    assert report.get_roots_parallel([]) == []
    assert report.get_endpoints_parallel([[], ['a']]) == ['a']
    assert report.get_roots_parallel(holden.Parallel(paths)) == ['a', 'c']
    assert report.get_roots_parallel([holden.Serial(['x', 'y'])]) == ['x']


def test_serial() -> None:
    """Tests `get_roots_serial` and `get_endpoints_serial`."""
    assert report.get_roots_serial(['a', 'b', 'c']) == ['a']
    assert report.get_endpoints_serial(['a', 'b', 'c']) == ['c']
    assert report.get_roots_serial([]) == []
    assert report.get_endpoints_serial([]) == []
    assert report.get_roots_serial(holden.Serial(['a', 'b'])) == ['a']
    assert report.get_endpoints_serial(holden.Serial(['a', 'b'])) == ['b']


def test_generic(
        edges: list[tuple[str, str]],
        adjacency: dict[str, set[str]],
        matrix: tuple[list[list[int]], list[str]]) -> None:
    """Tests `get_roots` and `get_endpoints`."""
    for item in (edges, adjacency, matrix, holden.System(adjacency)):
        assert report.get_roots(item) == ['a', 'c']
        assert report.get_endpoints(item) == ['b', 'e']
    assert report.get_roots(['a', 'b']) == ['a']
    assert report.get_endpoints([['a', 'b'], ['c']]) == ['b', 'c']


def test_generic_unsupported_form() -> None:
    """Tests that a form without a report function raises an error."""
    import dataclasses
    from typing import Any

    @dataclasses.dataclass
    class Custom(holden.Composite):
        contents: list[Any] = dataclasses.field(default_factory = list)

    holden.check.add_checker('is_custom', lambda x: isinstance(x, Custom))
    try:
        with pytest.raises(NotImplementedError):
            report.get_roots(Custom())
        with pytest.raises(NotImplementedError):
            report.get_endpoints(Custom())
    finally:
        del holden.check.is_custom  # type: ignore[attr-defined]
