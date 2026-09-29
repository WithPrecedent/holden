"""Tests for `holden.traverse`."""

from __future__ import annotations

import pytest

import holden
from holden import traverse

DAG_PATHS = [['a', 'b'], ['a', 'd', 'e'], ['c', 'd', 'e']]


def test_walk_adjacency(adjacency: dict[str, set[str]]) -> None:
    """Tests `walk_adjacency`."""
    assert traverse.walk_adjacency(adjacency, 'a', 'e') == [['a', 'd', 'e']]
    assert traverse.walk_adjacency(adjacency, 'a', 'b') == [['a', 'b']]
    assert traverse.walk_adjacency(adjacency, 'c', 'b') == []
    assert traverse.walk_adjacency(adjacency, 'a', 'a') == [['a']]
    assert traverse.walk_adjacency(adjacency, 'z', 'e') == []
    assert traverse.walk_adjacency(adjacency, 'a', 'z') == []
    assert traverse.walk_adjacency(holden.System(adjacency), 'c', 'e') == [
        ['c', 'd', 'e']]


def test_walk_adjacency_multiple_paths() -> None:
    """Tests that every path is found in a deterministic order."""
    diamond = {'a': {'b', 'c'}, 'b': {'d'}, 'c': {'d'}, 'd': set()}
    assert traverse.walk_adjacency(diamond, 'a', 'd') == [
        ['a', 'b', 'd'], ['a', 'c', 'd']]


def test_walk_adjacency_cycle() -> None:
    """Tests that a cycle does not cause an infinite loop."""
    cycle = {'a': {'b'}, 'b': {'c'}, 'c': {'a', 'd'}, 'd': set()}
    assert traverse.walk_adjacency(cycle, 'a', 'd') == [['a', 'b', 'c', 'd']]
    assert traverse.walk_adjacency(cycle, 'a', 'z') == []


def test_walk_adjacency_prefix() -> None:
    """Tests the `path` argument."""
    adjacency = {'a': {'b'}, 'b': set()}
    assert traverse.walk_adjacency(adjacency, 'a', 'b', path = ['x']) == [
        ['x', 'a', 'b']]


def test_walk_adjacency_long_path() -> None:
    """Tests that a long path does not exceed the recursion limit."""
    length = 3000
    adjacency = {i: {i + 1} for i in range(length)}
    adjacency[length] = set()
    assert traverse.walk_adjacency(adjacency, 0, length) == [
        list(range(length + 1))]


def test_walk_edges(edges: list[tuple[str, str]]) -> None:
    """Tests `walk_edges`."""
    assert traverse.walk_edges(edges, 'a', 'e') == [['a', 'd', 'e']]
    assert traverse.walk_edges(edges, 'a', 'c') == []
    assert traverse.walk_edges(holden.Edges(edges), 'c', 'e') == [
        ['c', 'd', 'e']]


def test_walk_matrix(matrix: tuple[list[list[int]], list[str]]) -> None:
    """Tests `walk_matrix`."""
    assert traverse.walk_matrix(matrix, 'a', 'e') == [['a', 'd', 'e']]
    assert traverse.walk_matrix(matrix, 'b', 'e') == []
    assert traverse.walk_matrix(
        holden.Matrix(matrix[0], matrix[1]), 'c', 'e') == [['c', 'd', 'e']]


def test_walk_serial() -> None:
    """Tests `walk_serial`."""
    path = ['a', 'b', 'c', 'd']
    assert traverse.walk_serial(path, 'a', 'd') == [['a', 'b', 'c', 'd']]
    assert traverse.walk_serial(path, 'b', 'c') == [['b', 'c']]
    assert traverse.walk_serial(path, 'b', 'b') == [['b']]
    assert traverse.walk_serial(path, 'c', 'b') == []
    assert traverse.walk_serial(path, 'z', 'b') == []
    assert traverse.walk_serial(path, 'a', 'z') == []
    assert traverse.walk_serial(holden.Serial(path), 'b', 'd') == [
        ['b', 'c', 'd']]
    # The returned path is a copy
    result = traverse.walk_serial(path, 'a', 'd')
    result[0].append('x')
    assert path == ['a', 'b', 'c', 'd']


def test_walk_parallel() -> None:
    """Tests `walk_parallel`."""
    assert traverse.walk_parallel(DAG_PATHS, 'a', 'e') == [['a', 'd', 'e']]
    assert traverse.walk_parallel(DAG_PATHS, 'd', 'e') == [
        ['d', 'e'], ['d', 'e']]
    assert traverse.walk_parallel(DAG_PATHS, 'e', 'a') == []
    assert traverse.walk_parallel(holden.Parallel(DAG_PATHS), 'c', 'e') == [
        ['c', 'd', 'e']]


def test_walk(
        edges: list[tuple[str, str]],
        adjacency: dict[str, set[str]],
        matrix: tuple[list[list[int]], list[str]]) -> None:
    """Tests `walk` for every form."""
    for item in (edges, adjacency, matrix, holden.System(adjacency)):
        assert traverse.walk(item) == DAG_PATHS
        assert traverse.walk(item, start = 'a') == [
            ['a', 'b'], ['a', 'd', 'e']]
        assert traverse.walk(item, stop = 'e') == [
            ['a', 'd', 'e'], ['c', 'd', 'e']]
        assert traverse.walk(item, 'a', 'e') == [['a', 'd', 'e']]
        assert traverse.walk(item, start = ['a', 'c'], stop = 'e') == [
            ['a', 'd', 'e'], ['c', 'd', 'e']]
    assert traverse.walk(DAG_PATHS, 'a', 'e') == [['a', 'd', 'e']]
    assert traverse.walk(['a', 'b', 'c']) == [['a', 'b', 'c']]
    assert traverse.walk(['a', 'b', 'c'], 'b') == [['b', 'c']]


def test_walk_unsupported_form() -> None:
    """Tests that a form without a walk function raises an error."""
    import dataclasses
    from typing import Any

    @dataclasses.dataclass
    class Custom(holden.Composite):
        contents: list[Any] = dataclasses.field(default_factory = list)

    holden.check.add_checker('is_custom', lambda x: isinstance(x, Custom))
    try:
        with pytest.raises(NotImplementedError):
            traverse.walk(Custom())
    finally:
        del holden.check.is_custom  # type: ignore[attr-defined]
