"""Composite data structures that store paths.

Contents:
    Parallel: `list`-like class containing Serial instances.
    Serial: `list`-like class containing nodes.

To Do:
    Complete Tree class and related functions

"""

from __future__ import annotations

import copy
import dataclasses
from collections.abc import MutableSequence
from typing import TYPE_CHECKING, Any

import bunches

from . import base, check, traits, utilities

if TYPE_CHECKING:
    from collections.abc import Hashable

    from . import kinds

__all__: list[str] = ['Parallel', 'Serial']


@dataclasses.dataclass
class Parallel(
    base.Composite,
    traits.Directed,
    traits.Fungible,
    traits.Exportable,
    bunches.Listing):
    """Base class for a list of serial composites.

    Each path in a Parallel is a `list` of nodes (or a `Serial`) that goes from
    one of its roots to one of its endpoints. A Parallel is `Directed`,
    `Fungible`, and `Exportable`.

    Args:
        contents: Listing of Serial instances (or lists of nodes). Defaults to
            an empty list.

    """

    contents: MutableSequence[Serial | MutableSequence[Hashable]] = (
        dataclasses.field(default_factory = list))

    """ Properties """

    @property
    def nodes(self) -> set[Hashable]:
        """Returns a set of all nodes in the stored composite."""
        return {
            node for path in self.contents for node in utilities._rawify(path)}

    """ Public Methods """

    def add(self, item: Any, **kwargs: Any) -> None:
        """Adds a path or a node to the stored composite.

        Args:
            item: a non-empty list of nodes (or a `Serial`) to add as a new
                path or a single node to add as a new path of one node.
            **kwargs: additional keyword arguments.

        Raises:
            ValueError: if `item` is an empty or otherwise invalid path or a
                node that is already in the stored composite.
            TypeError: if `item` is not a node.

        """
        if isinstance(item, MutableSequence):
            if not item or not check.is_serial(item):
                raise ValueError('A path must be a non-empty list of nodes')
            self.contents.append(item)
            return
        super().add(item, **kwargs)

    def append(
        self,
        item: Any,
        attachment: Hashable | MutableSequence[Hashable] | None = None,  # noqa: ARG002
        **kwargs: Any) -> None:
        """Appends `item` to the end of every path.

        If `item` has more than one path, every existing path is followed by
        every path of `item`.

        Args:
            item: node, path, or other composite data structure (or raw form).
            attachment: unused. It is accepted so that the method matches
                `Directed.append`, because paths always attach at their ends.
            **kwargs: additional keyword arguments.

        """
        other = _to_paths(item)
        if not other:
            return
        if not self.contents:
            self.contents.extend(other)
            return
        self.contents[:] = [
            [*utilities._rawify(path), *new_path]
            for path in self.contents
            for new_path in other]

    def prepend(self, item: Any, **kwargs: Any) -> None:
        """Prepends `item` to the start of every path.

        If `item` has more than one path, every path of `item` precedes every
        existing path.

        Args:
            item: node, path, or other composite data structure (or raw form).
            **kwargs: additional keyword arguments.

        """
        other = _to_paths(item)
        if not other:
            return
        if not self.contents:
            self.contents.extend(other)
            return
        self.contents[:] = [
            [*new_path, *utilities._rawify(path)]
            for new_path in other
            for path in self.contents]

    """ Private Methods """

    def _add(self, item: Hashable, **kwargs: Any) -> None:
        """Adds node to the stored composite as a path with a single node.

        Args:
            item: node to add to the stored composite.
            **kwargs: additional keyword arguments.

        """
        self.contents.append([item])

    def _delete(self, item: Hashable, **kwargs: Any) -> None:
        """Deletes node from every path in the stored composite.

        Paths that no longer have any nodes are removed.

        Args:
            item: node to delete from the stored composite.
            **kwargs: additional keyword arguments.

        """
        for path in self.contents:
            nodes = utilities._rawify(path)
            nodes[:] = [node for node in nodes if node != item]
        self.contents[:] = [
            path for path in self.contents if utilities._rawify(path)]

    def _merge(self, item: Any, **kwargs: Any) -> None:
        """Combines `item` with the stored composite.

        Args:
            item: another Composite object or raw form to add to the stored
                composite. Its paths are added as new paths.
            **kwargs: additional keyword arguments.

        """
        self.contents.extend(_to_paths(item))

    def _subset(
        self,
        include: list[Hashable] | None = None,
        exclude: list[Hashable] | None = None) -> Parallel:
        """Returns a new composite with a subset of the stored nodes.

        Args:
            include: nodes which should be included in the new composite. If
                `None`, all nodes are included.
            exclude: nodes which should not be included in the new composite.

        Returns:
            Parallel with only selected nodes. Paths that have no selected nodes
                are not included.

        """
        paths = [
            self._selected(utilities._rawify(path), include, exclude)
            for path in self.contents]
        new_composite = copy.copy(self)
        new_composite.contents = [path for path in paths if path]
        return new_composite


