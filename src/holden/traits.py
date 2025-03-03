"""Characteristics of graphs, edges, and nodes.

Contents:
    Directed: a directed graph with unweighted edges.
    Exportable: mixin to allow exporting a graph to file.
    Fungible: mixin supporting conversion to other composite objects.
    Labeled: mixin to add a name attribute.
    # Storage:
    Weighted: mixin to add a weight attribute to an edge.

To Do:


"""
from __future__ import annotations

import abc
import contextlib
import dataclasses
from typing import TYPE_CHECKING, Any

from . import base, export, utilities

if TYPE_CHECKING:
    import pathlib
    from collections.abc import Collection, Hashable

    from . import composites, graphs


@dataclasses.dataclass
class Directed(abc.ABC):
    """Base class for directed graph data structures.

    Args:
        contents: stored collection of nodes and/or edges.

    """
    contents: Collection[Any]

    """ Required Subclass Properties """

    @property
    @abc.abstractmethod
    def endpoint(self) -> Hashable | Collection[Hashable]:
        """Returns the endpoint(s) of the stored composite."""  # noqa: D402

    @property
    @abc.abstractmethod
    def root(self) -> Hashable | Collection[Hashable]:
        """Returns the root(s) of the stored composite."""  # noqa: D402

    """ Required Subclass Methods """

    @abc.abstractmethod
    def append(self, item: Hashable | base.Graph, **kwargs: Any) -> None:
        """Appends `item` to the endpoint(s) of the stored composite.

        Args:
            item: a Node or Graph to add to the stored composite.
            kwargs: additional keyword arguments.

        """

    @abc.abstractmethod
    def prepend(self, item: Hashable | base.Graph, **kwargs: Any) -> None:
        """Prepends `item` to the root(s) of the stored composite.

        Args:
            item: a Node or Graph to add to the stored composite.
            kwargs: additional keyword arguments.

        """

    @abc.abstractmethod
    def walk(
        self,
        start: Hashable | None = None,
        stop: Hashable | None = None,
        path: base.Path | None = None,
        **kwargs: Any) -> base.Path:
        """Returns path in the stored composite from `start` to `stop`.

        Args:
            start: Node to start paths from. Defaults to None. If it is None,
                `start` will be assigned to `stop`.
            stop: Node to stop paths at. Defaults to None. If it is None,
                `stop` will be assigned to `endpoint`.
            path: a path from `start` to `stop`. Defaults to None. This
                parameter is used for recursively determining a path.
            kwargs: additional keyword arguments.

        Returns:
            Path(s) through the graph.

        """

    """ Dunder Methods """

    def __add__(self, other: base.Graph) -> None:
        """Adds `other` to the stored composite using `append`.

        Args:
            other: another graph to add to the current one.

        """
        self.append(item = other)
        return

    def __radd__(self, other: base.Graph) -> None:
        """Adds `other` to the stored composite using `prepend`.

        Args:
            other: another graph to add to the current one.

        """
        self.prepend(item = other)
        return


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
            path: path to export to. Defaults to None.
            name: name to put in the dot str. Defaults to None.
            settings: any global settings to add to the dot graph. Defaults to
                None.

        Returns:
            Composite object in graphviz dot format.

        """
        name = name or utilities._namify(self)
        return export.to_dot(
            item = self,
            path = path,
            name = name,
            settings = settings)

    def to_mermaid(
        self,
        path: str | pathlib.Path | None = None,
        name: str | None = None,
        settings: dict[str, Any] | None = None) -> str:
        """Converts the stored composite to a mermaid format.

        Args:
            path: path to export to. Defaults to None.
            name: name to put in the mermaid str. Defaults to None.
            settings: any global settings to add to the mermaid graph. Defaults
                to None.

        Returns:
            Composite object in mermaid format.

        """
        name = name or utilities._namify(self)
        return export.to_mermaid(
            item = self,
            path = path,
            name = name,
            settings = settings)


@dataclasses.dataclass
class Fungible(abc.ABC):  # noqa: B024
    """Mixin requirements for graphs that can be internally transformed."""

    """ Properties """

    @property
    def adjacency(self) -> graphs.Adjacency:
        """Returns the stored composite as an Adjacency."""
        return base.transform(
            item = self,
            output = 'adjacency',
            raise_same_error = False)

    @property
    def edges(self) -> graphs.Edges:
        """Returns the stored composite as an Edges."""
        return base.transform(
            item = self,
            output = 'edges',
            raise_same_error = False)

    @property
    def matrix(self) -> graphs.Matrix:
        """Returns the stored composite as a Matrix."""
        return base.transform(
            item = self,
            output = 'matrix',
            raise_same_error = False)

    @property
    def parallel(self) -> composites.Parallel:
        """Returns the stored composite as a Parallel."""
        return base.transform(
            item = self,
            output = 'parallel',
            raise_same_error = False)

    @property
    def serial(self) -> composites.Serial:
        """Returns the stored composite as a Serial."""
        return base.transform(
            item = self,
            output = 'serial',
            raise_same_error = False)

    """ Class Methods """

    @classmethod
    def from_adjacency(cls, item: graphs.Adjacency) -> Fungible:
        """Creates a composite data structure from an Adjacency."""
        return cls(contents = base.transform(
            item = item,
            output = base.classify(cls),
            raise_same_error = False))

    @classmethod
    def from_edges(cls, item: graphs.Edges) -> Fungible:
        """Creates a composite data structure from an Edges."""
        return cls(contents = base.transform(
            item = item,
            output = base.classify(cls),
            raise_same_error = False))

    @classmethod
    def from_matrix(cls, item: graphs.Matrix) -> Fungible:
        """Creates a composite data structure from a Matrix."""
        return cls(contents = base.transform(
            item = item,
            output = base.classify(cls),
            raise_same_error = False))

    @classmethod
    def from_parallel(cls, item: composites.Parallel) -> Fungible:
        """Creates a composite data structure from a Parallel."""
        return cls(contents = base.transform(
            item = item,
            output = base.classify(cls),
            raise_same_error = False))

    @classmethod
    def from_serial(cls, item: composites.Serial) -> Fungible:
        """Creates a composite data structure from a Serial."""
        return cls(contents = base.transform(
            item = item,
            output = base.classify(cls),
            raise_same_error = False))


@dataclasses.dataclass
class Labeled(abc.ABC):  # noqa: B024
    """Mixin for labeling a composite object.

    Args:
        name: designates the name of a class instance that is used for internal
            and external referencing in a composite object. Defaults to None.
        contents: any stored item(s). Defaults to None.

    """
    name: str | None = None
    contents: Any | None = None

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes instance."""
        # To support usage as a mixin, it is important to call other base class
        # '__post_init__' methods, if they exist.
        with contextlib.suppress(AttributeError):
            super().__post_init__()
        self.name = self.name or self._namify()

    """ Private Methods """

    def _namify(self) -> str:
        """Returns str name of an instance.

        By default, if `contents` is None, 'none' will be returned. Otherwise,
        `utilities._namify` will be called based on the value of the `contents`
        attribute and its return value will be returned.

        For different naming rules, subclasses should override this method,
        which is automatically called when an instance is initialized.

        Returns:
            str label for part of a composite data structute.

        """
        return 'none' if self.contents is None else utilities._namify(self.contents)

    """ Dunder Methods """

    def __hash__(self) -> int:
        """Makes Node hashable based on `name`.

        Returns:
            int: hashable of `name`.

        """
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        """Determines equality based on `name` attribute.

        Args:
            other: other object to test for equivalance.

        Returns:
            bool: whether `name` is the same as `other.name`.

        """
        try:
            return str(self.name) == str(other.name)
        except AttributeError:
            return str(self.name) == other

    # def __ne__(self, other: object) -> bool:
    #     """Determines inequality based on 'name' attribute.

    #     Args:
    #         other (object): other object to test for equivalance.

    #     Returns:
    #         bool: whether 'name' is not the same as 'other.name'.

    #     """
    #     return not(self == other)


# @dataclasses.dataclass
# class Storage(abc.ABC):
#     """Mixin for storage of nodes in a Library with the composite object.

#     Args:
#         contents: stored collection of nodes and/or edges.

#     """
#     contents: Collection[Any]
#     nodes: MutableMapping[Hashable, Any] = dataclasses.field(
#         default_factory = dict)


@dataclasses.dataclass
class Weighted(abc.ABC):  # noqa: B024
    """Mixin for weighted nodes.

    Args:
        weight: the weight of the object. Defaults to 1.0.

    """
    weight: float | None = 1.0

    """ Dunder Methods """

    def __len__(self) -> float:
        """Returns `weight`.

        Returns:
            float: weight of the edge.

        """
        return self.weight
