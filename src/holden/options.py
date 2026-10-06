"""Settings for default classes for each graph form.

The default class for a form is the class that `holden.Forms` uses when it
transforms a composite data structure to that form (for example, when the
`Fungible.edges` property is accessed).

Contents:
    get_base: returns the default class for a form.
    set_base: sets the default class for a form.

"""

from __future__ import annotations

from typing import cast

from . import base, composites, graphs


_BASE_ADJACENCY: type[base.Composite] = graphs.Adjacency
_BASE_EDGES: type[base.Composite] = graphs.Edges
_BASE_MATRIX: type[base.Composite] = graphs.Matrix
_BASE_PARALLEL: type[base.Composite] = composites.Parallel
_BASE_SERIAL: type[base.Composite] = composites.Serial


def get_base(name: str) -> type[base.Composite]:
    """Returns the default base class for a form of composite data structure.

    Args:
        name: name of form to get.

    Raises:
        KeyError: if `name` is not a registered form.

    Returns:
        Class used as the base type for the `name` form.

    """
    try:
        return cast('type[base.Composite]', base.Forms.registry[name.lower()])
    except KeyError as error:
        raise KeyError(f'{name} is not a registered form') from error


def set_base(name: str, value: type[base.Composite]) -> None:
    """Sets default base class for a form of composite data structure.

    Args:
        name: name of form to set.
        value: Composite subclass to use as the base type for the `name` form.

    Raises:
        KeyError: if `name` is not a registered form.
        TypeError: if `value` is not a Composite subclass.

    """
    name = name.lower()
    if name not in base.Forms.registry:
        raise KeyError(f'{name} is not a registered form')
    if not (isinstance(value, type) and issubclass(value, base.Composite)):
        raise TypeError('value must be a Composite subclass')
    base.Forms.registry[name] = value
    globals()[f'_BASE_{name.upper()}'] = value
