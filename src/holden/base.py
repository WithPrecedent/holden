"""Base classes for composite data structures.

Contents:
    Structural: metaclass that allows raw python structures to pass
        `isinstance` checks for the forms of composite data structures.
    Forms: stores all direct subclasses of `Composite` and `Graph` and provides
        convenient classification and transformation methods.
    Composite: base class for all composite data structures.
    Graph: base class for graphs.
    Edge: base class for an edge in a graph. Many graphs will not require edge
        instances, but the class is made available for more complex graphs and
        type checking.
    Node: wrapper for items that can be stored in a composite data structure.

    classify: returns name of the form of the passed item.
    transform: general form transformer that allows any base form of a
        Composite or Graph to be changed to any other recognized form.

"""

from __future__ import annotations

import abc
import copy
import dataclasses
import inspect
from collections.abc import (
    Collection,
    Hashable,
    Iterable,
    MutableMapping,
    MutableSequence,
    Sequence)
from typing import Any, ClassVar, TypeAlias

import wonka

from . import check, utilities, workshop


GenericDict: TypeAlias = MutableMapping[Hashable, Any]
GenericList: TypeAlias = MutableSequence[Any]

# The order in which the built-in forms are checked by `classify`. This matters
# when a raw structure (such as an empty `list`) matches more than one form.
_PRIORITY: tuple[str, ...] = (
    'adjacency',
    'edges',
    'matrix',
    'parallel',
    'serial')


class Structural(abc.ABCMeta):
    """Metaclass that provides structural subtyping for composite forms.

    A class with this metaclass treats a raw python object as an instance if
    the object has the structure of the form that the class represents. For
    example, `isinstance({"a": {"b"}, "b": set()}, holden.Adjacency)` is `True`
    because the `dict` is structured as an adjacency list.

    """

    def __instancecheck__(cls, instance: object) -> bool:
        """Returns whether `instance` is an instance or has the right structure.

        Args:
            instance: item to test as an instance.

        Returns:
            Whether `instance` is an instance of `cls` or, if `cls` represents a
                form of composite, has the structure of that form.

        """
        if super().__instancecheck__(instance):
            return True
        checker = _get_checker(cls)
        return checker is not None and checker(instance)


@dataclasses.dataclass
class Forms(wonka.Registrar):
    """Registry of composite data structures.

    Attributes:
        registry: stores classes to be used in item construction. Keys are the
            snake case names of the classes. Defaults to an empty `dict`.

    """

    registry: ClassVar[GenericDict] = {}

    """ Public Methods """

    @classmethod
    def classify(cls, item: object) -> str:
        """Determines which form of composite that `item` is.

        There is no difference between this classmethod and the `classify`
        function.

        Args:
            item: object to classify.

        Returns:
            Name of form that `item` is.

        """
        return classify(item)

    @classmethod
    def register(cls, item: type[Composite], name: str | None = None) -> None:
        """Adds `item` to `registry`.

        The key assigned for storing `item` is determined using the `_namify`
        function if `name` is not passed.

        Args:
            item: class to register.
            name: key to use for storing `item`. Defaults to `None`.

        """
        name = name or utilities._namify(item)
        cls.registry[name] = item

    @classmethod
    def transform(
        cls,
        item: Any,
        output: str,
        *,
        raise_same_error: bool | None = True) -> Any:
        """General transform method that will call appropriate transformer.

        Unlike the `transform` function, this method will return a Composite
        wrapped in the form type stored in the `Forms` registry (as opposed to
        the raw type). So, if `output` is `edges`, this method will return an
        edge list in the `Edges` class. In contrast, the `transform` function
        will return the structural type of an edge list without using the
        `Edges` class. The rest of the logic is identical between the function
        and method.

        Args:
            item: composite data structure or raw form to transform.
            output: name of form to transform `item` to.
            raise_same_error: whether to raise an error if the form of `item`
                is the same as `output`. If `True`, a `ValueError` will be
                raised. If `False`, `item` will be returned without any change.
                Defaults to `True`.

        Raises:
            ValueError: if the form of `item` is the same as `output` and
                `raise_same_error` is `True` or if `output` is not a registered
                form.

        Returns:
            Transformed composite data structure.

        """
        form = cls.classify(item)
        if form == output:
            if raise_same_error:
                raise ValueError('The passed item and output are the same type')
            return item
        raw = _to_raw(item, output)
        return _wrap(cls.registry[output], output, raw)


