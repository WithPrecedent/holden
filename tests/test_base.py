"""Tests for `holden.base`."""

from __future__ import annotations

import dataclasses
from typing import Any

import pytest

import holden
from holden import base

from .conftest import Something


@dataclasses.dataclass
class TinyComposite(base.Composite):
    """Smallest concrete composite (a list of nodes)."""

    contents: list[Any] = dataclasses.field(default_factory = list)

    @property
    def nodes(self) -> set[Any]:
        return set(self.contents)

    def _add(self, item: Any, **kwargs: Any) -> None:
        self.contents.append(item)

    def _delete(self, item: Any, **kwargs: Any) -> None:
        self.contents.remove(item)

    def _merge(self, item: Any, **kwargs: Any) -> None:
        self.contents.extend(item)

    def _subset(self, include: Any = None, exclude: Any = None) -> Any:
        return self.__class__(self._selected(self.contents, include, exclude))


class Unregistered(holden.Adjacency):
    """Subclass of a form (which should not be registered)."""


def test_forms_registry() -> None:
    """Tests that the built-in forms are registered."""
    assert holden.Forms.registry['adjacency'] is holden.Adjacency
    assert holden.Forms.registry['edges'] is holden.Edges
    assert holden.Forms.registry['matrix'] is holden.Matrix
    assert holden.Forms.registry['parallel'] is holden.Parallel
    assert holden.Forms.registry['serial'] is holden.Serial
    assert 'system' not in holden.Forms.registry
    assert 'unregistered' not in holden.Forms.registry
    assert 'graph' not in holden.Forms.registry
    assert 'composite' not in holden.Forms.registry


def test_forms_register() -> None:
    """Tests `Forms.register`."""
    holden.Forms.register(TinyComposite)
    assert holden.Forms.registry['tiny_composite'] is TinyComposite
    holden.Forms.register(TinyComposite, name = 'small')
    assert holden.Forms.registry['small'] is TinyComposite


def test_direct_subclass_is_registered() -> None:
    """Tests that a direct subclass of `Composite` is registered."""
    @dataclasses.dataclass
    class Direct(base.Composite):
        contents: list[Any] = dataclasses.field(default_factory = list)

    @dataclasses.dataclass
    class Indirect(Direct):
        pass

    assert holden.Forms.registry['direct'] is Direct
    assert 'indirect' not in holden.Forms.registry


def test_classify(
        edges: list[tuple[str, str]],
        adjacency: dict[str, set[str]],
        matrix: tuple[list[list[int]], list[str]]) -> None:
    """Tests `classify` and `Forms.classify`."""
    assert base.classify(adjacency) == 'adjacency'
    assert base.classify(edges) == 'edges'
    assert base.classify(matrix) == 'matrix'
    assert base.classify(['a', 'b']) == 'serial'
    assert base.classify([['a', 'b'], ['c']]) == 'parallel'
    assert base.classify([]) == 'edges'
    assert base.classify(holden.System()) == 'adjacency'
    assert base.classify(holden.System) == 'adjacency'
    assert base.classify(holden.Edges()) == 'edges'
    assert base.classify(holden.Matrix()) == 'matrix'
    assert base.classify(holden.Parallel()) == 'parallel'
    assert base.classify(holden.Serial()) == 'serial'
    assert base.classify(Unregistered()) == 'adjacency'
    assert holden.Forms.classify(adjacency) == 'adjacency'
    for unrecognized in ('a', 5, None, {'a': 1}, [('a', 'b', 'c')]):
        with pytest.raises(TypeError):
            base.classify(unrecognized)


def test_classify_custom_form() -> None:
    """Tests that `classify` checks custom forms using `add_checker`."""
    @dataclasses.dataclass
    class Custom(base.Composite):
        contents: list[Any] = dataclasses.field(default_factory = list)

    holden.check.add_checker('is_custom', lambda x: x == 'custom')
    try:
        assert base.classify('custom') == 'custom'
        assert base.classify(Custom()) == 'custom'
    finally:
        del holden.check.is_custom  # type: ignore[attr-defined]


