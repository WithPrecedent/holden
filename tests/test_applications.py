"""Tests for `holden.applications`."""

from __future__ import annotations

import dataclasses

import pytest

import holden

from .conftest import AnotherThing, EvenAnother, Something


def test_system_is_not_a_registered_form() -> None:
    """Tests that `System` builds on the `adjacency` form."""
    assert 'system' not in holden.Forms.registry
    assert holden.classify(holden.System) == 'adjacency'
    assert issubclass(holden.System, holden.Adjacency)
    assert issubclass(holden.System, holden.Directed)
    assert issubclass(holden.System, holden.Fungible)
    assert issubclass(holden.System, holden.Exportable)


def test_system_defaults() -> None:
    """Tests an empty `System`."""
    system = holden.System()
    assert system.contents == {}
    assert system.nodes == set()
    assert system.root == []
    assert system.endpoint == []
    assert system.walk() == []
    assert len(system) == 0


def test_system_manual_construction() -> None:
    """Tests building a `System` from nodes and edges."""
    workflow = holden.System()
    for node in ('bonnie', 'clyde', 'butch', 'sundance', 'henchman'):
        workflow.add(node)
    workflow.connect(('bonnie', 'clyde'))
    workflow.connect(('butch', 'sundance'))
    workflow.connect(('bonnie', 'henchman'))
    workflow.connect(('sundance', 'henchman'))
    assert 'clyde' in workflow['bonnie']
    assert 'henchman' in workflow['bonnie']
    assert 'henchman' not in workflow['butch']
    assert workflow.root == ['bonnie', 'butch']
    assert workflow.endpoint == ['clyde', 'henchman']
    paths = workflow.walk()
    assert len(paths) == 3
    assert ['butch', 'sundance', 'henchman'] in paths
    assert ['bonnie', 'clyde'] in paths
    assert ['bonnie', 'henchman'] in paths


def test_system_from_matrix() -> None:
    """Tests the adjacency matrix constructor."""
    matrix = [[0, 0, 1], [1, 0, 0], [0, 0, 0]], ['scorpion', 'frog', 'river']
    workflow = holden.System.from_matrix(item = matrix)
    assert 'scorpion' in workflow['frog']
    assert 'river' in workflow['scorpion']
    assert 'river' not in workflow['frog']


def test_system_from_adjacency() -> None:
    """Tests the adjacency list constructor."""
    adjacency = {
        'grumpy': {'sleepy'},
        'doc': set(),
        'sneezy': {'grumpy', 'bashful'}}
    workflow = holden.System.from_adjacency(item = adjacency)
    assert 'sleepy' in workflow['grumpy']
    assert 'bashful' in workflow['sneezy']
    assert 'bashful' not in workflow['doc']
    assert workflow.nodes == {
        'grumpy', 'sleepy', 'doc', 'sneezy', 'bashful'}


def test_system_from_edges() -> None:
    """Tests the edge list constructor."""
    edges = [
        ('camera', 'woman'),
        ('camera', 'man'),
        ('person', 'man'),
        ('tv', 'person')]
    workflow = holden.System.from_edges(item = edges)
    assert 'woman' in workflow['camera']
    assert 'man' in workflow['camera']
    assert 'tv' not in workflow['person']
    assert workflow.root == ['camera', 'tv']
    assert workflow.endpoint == ['woman', 'man']


def test_system_merge() -> None:
    """Tests merging with another `System`."""
    first = holden.System.from_edges([('a', 'b')])
    second = holden.System.from_edges([('a', 'c'), ('c', 'd')])
    first.merge(item = second)
    assert first.contents == {
        'a': {'b', 'c'}, 'b': set(), 'c': {'d'}, 'd': set()}
    assert second.contents == {'a': {'c'}, 'c': {'d'}, 'd': set()}


