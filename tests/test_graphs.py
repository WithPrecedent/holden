"""Tests for `holden.graphs`."""

from __future__ import annotations

from typing import Any

import pytest

import holden

from .conftest import AnotherThing, Something


def raw(graph: holden.Composite, form: str) -> Any:
    """Returns the raw structure of `form` for `graph`."""
    return holden.utilities._rawify(
        holden.transform(graph, form, raise_same_error = False))


def make_adjacency() -> holden.Adjacency:
    """Returns an `Adjacency` with a small graph."""
    return holden.Adjacency({'a': {'b', 'd'}, 'b': set(), 'c': {'d'},
                             'd': {'e'}, 'e': set()})


def make_edges() -> holden.Edges:
    """Returns an `Edges` with a small graph."""
    return holden.Edges([('a', 'b'), ('c', 'd'), ('a', 'd'), ('d', 'e')])


def make_matrix() -> holden.Matrix:
    """Returns a `Matrix` with a small graph."""
    return holden.Matrix(
        [[0, 1, 0, 1, 0],
         [0, 0, 0, 0, 0],
         [0, 0, 0, 1, 0],
         [0, 0, 0, 0, 1],
         [0, 0, 0, 0, 0]],
        ['a', 'b', 'c', 'd', 'e'])


ALL = pytest.mark.parametrize(
    'factory', [make_adjacency, make_edges, make_matrix])


@ALL
def test_nodes_and_contains(factory) -> None:
    """Tests `nodes` and `in` for every form."""
    graph = factory()
    assert graph.nodes == {'a', 'b', 'c', 'd', 'e'}
    assert 'a' in graph
    assert 'z' not in graph
    assert [] not in graph


@ALL
def test_forms_agree_on_structure(factory) -> None:
    """Tests that every form has the same adjacency."""
    graph = factory()
    assert raw(graph, 'adjacency') == {
        'a': {'b', 'd'}, 'b': set(), 'c': {'d'}, 'd': {'e'}, 'e': set()}


@ALL
def test_connect_disconnect(factory) -> None:
    """Tests `connect` and `disconnect` for every form."""
    graph = factory()
    graph.connect(('b', 'e'))
    assert raw(graph, 'adjacency')['b'] == {'e'}
    graph.connect(('b', 'e'))
    assert raw(graph, 'edges').count(('b', 'e')) == 1
    graph.disconnect(('b', 'e'))
    assert raw(graph, 'adjacency')['b'] == set()
    with pytest.raises(ValueError, match = 'not in the graph'):
        graph.disconnect(('b', 'e'))
    with pytest.raises(ValueError, match = 'same as'):
        graph.connect(('a', 'a'))
    if isinstance(graph, holden.Edges):
        # An edge list creates the nodes of an edge that it does not have
        graph.connect(('a', 'z'))
        assert 'z' in graph
    else:
        with pytest.raises(ValueError, match = 'not in the graph'):
            graph.connect(('a', 'z'))


@ALL
def test_delete(factory) -> None:
    """Tests that `delete` removes a node and all of its edges."""
    graph = factory()
    graph.delete('d')
    assert 'd' not in graph
    assert 'd' not in graph.nodes
    adjacency = raw(graph, 'adjacency')
    assert 'd' not in adjacency
    assert all('d' not in connections for connections in adjacency.values())
    assert adjacency['a'] == {'b'}
    with pytest.raises(KeyError):
        graph.delete('d')


@ALL
def test_merge_every_form(factory) -> None:
    """Tests `merge` with each form of composite and raw structure."""
    other_adjacency = {'x': {'y'}, 'y': set(), 'a': {'x'}}
    for other in (
            other_adjacency,
            holden.Adjacency(dict(other_adjacency)),
            [('x', 'y'), ('a', 'x')],
            holden.Edges([('x', 'y'), ('a', 'x')]),
            ([[0, 1, 0], [0, 0, 0], [1, 0, 0]], ['x', 'y', 'a']),
            [['a', 'x', 'y']],
            ['a', 'x', 'y']):
        graph = factory()
        graph.merge(other)
        adjacency = raw(graph, 'adjacency')
        assert {'x', 'y'} <= graph.nodes
        assert 'x' in adjacency['a']
        assert adjacency['a'] >= {'b', 'd', 'x'}
        assert 'y' in adjacency['x']
    with pytest.raises(TypeError):
        factory().merge(5)


