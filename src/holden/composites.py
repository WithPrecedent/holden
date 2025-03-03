"""Base types of other composite data structures.

Contents:
    Parallel: `list`-like class containing Serial instances.
    Serial: `list`-like class containing nodes.

To Do:
    Complete Tree class and related functions

"""
from __future__ import annotations

import copy
import dataclasses
from typing import TYPE_CHECKING, Any

import bunches

from . import base, check, report, traits, traverse

if TYPE_CHECKING:
    from collections.abc import Hashable, MutableSequence, Sequence


@dataclasses.dataclass
class Parallel(bunches.Listing, traits.Directed, base.Composite):
    """Base class for a list of serial composites.

    Args:
        contents: Listing of Serial instances. Defaults to an empty list.

    """
    contents: MutableSequence[Serial] = dataclasses.field(
        default_factory = list)

    """ Properties """

    @property
    def endpoint(self) -> MutableSequence[Hashable]:
        """Returns the endpoints of the stored composite."""
        return report.get_endpoints_parallel(item = self)

    @property
    def root(self) -> MutableSequence[Hashable]:
        """Returns the roots of the stored composite."""
        return report.get_roots_parallel(item = self)

    """ Public Methods """

    def walk(
        self,
        start: Hashable | None = None,
        stop: Hashable | None = None) -> Parallel:
        """Returns all paths in graph from `start` to `stop`.

        Args:
            start: node to start paths from.
            stop: node to stop paths.

        Returns:
            A list of possible paths (each path is a list nodes) from `start` to
                `stop`.

        """
        root = self.root if start is None else bunches.listify(start)
        endpoint = self.endpoint if stop is None else self.bunches.listify(stop)
        return traverse.walk_parallel(
            item = self,
            start = root,
            stop = endpoint)

    """ Private Methods """

    def _add(self, item: Hashable, **kwargs: Any) -> None:
        """Adds node to the stored composite.

        Args:
            item: node to add to the stored composite.
            kwargs: additional keyword arguments.

        """
        self.contents.append(item)
        return

    def _delete(self, item: Hashable, **kwargs: Any) -> None:
        """Deletes node from the stored composite.

        Args:
            item: node to delete from `contents`.
            kwargs: additional keyword arguments.

        """
        del self.contents[item]
        return

    def _merge(self, item: base.Composite, **kwargs: Any) -> None:
        """Combines `item` with the stored composite.

        Subclasses must provide their own specific methods for merging with
        another composite. The provided `merge` method offers all of the error
        checking. Subclasses just need to provide the mechanism for merging
        ithout worrying about validation or error-checking.

        Args:
            item: another Composite object to add to the stored composite.
            kwargs: additional keyword arguments.

        """
        other = base.transform(
            item = item,
            output = 'parallel',
            raise_same_error = False)
        for serial in other:
            self.contents.append(serial)
        return

    def _subset(
        self,
        include: Hashable | Sequence[Hashable] = None,
        exclude: Hashable | Sequence[Hashable] = None) -> Parallel:
        """Returns a new composite without a subset of `contents`.

        Subclasses must provide their own specific methods for deleting a single
        edge. Subclasses just need to provide the mechanism for returning a
        subset without worrying about validation or error-checking.

        Args:
            include: nodes or edges which should be included in the new
                composite.
            exclude: nodes or edges which should not be included in the new
                composite.

        Returns:
           Parallel with only selected nodes and edges.

        """
        raise NotImplementedError

    """ Dunder Methods """

    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        """Returns whether `instance` meets criteria to be a subclass.

        Args:
            instance: item to test as an instance.

        Returns:
            Whether `instance` meets criteria to be a subclass.

        """
        return check.is_parallel(item = instance)


@dataclasses.dataclass
class Serial(bunches.DictList, traits.Directed, base.Composite):
    """Base class for serial composites.

    Args:
        contents: list of nodes. Defaults to an empty list.

    """
    contents: MutableSequence[Hashable] = dataclasses.field(
        default_factory = list)

    """ Properties """

    @property
    def endpoint(self) -> MutableSequence[Hashable]:
        """Returns the endpoints of the stored composite."""
        return report.get_endpoints_serial(item = self)

    @property
    def root(self) -> MutableSequence[Hashable]:
        """Returns the roots of the stored composite."""
        return report.get_roots_serial(item = self)

    """ Public Methods """

    def walk(
        self,
        start: Hashable | None = None,
        stop: Hashable | None = None) -> Parallel:
        """Returns all paths in graph from `start` to `stop`.

        Args:
            start: node to start paths from.
            stop: node to stop paths.

        Returns:
            Parallel list of possible paths (each path is a list nodes) from
                `start` to `stop`.

        """
        if start is None:
            start = self.root[0]
        if stop is None:
            stop = self.endpoint[0]
        return traverse.walk_serial(item = self, start = start, stop = stop)

    """ Private Methods """

    def _add(self, item: Hashable, **kwargs: Any) -> None:
        """Adds node to the stored composite.

        Args:
            item: node to add to the stored composite.
            kwargs: additional keyword arguments.

        """
        self.contents.append(item)
        return

    def _delete(self, item: Hashable, **kwargs: Any) -> None:
        """Deletes node from the stored composite.

        Args:
            item: node to delete from `contents`.
            kwargs: additional keyword arguments.

        """
        del self.contents[item]
        return

    def _merge(self, item: base.Composite, **kwargs: Any) -> None:
        """Combines `item` with the stored composite.

        Subclasses must provide their own specific methods for merging with
        another composite. The provided `merge` method offers all of the error
        checking. Subclasses just need to provide the mechanism for merging
        ithout worrying about validation or error-checking.

        Args:
            item: another Composite object to add to the stored composite.
            kwargs: additional keyword arguments.

        """
        other = base.transform(
            item = item,
            output = 'serial',
            raise_same_error = False)
        self.contents.extend(other)
        return

    def _subset(
        self,
        include: Hashable | Sequence[Hashable] = None,
        exclude: Hashable | Sequence[Hashable] = None) -> Serial:
        """Returns a new composite without a subset of `contents`.

        Subclasses must provide their own specific methods for deleting a single
        edge. Subclasses just need to provide the mechanism for returning a
        subset without worrying about validation or error-checking.

        Args:
            include: nodes or edges which should be included in the new
                composite.
            exclude: nodes or edges which should not be included in the new
                composite.

        Returns:
           Serial with only selected nodes and edges.

        """
        if include:
            new_serial = [i for i in self.contents if i in include]
        else:
            new_serial = copy.deepcopy(self.contents)
        if exclude:
            new_serial = [i for i in self.contents if i not in exclude]
        return self.__class__(contents = new_serial)

    """ Dunder Methods """

    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        """Returns whether `instance` meets criteria to be a subclass.

        Args:
            instance: item to test as an instance.

        Returns:
            Whether `instance` meets criteria to be a subclass.

        """
        return check.is_serial(item = instance)


