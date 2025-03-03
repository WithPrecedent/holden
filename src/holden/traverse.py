"""Internal storage formats for graphs.

Contents:
    walk_adjacency: returns path(s) through an adjacency list.
    walk_edges: returns path(s) through an edge list.
    walk_matrix: returns path(s) through an adjacency matrix.
    walk_parallel: returns path(s) through a parallel structure.
    walk_serial: returns path(s) through a serial structure.

To Do:
    Complete not implemented functions
    For adjacency matrix walk, consider the efficient approach here:
        https://www.geeksforgeeks.org/count-possible-paths-source-destination-exactly-k-edges/

"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Hashable, Sequence

    from . import composites, graphs


def walk_adjacency(
    item: graphs.Adjacency,
    start: Hashable,
    stop: Hashable,
    path: Sequence[Hashable] | None = None) -> Sequence[Hashable]:
    """Returns all paths in `item` from `start` to `stop`.

    The code here is adapted from: https://www.python.org/doc/essays/graphs/

    Args:
        item: item in which to find paths.
        start: node to start paths from.
        stop: node to stop paths.
        path: a path from `start` to `stop`. This is used for recursion within
            the function to accumulate all possible paths. Defaults to None.

    Returns:
        A list of possible paths (each path is a list nodes) from `start` to
            `stop`.

    """
    if path is None:
        path = []
    path = [*path, start]
    if start == stop:
        return [path]
    if start not in item:
        return []
    paths = []
    for node in item[start]:
        if node not in path:
            new_paths = walk_adjacency(
                item = item,
                start = node,
                stop = stop,
                path = path)
            paths.extend(iter(new_paths))
    return paths

def walk_edges(
    item: graphs.Edges,
    start: Hashable,
    stop: Hashable,
    path: Sequence[Hashable] | None = None) -> Sequence[Hashable]:
    """Returns all paths in `item` from `start` to `stop`.

    Args:
        item: item in which to find paths.
        start: node to start paths from.
        stop: node to stop paths.
        path: a path from `start` to `stop`. Defaults to None.

    Returns:
        A list of possible paths (each path is a list nodes) from `start` to
            `stop`.

    """
    raise NotImplementedError

def walk_matrix(
    item: graphs.Matrix,
    start: Hashable,
    stop: Hashable,
    path: Sequence[Hashable] | None = None) -> Sequence[Hashable]:
    """Returns all paths in `item` from `start` to `stop`.

    Args:
        item: item in which to find paths.
        start: node to start paths from.
        stop: node to stop paths.
        path: a path from `start` to `stop`. Defaults to None.

    Returns:
        A list of possible paths (each path is a list nodes)
            from `start` to `stop`.

    """
    raise NotImplementedError

def walk_parallel(
    item: composites.Parallel,
    start: Hashable,
    stop: Hashable) -> Sequence[Hashable]:
    """Returns all paths in `item` from `start` to `stop`.

    Args:
        item: item in which to find paths.
        start: node to start paths from.
        stop: node to stop paths.

    Returns:
        A list of possible paths (each path is a list nodes) from `start` to
            `stop`.

    """
    return [walk_serial(item = p, start = start, stop = stop) for p in item]

def walk_serial(
    item: composites.Serial,
    start: Hashable,
    stop: Hashable) -> Sequence[Hashable]:
    """Returns all paths in `item` from `start` to `stop`.

    Args:
        item: item in which to find paths.
        start: node to start paths from.
        stop: node to stop paths.

    Returns:
        Sequence: a list of possible paths (each path is a list nodes) from
            `start` to `stop`.

    """
    index_start = item.index(start)
    index_stop = item.index(stop)
    if index_stop > len(item):
        path = item[index_start:]
    else:
        path = item[index_start:index_stop]
    return path
