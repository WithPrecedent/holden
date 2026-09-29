"""Tests for `holden.check`."""

from __future__ import annotations

import pytest

import holden
from holden import check


def test_is_adjacency(adjacency: dict[str, set[str]]) -> None:
    """Tests `is_adjacency`."""
    assert check.is_adjacency(adjacency)
    assert check.is_adjacency({})
    assert check.is_adjacency(holden.System(adjacency))
    assert not check.is_adjacency({'a': ['b']})
    assert not check.is_adjacency({'a': {'b'}, 'b': None})
    assert not check.is_adjacency([('a', 'b')])
    assert not check.is_adjacency('a')


def test_is_composite() -> None:
    """Tests `is_composite`."""
    assert check.is_composite(holden.System())
    assert check.is_composite(holden.System)
    assert check.is_composite(holden.Serial())
    assert not check.is_composite(3)
    assert not check.is_composite({})
    assert not check.is_composite([])
    assert not check.is_composite(None)


def test_is_edge() -> None:
    """Tests `is_edge`."""
    assert check.is_edge(('a', 'b'))
    assert check.is_edge((1, 2))
    assert check.is_edge(holden.Edge('a', 'b'))
    assert not check.is_edge(['a', 'b'])
    assert not check.is_edge(('a', 'b', 'c'))
    assert not check.is_edge(('a',))
    assert not check.is_edge('ab')
    assert not check.is_edge(b'ab')
    assert not check.is_edge((['a'], 'b'))
    assert not check.is_edge(5)


def test_is_edges(edges: list[tuple[str, str]]) -> None:
    """Tests `is_edges`."""
    assert check.is_edges(edges)
    assert check.is_edges([])
    assert check.is_edges([holden.Edge('a', 'b')])
    assert check.is_edges(holden.Edges(edges))
    assert not check.is_edges(tuple(edges))
    assert not check.is_edges([['a', 'b']])
    assert not check.is_edges(['a', 'b'])
    assert not check.is_edges({'a': {'b'}})


def test_is_graph() -> None:
    """Tests `is_graph`."""
    assert check.is_graph(holden.System())
    assert check.is_graph(holden.Adjacency)
    assert check.is_graph(holden.Edges())
    assert check.is_graph(holden.Matrix())
    assert not check.is_graph(holden.Serial())
    assert not check.is_graph(holden.Parallel())
    assert not check.is_graph({})


def test_is_matrix(matrix: tuple[list[list[int]], list[str]]) -> None:
    """Tests `is_matrix`."""
    assert check.is_matrix(matrix)
    assert check.is_matrix(([[0, 1.5], [0, 0]], ['a', 'b']))
    assert check.is_matrix(([], []))
    assert not check.is_matrix(([[0, 1], [0, 0]], ['a']))
    assert not check.is_matrix(([[0, 1], [0]], ['a', 'b']))
    assert not check.is_matrix(([[0, 'x'], [0, 0]], ['a', 'b']))
    assert not check.is_matrix(([[0, 1], [0, 0]], [['a'], 'b']))
    assert not check.is_matrix((([0, 1], [0, 0]), ['a', 'b']))
    assert not check.is_matrix(([[0, 1], [0, 0]],))
    assert not check.is_matrix([('a', 'b'), ('c', 'd')])
    assert not check.is_matrix(5)


def test_is_node() -> None:
    """Tests `is_node`."""
    assert check.is_node('a')
    assert check.is_node(1)
    assert check.is_node(('a', 'b'))
    assert check.is_node(holden.Node())
    assert check.is_node(str)
    assert not check.is_node([])
    assert not check.is_node({})
    assert not check.is_node(list)
    assert not check.is_node(holden.System())


def test_is_nodes() -> None:
    """Tests `is_nodes`."""
    assert check.is_nodes(['a', 'b'])
    assert check.is_nodes(('a', 'b'))
    assert check.is_nodes({'a', 'b'})
    assert check.is_nodes([])
    assert not check.is_nodes('ab')
    assert not check.is_nodes([['a'], 'b'])
    assert not check.is_nodes(5)


def test_is_parallel() -> None:
    """Tests `is_parallel`."""
    assert check.is_parallel([['a', 'b'], ['c']])
    assert check.is_parallel([])
    assert check.is_parallel([holden.Serial(['a', 'b'])])
    assert check.is_parallel(holden.Parallel([['a']]))
    assert not check.is_parallel(['a', 'b'])
    assert not check.is_parallel([('a', 'b')])
    assert not check.is_parallel(('a', 'b'))


def test_is_serial() -> None:
    """Tests `is_serial`."""
    assert check.is_serial(['a', 'b'])
    assert check.is_serial([])
    assert check.is_serial(holden.Serial(['a', 'b']))
    assert not check.is_serial(('a', 'b'))
    assert not check.is_serial([('a', 'b')])
    assert not check.is_serial([['a', 'b']])
    assert not check.is_serial('ab')


def test_add_checker() -> None:
    """Tests `add_checker`."""
    def is_special(item: object) -> bool:
        return item == 'special'

    check.add_checker('is_special', is_special)
    try:
        assert check.is_special('special')  # type: ignore[attr-defined]
        assert not check.is_special('other')  # type: ignore[attr-defined]
        with pytest.raises(ValueError, match = 'is_'):
            check.add_checker('special', is_special)
    finally:
        del check.is_special  # type: ignore[attr-defined]
