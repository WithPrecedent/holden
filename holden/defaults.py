"""
defaults: settings for default classes for each graph form
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2022, Corey Rayburn Yung
License: Apache-2.0

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

This module does not presently have any function. It is intended to be used by
other packages which wish to use holden tools with other base type classes.

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

                     