"""Shared private tools used throughout `holden`.

Contents:
    _iterify: returns an item as an iterator without iterating over strings.
    _listify: returns an item as a list without splitting strings or nodes.
    _namify: returns a `str` name for an item.
    _pathlibify: converts a `str` to a `pathlib.Path`.
    _rawify: returns the raw structure stored in a composite data structure.
    _snakify: converts a capitalized `str` to snake case.
    _stabilize: returns items in a deterministic order.
    _typify: converts a `str` to an appropriate python type.
    _windowify: returns a sliding window over a sequence.

"""

from __future__ import annotations

import collections
import inspect
import itertools
import pathlib
import re
from collections.abc import Hashable, Iterable, Iterator, Sequence
from typing import Any

_SNAKE_FIRST = re.compile('(.)([A-Z][a-z]+)')
_SNAKE_SECOND = re.compile('([a-z0-9])([A-Z])')
_MISSING: Any = object()


def _iterify(item: Any) -> Iterator[Any]:
    """Returns `item` as an iterator, but does not iterate `str` types.

    Args:
        item: item to turn into an iterator.

    Returns:
        Iterator of `item`. A `str` or `bytes` type will be stored as a single
            item in the iterator. `None` returns an empty iterator.

    """
    if item is None:
        return iter(())
    if isinstance(item, str | bytes):
        return iter([item])
    try:
        return iter(item)
    except TypeError:
        return iter((item,))


def _listify(item: Any) -> list[Any]:
    """Returns `item` as a `list`.

    Lists, tuples, sets, frozensets, and deques are converted to a `list`.
    Any other object (including a `str`) is wrapped in a new `list`. `None`
    returns an empty `list`.

    Because a tuple is treated as a collection of nodes, a tuple that is meant
    to be a single node should be wrapped in a list by the caller.

    Args:
        item: item to turn into a `list`.

    Returns:
        `item` as a `list`.

    """
    if item is None:
        return []
    if isinstance(item, list | tuple | set | frozenset | collections.deque):
        return list(item)
    return [item]


def _namify(item: Any, /, default: str | None = None) -> str | None:
    """Returns `str` name representation of `item`.

    Args:
        item: item to determine a `str` name for.
        default: default name to return if other methods at name creation fail.
            Defaults to `None`.

    Returns:
        A name representation of `item`. If `item` is a `str`, it is returned.
            If `item` has a `str` `name` attribute, that is returned. Otherwise,
            the snake case name of the class of `item` (or of `item`, if it is
            a class) is returned.

    """
    if isinstance(item, str):
        return item
    if (
        hasattr(item, 'name')
        and not inspect.isclass(item)
        and isinstance(item.name, str)):
        return item.name
    try:
        return _snakify(item.__name__)
    except AttributeError:
        name = getattr(item.__class__, '__name__', None)
        return default if name is None else _snakify(name)


def _pathlibify(item: str | pathlib.Path) -> pathlib.Path:
    """Converts `str` `item` to a `pathlib.Path` object.

    Args:
        item: either a `str` of a path or a `pathlib.Path` object.

    Raises:
        TypeError: if `item` is neither a `str` or `pathlib.Path` type.

    Returns:
        `pathlib.Path` object.

    """
    if isinstance(item, str):
        return pathlib.Path(item)
    if isinstance(item, pathlib.Path):
        return item
    raise TypeError('item must be str or pathlib.Path type')


def _rawify(item: Any) -> Any:
    """Returns the raw structure stored in `item`.

    Composite data structures store their data in a `contents` attribute (and,
    for a `Matrix`, a `labels` attribute). Raw python structures are returned
    unchanged.

    Args:
        item: composite data structure or raw structure.

    Returns:
        The raw structure. For a `Matrix`, this is a `tuple` of the stored
            matrix and its labels.

    """
    if isinstance(item, str | bytes | list | tuple | dict | set | frozenset):
        return item
    contents = getattr(item, 'contents', _MISSING)
    if contents is _MISSING:
        return item
    labels = getattr(item, 'labels', _MISSING)
    if labels is _MISSING:
        return contents
    return contents, labels


def _snakify(item: str) -> str:
    """Converts a capitalized `str` to snake case.

    Args:
        item: `str` to convert.

    Returns:
        `item` converted to snake case.

    """
    item = _SNAKE_FIRST.sub(r'\1_\2', item)
    return _SNAKE_SECOND.sub(r'\1_\2', item).lower()


def _stabilize(items: Iterable[Any]) -> list[Any]:
    """Returns `items` in a deterministic order.

    Sets (such as those used for the values of an adjacency list) do not have a
    stable iteration order between python sessions. This function sorts by the
    `str` representation of each item so that output derived from sets is
    reproducible.

    Args:
        items: items to order.

    Returns:
        `items` as a `list` sorted by their `str` representations.

    """
    return sorted(items, key = str)


def _typify(item: Any) -> Any:
    """Converts `str` `item` to an appropriate, supported datatype.

    The function converts strings to `list` (if ', ' is present), `int`,
    `float`, or `bool` datatypes based upon the content of the string. If no
    alternative datatype is found, the item is returned in its original form.

    Args:
        item: `str` to be converted to appropriate datatype. Any other type is
            returned unchanged.

    Returns:
        Converted `item`.

    """
    if not isinstance(item, str):
        return item
    try:
        return int(item)
    except ValueError:
        try:
            return float(item)
        except ValueError:
            if item.lower() in {'true', 'yes'}:
                return True
            if item.lower() in {'false', 'no'}:
                return False
            if ', ' in item:
                return [_typify(i) for i in item.split(', ')]
            return item


def _windowify(
    item: Sequence[Hashable],
    length: int,
    fill_value: Any | None = None,
    step: int = 1) -> Iterator[tuple[Any, ...]]:
    """Returns a sliding window of `length` over `item`.

    This code is adapted from `more_itertools.windowed` to remove a dependency.

    Args:
        item: sequence from which to return windows.
        length: length of window.
        fill_value: value to use for items in a window that do not exist when
            `length` > `len(item)`. Defaults to `None`.
        step: number of items to advance between each window. Defaults to 1.

    Raises:
        ValueError: if `length` is less than 0 or `step` is less than 1.

    Yields:
        tuple[Any, ...]: windows derived from the arguments.

    """
    if length < 0:
        raise ValueError('length must be >= 0')
    if length == 0:
        yield ()
        return
    if step < 1:
        raise ValueError('step must be >= 1')
    window: collections.deque[Any] = collections.deque(maxlen = length)
    remaining = length
    for _ in map(window.append, item):
        remaining -= 1
        if not remaining:
            remaining = step
            yield tuple(window)
    size = len(window)
    if size == 0:
        return
    if size < length:
        yield tuple(
            itertools.chain(window,
                itertools.repeat(fill_value, length - size)))
    elif 0 < remaining < min(step, length):
        window += (fill_value,) * remaining
        yield tuple(window)
