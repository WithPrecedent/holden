"""Settings for default classes for each graph form.

Contents:
    
          
To Do:

    
"""
from __future__ import annotations
from typing import Type

from . import base
from . import composites
from . import graphs


_BASE_ADJACENCY: Type[base.Graph] = graphs.Adjacency
_BASE_EDGES: Type[base.Graph] = graphs.Edges
_BASE_MATRIX: Type[base.Graph] = graphs.Matrix
_BASE_PARALLEL: Type[base.Graph] = composites.Parallel
_BASE_SERIAL: Type[base.Graph] = composites.Serial

def set_base(name: str, value: Type[base.Graph]) -> None:
    """Sets default base class for a form of graph.

    Args:
        name (str): name of form to set.
        value (Type[base.Graph]): Graph subclass to use as the base type for
            the 'name' form.
            
    """
    variable = f'(_BASE_{name.upper()})'
    globals()[variable] = value
    return

                     