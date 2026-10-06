"""Characteristics of graphs, edges, and nodes.

Traits are mixin classes. When combined with a form of graph, put `Directed`
before the form so that its operators (`+` and `+=`) are used.

Contents:
    Directed: mixin for directed graphs with roots, endpoints, and paths.
    Exportable: mixin to allow exporting a graph to file.
    Fungible: mixin supporting conversion to other composite objects.
    Labeled: mixin to add a name attribute.
    Storage: mixin to store data for nodes separate from the graph structure.
    Weighted: mixin to add a weight attribute to an edge.

"""

from __future__ import annotations

import abc
import dataclasses
from typing import TYPE_CHECKING, Any, Self, cast
from collections.abc import Hashable, MutableMapping, MutableSequence

from . import base, check, export, report, traverse, utilities

if TYPE_CHECKING:
    import pathlib
    from . import composites, graphs, kinds


@dataclasses.dataclass
class Directed(abc.ABC):  # noqa: B024
    """Mixin for directed graph data structures.

    The methods of `Directed` work for any form of graph (or composite data
    structure) that `holden` recognizes. Subclasses may override the methods and
    properties to use more efficient approaches for their internal storage
    formats.

    """

    """ Properties """

    @property
    def endpoint(self) -> list[Hashable]:
        """Returns the endpoints of the stored composite."""
        return list(report.get_endpoints(self))

    @property
    def root(self) -> list[Hashable]:
        """Returns the roots of the stored composite."""
        return list(report.get_roots(self))

    """ Public Methods """

    def append(
        self,
        item: Any,
        attachment: Hashable | MutableSequence[Hashable] | None = None,
        **kwargs: Any) -> None:
        """Appends `item` to the endpoint(s) of the stored composite.

        Appending merges `item` into the stored composite and creates an edge
        from every endpoint of the stored composite to every root of `item`.

        Args:
            item: a node, another composite data structure, or a raw form of a
                composite data structure to add to the stored composite.
            attachment: the endpoint or endpoints to attach `item` to.
                If `None`, all existing endpoints of the stored composite are
                used.
            **kwargs: additional keyword arguments passed to `add`.

        Raises:
            TypeError: if `item` is neither a recognized composite form nor a
                node.

        """
        graph: Any = self
        if attachment is None:
            endpoints = self.endpoint
        else:
            endpoints = utilities._listify(attachment)
        other = _to_adjacency(item)
        if other is not None:
            graph.merge(item = item)
            for endpoint in endpoints:
                for root in report.get_roots_adjacency(other):
                    if endpoint != root:
                        graph.connect((endpoint, root))
        elif check.is_node(item):
            self._include(item, endpoints, **kwargs)
            for endpoint in endpoints:
                if endpoint != item:
                    graph.connect((endpoint, item))
        else:
            raise TypeError('item is not a recognized graph or node type')

    def prepend(self, item: Any, **kwargs: Any) -> None:
        """Prepends `item` to the root(s) of the stored composite.

        Prepending merges `item` into the stored composite and creates an edge
        from every endpoint of `item` to every root of the stored composite.

        Args:
            item: a node, another composite data structure, or a raw form of a
                composite data structure to add to the stored composite.
            **kwargs: additional keyword arguments passed to `add`.

        Raises:
            TypeError: if `item` is neither a recognized composite form nor a
                node.

        """
        graph: Any = self
        roots = self.root
        other = _to_adjacency(item)
        if other is not None:
            graph.merge(item = item)
            for root in roots:
                for endpoint in report.get_endpoints_adjacency(other):
                    if endpoint != root:
                        graph.connect((endpoint, root))
        elif check.is_node(item):
            self._include(item, roots, **kwargs)
            for root in roots:
                if root != item:
                    graph.connect((item, root))
        else:
            raise TypeError('item is not a recognized graph or node type')

    def walk(
        self,
        start: Hashable | list[Hashable] | None = None,
        stop: Hashable | list[Hashable] | None = None) -> kinds.RawParallel:
        """Returns all paths in the stored composite from `start` to `stop`.

        Args:
            start: node (or list of nodes) to start paths from. If it is `None`,
                paths start from every root. Defaults to `None`.
            stop: node (or list of nodes) to stop paths at. If it is `None`,
                paths stop at every endpoint. Defaults to `None`.

        Returns:
            A list of possible paths (each path is a list of nodes) from `start`
                to `stop`.

        """
        return traverse.walk(self, start = start, stop = stop)

    """ Private Methods """

    def _include(
        self, item: Hashable, others: list[Hashable], **kwargs: Any) -> None:
        """Adds a node to the stored composite if it is not already stored.

        Args:
            item: node to add to the stored composite.
            others: nodes that `item` will be connected to.
            **kwargs: additional keyword arguments passed to `add`.

        Raises:
            ValueError: if the stored composite can only store nodes that are
                part of an edge and there is no other node to connect `item` to.

        """
        graph: Any = self
        if getattr(self, '_implicit_nodes', False):
            if not others:
                raise ValueError(
                    'A node cannot be stored by itself in this composite '
                    'data structure')
        elif item not in graph:
            graph.add(item, **kwargs)

    """ Dunder Methods """

    def __add__(self, other: Any) -> Self:
        """Adds `other` to the stored composite using `append`.

        Args:
            other: another graph or node to add to the current one.

        Returns:
            This instance after `other` has been appended.

        """
        self.append(item = other)
        return self

    def __iadd__(self, other: Any) -> Self:
        """Adds `other` to the stored composite using `append`.

        Args:
            other: another graph or node to add to the current one.

        Returns:
            This instance after `other` has been appended.

        """
        self.append(item = other)
        return self

    def __radd__(self, other: Any) -> Self:
        """Adds `other` to the stored composite using `prepend`.

        Args:
            other: another graph or node to add to the current one.

        Returns:
            This instance after `other` has been prepended.

        """
        self.prepend(item = other)
        return self


