"""Tests for `holden.composites`."""

from __future__ import annotations

import pytest

import holden


def test_registration() -> None:
    """Tests that `Parallel` and `Serial` are registered forms."""
    assert holden.Forms.registry['parallel'] is holden.Parallel
    assert holden.Forms.registry['serial'] is holden.Serial


class TestSerial:
    """Tests for `Serial`."""

    def test_defaults(self) -> None:
        """Tests default values."""
        serial = holden.Serial()
        assert serial.contents == []
        assert len(serial) == 0
        assert serial.root == []
        assert serial.endpoint == []
        assert serial.nodes == set()

    def test_nodes_root_endpoint(self) -> None:
        """Tests `nodes`, `root`, and `endpoint`."""
        serial = holden.Serial(['a', 'b', 'c'])
        assert serial.nodes == {'a', 'b', 'c'}
        assert serial.root == ['a']
        assert serial.endpoint == ['c']
        assert 'b' in serial
        assert 'z' not in serial

    def test_add_delete(self) -> None:
        """Tests `add` and `delete`."""
        serial = holden.Serial(['a'])
        serial.add('b')
        assert serial.contents == ['a', 'b']
        with pytest.raises(ValueError, match = 'already'):
            serial.add('a')
        with pytest.raises(TypeError):
            serial.add(['a'])
        serial.delete('a')
        assert serial.contents == ['b']
        with pytest.raises(KeyError):
            serial.delete('a')

    def test_delete_removes_every_occurrence(self) -> None:
        """Tests that `delete` removes a node that appears more than once."""
        serial = holden.Serial(['a', 'b', 'a'])
        serial.delete('a')
        assert serial.contents == ['b']

    def test_append_and_prepend(self) -> None:
        """Tests `append` and `prepend` with nodes and other composites."""
        serial = holden.Serial(['b'])
        serial.append('c')
        serial.prepend('a')
        assert serial.contents == ['a', 'b', 'c']
        serial.append(['d', 'e'])
        serial.prepend(holden.Serial(['x', 'y']))
        assert serial.contents == ['x', 'y', 'a', 'b', 'c', 'd', 'e']
        serial.append(('t', 'u'))
        assert serial.contents[-1] == ('t', 'u')
        with pytest.raises(TypeError):
            serial.append({'a': 1})
        with pytest.raises(TypeError):
            serial.prepend({'a': 1})

    def test_append_ignores_attachment(self) -> None:
        """Tests that `attachment` is accepted, but paths attach at the end."""
        serial = holden.Serial(['a', 'b'])
        serial.append('c', attachment = 'a')
        assert serial.contents == ['a', 'b', 'c']
        parallel = holden.Parallel([['a'], ['b']])
        parallel.append('c', attachment = 'a')
        assert parallel.contents == [['a', 'c'], ['b', 'c']]

    def test_append_graph(self) -> None:
        """Tests appending a graph, which adds the nodes of each path."""
        serial = holden.Serial(['a'])
        serial.append({'b': {'c'}, 'c': set()})
        assert serial.contents == ['a', 'b', 'c']

    def test_operators(self) -> None:
        """Tests `+` and `+=`."""
        serial = holden.Serial(['a'])
        result = serial + 'b'
        assert result is serial
        assert serial.contents == ['a', 'b']
        serial += ['c']
        assert serial.contents == ['a', 'b', 'c']
        prefixed = ['x'] + serial
        assert prefixed is serial
        assert serial.contents == ['x', 'a', 'b', 'c']

    def test_merge(self) -> None:
        """Tests `merge`."""
        serial = holden.Serial(['a'])
        serial.merge(['b', 'c'])
        serial.merge(holden.Serial(['d']))
        serial.merge({'e': {'f'}, 'f': set()})
        assert serial.contents == ['a', 'b', 'c', 'd', 'e', 'f']
        with pytest.raises(TypeError):
            serial.merge('a')

    def test_subset(self) -> None:
        """Tests `subset`."""
        serial = holden.Serial(['a', 'b', 'c', 'd'])
        assert serial.subset(include = ['a', 'c']).contents == ['a', 'c']
        assert serial.subset(exclude = ['b']).contents == ['a', 'c', 'd']
        assert serial.subset(include = ['a', 'b'],
            exclude = ['a']).contents == [
            'b']
        assert type(serial.subset(include = 'a')) is holden.Serial
        assert serial.contents == ['a', 'b', 'c', 'd']
        with pytest.raises(ValueError, match = 'include or exclude'):
            serial.subset()
        with pytest.raises(ValueError, match = 'include'):
            serial.subset(include = ['z'])

    def test_walk(self) -> None:
        """Tests `walk`."""
        serial = holden.Serial(['a', 'b', 'c', 'd'])
        assert serial.walk() == [['a', 'b', 'c', 'd']]
        assert serial.walk(start = 'b') == [['b', 'c', 'd']]
        assert serial.walk(stop = 'c') == [['a', 'b', 'c']]
        assert serial.walk('b', 'c') == [['b', 'c']]
        assert serial.walk('c', 'b') == []

    def test_indexing(self) -> None:
        """Tests access by index, slice, and name."""
        serial = holden.Serial(['a', 'b', 'c'])
        assert serial[0] == 'a'
        assert serial[-1] == 'c'
        assert serial[0:2] == ['a', 'b']
        assert serial['b'] == 'b'
        with pytest.raises(KeyError):
            serial['z']

    def test_conversions(self) -> None:
        """Tests `Fungible` properties."""
        serial = holden.Serial(['a', 'b', 'c'])
        assert serial.serial is serial
        assert serial.parallel.contents == [['a', 'b', 'c']]
        assert serial.adjacency.contents == {
            'a': {'b'}, 'b': {'c'}, 'c': set()}
        assert serial.edges.contents == [('a', 'b'), ('b', 'c')]
        assert serial.matrix.labels == ['a', 'b', 'c']

    def test_from_forms(self) -> None:
        """Tests the `Fungible` class methods."""
        assert holden.Serial.from_edges([('a', 'b'), ('b', 'c')]).contents == [
            'a', 'b', 'c']
        assert holden.Serial.from_adjacency(
            {'a': {'b'}, 'b': set()}).contents == [
            'a', 'b']
        assert holden.Serial.from_parallel([['a', 'b']]).contents == ['a', 'b']
        assert holden.Serial.from_serial(['a']).contents == ['a']
        assert holden.Serial.from_matrix(
            ([[0, 1], [0, 0]], ['a', 'b'])).contents == [
            'a', 'b']

    def test_equality(self) -> None:
        """Tests that serials with the same nodes are equal."""
        assert holden.Serial(['a']) == holden.Serial(['a'])
        assert holden.Serial(['a']) != holden.Serial(['b'])


