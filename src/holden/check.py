"""Functions that type check composite forms using structural subtyping.

Contents:
    add_checker: adds another checker to the module namespace.
    is_adjacency: returns whether the passed item is an adjacency list.
    is_edge: returns whether the passed item is an edge.
    is_edges: returns whether the passed item is an edge list.
    is_graph: returns whether the passed item is a graph.
    is_matrix: returns whether the passed item is an adjacency matrix.
    is_node: returns whether the passed item is a node.
    is_nodes: returns whether the passed item is a collection of nodes.
    is_parallel: returns whether the passed item is a list of serials.
    is_serial: returns whether the passed item is a serial list.

To Do:


"""
from __future__ import annotations

import inspect
import itertools
from collections.abc import (
    Callable,
    Collection,
    Hashable,
    MutableMapping,
    MutableSequence,
    Sequence,
)
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from . import base


def add_checker(name: str, item: Callable[[base.Graph]]) -> None:
    """Adds a checker to the local namespace.

    This allows the function to be found by the 'holden.classify' function and
    the 'holden.Forms.classify' class method.

    Args:
        name: name of the checker function. It needs to be in the 'is_{form}'
            format.
        item: callable checker which should have a single parameter, item which
            should be a base.Graph type.

    """
    globals()[name] = item
    return

def is_adjacency(item: object) -> bool:
    """Returns whether `item` is an adjacency list.

    Args:
        item: instance to test.

    Returns:
        Whether `item` is an adjacency list.

    """
    if isinstance(item, MutableMapping):
        connections = list(item.values())
        nodes = list(itertools.chain.from_iterable(item.values()))
        return (
            all(isinstance(e, set) for e in connections)
            and all(is_node(item = i) for i in nodes))
    else:
        return False

def is_composite(item: type[Any] | object) -> bool:
    """Returns whether `item` is a composite data structure.

    Args:
        item: instance to test.

    Returns:
        Whether `item` is a composite data structure.

    """
    methods = ['add', 'delete', 'merge', 'subset']
    return all(inspect.ismethod(getattr(item, method)) for method in methods)

def is_edge(item: object) -> bool:
    """Returns whether `item` is an edge.

    Args:
        item: instance to test.

    Returns:
        Whether `item` is an edge.

    """
    return (
        isinstance(item, Sequence)
        and not isinstance(item, str)
        and len(item) == 2  # noqa: PLR2004
        and is_node(item = item[0])
        and is_node(item = item[1]))

def is_edges(item: object) -> bool:
    """Returns whether `item` is an edge list.

    Args:
        item: instance to test.

    Returns:
        Whether `item` is an edge list.

    """
    return (
        isinstance(item, MutableSequence)
        and all(is_edge(item = i) for i in item))

def is_graph(item: type[Any] | object) -> bool:
    """Returns whether `item` is a graph.

    Args:
        item: instance to test.

    Returns:
        Whether `item` is a graph.

    """
    return (
        is_composite(item = item)
        and inspect.ismethod(item.connect)
        and inspect.ismethod(item.disconnect))

def is_matrix(item: object) -> bool:
    """Returns whether `item` is an adjacency matrix.

    Args:
        item: instance to test.

    Returns:
        Whether `item` is an adjacency matrix.

    """
    if isinstance(item, Sequence) and len(item) == 2:  # noqa: PLR2004
        matrix = item[0]
        labels = item[1]
        connections = list(itertools.chain.from_iterable(matrix))
        return (
            isinstance(matrix, MutableSequence)
            and isinstance(labels, MutableSequence)
            and all(isinstance(i, MutableSequence) for i in matrix)
            and all(isinstance(n, Hashable) for n in labels)
            and all(isinstance(c, int | float) for c in connections))
    else:
        return False

def is_node(item: object | type[Any]) -> bool:
    """Returns whether `item` is a node.

    Args:
        item: instance or class to test.

    Returns:
        Whether `item` is a node.

    """
    if inspect.isclass(item):
        return issubclass(item, Hashable)
    else:
        return isinstance(item, Hashable)

def is_nodes(item: object) -> bool:
    """Returns whether `item` is a collection of nodes.

    Args:
        item: instance to test.

    Returns:
        Whether `item` is a collection of nodes.

    """
    return (
        isinstance(item, Collection) and all(is_node(item = i) for i in item))

def is_parallel(item: object) -> bool:
    """Returns whether `item` is sequence of parallel.

    Args:
        item: instance to test.

    Returns:
        Whether `item` is a sequence of parallel.

    """
    return (
        isinstance(item, MutableSequence)
        and all(is_serial(item = i) for i in item))

def is_serial(item: object) -> bool:
    """Returns whether `item` is a serial.

    Args:
        item: instance to test.

    Returns:
        Whether `item` is a serial.

    """
    return (
        isinstance(item, MutableSequence)
        and all(is_node(item = i) for i in item)
        and all(not isinstance(i, tuple) for i in item))