@dataclasses.dataclass
class Exportable(abc.ABC):  # noqa: B024
    """Mixin for exporting graphs to other formats."""

    """ Public Methods """

    def to_dot(
        self,
        path: str | pathlib.Path | None = None,
        name: str | None = None,
        settings: dict[str, Any] | None = None) -> str:
        """Converts the stored composite to a dot format.

        Args:
            path: path to export to. Defaults to `None`.
            name: name to put in the dot `str`. Defaults to the snake case name
                of the class.
            settings: any global settings to add to the dot graph. Defaults to
                `None`.

        Returns:
            Composite object in graphviz dot format.

        """
        name = name or utilities._namify(self)
        return export.to_dot(
            item = self, path = path, name = name or 'holden',
                settings = settings)

    def to_mermaid(
        self,
        path: str | pathlib.Path | None = None,
        name: str | None = None,
        settings: dict[str, Any] | None = None) -> str:
        """Converts the stored composite to a mermaid format.

        Args:
            path: path to export to. Defaults to `None`.
            name: name to put in the mermaid `str`. Defaults to the snake case
                name of the class.
            settings: any global settings to add to the mermaid graph. Defaults
                to `None`.

        Returns:
            Composite object in mermaid format.

        """
        name = name or utilities._namify(self)
        return export.to_mermaid(
            item = self, path = path, name = name or 'holden',
                settings = settings)


