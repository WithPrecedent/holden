"""Tests for `holden.workshop`."""

from __future__ import annotations

import itertools

import pytest

import holden
from holden import workshop

FORMS = ('adjacency', 'edges', 'matrix', 'parallel', 'serial')


def test_transformer_names() -> None:
    """Tests that a transformer exists for every pair of different forms."""
    for source, output in itertools.permutations(FORMS, 2):
        assert callable(getattr(workshop, f'{source}_to_{output}'))


def test_adjacency_to_edges(
        adjacency: dict[str, set[str]], edges: list[tuple[str, str]]) -> None:
    """Tests `adjacency_to_edges`."""
    result = workshop.adjacency_to_edges(adjacency)
    assert result == [('a', 'b'), ('a', 'd'), ('c', 'd'), ('d', 'e')]
    assert isinstance(result, list)
    assert holden.is_edges(result)
    assert sorted(result) == sorted(edges)
    assert workshop.adjacency_to_edges({}) == []
    assert workshop.adjacency_to_edges({'a': set()}) == []


def test_adjacency_to_matrix(
        adjacency: dict[str, set[str]],
        matrix: tuple[list[list[int]], list[str]]) -> None:
    """Tests `adjacency_to_matrix`."""
    assert workshop.adjacency_to_matrix(adjacency) == matrix
    assert holden.is_matrix(workshop.adjacency_to_matrix(adjacency))
    assert workshop.adjacency_to_matrix({}) == ([], [])


def test_adjacency_to_matrix_with_unlisted_node() -> None:
    """Tests that nodes that only appear as connections are included."""
    result = workshop.adjacency_to_matrix({'a': {'b'}})
    assert result == ([[0, 1], [0, 0]], ['a', 'b'])


def test_adjacency_to_parallel(adjacency: dict[str, set[str]]) -> None:
    """Tests `adjacency_to_parallel`."""
    assert workshop.adjacency_to_parallel(adjacency) == [
        ['a', 'b'], ['a', 'd', 'e'], ['c', 'd', 'e']]
    assert workshop.adjacency_to_parallel({}) == []
    assert workshop.adjacency_to_parallel({'a': set()}) == [['a']]
    assert workshop.adjacency_to_parallel({'a': {'b'}, 'b': {'a'}}) == []


def test_adjacency_to_serial(adjacency: dict[str, set[str]]) -> None:
    """Tests `adjacency_to_serial`."""
    assert workshop.adjacency_to_serial(
        {'a': {'b'}, 'b': {'c'}, 'c': set()}) == [
        'a', 'b', 'c']
    assert workshop.adjacency_to_serial(adjacency) == [
        'a', 'b', 'a', 'd', 'e', 'c', 'd', 'e']
    assert workshop.adjacency_to_serial({}) == []


def test_edges_to_adjacency(
        edges: list[tuple[str, str]], adjacency: dict[str, set[str]]) -> None:
    """Tests `edges_to_adjacency`."""
    result = workshop.edges_to_adjacency(edges)
    assert result == adjacency
    assert holden.is_adjacency(result)
    assert list(result) == ['a', 'b', 'c', 'd', 'e']
    assert workshop.edges_to_adjacency([]) == {}
    assert workshop.edges_to_adjacency(
        [holden.Edge('a', 'b')]) == {'a': {'b'}, 'b': set()}


def test_edges_to_others(
        edges: list[tuple[str, str]],
        adjacency: dict[str, set[str]],
        matrix: tuple[list[list[int]], list[str]]) -> None:
    """Tests `edges_to_matrix`, `edges_to_parallel`, and `edges_to_serial`."""
    assert workshop.edges_to_matrix(edges) == matrix
    assert workshop.edges_to_parallel(edges) == [
        ['a', 'b'], ['a', 'd', 'e'], ['c', 'd', 'e']]
    assert workshop.edges_to_serial(edges) == workshop.adjacency_to_serial(
        adjacency)


def test_matrix_to_adjacency(
        adjacency: dict[str, set[str]],
        matrix: tuple[list[list[int]], list[str]]) -> None:
    """Tests `matrix_to_adjacency`."""
    result = workshop.matrix_to_adjacency(matrix)
    assert result == adjacency
    assert holden.is_adjacency(result)
    assert workshop.matrix_to_adjacency(([], [])) == {}
    weighted = ([[0, 2.5], [0, 0]], ['a', 'b'])
    assert workshop.matrix_to_adjacency(weighted) == {'a': {'b'}, 'b': set()}


def test_matrix_to_adjacency_invalid() -> None:
    """Tests that a matrix with the wrong shape raises an error."""
    with pytest.raises(ValueError, match = 'square'):
        workshop.matrix_to_adjacency(([[0, 1], [0, 0]], ['a']))
    with pytest.raises(ValueError, match = 'square'):
        workshop.matrix_to_adjacency(([[0, 1], [0]], ['a', 'b']))


def test_matrix_to_others(
        edges: list[tuple[str, str]],
        matrix: tuple[list[list[int]], list[str]]) -> None:
    """Tests `matrix_to_edges`, `matrix_to_parallel`, and `matrix_to_serial`."""
    assert workshop.matrix_to_edges(matrix) == [
        ('a', 'b'), ('a', 'd'), ('c', 'd'), ('d', 'e')]
    assert workshop.matrix_to_parallel(matrix) == [
        ['a', 'b'], ['a', 'd', 'e'], ['c', 'd', 'e']]
    assert workshop.matrix_to_serial(matrix) == [
        'a', 'b', 'a', 'd', 'e', 'c', 'd', 'e']