""" Base Classes for Composite Data Structures """


@dataclasses.dataclass
class Composite(abc.ABC, metaclass = Structural):
    """Base class for composite data structures.

    A subclass must provide the `nodes` property and the `_add`, `_delete`,
    `_merge`, and `_subset` methods. The public methods of `Composite` provide
    validation and error-checking so that subclasses only need to provide the
    mechanism for each operation on the internal storage format they use.

    Every direct subclass of `Composite` is automatically registered in
    `Forms`.

    Args:
        contents: stored nodes or node labels. Subclasses should narrow the
            type for contents based on the internal storage format used.

    """

    contents: Collection[Any] | None = None

    """ Initialization Methods """

    def __init_subclass__(cls, *args: Any, **kwargs: Any) -> None:
        """Automatically registers subclass.

        Args:
            *args: positional arguments passed to other `__init_subclass__`
                methods.
            **kwargs: keyword arguments passed to other `__init_subclass__`
                methods.

        """
        # Because Composite will be used with mixins, it is important to call
        # other `__init_subclass__` methods, if they exist.
        super().__init_subclass__(*args, **kwargs)
        # Adds a subclass to the Forms registry only if it is a direct subclass
        # of Composite.
        if Composite in cls.__bases__ and abc.ABC not in cls.__bases__:
            Forms.register(item = cls)

    """ Properties """

    @property
    def nodes(self) -> set[Hashable]:
        """Returns a set of all nodes in the stored composite data structure.

        Raises:
            NotImplementedError: if a subclass does not provide `nodes`.

        """
        raise NotImplementedError

    """ Public Methods """

    def add(self, item: Hashable, **kwargs: Any) -> None:
        """Adds node to the stored composite data structure.

        Args:
            item: node to add to the stored composite data structure.
            **kwargs: additional keyword arguments.

        Raises:
            TypeError: if `item` is not a node type.
            ValueError: if `item` is already in the stored composite data
                structure.

        """
        if not check.is_node(item):
            raise TypeError(f'{item} is not a node type')
        if item in self:
            raise ValueError(
                f'{item} is already in the composite data structure')
        self._add(item, **kwargs)

    def delete(self, item: Hashable, **kwargs: Any) -> None:
        """Deletes node from the stored composite data structure.

        Args:
            item: node to delete from the stored composite data structure.
            **kwargs: additional keyword arguments.

        Raises:
            KeyError: if `item` is not in the stored composite data structure.
            TypeError: if `item` is not a node type.

        """
        if not check.is_node(item):
            raise TypeError(f'{item} is not a node type')
        if item not in self:
            raise KeyError(
                f'{item} does not exist in the composite data structure')
        try:
            self._delete(item, **kwargs)
        except KeyError as error:
            message = f'{item} does not exist in the composite data structure'
            raise KeyError(message) from error

    def merge(self, item: Any, **kwargs: Any) -> None:
        """Adds `item` to this Composite.

        This method is roughly equivalent to a `dict.update`, just adding `item`
        to the existing stored composite data structure while maintaining its
        structure.

        Args:
            item: another Composite or a raw form of a composite data structure
                to merge with.
            **kwargs: additional keyword arguments.

        Raises:
            TypeError: if `item` is not compatible composite data structure
                type.

        """
        try:
            classify(item)
        except TypeError as error:
            raise TypeError(f'{item} is not a compatible type') from error
        self._merge(item, **kwargs)

    def subset(
        self,
        include: Hashable | Sequence[Hashable] | None = None,
        exclude: Hashable | Sequence[Hashable] | None = None) -> Composite:
        """Returns a new Composite with a subset of the stored nodes.

        All edges will be removed that include any nodes that are not part of
        the new composite data structure.

        Any extra attributes that are part of a Composite (or a subclass) are
        maintained in the returned composite data structure.

        Args:
            include: node(s) which should be included in the new composite data
                structure. If `None`, all nodes are included (except those in
                `exclude`). Defaults to `None`.
            exclude: node(s) which should not be included in the new composite
                data structure. Defaults to `None`.

        Raises:
            ValueError: if `include` and `exclude` are both `None` or if any
                node in `include` or `exclude` is not in the stored composite
                data structure.

        Returns:
           Composite with only selected nodes and edges.

        """
        if include is None and exclude is None:
            raise ValueError('Either include or exclude must not be None')
        included = None if include is None else utilities._listify(include)
        excluded = utilities._listify(exclude)
        for label, values in (('include', included), ('exclude', excluded)):
            missing = [i for i in values or [] if i not in self]
            if missing:
                raise ValueError(
                    f'Some values in {label} are not in the composite data '
                    f'structure: {missing}')
        return self._subset(included, excluded)

    """ Private Methods """

    def _add(self, item: Hashable, **kwargs: Any) -> None:
        """Adds node to the stored composite data structure.

        Subclasses must provide their own specific methods for adding a single
        node. The provided `add` method offers all of the error checking.
        Subclasses just need to provide the mechanism for adding a single node
        without worrying about validation or error-checking.

        Args:
            item: node to add to the stored composite data structure.
            **kwargs: additional keyword arguments.

        """
        raise NotImplementedError

    def _delete(self, item: Hashable, **kwargs: Any) -> None:
        """Deletes node from the stored composite data structure.

        Subclasses must provide their own specific methods for deleting a single
        node. The provided `delete` method offers all of the error checking.
        Subclasses just need to provide the mechanism for deleting a single node
        without worrying about validation or error-checking.

        Args:
            item: node to delete from the stored composite data structure.
            **kwargs: additional keyword arguments.

        """
        raise NotImplementedError

    def _merge(self, item: Any, **kwargs: Any) -> None:
        """Combines `item` with the stored composite data structure.

        Subclasses must provide their own specific methods for merging with
        another composite data structure. The provided `merge` method offers all
        of the error checking. Subclasses just need to provide the mechanism for
        merging without worrying about validation or error-checking.

        Args:
            item: another Composite object or raw form to add to the stored
                composite data structure.
            **kwargs: additional keyword arguments.

        """
        raise NotImplementedError

    def _subset(
        self,
        include: list[Hashable] | None = None,
        exclude: list[Hashable] | None = None) -> Composite:
        """Returns a new Composite with a subset of the stored nodes.

        Subclasses must provide their own specific methods for returning a
        subset. Subclasses just need to provide the mechanism for returning a
        subset without worrying about validation or error-checking.

        Args:
            include: nodes which should be included in the new composite data
                structure. If `None`, all nodes are included.
            exclude: nodes which should not be included in the new composite
                data structure.

        Returns:
           Composite with only selected nodes and edges.

        """
        raise NotImplementedError

    @staticmethod
    def _selected(
        nodes: Iterable[Hashable],
        include: list[Hashable] | None,
        exclude: list[Hashable] | None) -> list[Hashable]:
        """Returns the nodes that should be kept in a subset.

        Args:
            nodes: nodes to select from.
            include: nodes that may be kept. If `None`, all nodes may be kept.
            exclude: nodes that may not be kept.

        Returns:
            Nodes in `nodes` (in their original order) that are in `include` (if
                it is not `None`) and are not in `exclude`.

        """
        return [
            node
            for node in nodes
            if (include is None or node in include)
            and node not in (exclude or [])]

    """ Dunder Methods """

    def __contains__(self, item: object) -> bool:
        """Returns whether `item` is a node in the composite data structure.

        Args:
            item: item to look for.

        Returns:
            Whether `item` is a node in the stored composite data structure.

        """
        try:
            return item in self.nodes
        except TypeError:
            return False