def test_transform(
        edges: list[tuple[str, str]],
        adjacency: dict[str, set[str]],
        matrix: tuple[list[list[int]], list[str]]) -> None:
    """Tests the `transform` function."""
    assert base.transform(edges, 'adjacency') == adjacency
    assert base.transform(adjacency, 'edges') == [
        ('a', 'b'), ('a', 'd'), ('c', 'd'), ('d', 'e')]
    assert base.transform(adjacency, 'matrix') == matrix
    assert base.transform(matrix, 'adjacency') == adjacency
    assert base.transform(holden.System(adjacency), 'serial') == [
        'a', 'b', 'a', 'd', 'e', 'c', 'd', 'e']
    assert base.transform(
        holden.Edges(list(edges)), 'adjacency') == adjacency
    assert base.transform(
        holden.Matrix(matrix[0], matrix[1]), 'adjacency') == adjacency
    same = base.transform(adjacency, 'adjacency', raise_same_error = False)
    assert same is adjacency
    with pytest.raises(ValueError, match = 'same'):
        base.transform(adjacency, 'adjacency')
    with pytest.raises(ValueError, match = 'registered'):
        base.transform(adjacency, 'unknown')
    with pytest.raises(TypeError):
        base.transform('a', 'edges')


def test_transform_missing_transformer() -> None:
    """Tests that a missing transformer raises `NotImplementedError`."""
    @dataclasses.dataclass
    class Custom(base.Composite):
        contents: list[Any] = dataclasses.field(default_factory = list)

    with pytest.raises(NotImplementedError):
        base.transform(holden.System(), 'custom')


def test_forms_transform(
        edges: list[tuple[str, str]],
        matrix: tuple[list[list[int]], list[str]]) -> None:
    """Tests `Forms.transform`."""
    result = holden.Forms.transform(edges, 'adjacency')
    assert isinstance(result, holden.Adjacency)
    assert type(result) is holden.Adjacency
    assert result.contents['a'] == {'b', 'd'}
    result = holden.Forms.transform(edges, 'matrix')
    assert type(result) is holden.Matrix
    assert result.contents == matrix[0]
    assert result.labels == matrix[1]
    result = holden.Forms.transform(edges, 'serial')
    assert type(result) is holden.Serial
    result = holden.Forms.transform(edges, 'parallel')
    assert type(result) is holden.Parallel
    system = holden.System.from_edges(edges)
    assert holden.Forms.transform(
        system, 'adjacency', raise_same_error = False) is system
    with pytest.raises(ValueError, match = 'same'):
        holden.Forms.transform(system, 'adjacency')


def test_structural_isinstance(
        edges: list[tuple[str, str]],
        adjacency: dict[str, set[str]],
        matrix: tuple[list[list[int]], list[str]]) -> None:
    """Tests that raw forms are instances of the matching form classes."""
    assert isinstance(adjacency, holden.Adjacency)
    assert isinstance(edges, holden.Edges)
    assert isinstance(matrix, holden.Matrix)
    assert isinstance([['a', 'b']], holden.Parallel)
    assert isinstance(['a', 'b'], holden.Serial)
    assert not isinstance(edges, holden.Adjacency)
    assert not isinstance(adjacency, holden.Edges)
    assert not isinstance(adjacency, holden.Serial)
    assert not isinstance('a', holden.Adjacency)
    # A real instance is still an instance
    assert isinstance(holden.System(), holden.Adjacency)
    assert not isinstance(holden.Adjacency(), holden.Edges)
    # Only registered forms accept raw structures
    assert not isinstance(adjacency, holden.System)
    assert not isinstance(adjacency, Unregistered)
    assert isinstance(Unregistered(), holden.Adjacency)


def test_structural_isinstance_bases() -> None:
    """Tests structural `isinstance` checks for `Composite` and `Graph`."""
    assert isinstance(holden.System(), base.Composite)
    assert isinstance(holden.System(), base.Graph)
    assert isinstance(holden.Serial(), base.Composite)
    assert not isinstance(holden.Serial(), base.Graph)
    assert not isinstance({}, base.Composite)
    assert not isinstance(3, base.Graph)

    class Duck:
        def add(self) -> None: ...
        def delete(self) -> None: ...
        def merge(self) -> None: ...
        def subset(self) -> None: ...

    assert isinstance(Duck(), base.Composite)
    assert not isinstance(Duck(), base.Graph)


