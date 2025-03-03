"""Inspection tools for composite data structures.

Contents:
    get_endpoints_adjacency: returns endpoint(s) for an adjacency list.
    get_roots_adjacency: returns root(s) for an adjacency list.
    get_endpoints_edges: returns endpoint(s) for an edge list.
    get_roots_edges: returns root(s) for an edge list.
    get_endpoints_matrix: returns endpoint(s) for an adjacency matrix.
    get_roots_matrix: returns root(s) for an adjacency matrix.

To Do:
    Implement remaining functions.

"""
from __future__ import annotations

# import functools
import itertools
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Hashable, MutableSequence

    from . import composites, graphs


""" Introspection Tools """

def get_endpoints_adjacency(
    item: graphs.Adjacency) -> MutableSequence[Hashable]:
    """Returns the endpoints in `item`.

    Args:
        item: adjacency list object to examine.

    Returns:
        list of endpoints.

    """
    return [k for k in item if not item[k]]

def get_roots_adjacency(item: graphs.Adjacency) -> MutableSequence[Hashable]:
    """Returns the roots in `item`.

    Args:
        item: adjacency list object to examine.

    Returns:
        list of roots.

    """
    stops = list(itertools.chain.from_iterable(item.values()))
    return [k for k in item if k not in stops]

def get_endpoints_edges(item: graphs.Edges) -> MutableSequence[Hashable]:
    """Returns the endpoints in `item`.

    Args:
        item: edge list object to examine.

    Returns:
        list of endpoints.

    """
    raise NotImplementedError

def get_roots_edges(item: graphs.Edges) -> MutableSequence[Hashable]:
    """Returns the roots in `item`.

    Args:
        item: edge list object to examine.

    Returns:
        list of roots.

    """
    raise NotImplementedError

def get_endpoints_matrix(item: graphs.Matrix) -> MutableSequence[Hashable]:
    """Returns the endpoints in `item`.

    Args:
        item: adjacency matrix object to examine.

    Returns:
        list of endpoints.

    """
    raise NotImplementedError

def get_roots_matrix(item: graphs.Matrix) -> MutableSequence[Hashable]:
    """Returns the roots in `item`.

    Args:
        item: adjacency matrix object to examine.

    Returns:
        list of roots.

    """
    raise NotImplementedError

def get_endpoints_parallel(
    item: composites.Parallel) -> MutableSequence[Hashable]:
    """Returns the endpoints in `item`.

    Args:
        item: parallel object to examine.

    Returns:
        list of endpoints.

    """
    return [p[-1] for p in item]

def get_roots_parallel(item: composites.Parallel) -> MutableSequence[Hashable]:
    """Returns the roots in `item`.

    Args:
        item: parallel object to examine.

    Returns:
        list of roots.

    """
    return [p[0] for p in item]

def get_endpoints_serial(item: composites.Serial) -> MutableSequence[Hashable]:
    """Returns the endpoints in `item`.

    Args:
        item: serial object to examine.

    Returns:
        list of endpoints.

    """
    return [item[-1]]

def get_roots_serial(item: composites.Serial) -> MutableSequence[Hashable]:
    """Returns the roots in `item`.

    Args:
        item: serial object to examine.

    Returns:
        list of roots.

    """
    return [item[0]]
