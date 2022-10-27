"""
report: inspection tools for composite data structures.
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

Contents:
    get_endpoints_adjacency
    get_roots_adjacency
    get_endpoints_edges
    get_roots_edges
    get_endpoints_matrix
    get_roots_matrix  
           
To Do:
    Implement remaining functions.
    
"""
from __future__ import annotations
from collections.abc import Hashable, MutableSequence
# import functools
import itertools
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import composites
    from . import graphs

    
""" Introspection Tools """

def get_endpoints_adjacency(
    item: graphs.Adjacency) -> MutableSequence[Hashable]:
    """Returns the endpoints in 'item'.

    Args:
        item (graphs.Adjacency): adjacency list object to examine.

    Returns:
        MutableSequence[Hashable]: list of endpoints.
        
    """  
    return [k for k in item.keys() if not item[k]]

def get_roots_adjacency(item: graphs.Adjacency) -> MutableSequence[Hashable]:
    """Returns the roots in 'item'.

    Args:
        item (graphs.Adjacency): adjacency list object to examine.

    Returns:
        MutableSequence[Hashable]: list of roots.
        
    """  
    stops = list(itertools.chain.from_iterable(item.values()))
    return [k for k in item.keys() if k not in stops]  

def get_endpoints_edges(item: graphs.Edges) -> MutableSequence[Hashable]:
    """Returns the endpoints in 'item'.

    Args:
        item (graphs.Edges): edge list object to examine.

    Returns:
        MutableSequence[Hashable]: list of endpoints.
        
    """  
    raise NotImplementedError

def get_roots_edges(item: graphs.Edges) -> MutableSequence[Hashable]:
    """Returns the roots in 'item'.

    Args:
        item (graphs.Edges): edge list object to examine.

    Returns:
        MutableSequence[Hashable]: list of roots.
        
    """  
    raise NotImplementedError    

def get_endpoints_matrix(item: graphs.Matrix) -> MutableSequence[Hashable]:
    """Returns the endpoints in 'item'.

    Args:
        item (graphs.Matrix): adjacency matrix object to examine.

    Returns:
        MutableSequence[Hashable]: list of endpoints.
        
    """  
    raise NotImplementedError

def get_roots_matrix(item: graphs.Matrix) -> MutableSequence[Hashable]:
    """Returns the roots in 'item'.

    Args:
        item (graphs.Matrix): adjacency matrix object to examine.

    Returns:
        MutableSequence[Hashable]: list of roots.
        
    """  
    raise NotImplementedError    

def get_endpoints_parallel(
    item: composites.Parallel) -> MutableSequence[Hashable]:
    """Returns the endpoints in 'item'.

    Args:
        item (composites.Parallel): parallel object to examine.

    Returns:
        MutableSequence[Hashable]: list of endpoints.
        
    """  
    return [p[-1] for p in item]

def get_roots_parallel(item: composites.Parallel) -> MutableSequence[Hashable]:
    """Returns the roots in 'item'.

    Args:
        item (composites.Parallel): parallel object to examine.

    Returns:
        MutableSequence[Hashable]: list of roots.
        
    """  
    return [p[0] for p in item]   

def get_endpoints_serial(item: composites.Serial) -> MutableSequence[Hashable]:
    """Returns the endpoints in 'item'.

    Args:
        item (composites.Serial): serial object to examine.

    Returns:
        MutableSequence[Hashable]: list of endpoints.
        
    """  
    return [item[-1]]

def get_roots_serial(item: composites.Serial) -> MutableSequence[Hashable]:
    """Returns the roots in 'item'.

    Args:
        item (composites.Serial): serial object to examine.

    Returns:
        MutableSequence[Hashable]: list of roots.
        
    """  
    return [item[0]]