def test_parallel_to_adjacency(adjacency: dict[str, set[str]]) -> None:
    """Tests `parallel_to_adjacency`."""
    paths = [['a', 'b'], ['a', 'd', 'e'], ['c', 'd', 'e']]
    assert workshop.parallel_to_adjacency(paths) == adjacency
    assert workshop.parallel_to_adjacency([]) == {}
    assert workshop.parallel_to_adjacency([['a']]) == {'a': set()}
    # A path can be a `Serial`
    assert workshop.parallel_to_adjacency(
        [holden.Serial(['a', 'b']), ['b', 'c']]) == {
            'a': {'b'}, 'b': {'c'}, 'c': set()}
    # Nodes that are in more than one path keep all of their connections
    assert workshop.parallel_to_adjacency(
        [['a', 'b'], ['b', 'c'], ['a', 'c']]) == {
        'a': {'b', 'c'}, 'b': {'c'}, 'c': set()}


def test_parallel_to_others(
        matrix: tuple[list[list[int]], list[str]]) -> None:
    """Tests conversions from a parallel structure."""
    paths = [['a', 'b'], ['a', 'd', 'e'], ['c', 'd', 'e']]
    # Nodes are in the order in which they first appear in the paths
    assert workshop.parallel_to_edges(paths) == [
        ('a', 'b'), ('a', 'd'), ('d', 'e'), ('c', 'd')]
    result = workshop.parallel_to_matrix(paths)
    assert result[1] == ['a', 'b', 'd', 'e', 'c']
    assert workshop.matrix_to_adjacency(result) == workshop.matrix_to_adjacency(
        matrix)
    assert workshop.parallel_to_serial(paths) == [
        'a', 'b', 'a', 'd', 'e', 'c', 'd', 'e']
    assert workshop.parallel_to_serial([['a', 'b']]) == ['a', 'b']
    assert workshop.parallel_to_serial([]) == []
    assert workshop.parallel_to_serial(
        [holden.Serial(['a']), ['b']]) == ['a', 'b']


def test_serial_to_adjacency() -> None:
    """Tests `serial_to_adjacency`."""
    assert workshop.serial_to_adjacency(['a', 'b', 'c']) == {
        'a': {'b'}, 'b': {'c'}, 'c': set()}
    assert workshop.serial_to_adjacency(['a']) == {'a': set()}
    assert workshop.serial_to_adjacency([]) == {}
    assert workshop.serial_to_adjacency('a') == {  # type: ignore[arg-type]
        'a': set()}
    assert workshop.serial_to_adjacency(5) == {  # type: ignore[arg-type]
        5: set()}
    assert workshop.serial_to_adjacency(holden.Serial(['a', 'b'])) == {
        'a': {'b'}, 'b': set()}
    assert workshop.serial_to_adjacency(['a', 'b', 'a']) == {
        'a': {'b'}, 'b': {'a'}}
    # A parallel structure is also accepted
    assert workshop.serial_to_adjacency(  # type: ignore[arg-type]
        [['a', 'b'], ['b', 'c']]) == {
        'a': {'b'}, 'b': {'c'}, 'c': set()}


def test_serial_to_others(matrix: tuple[list[list[int]], list[str]]) -> None:
    """Tests conversions from a serial structure."""
    assert workshop.serial_to_edges(['a', 'b', 'c']) == [
        ('a', 'b'), ('b', 'c')]
    assert workshop.serial_to_matrix(['a', 'b']) == (
        [[0, 1], [0, 0]], ['a', 'b'])
    assert workshop.serial_to_parallel(['a', 'b']) == [['a', 'b']]
    assert workshop.serial_to_parallel([]) == []
    original = ['a', 'b']
    assert workshop.serial_to_parallel(original)[0] is not original


def test_transformers_accept_composites(
        adjacency: dict[str, set[str]],
        matrix: tuple[list[list[int]], list[str]]) -> None:
    """Tests that transformers accept composite data structures."""
    assert workshop.adjacency_to_edges(holden.System(adjacency)) == [
        ('a', 'b'), ('a', 'd'), ('c', 'd'), ('d', 'e')]
    assert workshop.matrix_to_adjacency(
        holden.Matrix(matrix[0], matrix[1])) == adjacency
    assert workshop.edges_to_adjacency(
        holden.Edges([('a', 'b')])) == {'a': {'b'}, 'b': set()}
    assert workshop.serial_to_adjacency(holden.Serial(['a', 'b'])) == {
        'a': {'b'}, 'b': set()}


@pytest.mark.parametrize('source', FORMS)
@pytest.mark.parametrize('output', FORMS)
def test_round_trips_preserve_a_path(source: str, output: str) -> None:
    """Tests that converting a single path between forms keeps its order."""
    path = ['a', 'b', 'c']
    raw = workshop.serial_to_adjacency(path)
    converters = {
        'adjacency': lambda x: x,
        'edges': workshop.adjacency_to_edges,
        'matrix': workshop.adjacency_to_matrix,
        'parallel': workshop.adjacency_to_parallel,
        'serial': workshop.adjacency_to_serial}
    start = converters[source](raw)
    if source == output:
        return
    result = getattr(workshop, f'{source}_to_{output}')(start)
    assert converters[output](raw) == result


def test_add_transformer() -> None:
    """Tests `add_transformer`."""
    workshop.add_transformer('serial_to_thing', lambda item: ('thing', item))
    try:
        assert workshop.serial_to_thing(  # type: ignore[attr-defined]
            ['a']) == ('thing', ['a'])
        for name in ('thing', 'to_thing', 'serial_to_', '_to_thing'):
            with pytest.raises(ValueError, match = 'format'):
                workshop.add_transformer(name, lambda item: item)
    finally:
        del workshop.serial_to_thing  # type: ignore[attr-defined]
