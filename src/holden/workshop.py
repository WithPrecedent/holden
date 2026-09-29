"""Functions to change the internal storage format for a data structure.

Every transformer takes a raw form (or a `holden` composite data structure that
stores that form) and returns a new raw form. The raw forms are:

    adjacency: `dict` with nodes as keys and a `set` of nodes as values.
    edges: `list` of `tuple` (or `Edge`) instances of two nodes.
    matrix: `tuple` of a `list` of `list` instances of numbers and a `list` of
        labels for the nodes.
    parallel: `list` of `list` instances of nodes (each is a path).
    serial: `list` of nodes (a single path).

Converting to `parallel` or `serial` follows the paths from the roots of a
graph to its endpoints. When a graph has more than one path, `serial`
concatenates all of the paths in order.

Contents:
    add_transformer: adds a transformer to this module's namespace.
    adjacency_to_edges
    adjacency_to_matrix
    adjacency_to_parallel
    adjacency_to_serial
    edges_to_adjacency
    edges_to_matrix
    edges_to_parallel
    edges_to_serial
    matrix_to_adjacency
    matrix_to_edges
    matrix_to_parallel
    matrix_to_serial
    parallel_to_adjacency
    parallel_to_edges
    parallel_to_matrix
    parallel_to_serial
    serial_to_adjacency
    serial_to_edges
    serial_to_matrix
    serial_to_parallel

"""

from __future__ import annotations

import itertools
from collections.abc import Collection
from typing import TYPE_CHECKING, Any

from . import check, report, traverse, utilities

if TYPE_CHECKING:
    from collections.abc import Callable, Hashable

    from . import composites, graphs

__all__: list[str] = [
    "add_transformer",
    "adjacency_to_edges",
    "adjacency_to_matrix",
    "adjacency_to_parallel",
    "adjacency_to_serial",
    "edges_to_adjacency",
    "edges_to_matrix",
    "edges_to_parallel",
    "edges_to_serial",
    "matrix_to_adjacency",
    "matrix_to_edges",
    "matrix_to_parallel",
    "matrix_to_serial",
    "parallel_to_adjacency",
    "parallel_to_edges",
    "parallel_to_matrix",
    "parallel_to_serial",
    "serial_to_adjacency",
    "serial_to_edges",
    "serial_to_matrix",
    "serial_to_parallel",
]


def _transformer_name(source: str, output: str) -> str:
    """Returns the name of the transformer between two forms.

    Args:
        source: name of the form to transform from.
        output: name of the form to transform to.

    Returns:
        Name of the transformer function in the `{source}_to_{output}` format.

    """
    return f"{source}_to_{output}"


def add_transformer(name: str, item: Callable[[Any], Any]) -> None:
    """Adds a transformer to this module's namespace.

    This allows the function to be found by the `transform` function.

    Args:
        name: name of the transformer function. It needs to be in the
            `{source}_to_{output}` format, where `source` and `output` are names
            of forms in `holden.Forms`.
        item: callable transformer which should have a single parameter, `item`,
            which should be a composite data structure or raw form.

    Raises:
        ValueError: if `name` is not in the `{source}_to_{output}` format.

    """
    source, separator, output = name.partition("_to_")
    if not (source and separator and output):
        raise ValueError("name must be in the '{source}_to_{output}' format")
    globals()[name] = item


def adjacency_to_edges(
    item: graphs.Adjacency | dict[Hashable, set[Hashable]],
) -> list[tuple[Hashable, Hashable]]:
    """Converts `item` to an edge list.

    Nodes without any edges cannot be represented in an edge list and are not
    included in the returned edge list.

    Args:
        item: adjacency list to convert to an edge list.

    Returns:
        Edge list derived from `item`.

    """
    adjacency = utilities._rawify(item)
    return [
        (node, connection)
        for node, connections in adjacency.items()
        for connection in utilities._stabilize(connections)
    ]


def adjacency_to_matrix(
    item: graphs.Adjacency | dict[Hashable, set[Hashable]],
) -> tuple[list[list[int]], list[Hashable]]:
    """Converts `item` to an adjacency matrix.

    Args:
        item: adjacency list to convert to an adjacency matrix.

    Returns:
        Adjacency matrix derived from `item`. It is a `tuple` of the matrix
            (with a 1 for every edge and a 0 otherwise) and a list of the labels
            of the nodes that correspond to the rows and columns of the matrix.

    """
    adjacency = utilities._rawify(item)
    names = report._nodes_adjacency(adjacency)
    index = {name: i for i, name in enumerate(names)}
    matrix = [[0] * len(names) for _ in names]
    for node, connections in adjacency.items():
        for connection in connections:
            matrix[index[node]][index[connection]] = 1
    return matrix, names


