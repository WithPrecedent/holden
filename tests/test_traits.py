"""Tests for `holden.traits`."""

from __future__ import annotations

import dataclasses
import pathlib
from typing import Any

import pytest

import holden

from .conftest import AnotherThing, Something


@dataclasses.dataclass
class DirectedEdges(holden.Directed, holden.Edges, holden.Fungible):
    """Edge list with the directed and fungible traits."""


@dataclasses.dataclass
class DirectedMatrix(holden.Directed, holden.Matrix, holden.Fungible):
    """Adjacency matrix with the directed and fungible traits."""


@dataclasses.dataclass
class FungibleMatrix(holden.Matrix, holden.Fungible):
    """Adjacency matrix with the fungible trait."""


@dataclasses.dataclass
class FungibleEdges(holden.Edges, holden.Fungible):
    """Edge list with the fungible trait."""


def make_system() -> holden.System:
    """Returns a `System` with a small graph."""
    return holden.System.from_edges([('a', 'b'), ('c', 'd')])


class TestDirected:
    """Tests for `Directed`."""

    def test_root_endpoint_walk(self) -> None:
        """Tests `root`, `endpoint`, and `walk`."""
        system = make_system()
        assert system.root == ['a', 'c']
        assert system.endpoint == ['b', 'd']
        assert system.walk() == [['a', 'b'], ['c', 'd']]
        assert system.walk('a') == [['a', 'b']]
        assert system.walk(stop = 'd') == [['c', 'd']]
        assert system.walk('a', 'd') == []

    @pytest.mark.parametrize('form', [DirectedEdges, DirectedMatrix])
    def test_other_forms(self, form: type) -> None:
        """Tests that other forms of graph can be directed."""
        graph = form.from_edges([('a', 'b'), ('c', 'd')])
        assert graph.root == ['a', 'c']
        assert graph.endpoint == ['b', 'd']
        assert graph.walk() == [['a', 'b'], ['c', 'd']]
        graph.append('e')
        assert graph.adjacency.contents['b'] == {'e'}
        assert graph.adjacency.contents['d'] == {'e'}
        graph.prepend('z')
        assert graph.adjacency.contents['z'] == {'a', 'c'}
        graph.append(holden.System.from_edges([('x', 'y')]))
        assert graph.adjacency.contents['e'] == {'x'}
        assert graph.adjacency.contents['x'] == {'y'}

    def test_append_node(self) -> None:
        """Tests appending a node."""
        system = make_system()
        system.append('z')
        assert system.contents == {
            'a': {'b'}, 'b': {'z'}, 'c': {'d'}, 'd': {'z'}, 'z': set()}
        assert system.endpoint == ['z']

    def test_append_with_attachment(self) -> None:
        """Tests appending to chosen endpoints instead of all of them."""
        system = make_system()
        system.append('z', attachment = 'b')
        assert system['b'] == {'z'}
        assert system['d'] == set()
        system = make_system()
        system.append('z', attachment = ['b', 'd'])
        assert system['b'] == {'z'}
        assert system['d'] == {'z'}
        system = make_system()
        system.append(
            holden.System.from_edges([('x', 'y')]), attachment = 'd')
        assert system['d'] == {'x'}
        assert system['b'] == set()
        assert system['x'] == {'y'}

    def test_append_existing_node(self) -> None:
        """Tests that appending a node that is already stored connects it."""
        system = holden.System.from_edges([('a', 'b'), ('a', 'c')])
        system.append('c')
        assert system['b'] == {'c'}
        assert system['c'] == set()

    def test_prepend_node(self) -> None:
        """Tests prepending a node."""
        system = make_system()
        system.prepend('z')
        assert system['z'] == {'a', 'c'}
        assert system.root == ['z']

    def test_append_graph(self) -> None:
        """Tests appending a graph, a raw form, and a path."""
        system = make_system()
        system.append(holden.System.from_edges([('x', 'y')]))
        assert system['b'] == {'x'}
        assert system['d'] == {'x'}
        assert system['x'] == {'y'}
        system = make_system()
        system.append({'x': {'y'}, 'y': set()})
        assert system['b'] == {'x'}
        system = make_system()
        system.append(['x', 'y'])
        assert system['b'] == {'x'}
        assert system['x'] == {'y'}
        system = make_system()
        system.append(holden.Serial(['x']))
        assert system['d'] == {'x'}

    def test_prepend_graph(self) -> None:
        """Tests prepending a graph."""
        system = make_system()
        system.prepend(holden.System.from_edges([('x', 'y')]))
        assert system['y'] == {'a', 'c'}
        assert system.root == ['x']
        assert system.walk('x', 'b') == [['x', 'y', 'a', 'b']]

    def test_append_graph_with_shared_node(self) -> None:
        """Tests that a node is not connected to itself."""
        system = holden.System.from_edges([('a', 'b')])
        system.append(holden.System.from_edges([('b', 'c')]))
        assert system.contents == {'a': {'b'}, 'b': {'c'}, 'c': set()}

    def test_prepend_shared_nodes_are_not_connected_to_themselves(self) -> None:
        """Tests that prepending does not connect a node to itself."""
        system = holden.System.from_edges([('a', 'b')])
        system.prepend(holden.System.from_edges([('x', 'a')]))
        assert system.contents == {'a': {'b'}, 'b': set(), 'x': {'a'}}
        system = holden.System.from_edges([('a', 'b')])
        system.prepend('a')
        assert system.contents == {'a': {'b'}, 'b': set()}

    def test_append_to_empty(self) -> None:
        """Tests appending to an empty graph."""
        system = holden.System()
        system.append('a')
        assert system.contents == {'a': set()}
        system = holden.System()
        system.prepend(holden.System.from_edges([('a', 'b')]))
        assert system.contents == {'a': {'b'}, 'b': set()}

    def test_edges_cannot_store_lone_node(self) -> None:
        """Tests that a lone node cannot be appended to an empty edge list."""
        graph = DirectedEdges()
        with pytest.raises(ValueError, match = 'by itself'):
            graph.append('a')
        with pytest.raises(ValueError, match = 'by itself'):
            graph.prepend('a')

    def test_append_invalid(self) -> None:
        """Tests that an unrecognized item raises an error."""
        system = make_system()
        with pytest.raises(TypeError):
            system.append({'a': 1})
        with pytest.raises(TypeError):
            system.prepend({'a': 1})
        assert system.contents == make_system().contents

    def test_operators(self) -> None:
        """Tests `+`, `+=`, and reflected `+`."""
        system = make_system()
        result = system + 'z'
        assert result is system
        assert system['b'] == {'z'}
        system = make_system()
        system += 'z'
        assert system['d'] == {'z'}
        system = make_system()
        result = 'z' + system
        assert result is system
        assert system['z'] == {'a', 'c'}
        system = make_system()
        system += holden.System.from_edges([('x', 'y')])
        assert system['b'] == {'x'}
        system = make_system()
        assert ['x', 'y'] + system is system
        assert system['y'] == {'a', 'c'}

    def test_append_extra_arguments_reach_add(self) -> None:
        """Tests that keyword arguments are passed on to `add`."""
        received: dict[str, Any] = {}

        @dataclasses.dataclass
        class Recording(holden.System):
            def _add(self, item: Any, **kwargs: Any) -> None:
                received.update(kwargs)
                super()._add(item)

        graph = Recording.from_edges([('a', 'b')])
        graph.append('c', option = 1)
        assert received == {'option': 1}


