"""Graphs with different internal storage formats.

Contents:
    Adjacency: a graph stored as an adjacency list.
    Edges: a graph stored as an edge list.
    Matrix: a graph stored as an adjacency matrix.

"""

from __future__ import annotations

import copy
import dataclasses
from typing import TYPE_CHECKING, Any, ClassVar, cast

import bunches

from . import base, check, report

if TYPE_CHECKING:
    from collections.abc import Hashable, MutableMapping, MutableSequence

__all__: list[str] = ['Adjacency', 'Edges', 'Matrix']

""" Graph Form Base Classes """


@dataclasses.dataclass
class Adjacency(base.Graph, bunches.Dictionary):
    """Base class for adjacency-list graphs.

    Args:
        contents: keys are hashable representations of nodes. Values are the
            nodes to which the key node are connected. In a directed graph, the
            key node is assumed to come before the value node in order. Nodes
            that only appear in a value are added as keys with no connections.
            Defaults to an empty `dict`.

    """

    contents: MutableMapping[Hashable, set[Hashable]] = dataclasses.field(
        default_factory = dict)

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Adds a key for every node that only appears as a connection."""
        parent = getattr(super(), '__post_init__', None)
        if parent is not None:
            parent()
        for node in report._nodes_adjacency(self.contents):
            self.contents.setdefault(node, set())

    """ Properties """

    @property
    def nodes(self) -> set[Hashable]:
        """Returns a set of all nodes in the graph."""
        return set(report._nodes_adjacency(self.contents))

    """ Private Methods """

    def _add(self, item: Hashable, **kwargs: Any) -> None:
        """Adds node to the stored graph.

        Args:
            item: node to add to the stored graph.
            **kwargs: additional keyword arguments.

        """
        self.contents[item] = set()

    def _connect(
        self, item: base.Edge | tuple[Hashable, Hashable],
            **kwargs: Any) -> None:
        """Adds edge to the stored graph.

        Args:
            item: edge to add to the stored graph.
            **kwargs: additional keyword arguments.

        """
        self.contents.setdefault(item[0], set()).add(item[1])
        self.contents.setdefault(item[1], set())

    def _delete(self, item: Hashable, **kwargs: Any) -> None:
        """Deletes node from the stored graph.

        Args:
            item: node to delete from the stored graph.
            **kwargs: additional keyword arguments.

        """
        self.contents.pop(item, None)
        for connections in self.contents.values():
            connections.discard(item)

    def _disconnect(
        self, item: base.Edge | tuple[Hashable, Hashable],
            **kwargs: Any) -> None:
        """Removes edge from the stored graph.

        Args:
            item: edge to delete from the stored graph.
            **kwargs: additional keyword arguments.

        """
        self.contents[item[0]].remove(item[1])

    def _merge(self, item: Any, **kwargs: Any) -> None:
        """Combines `item` with the stored graph.

        Args:
            item: another Graph object or raw form to add to the stored graph.
            **kwargs: additional keyword arguments.

        """
        other = base._to_raw(item, 'adjacency')
        for node, connections in other.items():
            self.contents.setdefault(node, set()).update(connections)
        for node in report._nodes_adjacency(self.contents):
            self.contents.setdefault(node, set())

    def _subset(
        self,
        include: list[Hashable] | None = None,
        exclude: list[Hashable] | None = None) -> Adjacency:
        """Returns a new graph with a subset of the stored nodes.

        Args:
            include: nodes which should be included in the new graph. If
                `None`, all nodes are included.
            exclude: nodes which should not be included in the new graph.

        Returns:
            Adjacency with only selected nodes and edges.

        """
        nodes = self._selected(
            report._nodes_adjacency(self.contents), include, exclude)
        keep = set(nodes)
        new_graph = copy.copy(self)
        new_graph.contents = {
            node: {c for c in self.contents[node] if c in keep}
            for node in nodes}
        return new_graph


@dataclasses.dataclass
class Edges(base.Graph, bunches.Listing):
    """Base class for edge-list graphs.

    An edge list can only store nodes that are part of an edge. As a result, a
    graph is built up by adding edges with `connect` (which adds the nodes of
    the edge, if necessary) or with `add` (which only accepts edges). A node
    with no edges cannot be added on its own.

    Args:
        contents: Listing of edges. Defaults to an empty list.

    """

    contents: MutableSequence[base.Edge | tuple[Hashable, Hashable]] = (
        dataclasses.field(default_factory = list))

    _implicit_nodes: ClassVar[bool] = True

    """ Properties """

    @property
    def nodes(self) -> set[Hashable]:
        """Returns a set of all nodes in the graph."""
        return {node for edge in self.contents for node in (edge[0], edge[1])}

    """ Private Methods """

    def _add(self, item: Hashable, **kwargs: Any) -> None:
        """Adds edge to the stored graph.

        Args:
            item: edge to add to the stored graph.
            **kwargs: additional keyword arguments.

        Raises:
            ValueError: if `item` is not an edge.

        """
        if not check.is_edge(item):
            raise ValueError(
                'An edge list can only add edges. Use `connect` to create an '
                'edge between nodes.')
        self.contents.append(
            cast('base.Edge | tuple[Hashable, Hashable]', item))

    def _connect(
        self, item: base.Edge | tuple[Hashable, Hashable],
            **kwargs: Any) -> None:
        """Adds edge to the stored graph if it is not already stored.

        Args:
            item: edge to add to the stored graph.
            **kwargs: additional keyword arguments.

        """
        if item not in self.contents:
            self.contents.append(item)

    def _delete(
        self,
        item: Hashable | base.Edge | tuple[Hashable, Hashable],
        **kwargs: Any) -> None:
        """Removes node (and its edges) or edge from the stored graph.

        Args:
            item: node or edge to delete from the stored graph. If `item` is a
                node, all of the edges that include it are deleted.
            **kwargs: additional keyword arguments.

        """
        if item in self.nodes:
            self.contents[:] = [
                edge for edge in self.contents
                    if item not in {edge[0], edge[1]}]
        else:
            self.contents.remove(item)  # type: ignore[arg-type]

    def _disconnect(
        self, item: base.Edge | tuple[Hashable, Hashable],
            **kwargs: Any) -> None:
        """Removes edge from the stored graph.

        Args:
            item: edge to delete from the stored graph.
            **kwargs: additional keyword arguments.

        """
        self.contents.remove(item)

    def _merge(self, item: Any, **kwargs: Any) -> None:
        """Combines `item` with the stored graph.

        Args:
            item: another Graph object or raw form to add to the stored graph.
            **kwargs: additional keyword arguments.

        """
        for edge in base._to_raw(item, 'edges'):
            if edge not in self.contents:
                self.contents.append(edge)

    def _subset(
        self,
        include: list[Hashable] | None = None,
        exclude: list[Hashable] | None = None) -> Edges:
        """Returns a new graph with a subset of the stored nodes.

        Args:
            include: nodes which should be included in the new graph. If
                `None`, all nodes are included.
            exclude: nodes which should not be included in the new graph.

        Returns:
            Edges with only selected nodes and edges.

        """
        ordered = list(
            dict.fromkeys(
                node for edge in self.contents for node in (edge[0], edge[1])))
        keep = set(self._selected(ordered, include, exclude))
        new_graph = copy.copy(self)
        new_graph.contents = [
            edge
            for edge in self.contents
            if edge[0] in keep and edge[1] in keep]
        return new_graph

    """ Dunder Methods """

    def __contains__(self, item: object) -> bool:
        """Returns whether `item` is a node or an edge in the graph.

        Args:
            item: node or edge to look for.

        Returns:
            Whether `item` is a node in the graph or an edge in the graph.

        """
        try:
            return item in self.nodes or item in self.contents
        except TypeError:
            return False


@dataclasses.dataclass
class Matrix(base.Graph, bunches.Listing):
    """Base class for adjacency-matrix graphs.

    Any non-zero value in the matrix is an edge from the node of the row to the
    node of the column.

    Args:
        contents: a list of list of numbers indicating edges between nodes in
            the matrix. Defaults to an empty list.
        labels: names of nodes in the matrix. The label at each index
            corresponds to the row and column at that index. Defaults to an
            empty list.

    Raises:
        ValueError: if the matrix is not square or its size does not match the
            number of labels.

    """

    contents: MutableSequence[MutableSequence[float]] = dataclasses.field(
        default_factory = list)
    labels: MutableSequence[Hashable] = dataclasses.field(
        default_factory = list)

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Validates the shape of the matrix.

        Raises:
            ValueError: if the matrix is not square or its size does not match
                the number of labels.

        """
        parent = getattr(super(), '__post_init__', None)
        if parent is not None:
            parent()
        size = len(self.labels)
        if len(self.contents) != size or any(
            len(row) != size for row in self.contents):
            raise ValueError(
                'The matrix must be square with one label for each row and '
                'column')

    """ Properties """

    @property
    def nodes(self) -> set[Hashable]:
        """Returns a set of all nodes in the graph."""
        return set(self.labels)

    """ Private Methods """

    def _add(self, item: Hashable, **kwargs: Any) -> None:
        """Adds node to the stored graph.

        Args:
            item: node to add to the stored graph.
            **kwargs: additional keyword arguments.

        """
        for row in self.contents:
            row.append(0)
        self.labels.append(item)
        self.contents.append([0] * len(self.labels))

    def _connect(
        self, item: base.Edge | tuple[Hashable, Hashable],
            **kwargs: Any) -> None:
        """Adds edge to the stored graph.

        Args:
            item: edge to add to the stored graph.
            **kwargs: additional keyword arguments.

        """
        row = self.labels.index(item[0])
        column = self.labels.index(item[1])
        if not self.contents[row][column]:
            self.contents[row][column] = 1

    def _delete(self, item: Hashable, **kwargs: Any) -> None:
        """Removes node from the stored graph.

        Args:
            item: node to delete from the stored graph.
            **kwargs: additional keyword arguments.

        """
        index = self.labels.index(item)
        del self.contents[index]
        for row in self.contents:
            del row[index]
        del self.labels[index]

    def _disconnect(
        self, item: base.Edge | tuple[Hashable, Hashable],
            **kwargs: Any) -> None:
        """Removes edge from the stored graph.

        Args:
            item: edge to delete from the stored graph.
            **kwargs: additional keyword arguments.

        Raises:
            ValueError: if the edge is not in the stored graph.

        """
        row = self.labels.index(item[0])
        column = self.labels.index(item[1])
        if not self.contents[row][column]:
            raise ValueError('The edge is not in the graph')
        self.contents[row][column] = 0

    def _merge(self, item: Any, **kwargs: Any) -> None:
        """Combines `item` with the stored graph.

        Args:
            item: another Graph object or raw form to add to the stored graph.
            **kwargs: additional keyword arguments.

        """
        other = base._to_raw(item, 'adjacency')
        for node in report._nodes_adjacency(other):
            if node not in self:
                self._add(node)
        for node, connections in other.items():
            for connection in connections:
                self._connect((node, connection))

    def _subset(
        self,
        include: list[Hashable] | None = None,
        exclude: list[Hashable] | None = None) -> Matrix:
        """Returns a new graph with a subset of the stored nodes.

        Args:
            include: nodes which should be included in the new graph. If
                `None`, all nodes are included.
            exclude: nodes which should not be included in the new graph.

        Returns:
            Matrix with only selected nodes and edges.

        """
        keep = self._selected(self.labels, include, exclude)
        indices = [i for i, label in enumerate(self.labels) if label in keep]
        new_graph = copy.copy(self)
        new_graph.contents = [
            [self.contents[i][j] for j in indices] for i in indices]
        new_graph.labels = [self.labels[i] for i in indices]
        return new_graph