@dataclasses.dataclass
class Graph(Composite, abc.ABC):
    """Base class for holden graphs.

    Graph adds the requirements of `_connect` and `_disconnect` methods in
    addition to the requirements of Composite.

    Args:
        contents: stored nodes, node labels, edges, or edge labels. Subclasses
            should narrow the type for contents based on the internal storage
            format used.

    """

    contents: Collection[Any] | None = None

    # Whether `connect` should skip checking that the ends of an edge are
    # already nodes in the graph. It should be `True` for storage formats (such
    # as an edge list) which can only store nodes that are part of an edge.
    _implicit_nodes: ClassVar[bool] = False

    """ Initialization Methods """

    def __init_subclass__(cls, *args: Any, **kwargs: Any) -> None:
        """Automatically registers subclass.

        Args:
            *args: positional arguments passed to other `__init_subclass__`
                methods.
            **kwargs: keyword arguments passed to other `__init_subclass__`
                methods.

        """
        # Because Graph will be used with mixins, it is important to call other
        # `__init_subclass__` methods, if they exist.
        super().__init_subclass__(*args, **kwargs)
        # Adds a subclass to the Forms registry only if it is a direct subclass
        # of Graph.
        if Graph in cls.__bases__:
            Forms.register(item = cls)

    """ Public Methods """

    def connect(
        self, item: Edge | tuple[Hashable, Hashable], **kwargs: Any) -> None:
        """Adds edge to the stored graph.

        Args:
            item: edge to add to the stored graph.
            **kwargs: additional keyword arguments.

        Raises:
            TypeError: if `item` is not an edge type.
            ValueError: if the ends of the item are the same or if one of the
                edge ends does not currently exist in the stored graph.

        """
        if not check.is_edge(item):
            raise TypeError(f'{item} is not an edge type')
        if item[0] == item[1]:
            raise ValueError(
                'The starting point of an edge cannot be the same as the '
                'ending point')
        if not self._implicit_nodes:
            if item[0] not in self:
                raise ValueError(f'{item[0]} is not in the graph')
            if item[1] not in self:
                raise ValueError(f'{item[1]} is not in the graph')
        self._connect(item, **kwargs)

    def disconnect(
        self, item: Edge | tuple[Hashable, Hashable], **kwargs: Any) -> None:
        """Removes edge from the stored graph.

        Args:
            item: edge to delete from the stored graph.
            **kwargs: additional keyword arguments.

        Raises:
            TypeError: if `item` is not an edge type.
            ValueError: if the edge does not exist in the stored graph.

        """
        if not check.is_edge(item):
            raise TypeError(f'{item} is not an edge type')
        try:
            self._disconnect(item, **kwargs)
        except (KeyError, ValueError) as error:
            message = f'The edge ({item[0]}, {item[1]}) is not in the graph'
            raise ValueError(message) from error

    """ Private Methods """

    def _connect(
        self, item: Edge | tuple[Hashable, Hashable], **kwargs: Any) -> None:
        """Adds edge to the stored graph.

        Subclasses must provide their own specific methods for adding a single
        edge. The provided `connect` method offers all of the error checking.
        Subclasses just need to provide the mechanism for adding a single edge
        without worrying about validation or error-checking.

        Args:
            item: edge to add to the stored graph.
            **kwargs: additional keyword arguments.

        """
        raise NotImplementedError

    def _disconnect(
        self, item: Edge | tuple[Hashable, Hashable], **kwargs: Any) -> None:
        """Removes edge from the stored graph.

        Subclasses must provide their own specific methods for deleting a single
        edge. The provided `disconnect` method offers all of the error checking.
        Subclasses just need to provide the mechanism for deleting a single edge
        without worrying about validation or error-checking.

        Args:
            item: edge to delete from the stored graph.
            **kwargs: additional keyword arguments.

        """
        raise NotImplementedError