class TestExportable:
    """Tests for `Exportable`."""

    def test_to_dot(self, tmp_path: pathlib.Path) -> None:
        """Tests `to_dot`."""
        system = make_system()
        dot = system.to_dot()
        assert dot == 'digraph system {\na -> b\nc -> d\n}\n'
        assert system.to_dot(name = 'graph one').startswith(
            'digraph "graph one" {')
        path = tmp_path / 'system.dot'
        assert system.to_dot(path = path, settings = {'rankdir': 'LR'}) == (
            'digraph system {\nrankdir=LR;\na -> b\nc -> d\n}\n')
        assert path.read_text() == (
            'digraph system {\nrankdir=LR;\na -> b\nc -> d\n}\n')

    def test_to_mermaid(self, tmp_path: pathlib.Path) -> None:
        """Tests `to_mermaid`."""
        system = make_system()
        mermaid = system.to_mermaid(name = 'flow')
        assert mermaid == (
            '---\ntitle: flow\n---\nflowchart LR\n'
            '    a(a) --> b(b)\n    c(c) --> d(d)\n')
        assert system.to_mermaid().startswith('---\ntitle: system\n')
        path = tmp_path / 'system.mermaid'
        system.to_mermaid(path = path, name = 'flow')
        assert path.read_text() == mermaid

    def test_other_composites_are_exportable(self) -> None:
        """Tests `to_dot` for the `Serial` and `Parallel` composites."""
        assert holden.Serial(['a', 'b']).to_dot() == (
            'digraph serial {\na -> b\n}\n')
        assert holden.Parallel([['a', 'b'], ['a', 'c']]).to_dot(name = 'p') == (
            'digraph p {\na -> b\na -> c\n}\n')