@dataclasses.dataclass
class Serial(
    base.Composite,
    traits.Directed,
    traits.Fungible,
    traits.Exportable,
    bunches.DictList):
    """Base class for serial composites.

    A Serial is a single path of nodes. It is `Directed`, `Fungible`, and
    `Exportable`.

    Args:
        contents: list of nodes. Defaults to an empty list.

    """

    contents: MutableSequence[Hashable] = dataclasses.field(
        default_factory = list)

    """ Properties """

    @property
    def nodes(self) -> set[Hashable]:
        """Returns a set of all nodes in the stored composite."""
        return set(self.contents)

    """ Public Methods """

    def append(
        self,
        item: Any,
        attachment: Hashable | MutableSequence[Hashable] | None = None,  # noqa: ARG002
        **kwargs: Any) -> None:
        """Appends `item` to the end of the stored composite.

        Args:
            item: a node, another composite data structure (or raw form) whose
                nodes are added in order.
            attachment: unused. It is accepted so that the method matches
                `Directed.append`, because nodes are always added at the end.
            **kwargs: additional keyword arguments.

        Raises:
            TypeError: if `item` is neither a recognized composite form nor a
                node.

        """
        self.contents.extend(_to_nodes(item))

    def prepend(self, item: Any, **kwargs: Any) -> None:
        """Prepends `item` to the start of the stored composite.

        Args:
            item: a node, another composite data structure (or raw form) whose
                nodes are added in order.
            **kwargs: additional keyword arguments.

        Raises:
            TypeError: if `item` is neither a recognized composite form nor a
                node.

        """
        self.contents[:0] = _to_nodes(item)

    """ Private Methods """

    def _add(self, item: Hashable, **kwargs: Any) -> None:
        """Adds node to the end of the stored composite.

        Args:
            item: node to add to the stored composite.
            **kwargs: additional keyword arguments.

        """
        self.contents.append(item)

    def _delete(self, item: Hashable, **kwargs: Any) -> None:
        """Deletes every instance of a node from the stored composite.

        Args:
            item: node to delete from the stored composite.
            **kwargs: additional keyword arguments.

        """
        self.contents[:] = [node for node in self.contents if node != item]

    def _merge(self, item: Any, **kwargs: Any) -> None:
        """Combines `item` with the stored composite.

        Args:
            item: another Composite object or raw form to add to the stored
                composite. Its nodes are added to the end.
            **kwargs: additional keyword arguments.

        """
        self.contents.extend(base._to_raw(item, 'serial'))

    def _subset(
        self,
        include: list[Hashable] | None = None,
        exclude: list[Hashable] | None = None) -> Serial:
        """Returns a new composite with a subset of the stored nodes.

        Args:
            include: nodes which should be included in the new composite. If
                `None`, all nodes are included.
            exclude: nodes which should not be included in the new composite.

        Returns:
            Serial with only selected nodes.

        """
        new_composite = copy.copy(self)
        new_composite.contents = self._selected(self.contents, include, exclude)
        return new_composite

    """ Dunder Methods """

    def __getitem__(self, key: Any) -> Any:
        """Returns value(s) for `key` in `contents`.

        Args:
            key: index, slice, or name of a node to search for in `contents`.

        Returns:
            Node(s) stored in `contents` that correspond to `key`.

        """
        if isinstance(key, slice):
            return self.contents[key]
        return super().__getitem__(key)


def _to_nodes(item: Any) -> list[Hashable]:
    """Returns the nodes of `item` for use in a serial path.

    Args:
        item: a node, another composite data structure, or a raw form.

    Raises:
        TypeError: if `item` is neither a recognized composite form nor a node.

    Returns:
        List of nodes. A node is returned in a list of one.

    """
    try:
        return list(
            utilities._rawify(
                base.transform(item, 'serial', raise_same_error = False)))
    except TypeError:
        if check.is_node(item):
            return [item]
        raise TypeError(
            'item is not a recognized composite or node type') from None


def _to_paths(item: Any) -> kinds.RawParallel:
    """Returns the paths of `item` for use in a parallel structure.

    Args:
        item: a node, another composite data structure, or a raw form.

    Raises:
        TypeError: if `item` is neither a recognized composite form nor a node.

    Returns:
        List of paths. A node is returned as a single path of one node.

    """
    try:
        paths = utilities._rawify(
            base.transform(item, 'parallel', raise_same_error = False))
    except TypeError:
        if check.is_node(item):
            return [[item]]
        raise TypeError(
            'item is not a recognized composite or node type') from None
    return [list(utilities._rawify(path)) for path in paths]