def test_composite_add_delete() -> None:
    """Tests `Composite.add` and `Composite.delete`."""
    composite = TinyComposite()
    composite.add('a')
    composite.add('b')
    assert composite.contents == ['a', 'b']
    assert 'a' in composite
    assert 'z' not in composite
    assert [] not in composite
    with pytest.raises(ValueError, match = 'already'):
        composite.add('a')
    with pytest.raises(TypeError):
        composite.add(['unhashable'])
    composite.delete('a')
    assert composite.contents == ['b']
    with pytest.raises(KeyError):
        composite.delete('a')
    with pytest.raises(TypeError):
        composite.delete(['unhashable'])


def test_composite_delete_translates_key_error() -> None:
    """Tests that a `KeyError` in `_delete` gets a clear message."""
    @dataclasses.dataclass
    class Raises(TinyComposite):
        def _delete(self, item: Any, **kwargs: Any) -> None:
            raise KeyError(item)

    composite = Raises(['a'])
    with pytest.raises(KeyError, match = 'does not exist'):
        composite.delete('a')


def test_composite_merge() -> None:
    """Tests `Composite.merge`."""
    composite = TinyComposite(['a'])
    composite.merge(['b', 'c'])
    assert composite.contents == ['a', 'b', 'c']
    with pytest.raises(TypeError, match = 'compatible'):
        composite.merge(5)


def test_composite_subset() -> None:
    """Tests `Composite.subset`."""
    composite = TinyComposite(['a', 'b', 'c'])
    assert composite.subset(include = ['a', 'b']).contents == ['a', 'b']
    assert composite.subset(exclude = 'a').contents == ['b', 'c']
    assert composite.subset(include = ['a', 'b'], exclude = 'b').contents == [
        'a']
    assert composite.contents == ['a', 'b', 'c']
    with pytest.raises(ValueError, match = 'include or exclude'):
        composite.subset()
    with pytest.raises(ValueError, match = 'include'):
        composite.subset(include = ['z'])
    with pytest.raises(ValueError, match = 'exclude'):
        composite.subset(exclude = ['z'])


def test_composite_required_methods() -> None:
    """Tests that a subclass must implement the private methods."""
    @dataclasses.dataclass
    class Empty(base.Composite):
        contents: list[Any] = dataclasses.field(default_factory = list)

    composite = Empty()
    with pytest.raises(NotImplementedError):
        composite.nodes  # noqa: B018
    with pytest.raises(NotImplementedError):
        composite._add('a')
    with pytest.raises(NotImplementedError):
        composite._delete('a')
    with pytest.raises(NotImplementedError):
        composite._merge(['a'])
    with pytest.raises(NotImplementedError):
        composite._subset()


def test_graph_connect_disconnect() -> None:
    """Tests `Graph.connect` and `Graph.disconnect` validation."""
    graph = holden.Adjacency()
    graph.add('a')
    graph.add('b')
    with pytest.raises(TypeError):
        graph.connect(['a', 'b'])  # type: ignore[arg-type]
    with pytest.raises(ValueError, match = 'same as'):
        graph.connect(('a', 'a'))
    with pytest.raises(ValueError, match = 'not in the graph'):
        graph.connect(('a', 'z'))
    with pytest.raises(ValueError, match = 'not in the graph'):
        graph.connect(('z', 'a'))
    graph.connect(('a', 'b'))
    assert graph['a'] == {'b'}
    with pytest.raises(TypeError):
        graph.disconnect(['a', 'b'])  # type: ignore[arg-type]
    with pytest.raises(ValueError, match = 'not in the graph'):
        graph.disconnect(('b', 'a'))
    graph.disconnect(('a', 'b'))
    assert graph['a'] == set()


def test_graph_required_methods() -> None:
    """Tests that a graph subclass must implement connection methods."""
    @dataclasses.dataclass
    class Empty(base.Graph):
        contents: list[Any] = dataclasses.field(default_factory = list)

    graph = Empty()
    with pytest.raises(NotImplementedError):
        graph._connect(('a', 'b'))
    with pytest.raises(NotImplementedError):
        graph._disconnect(('a', 'b'))


def test_graph_subclass_is_registered() -> None:
    """Tests that a direct subclass of `Graph` is registered."""
    @dataclasses.dataclass
    class Special(base.Graph):
        contents: list[Any] = dataclasses.field(default_factory = list)

    assert holden.Forms.registry['special'] is Special