@dataclasses.dataclass(frozen = True, order = True)
class Edge(Sequence):  # noqa: PLW1641
    """Base class for an edge in a graph structure.

    Edges are not required for most of the base graph classes in holden. But
    they can be used by subclasses of those base classes for more complex data
    structures.

    An Edge is a drop-in replacement for a `tuple` of 2 nodes. It can be
    indexed, iterated over, unpacked, and compared to a `tuple`.

    Args:
        start: starting point for the edge.
        stop: stopping point for the edge.

    """

    start: Hashable
    stop: Hashable

    """ Dunder Methods """

    def __getitem__(self, index: Any) -> Any:
        """Allows Edge subclass to be accessed by index.

        Args:
            index: index (or slice) of the point(s) of the edge to return. 0 is
                `start` and 1 is `stop`.

        Raises:
            IndexError: if `index` is out of bounds.

        Returns:
            Contents of the point identified by `index`.

        """
        return (self.start, self.stop)[index]

    def __len__(self) -> int:
        """Returns length of 2.

        Returns:
            2

        """
        return 2

    def __eq__(self, other: object) -> bool:
        """Returns whether `other` is an equivalent edge or `tuple`.

        Args:
            other: another Edge or a `tuple` to compare to.

        Returns:
            Whether the start and stop of `other` match those of this edge.

        """
        if isinstance(other, Edge):
            return (self.start, self.stop) == (other.start, other.stop)
        if isinstance(other, tuple):
            return (self.start, self.stop) == other
        return NotImplemented