class TestParallel:
    """Tests for `Parallel`."""

    PATHS = [['a', 'b'], ['a', 'd', 'e'], ['c', 'd', 'e']]

    def make(self) -> holden.Parallel:
        """Returns a `Parallel` with three paths."""
        return holden.Parallel([list(path) for path in self.PATHS])

    def test_defaults(self) -> None:
        """Tests default values."""
        parallel = holden.Parallel()
        assert parallel.contents == []
        assert parallel.nodes == set()
        assert parallel.root == []
        assert parallel.endpoint == []

    def test_nodes_root_endpoint(self) -> None:
        """Tests `nodes`, `root`, and `endpoint`."""
        parallel = self.make()
        assert parallel.nodes == {'a', 'b', 'c', 'd', 'e'}
        assert parallel.root == ['a', 'c']
        assert parallel.endpoint == ['b', 'e']
        assert 'd' in parallel
        assert 'z' not in parallel

    def test_nodes_with_serial_paths(self) -> None:
        """Tests that paths can be `Serial` instances."""
        parallel = holden.Parallel([holden.Serial(['a', 'b']), ['c']])
        assert parallel.nodes == {'a', 'b', 'c'}
        assert parallel.root == ['a', 'c']

    def test_add(self) -> None:
        """Tests `add` with a node and with a path."""
        parallel = self.make()
        parallel.add('z')
        assert parallel.contents[-1] == ['z']
        parallel.add(['x', 'y'])
        assert parallel.contents[-1] == ['x', 'y']
        parallel.add(holden.Serial(['w']))
        assert len(parallel) == 6
        with pytest.raises(ValueError, match = 'already'):
            parallel.add('z')
        with pytest.raises(ValueError, match = 'path'):
            parallel.add([])
        with pytest.raises(ValueError, match = 'path'):
            parallel.add([['nested']])
        with pytest.raises(TypeError):
            parallel.add({'a': 1})

    def test_delete(self) -> None:
        """Tests that `delete` removes a node from every path."""
        parallel = self.make()
        parallel.delete('d')
        assert parallel.contents == [['a', 'b'], ['a', 'e'], ['c', 'e']]
        parallel.delete('b')
        assert parallel.contents == [['a'], ['a', 'e'], ['c', 'e']]
        with pytest.raises(KeyError):
            parallel.delete('d')

    def test_delete_removes_empty_paths_and_edits_serials(self) -> None:
        """Tests deleting a node from a path with one node or a `Serial`."""
        parallel = holden.Parallel([holden.Serial(['a', 'b']), ['c']])
        parallel.delete('c')
        assert len(parallel) == 1
        parallel.delete('b')
        assert parallel.contents[0].contents == ['a']

    def test_append(self) -> None:
        """Tests `append`."""
        parallel = self.make()
        parallel.append('z')
        assert parallel.contents == [
            ['a', 'b', 'z'], ['a', 'd', 'e', 'z'], ['c', 'd', 'e', 'z']]
        parallel = holden.Parallel([['a'], ['b']])
        parallel.append([['x', 'y'], ['z']])
        assert parallel.contents == [
            ['a', 'x', 'y'], ['a', 'z'], ['b', 'x', 'y'], ['b', 'z']]
        parallel = holden.Parallel()
        parallel.append(['a', 'b'])
        assert parallel.contents == [['a', 'b']]
        parallel.append([])
        assert parallel.contents == [['a', 'b']]
        parallel.append(holden.Serial(['c']))
        assert parallel.contents == [['a', 'b', 'c']]

    def test_prepend(self) -> None:
        """Tests `prepend`."""
        parallel = self.make()
        parallel.prepend('z')
        assert parallel.contents == [
            ['z', 'a', 'b'], ['z', 'a', 'd', 'e'], ['z', 'c', 'd', 'e']]
        parallel = holden.Parallel([['a'], ['b']])
        parallel.prepend([['x'], ['y', 'z']])
        assert parallel.contents == [
            ['x', 'a'], ['x', 'b'], ['y', 'z', 'a'], ['y', 'z', 'b']]
        parallel = holden.Parallel()
        parallel.prepend('a')
        assert parallel.contents == [['a']]
        parallel.prepend([])
        assert parallel.contents == [['a']]

    def test_append_and_prepend_reject_bad_items(self) -> None:
        """Tests that `append` and `prepend` raise for an invalid item."""
        parallel = self.make()
        with pytest.raises(TypeError):
            parallel.append({'a': 1})
        with pytest.raises(TypeError):
            parallel.prepend({'a': 1})
        assert parallel.contents == self.make().contents

    def test_merge(self) -> None:
        """Tests `merge`."""
        parallel = holden.Parallel([['a', 'b']])
        parallel.merge([['c', 'd']])
        parallel.merge(holden.Parallel([['e']]))
        parallel.merge({'f': {'g'}, 'g': set()})
        assert parallel.contents == [
            ['a', 'b'], ['c', 'd'], ['e'], ['f', 'g']]
        with pytest.raises(TypeError):
            parallel.merge(5)

    def test_merge_copies_paths(self) -> None:
        """Tests that a merged path is not shared with the original."""
        other = [['c', 'd']]
        parallel = holden.Parallel()
        parallel.merge(other)
        other[0].append('e')
        assert parallel.contents == [['c', 'd']]

    def test_subset(self) -> None:
        """Tests `subset`."""
        parallel = self.make()
        assert parallel.subset(include = ['a', 'b', 'e']).contents == [
            ['a', 'b'], ['a', 'e'], ['e']]
        assert parallel.subset(exclude = ['a', 'b']).contents == [
            ['d', 'e'], ['c', 'd', 'e']]
        assert parallel.subset(exclude = ['a', 'b', 'd', 'e']).contents == [
            ['c']]
        assert type(parallel.subset(include = 'a')) is holden.Parallel
        assert parallel.contents == self.PATHS
        with pytest.raises(ValueError, match = 'include or exclude'):
            parallel.subset()

    def test_walk(self) -> None:
        """Tests `walk`."""
        parallel = self.make()
        assert parallel.walk() == self.PATHS
        assert parallel.walk('a') == [['a', 'b'], ['a', 'd', 'e']]
        assert parallel.walk(stop = 'e') == [['a', 'd', 'e'], ['c', 'd', 'e']]
        assert parallel.walk('a', 'e') == [['a', 'd', 'e']]
        assert parallel.walk(['a', 'c'], ['e']) == [
            ['a', 'd', 'e'], ['c', 'd', 'e']]

    def test_conversions(self) -> None:
        """Tests `Fungible` properties."""
        parallel = self.make()
        assert parallel.parallel is parallel
        assert parallel.adjacency.contents == {
            'a': {'b', 'd'}, 'b': set(), 'd': {'e'}, 'e': set(), 'c': {'d'}}
        assert parallel.serial.contents == [
            'a', 'b', 'a', 'd', 'e', 'c', 'd', 'e']
        assert parallel.edges.nodes == parallel.nodes