@ALL
def test_subset(factory) -> None:
    """Tests `subset` for every form."""
    graph = factory()
    included = graph.subset(include = ['a', 'b', 'd'])
    assert type(included) is type(graph)
    assert raw(included, 'adjacency') == {
        'a': {'b', 'd'}, 'b': set(), 'd': set()}
    excluded = graph.subset(exclude = ['a', 'b'])
    assert 'a' not in excluded
    assert 'b' not in excluded
    both = graph.subset(include = ['a', 'b', 'c'], exclude = ['c'])
    assert 'c' not in both
    # The original is unchanged
    assert graph.nodes == {'a', 'b', 'c', 'd', 'e'}
    with pytest.raises(ValueError, match = 'include or exclude'):
        graph.subset()
    with pytest.raises(ValueError, match = 'include'):
        graph.subset(include = ['z'])


def test_post_init_of_other_classes_is_called() -> None:
    """Tests that mixins with a `__post_init__` work with the forms."""
    import dataclasses

    calls: list[str] = []

    @dataclasses.dataclass
    class Recorder:
        def __post_init__(self) -> None:
            calls.append('recorded')

    @dataclasses.dataclass
    class RecordedAdjacency(holden.Adjacency, Recorder):
        pass

    @dataclasses.dataclass
    class RecordedMatrix(holden.Matrix, Recorder):
        pass

    RecordedAdjacency({'a': {'b'}})
    RecordedMatrix([[0]], ['a'])
    assert calls == ['recorded', 'recorded']


def test_adjacency_defaults() -> None:
    """Tests default values of an `Adjacency`."""
    graph = holden.Adjacency()
    assert graph.contents == {}
    assert len(graph) == 0
    with pytest.raises(KeyError):
        graph['missing']
    assert 'missing' not in graph
    assert 'missing' not in graph.contents


def test_adjacency_add_and_connect() -> None:
    """Tests building an `Adjacency` by hand."""
    graph = holden.Adjacency()
    graph.add('a')
    graph.add('b')
    graph.connect(('a', 'b'))
    assert graph['a'] == {'b'}
    assert graph['b'] == set()
    assert list(graph) == ['a', 'b']
    assert graph.keys() == ('a', 'b')
    with pytest.raises(ValueError, match = 'already'):
        graph.add('a')
    with pytest.raises(TypeError):
        graph.add(['a'])


def test_adjacency_adds_missing_keys() -> None:
    """Tests that nodes that are only connections get their own key."""
    graph = holden.Adjacency({'a': {'b', 'c'}})
    assert graph.contents == {'a': {'b', 'c'}, 'b': set(), 'c': set()}
    assert graph.nodes == {'a', 'b', 'c'}


def test_adjacency_delete_updates_connections() -> None:
    """Tests that `delete` edits the stored sets."""
    graph = make_adjacency()
    graph.delete('e')
    assert graph['d'] == set()
    assert 'e' not in graph


def test_adjacency_subset_edges() -> None:
    """Tests that `subset` only keeps edges between kept nodes."""
    graph = make_adjacency()
    subset = graph.subset(include = ['a', 'd', 'e'])
    assert subset.contents == {'a': {'d'}, 'd': {'e'}, 'e': set()}
    assert subset.contents is not graph.contents
    subset.contents['a'].add('zzz')
    assert graph['a'] == {'b', 'd'}


def test_edges_add_and_connect() -> None:
    """Tests building an `Edges` graph."""
    graph = holden.Edges()
    graph.connect(('a', 'b'))
    graph.connect(('b', 'c'))
    assert graph.contents == [('a', 'b'), ('b', 'c')]
    assert graph.nodes == {'a', 'b', 'c'}
    graph.add(('c', 'd'))
    assert ('c', 'd') in graph
    assert graph.contents[-1] == ('c', 'd')
    with pytest.raises(ValueError, match = 'already'):
        graph.add(('c', 'd'))
    with pytest.raises(ValueError, match = 'only add edges'):
        graph.add('e')
    assert graph.nodes == {'a', 'b', 'c', 'd'}


def test_edges_contains_nodes_and_edges() -> None:
    """Tests `in` for a node, an edge, and an `Edge`."""
    graph = make_edges()
    assert 'a' in graph
    assert ('a', 'b') in graph
    assert holden.Edge('a', 'b') in graph
    assert ('b', 'a') not in graph
    assert [] not in graph


def test_edges_delete_edge_or_node() -> None:
    """Tests that `delete` can remove an edge or a node."""
    graph = make_edges()
    graph.delete(('a', 'b'))
    assert graph.contents == [('c', 'd'), ('a', 'd'), ('d', 'e')]
    assert 'b' not in graph
    graph.delete('d')
    assert graph.contents == []