def adjacency_to_parallel(
    item: graphs.Adjacency | dict[Hashable, set[Hashable]],
) -> list[list[Hashable]]:
    """Converts `item` to a parallel structure.

    Args:
        item: adjacency list to convert to a parallel structure.

    Returns:
        Parallel structure derived from `item`. It has a path for every route
            from a root to an endpoint of `item`.

    """
    adjacency = utilities._rawify(item)
    paths: list[list[Hashable]] = []
    for start in report.get_roots_adjacency(adjacency):
        for stop in report.get_endpoints_adjacency(adjacency):
            paths.extend(
                traverse.walk_adjacency(item=adjacency, start=start, stop=stop)
            )
    return paths


def adjacency_to_serial(
    item: graphs.Adjacency | dict[Hashable, set[Hashable]],
) -> list[Hashable]:
    """Converts `item` to a serial structure.

    Args:
        item: adjacency list to convert to a serial structure.

    Returns:
        Serial structure derived from `item`. If `item` has a single path, it is
            returned. Otherwise, all of the paths are concatenated in order.

    """
    return parallel_to_serial(item=adjacency_to_parallel(item=item))


def edges_to_adjacency(
    item: graphs.Edges | list[tuple[Hashable, Hashable]],
) -> dict[Hashable, set[Hashable]]:
    """Converts `item` to an adjacency list.

    Args:
        item: edge list to convert to an adjacency list.

    Returns:
        Adjacency list derived from `item`.

    """
    adjacency: dict[Hashable, set[Hashable]] = {}
    for start, stop in utilities._rawify(item):
        adjacency.setdefault(start, set()).add(stop)
        adjacency.setdefault(stop, set())
    return adjacency


def edges_to_matrix(
    item: graphs.Edges | list[tuple[Hashable, Hashable]],
) -> tuple[list[list[int]], list[Hashable]]:
    """Converts `item` to an adjacency matrix.

    Args:
        item: edge list to convert to an adjacency matrix.

    Returns:
        Adjacency matrix derived from `item`.

    """
    return adjacency_to_matrix(item=edges_to_adjacency(item=item))


def edges_to_parallel(
    item: graphs.Edges | list[tuple[Hashable, Hashable]],
) -> list[list[Hashable]]:
    """Converts `item` to a parallel structure.

    Args:
        item: edge list to convert to a parallel structure.

    Returns:
        Parallel structure derived from `item`.

    """
    return adjacency_to_parallel(item=edges_to_adjacency(item=item))


def edges_to_serial(
    item: graphs.Edges | list[tuple[Hashable, Hashable]],
) -> list[Hashable]:
    """Converts `item` to a serial structure.

    Args:
        item: edge list to convert to a serial structure.

    Returns:
        Serial structure derived from `item`.

    """
    return adjacency_to_serial(item=edges_to_adjacency(item=item))


def matrix_to_adjacency(
    item: graphs.Matrix | tuple[list[list[float]], list[Hashable]],
) -> dict[Hashable, set[Hashable]]:
    """Converts `item` to an adjacency list.

    Any non-zero value in the matrix is treated as an edge.

    Args:
        item: adjacency matrix to convert to an adjacency list.

    Raises:
        ValueError: if the matrix is not square or its labels do not match its
            size.

    Returns:
        Adjacency list derived from `item`.

    """
    matrix, names = utilities._rawify(item)
    if len(matrix) != len(names) or any(
        len(row) != len(names) for row in matrix
    ):
        raise ValueError(
            "The matrix must be square with one label for each row and column"
        )
    adjacency: dict[Hashable, set[Hashable]] = {name: set() for name in names}
    for name, row in zip(names, matrix, strict=True):
        adjacency[name].update(
            names[j] for j, connection in enumerate(row) if connection
        )
    return adjacency


def matrix_to_edges(
    item: graphs.Matrix | tuple[list[list[float]], list[Hashable]],
) -> list[tuple[Hashable, Hashable]]:
    """Converts `item` to an edge list.

    Args:
        item: adjacency matrix to convert to an edge list.

    Returns:
        Edge list derived from `item`. The edges are in the order of the rows
            and columns of the matrix.

    """
    matrix, names = utilities._rawify(item)
    edges: list[tuple[Hashable, Hashable]] = []
    for i, row in enumerate(matrix):
        edges.extend(
            (names[i], names[j])
            for j, connection in enumerate(row)
            if connection
        )
    return edges