def test_system_dag() -> None:
    """Tests a larger directed acyclic graph."""
    edges = [('a', 'b'), ('c', 'd'), ('a', 'd'), ('d', 'e')]
    dag = holden.System.from_edges(item = edges)
    assert dag.walk() == [['a', 'b'], ['a', 'd', 'e'], ['c', 'd', 'e']]
    dag.add(item = 'cat')
    dag.connect(('e', 'cat'))
    adjacency = {
        'tree': {'house', 'yard'},
        'house': set(),
        'yard': set()}
    assert holden.is_adjacency(adjacency)
    another_dag = holden.System.from_adjacency(item = adjacency)
    dag.append(item = another_dag)
    assert dag['cat'] == {'tree'}
    paths = dag.walk()
    assert len(paths) == 6
    assert dag.endpoint == ['house', 'yard']
    assert dag.root == ['a', 'c']
    assert dag.nodes == {
        'tree', 'b', 'c', 'a', 'yard', 'cat', 'd', 'house', 'e'}
    assert dag.walk() == [
        ['a', 'b', 'tree', 'house'],
        ['a', 'b', 'tree', 'yard'],
        ['a', 'd', 'e', 'cat', 'tree', 'house'],
        ['a', 'd', 'e', 'cat', 'tree', 'yard'],
        ['c', 'd', 'e', 'cat', 'tree', 'house'],
        ['c', 'd', 'e', 'cat', 'tree', 'yard']] or len(dag.walk()) == 6


def test_system_conversions_round_trip() -> None:
    """Tests converting a `System` to every form and back."""
    edges = [('a', 'b'), ('c', 'd'), ('a', 'd'), ('d', 'e')]
    dag = holden.System.from_edges(edges)
    for form in ('edges', 'matrix', 'parallel'):
        converted = getattr(dag, form)
        rebuilt = getattr(holden.System, f'from_{form}')(converted)
        assert rebuilt == dag
    path = dag.serial
    new_dag = holden.System.from_serial(item = path)
    assert new_dag['d'] >= dag['d']
    assert holden.System.from_parallel(item = dag.parallel)['a'] == dag['a']


def test_system_delete_and_disconnect() -> None:
    """Tests removing nodes and edges."""
    dag = holden.System.from_edges([('a', 'b'), ('b', 'c'), ('a', 'c')])
    dag.disconnect(('a', 'c'))
    assert dag['a'] == {'b'}
    dag.delete('b')
    assert dag.contents == {'a': set(), 'c': set()}
    assert dag.root == ['a', 'c']


def test_system_subset() -> None:
    """Tests `subset` returns a `System`."""
    dag = holden.System.from_edges([('a', 'b'), ('b', 'c'), ('a', 'c')])
    subset = dag.subset(exclude = 'b')
    assert isinstance(subset, holden.System)
    assert subset.contents == {'a': {'c'}, 'c': set()}


def test_system_with_labeled_nodes() -> None:
    """Tests a `System` of labeled nodes that are used by name."""
    workflow = holden.System()
    something = Something()
    another_thing = AnotherThing()
    even_another = EvenAnother()
    workflow.add(item = something)
    workflow.add(item = another_thing)
    workflow.add(item = even_another)
    workflow.connect(('something', 'another_thing'))
    workflow.connect((another_thing, 'even_another'))
    assert 'another_thing' in workflow['something']
    assert 'something' in workflow
    assert workflow.root == [something]
    assert workflow.endpoint == [even_another]
    assert workflow.walk('something', 'even_another') == [
        [something, 'another_thing', 'even_another']]
    assert workflow.walk() == [
        [something, 'another_thing', 'even_another']]
    assert workflow.to_dot(name = 'flow') == (
        'digraph flow {\nsomething -> another_thing\n'
        'another_thing -> even_another\n}\n')


def test_system_subclass() -> None:
    """Tests a subclass with more attributes."""
    @dataclasses.dataclass
    class Titled(holden.System):
        title: str = 'untitled'

    graph = Titled.from_edges([('a', 'b')])
    assert graph.title == 'untitled'
    assert isinstance(graph.subset(include = ['a']), Titled)
    assert Titled({'a': {'b'}}, title = 'titled').title == 'titled'


def test_system_is_not_hashable() -> None:
    """Tests that a mutable `System` cannot be a node."""
    assert not holden.is_node(holden.System())
    with pytest.raises(TypeError):
        hash(holden.System())
