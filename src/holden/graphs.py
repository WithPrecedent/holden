"""Graphs with different internal storage formats

Contents:
    Adjacency (base.Graph, bunches.Dictionary): a graph stored as an adjacency
        list.
    Edges (base.Graph, bunches.Listing): a graph stored as an edge list.
    Matrix (base.Graph, bunches.Listing): a graph stored as an adjacency matrix.

To Do:
    Add the remainder of the conversion methods between different forms
    Add private methods that currently raise NotImplementedError
    Integrate Kinds system when it is finished

"""
from __future__ import annotations

import collections
import copy
import dataclasses
from typing import TYPE_CHECKING, Any, Union

import bunches

from . import base, check, utilities

if TYPE_CHECKING:
    from collections.abc import (
        Hashable,
        MutableMapping,
        MutableSequence,
        Sequence,
    )

""" Graph Form Base Classes """

@dataclasses.dataclass
class Adjacency(base.Graph, bunches.Dictionary):
    """Base class for adjacency-list graphs.

    Args:
        contents (MutableMapping[Hashable, set[Hashable]]): keys are hashable
            representations of nodes. Values are the nodes to which the key node
            are connected. In a directed graph, the key node is assumed to come
            before the value node in order. Defaults to a defaultdict that has a
            set for its value type.

    """
    contents: MutableMapping[Hashable, set[Hashable]] = dataclasses.field(
            default_factory = lambda: collections.defaultdict(set))

    """ Public Methods """

    def add(self, item: Hashable, *args: Any, **kwargs: Any) -> None:
        """Adds node to the stored graph.

        Args:
            item (Hashable): node to add to the stored graph.

        """
        self.contents[item] = set()
        return

    def connect(self, item: base.Edge, *args: Any, **kwargs: Any) -> None:
        """Adds edge to the stored graph.

        Args:
            item (Edge): edge to add to the stored graph.

        """
        self.contents[item[0]].add(item[1])
        return

    def delete(self, item: Hashable, *args: Any, **kwargs: Any) -> None:
        """Deletes node from the stored graph.

        Args:
            item (Hashable): node to delete from 'contents'.


        """
        del self.contents[item]
        self.contents = {k: v.remove(item) for k, v in self.contents.items()}
        return

    def disconnect(self, item: base.Edge, *args: Any, **kwargs: Any) -> None:
        """Removes edge from the stored graph.

        Args:
            item (Edge): edge to delete from the stored graph.

        """
        self.contents[item[0]].remove(item[1])
        return

    def merge(self, item: base.Graph, *args: Any, **kwargs: Any) -> None:
        """Combines 'item' with the stored graph.

        Args:
            item (Graph): another Graph object to add to the stored graph.

        """
        other = base.transform(
            item = item,
            output = 'adjacency',
            raise_same_error = False)
        for node, edges in other.items():
            if node in self:
                self[node].update(edges)
            else:
                self[node] = edges
        return

    def subset(
        self,
        include: Hashable | Sequence[Hashable] = None,
        exclude: Hashable | Sequence[Hashable] = None) -> Adjacency:
        """Returns a new graph without a subset of 'contents'.

        Args:
            include (Union[Hashable, Sequence[Hashable]]): nodes or edges which
                should be included in the new graph.
            exclude (Union[Hashable, Sequence[Hashable]]): nodes or edges which
                should not be included in the new graph.

        Returns:
           Adjacency: with only selected nodes and edges.

        """
        excludables = [
            k for k in self.contents if k not in include] if include else []
        excludables.extend([i for i in self.contents if i in exclude])
        new_graph = copy.deepcopy(self)
        for node in utilities._iterify(excludables):
            new_graph.delete(node = node)
        return new_graph

    """ Dunder Methods """

    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        """Returns whether 'instance' meets criteria to be a subclass.

        Args:
            instance (object): item to test as an instance.

        Returns:
            bool: whether 'instance' meets criteria to be a subclass.

        """
        return check.is_adjacency(item = instance)


