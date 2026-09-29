"""Tools for finding paths through composite data structures.

Every `walk_{form}` function returns a `list` of paths. Each path is a `list` of
nodes that starts with the `start` node and ends with the `stop` node.

Contents:
    walk: returns path(s) through any recognized composite form.
    walk_adjacency: returns path(s) through an adjacency list.
    walk_edges: returns path(s) through an edge list.
    walk_matrix: returns path(s) through an adjacency matrix.
    walk_parallel: returns path(s) through a parallel structure.
    walk_serial: returns path(s) through a serial structure.

To Do:
    For adjacency matrix walk, consider the efficient approach here:
        https://www.geeksforgeeks.org/count-possible-paths-source-destination-exactly-k-edges/

"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from . import base, report, utilities, workshop

if TYPE_CHECKING:
    from collections.abc import Hashable, Sequence

    from . import composites, graphs

__all__: list[str] = [
    "walk",
    "walk_adjacency",
    "walk_edges",
    "walk_matrix",
    "walk_parallel",
    "walk_serial",
]


def walk(
    item: Any,
    start: Hashable | Sequence[Hashable] | None = None,
    stop: Hashable | Sequence[Hashable] | None = None,
) -> list[list[Hashable]]:
    """Returns all paths in any recognized composite form.

    Args:
        item: composite data structure or raw form in which to find paths.
        start: node (or list of nodes) to start paths from. If it is `None`,
            paths start from every root of `item`. Because a `tuple` is treated
            as a collection of nodes, a `tuple` node should be passed inside a
            `list`. Defaults to `None`.
        stop: node (or list of nodes) to stop paths at. If it is `None`, paths
            stop at every endpoint of `item`. Defaults to `None`.

    Raises:
        NotImplementedError: if there is no walk function for the form of
            `item`.

    Returns:
        A list of possible paths (each path is a list of nodes) from `start` to
            `stop`.

    """
    form = base.classify(item)
    function = globals().get(f"walk_{form}")
    if function is None:
        raise NotImplementedError(f"walk does not support {form} forms")
    starts = (
        report.get_roots(item) if start is None else utilities._listify(start)
    )
    stops = (
        report.get_endpoints(item) if stop is None else utilities._listify(stop)
    )
    paths: list[list[Hashable]] = []
    for first in starts:
        for last in stops:
            paths.extend(function(item, first, last))
    return paths


def walk_adjacency(
    item: graphs.Adjacency | dict[Hashable, set[Hashable]],
    start: Hashable,
    stop: Hashable,
    path: Sequence[Hashable] | None = None,
) -> list[list[Hashable]]:
    """Returns all paths in `item` from `start` to `stop`.

    A path never visits the same node twice, so cycles cannot cause the search
    to run forever. Paths are returned in a deterministic order.

    The code here is adapted from: https://www.python.org/doc/essays/graphs/

    Args:
        item: item in which to find paths.
        start: node to start paths from.
        stop: node to stop paths at.
        path: nodes to place in front of every returned path. Defaults to
            `None`.

    Returns:
        A list of possible paths (each path is a list of nodes) from `start` to
            `stop`. If `start` and `stop` are the same node, the only path is
            that single node.

    """
    adjacency = utilities._rawify(item)
    paths: list[list[Hashable]] = []
    stack = [[*(path or []), start]]
    while stack:
        current = stack.pop()
        node = current[-1]
        if node == stop:
            paths.append(current)
            continue
        stack.extend(
            [*current, child]
            for child in reversed(utilities._stabilize(adjacency.get(node, ())))
            if child not in current
        )
    return paths


def walk_edges(
    item: graphs.Edges | list[tuple[Hashable, Hashable]],
    start: Hashable,
    stop: Hashable,
    path: Sequence[Hashable] | None = None,
) -> list[list[Hashable]]:
    """Returns all paths in `item` from `start` to `stop`.

    Args:
        item: item in which to find paths.
        start: node to start paths from.
        stop: node to stop paths at.
        path: nodes to place in front of every returned path. Defaults to
            `None`.

    Returns:
        A list of possible paths (each path is a list of nodes) from `start` to
            `stop`.

    """
    return walk_adjacency(
        item=workshop.edges_to_adjacency(item=item),
        start=start,
        stop=stop,
        path=path,
    )


def walk_matrix(
    item: graphs.Matrix | tuple[list[list[float]], list[Hashable]],
    start: Hashable,
    stop: Hashable,
    path: Sequence[Hashable] | None = None,
) -> list[list[Hashable]]:
    """Returns all paths in `item` from `start` to `stop`.

    Args:
        item: item in which to find paths.
        start: node to start paths from.
        stop: node to stop paths at.
        path: nodes to place in front of every returned path. Defaults to
            `None`.

    Returns:
        A list of possible paths (each path is a list of nodes) from `start` to
            `stop`.

    """
    return walk_adjacency(
        item=workshop.matrix_to_adjacency(item=item),
        start=start,
        stop=stop,
        path=path,
    )


def walk_parallel(
    item: composites.Parallel | list[list[Hashable]],
    start: Hashable,
    stop: Hashable,
) -> list[list[Hashable]]:
    """Returns all paths in `item` from `start` to `stop`.

    Args:
        item: item in which to find paths.
        start: node to start paths from.
        stop: node to stop paths at.

    Returns:
        A list of possible paths (each path is a list of nodes) from `start` to
            `stop`. A path in `item` that does not contain `start` followed by
            `stop` does not contribute a path.

    """
    paths: list[list[Hashable]] = []
    for serial in utilities._rawify(item):
        paths.extend(walk_serial(item=serial, start=start, stop=stop))
    return paths


def walk_serial(
    item: composites.Serial | list[Hashable],
    start: Hashable,
    stop: Hashable,
) -> list[list[Hashable]]:
    """Returns all paths in `item` from `start` to `stop`.

    Args:
        item: item in which to find paths.
        start: node to start paths from.
        stop: node to stop paths at.

    Returns:
        A list with the single path from the first `start` in `item` to the
            next `stop` (inclusive of both) or an empty list if `item` has no
            such path.

    """
    nodes = list(utilities._rawify(item))
    try:
        index_start = nodes.index(start)
        index_stop = nodes.index(stop, index_start)
    except ValueError:
        return []
    return [nodes[index_start : index_stop + 1]]