def matrix_to_parallel(
    item: graphs.Matrix | tuple[list[list[float]], list[Hashable]],
) -> list[list[Hashable]]:
    """Converts `item` to a parallel structure.

    Args:
        item: adjacency matrix to convert to a parallel structure.

    Returns:
        Parallel structure derived from `item`.

    """
    return adjacency_to_parallel(item=matrix_to_adjacency(item=item))


def matrix_to_serial(
    item: graphs.Matrix | tuple[list[list[float]], list[Hashable]],
) -> list[Hashable]:
    """Converts `item` to a serial structure.

    Args:
        item: adjacency matrix to convert to a serial structure.

    Returns:
        Serial structure derived from `item`.

    """
    return adjacency_to_serial(item=matrix_to_adjacency(item=item))


def parallel_to_adjacency(
    item: composites.Parallel | list[list[Hashable]],
) -> dict[Hashable, set[Hashable]]:
    """Converts `item` to an adjacency list.

    Args:
        item: parallel structure to convert to an adjacency list.

    Returns:
        Adjacency list derived from `item`. It is the union of the adjacency
            lists of each path in `item`.

    """
    adjacency: dict[Hashable, set[Hashable]] = {}
    for serial in utilities._rawify(item):
        for key, value in serial_to_adjacency(item=serial).items():
            adjacency.setdefault(key, set()).update(value)
    return adjacency


def parallel_to_edges(
    item: composites.Parallel | list[list[Hashable]],
) -> list[tuple[Hashable, Hashable]]:
    """Converts `item` to an edge list.

    Args:
        item: parallel structure to convert to an edge list.

    Returns:
        Edge list derived from `item`.

    """
    return adjacency_to_edges(item=parallel_to_adjacency(item=item))


def parallel_to_matrix(
    item: composites.Parallel | list[list[Hashable]],
) -> tuple[list[list[int]], list[Hashable]]:
    """Converts `item` to an adjacency matrix.

    Args:
        item: parallel structure to convert to an adjacency matrix.

    Returns:
        Adjacency matrix derived from `item`.

    """
    return adjacency_to_matrix(item=parallel_to_adjacency(item=item))


def parallel_to_serial(
    item: composites.Parallel | list[list[Hashable]],
) -> list[Hashable]:
    """Converts `item` to a serial structure.

    Args:
        item: parallel structure to convert to a serial structure.

    Returns:
        Serial structure derived from `item`. If `item` has a single path, it is
            returned. Otherwise, all of the paths are concatenated in order.

    """
    paths = [
        list(utilities._rawify(serial)) for serial in utilities._rawify(item)
    ]
    return list(itertools.chain.from_iterable(paths))


def serial_to_adjacency(
    item: composites.Serial | list[Hashable],
) -> dict[Hashable, set[Hashable]]:
    """Converts `item` to an adjacency list.

    Args:
        item: serial structure to convert to an adjacency list. Each node is
            connected to the node that follows it. If `item` is a parallel
            structure, it is converted using `parallel_to_adjacency`.

    Returns:
        Adjacency list derived from `item`.

    """
    raw = utilities._rawify(item)
    if raw and check.is_parallel(raw):
        return parallel_to_adjacency(item=raw)
    if not isinstance(raw, Collection) or isinstance(raw, str | bytes):
        raw = [raw]
    adjacency: dict[Hashable, set[Hashable]] = {}
    for node in raw:
        adjacency.setdefault(node, set())
    for start, stop in itertools.pairwise(raw):
        adjacency[start].add(stop)
    return adjacency


def serial_to_edges(
    item: composites.Serial | list[Hashable],
) -> list[tuple[Hashable, Hashable]]:
    """Converts `item` to an edge list.

    Args:
        item: serial structure to convert to an edge list.

    Returns:
        Edge list derived from `item`.

    """
    return adjacency_to_edges(item=serial_to_adjacency(item=item))


def serial_to_matrix(
    item: composites.Serial | list[Hashable],
) -> tuple[list[list[int]], list[Hashable]]:
    """Converts `item` to an adjacency matrix.

    Args:
        item: serial structure to convert to an adjacency matrix.

    Returns:
        Adjacency matrix derived from `item`.

    """
    return adjacency_to_matrix(item=serial_to_adjacency(item=item))


def serial_to_parallel(
    item: composites.Serial | list[Hashable],
) -> list[list[Hashable]]:
    """Converts `item` to a parallel structure.

    Args:
        item: serial structure to convert to a parallel structure.

    Returns:
        Parallel structure derived from `item` with `item` as its only path or
            an empty list if `item` is empty.

    """
    nodes = list(utilities._rawify(item))
    return [nodes] if nodes else []