@dataclasses.dataclass
class Edges(base.Graph, bunches.Listing):
    """Base class for edge-list graphs.

    Args:
        contents (MutableSequence[base.Edge]): Listing of edges. Defaults to
            an empty list.

    """
    contents: MutableSequence[base.Edge] = dataclasses.field(
        default_factory = list)

    """ Private Methods """

    def add(self, item: base.Edge, *args: Any, **kwargs: Any) -> None:
        """Adds edge to the stored graph.

        Args:
            item (base.Edge): edge to add to the stored graph.

        """
        self.contents.append(item)
        return

    def connect(self, item: base.Edge, *args: Any, **kwargs: Any) -> None:
        """Adds edge to the stored graph.

        Args:
            item (Edge): edge to add to the stored graph.

        """
        self.contents.append(item)
        return

    def delete(self, item: base.Edge, *args: Any, **kwargs: Any) -> None:
        """Removes edge from the stored graph.

        Args:
            item (Edge): edge to delete from the stored graph.

        """
        self.contents.remove(item)
        return

    def disconnect(self, item: base.Edge, *args: Any, **kwargs: Any) -> None:
        """Removes edge from the stored graph.

        Args:
            item (Edge): edge to delete from the stored graph.

        """
        self.contents.remove(item)
        return

    def merge(self, item: base.Graph, *args: Any, **kwargs: Any) -> None:
        """Combines 'item' with the stored graph.

        Args:
            item (Graph): another Graph object to add to the stored graph.

        """
        other = base.transform(
            item = item,
            output = 'edges',
            raise_same_error = False)
        self.contents.extend(other)
        return

    def subset(
        self,
        include: Hashable | Sequence[Hashable] = None,
        exclude: Hashable | Sequence[Hashable] = None) -> Adjacency:
        """Returns a new graph without a subset of 'contents'.

        Args:
            include (Union[Hashable, Sequence[Hashable]]): nodes or edges which
                should be included in the new graph.
            exclude (Union[Hashable, Sequence[Hashable]]): nodes or edges which
                should not be included in the new graph.

        Returns:
           Adjacency: with only selected nodes and edges.

        """
        raise NotImplementedError

    """ Dunder Methods """

    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        """Returns whether 'instance' meets criteria to be a subclass.

        Args:
            instance (object): item to test as an instance.

        Returns:
            bool: whether 'instance' meets criteria to be a subclass.

        """
        return check.is_edges(item = instance)


@dataclasses.dataclass
class Matrix(base.Graph, bunches.Listing):
    """Base class for adjacency-matrix graphs.

    Args:
        contents (Sequence[Sequence[int]]): a list of list of integers
            indicating edges between nodes in the matrix. Defaults to an empty
            list.
        labels (Sequence[Hashable]): names of nodes in the matrix.
            Defaults to an empty list.

    """
    contents: MutableSequence[MutableSequence[int]] = dataclasses.field(
        default_factory = list)
    labels: MutableSequence[Hashable] = dataclasses.field(
        default_factory = list)

    """ Private Methods """

    def add(self, item: base.Edge, *args: Any, **kwargs: Any) -> None:
        """Adds edge to the stored graph.

        Args:
            item (base.Edge): edge to add to the stored graph.

        """
        raise NotImplementedError

    def connect(self, item: base.Edge, *args: Any, **kwargs: Any) -> None:
        """Adds edge to the stored graph.

        Args:
            item (Edge): edge to add to the stored graph.

        """
        raise NotImplementedError

    def delete(self, item: base.Edge, *args: Any, **kwargs: Any) -> None:
        """Removes edge from the stored graph.

        Args:
            item (Edge): edge to delete from the stored graph.

        """
        raise NotImplementedError

    def disconnect(self, item: base.Edge, *args: Any, **kwargs: Any) -> None:
        """Removes edge from the stored graph.

        Args:
            item (Edge): edge to delete from the stored graph.

        """
        raise NotImplementedError

    def merge(self, item: base.Graph, *args: Any, **kwargs: Any) -> None:
        """Combines 'item' with the stored graph.

        Args:
            item (Graph): another Graph object to add to the stored graph.

        """
        other = base.transform(
            item = item,
            output = 'matrix',
            raise_same_error = False)
        new_matrix = other[0]
        length = len(self.contents)
        for row in enumerate(new_matrix):
            for column in enumerate(row):
                self.contents[row + length][column + length] = (
                    new_matrix[row][column])
        self.labels.extend(other[1])
        return

    def subset(
        self,
        include: Hashable | Sequence[Hashable] = None,
        exclude: Hashable | Sequence[Hashable] = None) -> Adjacency:
        """Returns a new graph without a subset of 'contents'.

        Args:
            include (Union[Hashable, Sequence[Hashable]]): nodes or edges which
                should be included in the new graph.
            exclude (Union[Hashable, Sequence[Hashable]]): nodes or edges which
                should not be included in the new graph.

        Returns:
           Adjacency: with only selected nodes and edges.

        """
        raise NotImplementedError

    """ Dunder Methods """

    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        """Returns whether 'instance' meets criteria to be a subclass.

        Args:
            instance (object): item to test as an instance.

        Returns:
            bool: whether 'instance' meets criteria to be a subclass.

        """
        return check.is_matrix(item = instance)