def test_edges_with_edge_instances() -> None:
    """Tests using `Edge` instances in an `Edges`."""
    graph = holden.Edges([holden.Edge('a', 'b')])
    graph.connect(holden.Edge('b', 'c'))
    graph.connect(('a', 'b'))
    assert len(graph) == 2
    graph.disconnect(('b', 'c'))
    assert graph.contents == [holden.Edge('a', 'b')]
    assert raw(graph, 'adjacency') == {'a': {'b'}, 'b': set()}


def test_edges_merge_skips_duplicates() -> None:
    """Tests that `merge` does not repeat edges."""
    graph = make_edges()
    graph.merge([('a', 'b'), ('x', 'y')])
    assert graph.contents.count(('a', 'b')) == 1
    assert ('x', 'y') in graph


def test_matrix_validation() -> None:
    """Tests that a `Matrix` checks its shape."""
    assert holden.Matrix().contents == []
    with pytest.raises(ValueError, match = 'square'):
        holden.Matrix([[0, 1], [0, 0]], ['a'])
    with pytest.raises(ValueError, match = 'square'):
        holden.Matrix([[0, 1], [0]], ['a', 'b'])
    with pytest.raises(ValueError, match = 'square'):
        holden.Matrix([[0]], [])


def test_matrix_add_and_connect() -> None:
    """Tests building a `Matrix` by hand."""
    graph = holden.Matrix()
    graph.add('a')
    graph.add('b')
    graph.add('c')
    graph.connect(('a', 'c'))
    graph.connect(('c', 'b'))
    assert graph.labels == ['a', 'b', 'c']
    assert graph.contents == [[0, 0, 1], [0, 0, 0], [0, 1, 0]]
    graph.disconnect(('a', 'c'))
    assert graph.contents == [[0, 0, 0], [0, 0, 0], [0, 1, 0]]
    with pytest.raises(ValueError, match = 'already'):
        graph.add('a')


def test_matrix_delete_shrinks_matrix() -> None:
    """Tests that `delete` removes the row, the column, and the label."""
    graph = make_matrix()
    graph.delete('b')
    assert graph.labels == ['a', 'c', 'd', 'e']
    assert graph.contents == [
        [0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 0, 1], [0, 0, 0, 0]]


def test_matrix_subset_keeps_labels() -> None:
    """Tests that `subset` keeps the labels and the matrix in sync."""
    subset = make_matrix().subset(include = ['a', 'd', 'e'])
    assert subset.labels == ['a', 'd', 'e']
    assert subset.contents == [[0, 1, 0], [0, 0, 1], [0, 0, 0]]


def test_matrix_merge_new_and_existing_nodes() -> None:
    """Tests that `merge` combines matrices by label."""
    graph = holden.Matrix([[0, 1], [0, 0]], ['a', 'b'])
    graph.merge(([[0, 1], [0, 0]], ['b', 'c']))
    assert graph.labels == ['a', 'b', 'c']
    assert graph.contents == [[0, 1, 0], [0, 0, 1], [0, 0, 0]]


def test_matrix_with_weights() -> None:
    """Tests that non-zero values are edges and are preserved."""
    graph = holden.Matrix([[0, 2.5], [0, 0]], ['a', 'b'])
    graph.connect(('a', 'b'))
    assert graph.contents[0][1] == 2.5
    assert raw(graph, 'adjacency') == {'a': {'b'}, 'b': set()}


def test_labeled_nodes_in_a_graph() -> None:
    """Tests using labeled nodes and their names interchangeably."""
    graph = holden.Adjacency()
    something = Something()
    another = AnotherThing()
    graph.add(something)
    graph.add(another)
    assert 'something' in graph
    assert something in graph
    graph.connect(('something', 'another_thing'))
    assert 'another_thing' in graph['something']
    assert another in graph['something']
    assert graph['something'] == {'another_thing'}
    with pytest.raises(ValueError, match = 'already'):
        graph.add('something')
    graph.disconnect((something, another))
    assert graph['something'] == set()
    graph.delete('something')
    assert 'something' not in graph
    assert another in graph


def test_graph_subclass_keeps_extra_attributes() -> None:
    """Tests that a subset keeps attributes that a subclass adds."""
    import dataclasses

    @dataclasses.dataclass
    class Titled(holden.Adjacency):
        title: str = 'none'

    graph = Titled({'a': {'b'}, 'b': set()}, title = 'my graph')
    subset = graph.subset(include = ['a'])
    assert isinstance(subset, Titled)
    assert subset.title == 'my graph'
    assert subset.contents == {'a': set()}
