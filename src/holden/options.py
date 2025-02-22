"""Settings for default classes for each graph form.

Contents:


To Do:


"""
from __future__ import annotations

from . import base, composites, graphs

_BASE_ADJACENCY: type[base.Graph] = graphs.Adjacency
_BASE_EDGES: type[base.Graph] = graphs.Edges
_BASE_MATRIX: type[base.Graph] = graphs.Matrix
_BASE_PARALLEL: type[base.Graph] = composites.Parallel
_BASE_SERIAL: type[base.Graph] = composites.Serial

def set_base(name: str, value: type[base.Graph]) -> None:
    """Sets default base class for a form of graph.

    Args:
        name (str): name of form to set.
        value (Type[base.Graph]): Graph subclass to use as the base type for
            the 'name' form.

    """
    variable = f'(_BASE_{name.upper()})'
    globals()[variable] = value
    return