class TestFungible:
    """Tests for `Fungible`."""

    def test_properties(self) -> None:
        """Tests the properties that convert to each form."""
        system = make_system()
        assert system.adjacency is system
        assert isinstance(system.edges, holden.Edges)
        assert system.edges.contents == [('a', 'b'), ('c', 'd')]
        assert isinstance(system.matrix, holden.Matrix)
        assert system.matrix.labels == ['a', 'b', 'c', 'd']
        assert isinstance(system.parallel, holden.Parallel)
        assert system.parallel.contents == [['a', 'b'], ['c', 'd']]
        assert isinstance(system.serial, holden.Serial)
        assert system.serial.contents == ['a', 'b', 'c', 'd']

    def test_from_every_form(
            self,
            edges: list[tuple[str, str]],
            adjacency: dict[str, set[str]],
            matrix: tuple[list[list[int]], list[str]]) -> None:
        """Tests creating a `System` from each form."""
        expected = holden.System(adjacency)
        assert holden.System.from_edges(edges) == expected
        assert holden.System.from_adjacency(adjacency) == expected
        assert holden.System.from_matrix(matrix) == expected
        assert holden.System.from_parallel(
            [['a', 'b'], ['a', 'd', 'e'], ['c', 'd', 'e']]) == expected
        assert holden.System.from_serial(['a', 'b', 'c']) == holden.System(
            {'a': {'b'}, 'b': {'c'}, 'c': set()})

    def test_from_composite_instances(
            self,
            edges: list[tuple[str, str]],
            adjacency: dict[str, set[str]],
            matrix: tuple[list[list[int]], list[str]]) -> None:
        """Tests that instances of each composite class can be used."""
        expected = holden.System(adjacency)
        assert holden.System.from_edges(holden.Edges(edges)) == expected
        assert holden.System.from_matrix(
            holden.Matrix(matrix[0], matrix[1])) == expected
        assert holden.System.from_adjacency(
            holden.System(adjacency)) == expected
        assert holden.System.from_parallel(holden.Parallel(
            [['a', 'b'], ['a', 'd', 'e'], ['c', 'd', 'e']])) == expected
        assert holden.System.from_serial(holden.Serial(['a', 'b'])) == (
            holden.System({'a': {'b'}, 'b': set()}))

    def test_from_wrong_form(self, adjacency: dict[str, set[str]]) -> None:
        """Tests that a `from_{form}` method checks the form of its argument."""
        with pytest.raises(TypeError, match = 'edges'):
            holden.System.from_edges(adjacency)  # type: ignore[arg-type]
        with pytest.raises(TypeError, match = 'adjacency'):
            holden.System.from_adjacency([('a', 'b')])  # type: ignore[arg-type]
        with pytest.raises(TypeError):
            holden.System.from_serial('abc')  # type: ignore[arg-type]

    def test_from_empty(self) -> None:
        """Tests that an empty `list` can be any form that is a `list`."""
        for method in (
                holden.System.from_edges,
                holden.System.from_parallel,
                holden.System.from_serial):
            assert method([]).contents == {}
        assert holden.System.from_adjacency({}).contents == {}
        assert holden.System.from_matrix(([], [])).contents == {}
        assert holden.Serial.from_serial([]).contents == []

    def test_from_same_form_copies(self) -> None:
        """Tests that the new instance does not share containers."""
        adjacency = {'a': {'b'}, 'b': set()}
        system = holden.System.from_adjacency(adjacency)
        system.connect(('b', 'a'))
        assert adjacency == {'a': {'b'}, 'b': set()}
        original = holden.System({'a': {'b'}, 'b': set()})
        copied = holden.System.from_adjacency(original)
        copied.connect(('b', 'a'))
        assert original['b'] == set()
        matrix = holden.Matrix([[0, 1], [0, 0]], ['a', 'b'])
        copied_matrix = FungibleMatrix.from_matrix(matrix)
        copied_matrix.connect(('b', 'a'))
        copied_matrix.add('c')
        assert matrix.contents == [[0, 1], [0, 0]]
        assert matrix.labels == ['a', 'b']

    def test_other_forms_are_fungible(self) -> None:
        """Tests `Fungible` with the edge list and matrix forms."""
        edges = FungibleEdges.from_adjacency({'a': {'b'}, 'b': set()})
        assert edges.contents == [('a', 'b')]
        matrix = FungibleMatrix.from_edges([('a', 'b')])
        assert matrix.contents == [[0, 1], [0, 0]]
        assert matrix.labels == ['a', 'b']
        assert matrix.edges.contents == [('a', 'b')]
        assert matrix.matrix is matrix
        assert edges.serial.contents == ['a', 'b']

    def test_instance_class_is_kept(self) -> None:
        """Tests that a subclass creates instances of itself."""
        @dataclasses.dataclass
        class Custom(holden.System):
            pass

        assert type(Custom.from_edges([('a', 'b')])) is Custom

    def test_unregistered_class(self) -> None:
        """Tests that `Fungible` needs a recognized form."""
        @dataclasses.dataclass
        class Unrecognized(holden.Fungible):
            contents: list = dataclasses.field(default_factory = list)

        with pytest.raises(TypeError):
            Unrecognized.from_edges([('a', 'b')])