def test_edge() -> None:
    """Tests `Edge`."""
    edge = holden.Edge('a', 'b')
    assert edge.start == 'a'
    assert edge.stop == 'b'
    assert edge[0] == 'a'
    assert edge[1] == 'b'
    assert edge[-1] == 'b'
    assert edge[:] == ('a', 'b')
    assert len(edge) == 2
    assert list(edge) == ['a', 'b']
    assert tuple(edge) == ('a', 'b')
    start, stop = edge
    assert (start, stop) == ('a', 'b')
    assert 'a' in edge
    with pytest.raises(IndexError):
        edge[2]
    with pytest.raises(dataclasses.FrozenInstanceError):
        edge.start = 'c'  # type: ignore[misc]
    assert holden.check.is_edge(edge)


def test_edge_equality_and_hash() -> None:
    """Tests that an `Edge` can replace a `tuple`."""
    edge = holden.Edge('a', 'b')
    assert edge == holden.Edge('a', 'b')
    assert edge == ('a', 'b')
    assert edge != ('a', 'c')
    assert edge != holden.Edge('a', 'c')
    assert edge != 'ab'
    assert hash(edge) == hash(('a', 'b'))
    assert {edge: 1}[('a', 'b')] == 1
    assert edge < holden.Edge('b', 'a')
    assert sorted([holden.Edge('b', 'a'), edge]) == [
        edge, holden.Edge('b', 'a')]


def test_copy_raw() -> None:
    """Tests that `_copy_raw` copies the containers of every raw form."""
    adjacency = {'a': {'b'}, 'b': set()}
    copied = base._copy_raw(adjacency)
    assert copied == adjacency
    assert copied is not adjacency
    assert copied['a'] is not adjacency['a']
    matrix = ([[0, 1], [0, 0]], ['a', 'b'])
    copied_matrix = base._copy_raw(matrix)
    assert copied_matrix == matrix
    assert copied_matrix[0] is not matrix[0]
    assert copied_matrix[0][0] is not matrix[0][0]
    assert copied_matrix[1] is not matrix[1]
    paths = [['a', 'b'], ['c']]
    copied_paths = base._copy_raw(paths)
    assert copied_paths == paths
    assert copied_paths[0] is not paths[0]
    assert base._copy_raw(['a', 'b']) == ['a', 'b']
    assert base._copy_raw(5) == 5
    other = {1, 2}
    assert base._copy_raw(other) == other
    assert base._copy_raw(other) is not other


def test_node() -> None:
    """Tests `Node`."""
    node = holden.Node('contents')
    assert node.contents == 'contents'
    assert hash(node) == hash(holden.Node('contents'))
    assert node == holden.Node('contents')
    assert node != holden.Node('other')
    assert {node: 1}[holden.Node('contents')] == 1
    unhashable = holden.Node([1, 2])
    assert isinstance(hash(unhashable), int)
    assert hash(unhashable) == hash(holden.Node([1, 2]))
    assert unhashable == holden.Node([1, 2])


def test_node_subclass_keeps_hash() -> None:
    """Tests that dataclass subclasses of `Node` stay hashable."""
    @dataclasses.dataclass
    class Extended(holden.Node):
        extra: int = 0

    assert hash(Extended('a', 1)) == hash(Extended('a', 1))
    assert Extended('a', 1) == Extended('a', 1)
    assert Extended('a', 1) != Extended('a', 2)
    assert len({Extended('a', 1), Extended('a', 1), Extended('a', 2)}) == 2


def test_node_subclass_keeps_mixin_hash() -> None:
    """Tests that a mixin before `Node` controls hashing and equality."""
    node = Something()
    assert hash(node) == hash('something')
    assert node == 'something'
    assert node == Something()
    assert 'something' in {node}
    assert node in {'something'}


def test_node_subclass_with_explicit_methods() -> None:
    """Tests that explicit methods in a `Node` subclass are respected."""
    @dataclasses.dataclass
    class Explicit(holden.Node):
        def __hash__(self) -> int:
            return 1

    assert hash(Explicit('a')) == 1
    assert hash(Explicit('b')) == 1