@dataclasses.dataclass
class Fungible(abc.ABC):  # noqa: B024
    """Mixin for composite data structures that can be transformed.

    Every form can be accessed as a property. The property returns an instance
    of the default class for that form (see `holden.Forms`). If the composite is
    already that form, the composite itself is returned. Every form can also be
    used to create a new instance using the `from_{form}` class methods.

    """

    """ Properties """

    @property
    def adjacency(self) -> graphs.Adjacency:
        """Returns the stored composite as an Adjacency."""
        return cast(
            'graphs.Adjacency',
            base.Forms.transform(self, 'adjacency', raise_same_error = False))

    @property
    def edges(self) -> graphs.Edges:
        """Returns the stored composite as an Edges."""
        return cast(
            'graphs.Edges',
            base.Forms.transform(self, 'edges', raise_same_error = False))

    @property
    def matrix(self) -> graphs.Matrix:
        """Returns the stored composite as a Matrix."""
        return cast(
            'graphs.Matrix',
            base.Forms.transform(self, 'matrix', raise_same_error = False))

    @property
    def parallel(self) -> composites.Parallel:
        """Returns the stored composite as a Parallel."""
        return cast(
            'composites.Parallel',
            base.Forms.transform(self, 'parallel', raise_same_error = False))

    @property
    def serial(self) -> composites.Serial:
        """Returns the stored composite as a Serial."""
        return cast(
            'composites.Serial',
            base.Forms.transform(self, 'serial', raise_same_error = False))

    """ Class Methods """

    @classmethod
    def from_adjacency(
        cls, item: graphs.Adjacency | kinds.RawAdjacency) -> Self:
        """Creates a composite data structure from an adjacency list.

        Args:
            item: an `Adjacency` or a raw adjacency list.

        Returns:
            New instance of this class derived from `item`.

        """
        return cls._from(item, 'adjacency')

    @classmethod
    def from_edges(
        cls, item: graphs.Edges | kinds.RawEdges) -> Self:
        """Creates a composite data structure from an edge list.

        Args:
            item: an `Edges` or a raw edge list.

        Returns:
            New instance of this class derived from `item`.

        """
        return cls._from(item, 'edges')

    @classmethod
    def from_matrix(
        cls, item: graphs.Matrix | kinds.RawMatrix) -> Self:
        """Creates a composite data structure from an adjacency matrix.

        Args:
            item: a `Matrix` or a raw adjacency matrix (a `tuple` of the matrix
                and a list of labels for its nodes).

        Returns:
            New instance of this class derived from `item`.

        """
        return cls._from(item, 'matrix')

    @classmethod
    def from_parallel(
        cls, item: composites.Parallel | kinds.RawParallel) -> Self:
        """Creates a composite data structure from a parallel structure.

        Args:
            item: a `Parallel` or a raw list of lists of nodes.

        Returns:
            New instance of this class derived from `item`.

        """
        return cls._from(item, 'parallel')

    @classmethod
    def from_serial(cls, item: composites.Serial | kinds.RawSerial) -> Self:
        """Creates a composite data structure from a serial structure.

        Args:
            item: a `Serial` or a raw list of nodes.

        Returns:
            New instance of this class derived from `item`.

        """
        return cls._from(item, 'serial')

    @classmethod
    def _from(cls, item: Any, form: str) -> Self:
        """Creates an instance of this class from `item`.

        Args:
            item: composite data structure or raw form.
            form: name of the form that `item` is expected to be.

        Raises:
            TypeError: if `item` is not the form `form`.

        Returns:
            New instance of this class.

        """
        checker = getattr(check, f'is_{form}')
        if base.classify(item) != form and not checker(item):
            raise TypeError(f'item is not a(n) {form} form')
        output = base.classify(cls)
        raw = utilities._rawify(
            base.transform(item, output, raise_same_error = False))
        return cast('Self', base._wrap(
            cls, output, base._copy_raw(raw)))  # type: ignore[arg-type]