class TestLabeled:
    """Tests for `Labeled`."""

    def test_names(self) -> None:
        """Tests how a name is chosen."""
        assert holden.Labeled().name == 'none'
        assert holden.Labeled(name = 'set').name == 'set'
        assert holden.Labeled(contents = 'text').name == 'text'
        assert holden.Labeled(contents = 5).name == 'int'
        assert holden.Labeled(contents = [1]).name == 'list'
        assert Something().name == 'something'
        assert Something(name = 'other').name == 'other'
        assert AnotherThing().name == 'another_thing'

    def test_custom_namify(self) -> None:
        """Tests overriding `_namify`."""
        @dataclasses.dataclass
        class Shouting(holden.Labeled):
            def _namify(self) -> str:
                return 'LOUD'

        assert Shouting().name == 'LOUD'
        assert Shouting(name = 'quiet').name == 'quiet'

    def test_hash_and_equality(self) -> None:
        """Tests that labeled objects are compared by name."""
        assert hash(holden.Labeled(name = 'a')) == hash('a')
        assert holden.Labeled(name = 'a') == holden.Labeled(name = 'a')
        assert holden.Labeled(name = 'a') != holden.Labeled(name = 'b')
        assert holden.Labeled(name = 'a') == 'a'
        assert holden.Labeled(name = 'a') != 'b'
        assert holden.Labeled(name = 'a') != 5
        assert 'a' in {holden.Labeled(name = 'a')}
        assert holden.Labeled(name = 'a') in {'a'}

    def test_post_init_chaining(self) -> None:
        """Tests that `__post_init__` of other classes is called."""
        calls: list[str] = []

        @dataclasses.dataclass
        class Base:
            def __post_init__(self) -> None:
                calls.append('base')

        @dataclasses.dataclass
        class Both(holden.Labeled, Base):
            pass

        assert Both().name == 'none'
        assert calls == ['base']


class TestStorage:
    """Tests for `Storage`."""

    @dataclasses.dataclass
    class Library(holden.Storage, holden.System):
        """System that stores data for its nodes."""

    def test_store_and_retrieve(self) -> None:
        """Tests `store`, `retrieve`, and `discard`."""
        library = self.Library.from_edges([('a', 'b')])
        assert library.library == {}
        library.store('a', {'weight': 3})
        assert library.retrieve('a') == {'weight': 3}
        assert library.library == {'a': {'weight': 3}}
        library.store('a', 'replaced')
        assert library.retrieve('a') == 'replaced'
        library.discard('a')
        library.discard('a')
        with pytest.raises(KeyError, match = 'no data'):
            library.retrieve('a')

    def test_store_requires_node(self) -> None:
        """Tests that data can only be stored for nodes in the graph."""
        library = self.Library.from_edges([('a', 'b')])
        with pytest.raises(KeyError, match = 'not in'):
            library.store('z', 1)

    def test_libraries_are_not_shared(self) -> None:
        """Tests that every instance gets its own library."""
        first = self.Library()
        second = self.Library()
        first.add('a')
        first.store('a', 1)
        assert second.library == {}

    def test_storage_by_itself(self) -> None:
        """Tests that `Storage` works without a composite data structure."""
        @dataclasses.dataclass
        class Plain(holden.Storage):
            pass

        plain = Plain()
        plain.store('anything', 1)
        assert plain.retrieve('anything') == 1


class TestWeighted:
    """Tests for `Weighted`."""

    def test_weight(self) -> None:
        """Tests the `weight` attribute."""
        @dataclasses.dataclass
        class WeightedNode(holden.Weighted, holden.Node):
            pass

        node = WeightedNode()
        assert node.weight == 1.0
        assert float(node) == 1.0
        node = WeightedNode(weight = 2)
        assert float(node) == 2.0
        assert isinstance(float(node), float)

    def test_weighted_edge(self) -> None:
        """Tests adding a weight to an `Edge` subclass."""
        @dataclasses.dataclass(frozen = True)
        class WeightedEdge(holden.Edge):
            weight: float = 1.0

        edge = WeightedEdge('a', 'b', 2.5)
        assert len(edge) == 2
        assert tuple(edge) == ('a', 'b')
        assert edge.weight == 2.5
        assert holden.check.is_edge(edge)
        graph = holden.Edges()
        graph.connect(edge)
        assert graph.contents == [edge]
        assert holden.transform(graph, 'adjacency') == {'a': {'b'}, 'b': set()}
