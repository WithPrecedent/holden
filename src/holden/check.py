"""Functions that type check composite forms using structural subtyping.

Structural subtyping means that raw python objects with the right structure are
recognized as a form of composite data structure, even if they are not
instances of a `holden` class. For example, a `dict` of `set` values is
recognized as an adjacency list by `is_adjacency`.

Contents:
    add_checker: adds another checker to the module namespace.
    is_adjacency: returns whether the passed item is an adjacency list.
    is_composite: returns whether the passed item is a composite data structure.
    is_edge: returns whether the passed item is an edge.
    is_edges: returns whether the passed item is an edge list.
    is_graph: returns whether the passed item is a graph.
    is_matrix: returns whether the passed item is an adjacency matrix.
    is_node: returns whether the passed item is a node.
    is_nodes: returns whether the passed item is a collection of nodes.
    is_parallel: returns whether the passed item is a list of serials.
    is_serial: returns whether the passed item is a serial list.

"""

from __future__ import annotations

from collections.abc import (
    Callable,
    Hashable,
    MutableMapping,
    MutableSequence,
    Sequence,
)
from typing import Any

__all__: list[str] = [
    "add_checker",
    "is_adjacency",
    "is_composite",
    "is_edge",
    "is_edges",
    "is_graph",
    "is_matrix",
    "is_node",
    "is_nodes",
    "is_parallel",
    "is_serial",
]

_COMPOSITE_METHODS: tuple[str, ...] = ("add", "delete", "merge", "subset")
_GRAPH_METHODS: tuple[str, ...] = ("connect", "disconnect")


def add_checker(name: str, item: Callable[[Any], bool]) -> None:
    """Adds a checker to the local namespace.

    This allows the function to be found by the `holden.classify` function and
    the `holden.Forms.classify` class method.

    Args:
        name: name of the checker function. It needs to be in the `is_{form}`
            format, where `form` is the name of the form registered in
            `holden.Forms`.
        item: callable checker which should have a single parameter, `item`,
            and return whether `item` is the form.

    Raises:
        ValueError: if `name` does not start with "is_".

    """
    if not name.startswith("is_"):
        raise ValueError("name must be in the 'is_{form}' format")
    globals()[name] = item


def is_adjacency(item: object) -> bool:
    """Returns whether `item` is an adjacency list.

    An adjacency list is a mutable mapping where every value is a `set`.

    Args:
        item: instance to test.

    Returns:
        Whether `item` is an adjacency list.

    """
    return isinstance(item, MutableMapping) and all(
        isinstance(connections, set) for connections in item.values()
    )


def is_composite(item: object) -> bool:
    """Returns whether `item` is a composite data structure.

    A composite data structure is any object (or class) that has `add`,
    `delete`, `merge`, and `subset` methods.

    Args:
        item: instance or class to test.

    Returns:
        Whether `item` is a composite data structure.

    """
    return all(
        callable(getattr(item, method, None)) for method in _COMPOSITE_METHODS
    )


def is_edge(item: object) -> bool:
    """Returns whether `item` is an edge.

    An edge is an immutable sequence (such as a `tuple`) of exactly 2 nodes.
    Mutable sequences, such as a `list`, are not edges so that lists can be
    used unambiguously for serial and parallel paths.

    Args:
        item: instance to test.

    Returns:
        Whether `item` is an edge.

    """
    return (
        isinstance(item, Sequence)
        and not isinstance(item, str | bytes | MutableSequence)
        and len(item) == 2  # noqa: PLR2004
        and is_node(item[0])
        and is_node(item[1])
    )


def is_edges(item: object) -> bool:
    """Returns whether `item` is an edge list.

    Args:
        item: instance to test.

    Returns:
        Whether `item` is an edge list.

    """
    return isinstance(item, MutableSequence) and all(is_edge(i) for i in item)


def is_graph(item: object) -> bool:
    """Returns whether `item` is a graph.

    A graph is a composite data structure that also has `connect` and
    `disconnect` methods.

    Args:
        item: instance or class to test.

    Returns:
        Whether `item` is a graph.

    """
    return is_composite(item) and all(
        callable(getattr(item, method, None)) for method in _GRAPH_METHODS
    )


def is_matrix(item: object) -> bool:
    """Returns whether `item` is an adjacency matrix.

    A raw adjacency matrix is a 2-item sequence. The first item is a mutable
    sequence of equal-length mutable sequences of numbers (the rows). The second
    item is a mutable sequence of hashable labels for the nodes. The number of
    rows and the length of every row must match the number of labels.

    Args:
        item: instance to test.

    Returns:
        Whether `item` is an adjacency matrix.

    """
    if not (isinstance(item, Sequence) and len(item) == 2):  # noqa: PLR2004
        return False
    matrix, labels = item
    if not (
        isinstance(matrix, MutableSequence)
        and isinstance(labels, MutableSequence)
        and len(matrix) == len(labels)
    ):
        return False
    return (
        all(isinstance(label, Hashable) for label in labels)
        and all(
            isinstance(row, MutableSequence) and len(row) == len(labels)
            for row in matrix
        )
        and all(
            isinstance(connection, int | float)
            for row in matrix
            for connection in row
        )
    )


def is_node(item: object) -> bool:
    """Returns whether `item` is a node.

    Any hashable object (or class of hashable objects) can be a node.

    Args:
        item: instance or class to test.

    Returns:
        Whether `item` is a node.

    """
    if isinstance(item, type):
        return issubclass(item, Hashable)
    return isinstance(item, Hashable)


def is_nodes(item: object) -> bool:
    """Returns whether `item` is a collection of nodes.

    A `str` or `bytes` is treated as a single node, not a collection.

    Args:
        item: instance to test.

    Returns:
        Whether `item` is a collection of nodes.

    """
    return isinstance(item, list | tuple | set | frozenset) and all(
        is_node(i) for i in item
    )


def is_parallel(item: object) -> bool:
    """Returns whether `item` is a sequence of serial paths.

    Args:
        item: instance to test.

    Returns:
        Whether `item` is a sequence of serial paths.

    """
    return isinstance(item, MutableSequence) and all(is_serial(i) for i in item)


def is_serial(item: object) -> bool:
    """Returns whether `item` is a serial path.

    A serial path is a mutable sequence of nodes. Because a `tuple` is used for
    edges, a `tuple` cannot be a node in a serial path.

    Args:
        item: instance to test.

    Returns:
        Whether `item` is a serial path.

    """
    return isinstance(item, MutableSequence) and all(
        is_node(i) and not isinstance(i, tuple) for i in item
    )