# @dataclasses.dataclass
# class Tree(bunches.DictList, traits.Directed, base.Composite):
#     """Base class for an tree data structures.

#     The Tree class uses a DictList instead of a linked list for storing children
#     nodes to allow easier access of nodes further away from the root. For
#     example, a user might use 'a_tree["big_branch"]["small_branch"]["a_leaf"]'
#     to access a desired node instead of 'a_tree[2][0][3]' (although the latter
#     access technique is also supported).

#     Args:
#         contents (MutableSequence[Node]): list of stored Tree or other
#             Node instances. Defaults to an empty list.
#         name (Optional[str]): name of Tree node. Defaults to None.
#         parent (Optional[Tree]): parent Tree, if any. Defaults to None.
#         default_factory (Optional[Any]): default value to return or default
#             function to call when the 'get' method is used. Defaults to None.

#     """
#     contents: MutableSequence[Hashable] = dataclasses.field(
#         default_factory = list)
#     name: Optional[str] = None
#     parent: Optional[Tree] = None
#     default_factory: Optional[Any] = None

#     """ Properties """

#     @property
#     def children(self) -> MutableSequence[Hashable]:
#         """Returns child nodes of this Node."""
#         return self.contents

#     @children.setter
#     def children(self, value: MutableSequence[Hashable]) -> None:
#         """Sets child nodes of this Node."""
#         if bunches.is_sequence(value):
#             self.contents = value
#         else:
#             self.contents = [value]
#         return

#     @property
#     def endpoint(self) -> Union[Hashable, Collection[Hashable]]:
#         """Returns the endpoint(s) of the stored composite."""
#         if not self.contents:
#             return self
#         else:
#             return self.contents[0].endpoint

#     @property
#     def root(self) -> Union[Hashable, Collection[Hashable]]:
#         """Returns the root(s) of the stored composite."""
#         if self.parent is None:
#             return self
#         else:
#             return self.parent.root

#     """ Dunder Methods """

#     @classmethod
#     def __instancecheck__(cls, instance: object) -> bool:
#         """Returns whether `instance` meets criteria to be a subclass.

#         Args:
#             instance (object): item to test as an instance.

#         Returns:
#             bool: whether `instance` meets criteria to be a subclass.

#         """
#         return is_tree(item = instance)

#     def __missing__(self) -> Tree:
#         """Returns an empty tree if one does not exist.

#         Returns:
#             Tree: an empty instance of Tree.

#         """
#         return self.__class__()


# def is_tree(item: object) -> bool:
#     """Returns whether `item` is a tree.

#     Args:
#         item (object): instance to test.

#     Returns:
#         bool: whether `item` is a tree.

#     """
#     return (
#         isinstance(item, MutableSequence)
#         and all(isinstance(i, (MutableSequence, Hashable)) for i in item))

# def is_forest(item: object) -> bool:
#     """Returns whether `item` is a dict of tree.

#     Args:
#         item (object): instance to test.

#     Returns:
#         bool: whether `item` is a dict of tree.

#     """
#     return (
#         isinstance(item, MutableMapping)
#         and all(base.is_node(item = i) for i in item.keys())
#         and all(is_tree(item = i) for i in item.values()))


# # @functools.singledispatch
# def to_tree(item: Any) -> graphs.Tree:
#     """Converts `item` to a Tree.

#     Args:
#         item (Any): item to convert to a Tree.

#     Raises:
#         TypeError: if `item` is a type that is not registered.

#     Returns:
#         form.Tree: derived from `item`.

#     """
#     if check.is_tree(item = item):
#         return item
#     else:
#         raise TypeError(
#             f'item cannot be converted because it is an unsupported type: '
#             f'{type(item).__name__}')

# # @to_tree.register
# def matrix_to_tree(item: graphs.Matrix) -> graphs.Tree:
#     """Converts `item` to a Tree.

#     Args:
#         item (form.Matrix): item to convert to a Tree.

#     Raises:
#         TypeError: if `item` is a type that is not registered.

#     Returns:
#         form.Tree: derived from `item`.

#     """
#     tree = {}
#     for node in item:
#         children = item[:]
#         children.remove(node)
#         tree[node] = matrix_to_tree(children)
#     return tree