@dataclasses.dataclass
class Node(Hashable):
    """Vertex wrapper to provide hashability to any object.

    Node acts a basic wrapper for any item stored in a graph structure.

    Args:
        contents: any stored item(s). Defaults to `None`.

    """

    contents: Any | None = None

    """ Initialization Methods """

    def __init_subclass__(cls, *args: Any, **kwargs: Any) -> None:
        """Forces subclasses to keep the hash and equivalence methods.

        This is necessary because dataclasses, by design, do not automatically
        inherit the hash and equivalence dunder methods from their super
        classes. If a mixin (such as `Labeled`) that comes before `Node` in the
        method resolution order provides `__hash__` or `__eq__`, that mixin's
        version is kept.

        Args:
            *args: positional arguments passed to other `__init_subclass__`
                methods.
            **kwargs: keyword arguments passed to other `__init_subclass__`
                methods.

        """
        # Calls other `__init_subclass__` methods for parent and mixin classes.
        super().__init_subclass__(*args, **kwargs)
        # Explicitly stores inherited methods so that `dataclasses.dataclass`
        # does not overwrite them.
        if '__hash__' not in cls.__dict__:
            cls.__hash__ = cls.__hash__  # type: ignore[method-assign]
        if '__eq__' not in cls.__dict__ and cls.__eq__ not in {
            Node.__eq__,
            object.__eq__}:
            cls.__eq__ = cls.__eq__  # type: ignore[method-assign]

    """ Dunder Methods """

    def __hash__(self) -> int:
        """Makes Node hashable so that it can be used as a key in a dict.

        Rather than using the object ID, this method allows two Nodes with the
        same contents to be treated as the same node. If the stored contents
        are not hashable (such as a `list`), the hash of the `repr` is used.

        Returns:
            Hash of the values of all of the dataclass fields.

        """
        values = tuple(getattr(self, f.name) for f in dataclasses.fields(self))
        try:
            return hash(values)
        except TypeError:
            return hash(repr(self))


""" Subtype Checker """