@dataclasses.dataclass
class Labeled(abc.ABC):  # noqa: B024
    """Mixin for labeling a composite object.

    Labeled objects are hashed and compared by their `name`, so that a `str`
    equal to the name of a labeled node can be used in place of the node.

    Args:
        name: designates the name of a class instance that is used for internal
            and external referencing in a composite object. If it is not
            passed, `_namify` is used to create a name. Defaults to `None`.
        contents: any stored item(s). Defaults to `None`.

    """

    name: str | None = None
    contents: Any | None = None

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes instance."""
        # To support usage as a mixin, it is important to call other base class
        # '__post_init__' methods, if they exist.
        parent = getattr(super(), '__post_init__', None)
        if parent is not None:
            parent()
        self.name = self.name or self._namify()

    """ Private Methods """

    def _namify(self) -> str:
        """Returns `str` name of an instance.

        If a subclass sets a `str` class attribute called `name`, that is
        returned. Otherwise, if `contents` is `None`, "none" will be returned.
        Otherwise, `utilities._namify` will be called based on the value of the
        `contents` attribute and its return value will be returned.

        For different naming rules, subclasses should override this method,
        which is automatically called when an instance is initialized without a
        name.

        Returns:
            `str` label for part of a composite data structure.

        """
        class_name = getattr(type(self), 'name', None)
        if isinstance(class_name, str):
            return class_name
        if self.contents is None:
            return 'none'
        return str(utilities._namify(self.contents))

    """ Dunder Methods """

    def __hash__(self) -> int:
        """Makes the instance hashable based on `name`.

        Returns:
            Hash of `name`.

        """
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        """Determines equality based on `name` attribute.

        Args:
            other: other object to test for equivalence.

        Returns:
            Whether `name` is the same as `other.name` or, if `other` has no
                `name`, whether `name` equals `other`.

        """
        try:
            return str(self.name) == str(
                other.name)  # type: ignore[attr-defined]
        except AttributeError:
            return str(self.name) == other


@dataclasses.dataclass
class Storage(abc.ABC):  # noqa: B024
    """Mixin for storing data for nodes separate from the graph structure.

    The graph stores lightweight nodes (such as `str` labels). The data or
    objects that those labels represent are stored in `library`, so they can be
    reused without being part of the graph structure.

    Args:
        library: mapping of nodes to stored data. Defaults to an empty `dict`.

    """

    library: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = dict)

    """ Public Methods """

    def discard(self, node: Hashable) -> None:
        """Removes the data stored for `node`, if there is any.

        Args:
            node: node to remove stored data for.

        """
        self.library.pop(node, None)

    def retrieve(self, node: Hashable) -> Any:
        """Returns the data stored for `node`.

        Args:
            node: node to return the stored data of.

        Raises:
            KeyError: if there is no data stored for `node`.

        Returns:
            The data stored for `node`.

        """
        try:
            return self.library[node]
        except KeyError as error:
            raise KeyError(f'There is no data stored for {node}') from error

    def store(self, node: Hashable, item: Any) -> None:
        """Stores `item` as the data for `node`.

        Args:
            node: node to store data for. If this instance is a composite data
                structure, the node must be in it.
            item: data to store.

        Raises:
            KeyError: if this instance is a composite data structure and `node`
                is not in it.

        """
        if isinstance(self, base.Composite) and node not in self:
            raise KeyError(f'{node} is not in the composite data structure')
        self.library[node] = item


@dataclasses.dataclass
class Weighted(abc.ABC):  # noqa: B024
    """Mixin for weighted nodes and edges.

    Args:
        weight: the weight of the object. Defaults to 1.0.

    """

    weight: float = 1.0

    """ Dunder Methods """

    def __float__(self) -> float:
        """Returns `weight`.

        Returns:
            Weight of the object.

        """
        return float(self.weight)


def _to_adjacency(item: Any) -> kinds.RawAdjacency | None:
    """Returns `item` as a raw adjacency list if it is a composite form.

    Args:
        item: item to convert.

    Returns:
        Raw adjacency list derived from `item` or `None` if `item` is not a
            recognized composite form (for example, if it is a single node).

    """
    try:
        raw = utilities._rawify(
            base.transform(item, 'adjacency', raise_same_error = False))
    except TypeError:
        return None
    return cast('kinds.RawAdjacency', raw)
