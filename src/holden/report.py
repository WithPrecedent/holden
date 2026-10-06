"""Inspection tools for composite data structures.

A root is a node that no other node connects to. An endpoint is a node that
does not connect to any other node. A node with no edges is both a root and an
endpoint.

Contents:
    get_endpoints: returns endpoint(s) for any recognized composite form.
    get_roots: returns root(s) for any recognized composite form.
    get_endpoints_adjacency: returns endpoint(s) for an adjacency list.
    get_roots_adjacency: returns root(s) for an adjacency list.
    get_endpoints_edges: returns endpoint(s) for an edge list.
    get_roots_edges: returns root(s) for an edge list.
    get_endpoints_matrix: returns endpoint(s) for an adjacency matrix.
    get_roots_matrix: returns root(s) for an adjacency matrix.
    get_endpoints_parallel: returns endpoint(s) for a parallel structure.
    get_roots_parallel: returns root(s) for a parallel structure.
    get_endpoints_serial: returns endpoint(s) for a serial structure.
    get_roots_serial: returns root(s) for a serial structure.

"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from . import base, utilities, workshop

if TYPE_CHECKING:
    from collections.abc import Hashable, Mapping, MutableSequence

    from . import composites, graphs, kinds


def get_endpoints(item: Any) -> MutableSequence[Hashable]:
    """Returns the endpoints in any recognized composite form.

    Args:
        item: composite data structure or raw form to examine.

    Raises:
        NotImplementedError: if there is no endpoint function for the form of
            `item`.

    Returns:
        List of endpoints.

    """
    return _dispatch('endpoints', item)


def get_roots(item: Any) -> MutableSequence[Hashable]:
    """Returns the roots in any recognized composite form.

    Args:
        item: composite data structure or raw form to examine.

    Raises:
        NotImplementedError: if there is no root function for the form of
            `item`.

    Returns:
        List of roots.

    """
    return _dispatch('roots', item)


def get_endpoints_adjacency(
    item: graphs.Adjacency | kinds.RawAdjacency) -> MutableSequence[Hashable]:
    """Returns the endpoints in `item`.

    Args:
        item: adjacency list object to examine.

    Returns:
        List of endpoints in the order they appear in `item`.

    """
    item = utilities._rawify(item)
    return [n for n in _nodes_adjacency(item) if not item.get(n)]


def get_roots_adjacency(
    item: graphs.Adjacency | kinds.RawAdjacency) -> MutableSequence[Hashable]:
    """Returns the roots in `item`.

    Args:
        item: adjacency list object to examine.

    Returns:
        List of roots in the order they appear in `item`.

    """
    item = utilities._rawify(item)
    stops: set[Hashable] = set()
    for connections in item.values():
        stops.update(connections)
    return [n for n in _nodes_adjacency(item) if n not in stops]


def get_endpoints_edges(
    item: graphs.Edges | kinds.RawEdges) -> MutableSequence[Hashable]:
    """Returns the endpoints in `item`.

    Args:
        item: edge list object to examine.

    Returns:
        List of endpoints.

    """
    return get_endpoints_adjacency(
        item = workshop.edges_to_adjacency(item = item))


def get_roots_edges(
    item: graphs.Edges | kinds.RawEdges) -> MutableSequence[Hashable]:
    """Returns the roots in `item`.

    Args:
        item: edge list object to examine.

    Returns:
        List of roots.

    """
    return get_roots_adjacency(item = workshop.edges_to_adjacency(item = item))


def get_endpoints_matrix(
    item: graphs.Matrix | kinds.RawMatrix) -> MutableSequence[Hashable]:
    """Returns the endpoints in `item`.

    Args:
        item: adjacency matrix object to examine.

    Returns:
        List of endpoints.

    """
    return get_endpoints_adjacency(
        item = workshop.matrix_to_adjacency(item = item))


def get_roots_matrix(
    item: graphs.Matrix | kinds.RawMatrix) -> MutableSequence[Hashable]:
    """Returns the roots in `item`.

    Args:
        item: adjacency matrix object to examine.

    Returns:
        List of roots.

    """
    return get_roots_adjacency(item = workshop.matrix_to_adjacency(item = item))


def get_endpoints_parallel(
    item: composites.Parallel | kinds.RawParallel) -> MutableSequence[Hashable]:
    """Returns the endpoints in `item`.

    Args:
        item: parallel object to examine.

    Returns:
        List of the last node of each path (without duplicates).

    """
    item = utilities._rawify(item)
    return list(dict.fromkeys(path[-1] for path in map(_path, item) if path))


def get_roots_parallel(
    item: composites.Parallel | kinds.RawParallel) -> MutableSequence[Hashable]:
    """Returns the roots in `item`.

    Args:
        item: parallel object to examine.

    Returns:
        List of the first node of each path (without duplicates).

    """
    item = utilities._rawify(item)
    return list(dict.fromkeys(path[0] for path in map(_path, item) if path))


def get_endpoints_serial(
    item: composites.Serial | kinds.RawSerial) -> MutableSequence[Hashable]:
    """Returns the endpoints in `item`.

    Args:
        item: serial object to examine.

    Returns:
        List of the last node in `item` or an empty list if `item` is empty.

    """
    item = utilities._rawify(item)
    return [item[-1]] if item else []


def get_roots_serial(
    item: composites.Serial | kinds.RawSerial) -> MutableSequence[Hashable]:
    """Returns the roots in `item`.

    Args:
        item: serial object to examine.

    Returns:
        List of the first node in `item` or an empty list if `item` is empty.

    """
    item = utilities._rawify(item)
    return [item[0]] if item else []


def _dispatch(kind: str, item: Any) -> MutableSequence[Hashable]:
    """Calls the `get_{kind}_{form}` function that matches the form of `item`.

    Args:
        kind: either "roots" or "endpoints".
        item: composite data structure or raw form to examine.

    Raises:
        NotImplementedError: if there is no function for the form of `item`.

    Returns:
        List of the roots or endpoints of `item`.

    """
    form = base.classify(item)
    function = globals().get(f'get_{kind}_{form}')
    if function is None:
        raise NotImplementedError(f'get_{kind} does not support {form} forms')
    result: MutableSequence[Hashable] = function(item)
    return result


def _nodes_adjacency(
    item: Mapping[Hashable, set[Hashable]]) -> list[Hashable]:
    """Returns every node in an adjacency list, including dangling nodes.

    Args:
        item: raw adjacency list.

    Returns:
        Keys of `item` followed by any nodes that only appear as connections.

    """
    nodes = list(item)
    seen = set(nodes)
    for connections in item.values():
        for node in utilities._stabilize(connections):
            if node not in seen:
                seen.add(node)
                nodes.append(node)
    return nodes


def _path(item: Any) -> list[Hashable]:
    """Returns a raw list of the nodes in a serial path.

    Args:
        item: serial or raw list of nodes.

    Returns:
        List of nodes.

    """
    return list(utilities._rawify(item))