def classify(item: object) -> str:
    """Determines which form of composite data structure that `item` is.

    Registered classes are checked first. If `item` is not an instance (or
    subclass) of a registered class, the structure of `item` is checked against
    each form using the `is_{form}` functions in the `check` module.

    Args:
        item: object to classify.

    Raises:
        TypeError: if `item` is not a recognized form.

    Returns:
        Name of form that `item` is.

    """
    names = _ordered_forms()
    subtype = item if inspect.isclass(item) else item.__class__
    for name in names:
        if issubclass(subtype, Forms.registry[name]):
            return name
    for name in names:
        checker = getattr(check, f'is_{name}', None)
        if checker is not None and checker(item):
            return name
    raise TypeError('The passed item is not a recognized composite form')


""" Form Transformer """


def transform(
    item: Any,
    output: str,
    *,
    raise_same_error: bool | None = True) -> Any:
    """General transform function that will call appropriate transformer.

    Args:
        item: composite data structure or raw form to transform.
        output: name of form to transform `item` to.
        raise_same_error: whether to raise an error if the form of `item` is
            the same as `output`. If `True`, a `ValueError` will be raised. If
            `False`, `item` will be returned without any change. Defaults to
            `True`.

    Raises:
        ValueError: if the form of `item` is the same as `output` and
            `raise_same_error` is `True` or if `output` is not a registered
            form.

    Returns:
        Transformed composite data structure in its raw form (for example, a
            `dict` for `adjacency`).

    """
    form = classify(item)
    if form == output:
        if raise_same_error:
            raise ValueError('The passed item and output are the same type')
        return item
    return _to_raw(item, output)


""" Private Functions """


def _get_checker(cls: type) -> Any:
    """Returns the structural checker function for a composite class.

    Args:
        cls: class to find a checker for.

    Returns:
        The checker function for `cls` or `None` if `cls` does not represent a
            form of composite data structure.

    """
    if cls is Composite:
        return check.is_composite
    if cls is Graph:
        return check.is_graph
    for name, form in Forms.registry.items():
        if form is cls:
            return getattr(check, f'is_{name}', None)
    return None


def _ordered_forms() -> list[str]:
    """Returns the names of registered forms in the order they are checked.

    Returns:
        Names of the built-in forms (that are registered) followed by the names
            of any other registered forms.

    """
    names: list[str] = [name for name in _PRIORITY if name in Forms.registry]
    names.extend(str(name) for name in Forms.registry if name not in names)
    return names


def _to_raw(item: Any, output: str) -> Any:
    """Returns the raw form of `output` derived from `item`.

    Args:
        item: composite data structure or raw form to transform.
        output: name of form to transform `item` to.

    Raises:
        ValueError: if `output` is not a registered form.
        NotImplementedError: if there is no transformer to `output` from the
            form of `item`.

    Returns:
        Raw form of `output` derived from `item`.

    """
    if output not in Forms.registry:
        raise ValueError(f'{output} is not a registered form')
    form = classify(item)
    raw = utilities._rawify(item)
    if form == output:
        return raw
    transformer = getattr(
        workshop, workshop._transformer_name(form, output), None)
    if transformer is None:
        raise NotImplementedError(
            f'There is no transformer from {form} to {output}')
    return transformer(item = raw)


def _wrap(form: type[Composite], name: str, raw: Any) -> Composite:
    """Wraps a raw form in a composite class.

    Args:
        form: composite class to create.
        name: name of the form of `raw`.
        raw: raw form to store in the new instance.

    Returns:
        Instance of `form` that stores `raw`.

    """
    if name == 'matrix':
        return form(contents = raw[0],  # type: ignore[call-arg]
            labels = raw[1])
    return form(contents = raw)


def _copy_raw(item: Any) -> Any:
    """Returns a copy of the containers in a raw form.

    The nodes themselves are not copied.

    Args:
        item: raw form to copy.

    Returns:
        Copy of `item` where every mutable container is new.

    """
    if isinstance(item, MutableMapping):
        return {
            key: set(value) if isinstance(value, set) else value
            for key, value in item.items()}
    if isinstance(item, tuple):
        return tuple(_copy_raw(i) for i in item)
    if isinstance(item, list):
        return [_copy_raw(i) if isinstance(i, list) else i for i in item]
    return copy.copy(item)
