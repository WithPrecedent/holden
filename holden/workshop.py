"""
workshop: functions to change the internal storage format for a data structure
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
    add_transformer
    adjacency_to_edges
    adjacency_to_matrix
    adjacency_to_serial
    adjacency_to_parallel
    edges_to_adjacency
    edges_to_matrix
    edges_to_serial
    edges_to_parallel
    matrix_to_adjacency
    matrix_to_edges
    matrix_to_serial
    matrix_to_parallel
    serial_to_adjacency
    serial_to_edges
    serial_to_matrix
    serial_to_parallel
    parallel_to_adjacency
    parallel_to_edges
    parallel_to_matrix
    parallel_to_serial
           
To Do:
    Implement remaining functions.
    
"""
from __future__ import annotations
import collections
from collections.abc import (
    Collection, Hashable, MutableMapping, MutableSequence, Sequence, Set)
# import functools
import itertools
from typing import Callable, TYPE_CHECKING

import camina

from . import check
from . import traverse

if TYPE_CHECKING:
    from . import base
    from . import composites
    from . import graphs


""" Transformers """

def add_transformer(name: str, item: Callable[[base.Graph]]) -> None:
    """Adds a transformer to the local namespace.
    
    This allows the function to be found by the 'transform' function.

    Args:
        name (str): name of the transformer function. It needs to be in the 
            '{input form}_to_{output form}' format.
        item (Callable[[base.Graph]]): callable transformer which should have a
            single parameter, item which should be a base.Graph type.
        
    """
    globals()[name] = item
    return

# @to_edges.register # type: ignore
def adjacency_to_edges(item: graphs.Adjacency) -> graphs.Edges:
    """Converts 'item' to an graphs.Edges.
    
    Args:
        item (graphs.Adjacency): item to convert to an graphs.Edges.

    Returns:
        graphs.Edges: derived from 'item'.

    """ 
    edges = []
    for node, connections in item.items():
        for connection in connections:
            edges.append(tuple([node, connection]))
    return tuple(edges)

# @to_matrix.register # type: ignore 
def adjacency_to_matrix(item: graphs.Adjacency) -> graphs.Matrix:
    """Converts 'item' to a graphs.Matrix.
    
    Args:
        item (graphs.Adjacency): item to convert to a graphs.Matrix.

    Returns:
        graphs.Matrix: derived from 'item'.

    """ 
    names = list(item.keys())
    matrix = []
    for i in range(len(item)): 
        matrix.append([0] * len(item))
        for j in item[i]:
            matrix[i][j] = 1
    return tuple([matrix, names])    

# @to_parallel.register # type: ignore 
def adjacency_to_parallel(item: graphs.Adjacency) -> composites.Parallel:
    """Converts 'item' to a Serial.
    
    Args:
        item (graphs.Adjacency): item to convert to a Serial.

    Returns:
        Serial: derived from 'item'.

    """
    roots = get_roots_adjacency(item = item)
    endpoints = get_endpoints_adjacency(item = item)
    all_paths = []
    for start in roots:
        for end in endpoints:
            paths = traverse.walk_adjacency(
                item = item, 
                start = start, 
                stop = end)
            if paths:
                if all(isinstance(path, Hashable) for path in paths):
                    all_paths.append(paths)
                else:
                    all_paths.extend(paths)
    return all_paths

# @to_serial.register # type: ignore 
def adjacency_to_serial(item: graphs.Adjacency) -> composites.Serial:
    """Converts 'item' to a Serial.
    
    Args:
        item (graphs.Adjacency): item to convert to a Serial.

    Returns:
        Serial: derived from 'item'.

    """ 
    all_parallel = adjacency_to_parallel(item = item)
    if len(all_parallel) == 1:
        return all_parallel[0]
    else:
        return list(itertools.chain.from_iterable(all_parallel))
       
# @to_adjacency.register # type: ignore
def edges_to_adjacency(item: graphs.Edges) -> graphs.Adjacency:
    """Converts 'item' to an graphs.Adjacency.

    Args:
        item (graphs.Edges): item to convert to an graphs.Adjacency.

    Returns:
        graphs.Adjacency: derived from 'item'.

    """
    adjacency = collections.defaultdict(set)
    for edge_pair in item:
        if edge_pair[0] not in adjacency:
            adjacency[edge_pair[0]] = {edge_pair[1]}
        else:
            adjacency[edge_pair[0]].add(edge_pair[1])
        if edge_pair[1] not in adjacency:
            adjacency[edge_pair[1]] = set()
    return adjacency

# @to_matrix.register # type: ignore 
def edges_to_matrix(item: graphs.Edges) -> graphs.Matrix:
    """Converts 'item' to a graphs.Matrix.

    Args:
        item (graphs.Edges): item to convert to a graphs.Matrix.

    Returns:
        graphs.Matrix: derived from 'item'.

    """
    raise NotImplementedError
 
# @to_parallel.register # type: ignore 
def edges_to_parallel(item: graphs.Edges) -> composites.Parallel:
    """Converts 'item' to a Parallel.

    Args:
        item (graphs.Edges): item to convert to a Parallel.

    Returns:
        Parallel: derived from 'item'.

    """
    raise NotImplementedError
   
# @to_serial.register # type: ignore 
def edges_to_serial(item: graphs.Edges) -> composites.Serial:
    """Converts 'item' to a Serial.

    Args:
        item (graphs.Edges): item to convert to a Serial.

    Returns:
        Serial: derived from 'item'.

    """
    raise NotImplementedError

# @to_adjacency.register # type: ignore 
def matrix_to_adjacency(item: graphs.Matrix) -> graphs.Adjacency:
    """Converts 'item' to an graphs.Adjacency.

    Args:
        item (graphs.Matrix): item to convert to an graphs.Adjacency.

    Returns:
        graphs.Adjacency: derived from 'item'.

    """  
    matrix = item[0]
    names = item[1]
    name_mapping = dict(zip(range(len(matrix)), names))
    raw_adjacency = {
        i: [j for j, adjacent in enumerate(row) if adjacent] 
        for i, row in enumerate(matrix)}
    adjacency = collections.defaultdict(set)
    for key, value in raw_adjacency.items():
        new_key = name_mapping[key]
        new_values = set()
        for edge in value:
            new_values.add(name_mapping[edge])
        adjacency[new_key] = new_values
    return adjacency
    
# @to_edges.register # type: ignore 
def matrix_to_edges(item: graphs.Matrix) -> graphs.Edges:
    """Converts 'item' to an graphs.Edges.

    Args:
        item (graphs.Matrix): item to convert to an graphs.Edges.

    Returns:
        graphs.Edges: derived from 'item'.

    """
    matrix = item[0]
    labels = item[1]
    edges = []
    for i in enumerate(matrix):
        for j in enumerate(matrix):
            if matrix[i][j] > 0:
                edges.append((labels[i], labels[j]))
    return edges
 
# @to_parallel.register # type: ignore 
def matrix_to_parallel(item: graphs.Matrix) -> composites.Parallel:
    """Converts 'item' to a Parallel.

    Args:
        item (graphs.Matrix): item to convert to a Parallel.

    Returns:
        Parallel: derived from 'item'.

    """
    raise NotImplementedError
   
# @to_serial.register # type: ignore 
def matrix_to_serial(item: graphs.Matrix) -> composites.Serial:
    """Converts 'item' to a Serial.

    Args:
        item (graphs.Matrix): item to convert to a Serial.

    Returns:
        Serial: derived from 'item'.

    """
    raise NotImplementedError

# @to_adjacency.register # type: ignore 
def parallel_to_adjacency(item: composites.Parallel) -> graphs.Adjacency:
    """Converts 'item' to an graphs.Adjacency.

    Args:
        item (Parallel): item to convert to an graphs.Adjacency.

    Returns:
        graphs.Adjacency: derived from 'item'.

    """
    adjacency = collections.defaultdict(set)
    for serial in item:
        pipe_adjacency = serial_to_adjacency(item = serial)
        for key, value in pipe_adjacency.items():
            if key in adjacency:
                for inner_value in value:
                    if inner_value not in adjacency:
                        adjacency[key].add(inner_value)
            else:
                adjacency[key] = value
    return adjacency  
    
# @to_edges.register # type: ignore 
def parallel_to_edges(item: composites.Parallel) -> graphs.Edges:
    """Converts 'item' to an graphs.Edges.

    Args:
        item (Parallel): item to convert to an graphs.Edges.

    Returns:
        graphs.Edges: derived from 'item'.

    """
    raise NotImplementedError
 
# @to_matrix.register # type: ignore 
def parallel_to_matrix(item: composites.Parallel) -> graphs.Matrix:
    """Converts 'item' to a graphs.Matrix.

    Args:
        item (Parallel): item to convert to a graphs.Matrix.

    Returns:
        graphs.Matrix: derived from 'item'.

    """
    raise NotImplementedError
   
# @to_serial.register # type: ignore 
def parallel_to_serial(item: composites.Parallel) -> composites.Serial:
    """Converts 'item' to a Serial.

    Args:
        item (Parallel): item to convert to a Serial.

    Returns:
        Serial: derived from 'item'.

    """
    raise NotImplementedError
    
# @to_adjacency.register # type: ignore 
def serial_to_adjacency(item: composites.Serial) -> graphs.Adjacency:
    """Converts 'item' to an graphs.Adjacency.

    Args:
        item (Serial): item to convert to an graphs.Adjacency.

    Returns:
        graphs.Adjacency: derived from 'item'.

    """
    if check.is_parallel(item = item):
        return parallel_to_adjacency(item = item)
    else:
        if not isinstance(item, (Collection)) or isinstance(item, str):
            item = [item]
        adjacency = collections.defaultdict(set)
        if len(item) == 1:
            adjacency.update({item[0]: set()})
        else:
            edges = list(camina.windowify(item, 2))
            for edge_pair in edges:
                if edge_pair[0] in adjacency:
                    adjacency[edge_pair[0]].add(edge_pair[1])
                else:
                    adjacency[edge_pair[0]] = {edge_pair[1]} 
        return adjacency
    
# @to_edges.register # type: ignore 
def serial_to_edges(item: composites.Serial) -> graphs.Edges:
    """Converts 'item' to an graphs.Edges.

    Args:
        item (Serial): item to convert to an graphs.Edges.

    Returns:
        graphs.Edges: derived from 'item'.

    """
    raise NotImplementedError
    
# @to_matrix.register # type: ignore 
def serial_to_matrix(item: composites.Serial) -> graphs.Matrix:
    """Converts 'item' to a graphs.Matrix.

    Args:
        item (Serial): item to convert to a graphs.Matrix.

    Returns:
        graphs.Matrix: derived from 'item'.

    """
    raise NotImplementedError
 
# @to_parallel.register # type: ignore 
def serial_to_parallel(item: composites.Serial) -> composites.Parallel:
    """Converts 'item' to a Parallel.

    Args:
        item (Serial): item to convert to a Parallel.

    Returns:
        Parallel: derived from 'item'.

    """
    raise NotImplementedError

    
""" Introspection Tools """

def get_endpoints_adjacency(item: graphs.Adjacency) -> MutableSequence[Hashable]:
    """Returns the endpoints in 'item'."""
    return [k for k in item.keys() if not item[k]]

def get_roots_adjacency(item: graphs.Adjacency) -> MutableSequence[Hashable]:
    """Returns the roots in 'item'."""
    stops = list(itertools.chain.from_iterable(item.values()))
    return [k for k in item.keys() if k not in stops]  

""" 
These are functions design to implement a dispatch system for the form
tranformers. However, functools.singledispatch has some shortcomings. If a new
dispatch system is developed in camina or the functools decorator is improved,
these functions may be restored to allow more flexible function calls.

"""          
# @functools.singledispatch
# def to_adjacency(item: object) -> graphs.Adjacency:
#     """Converts 'item' to an graphs.Adjacency.
    
#     Args:
#         item (object): item to convert to an graphs.Adjacency.

#     Raises:
#         TypeError: if 'item' is a type that is not registered with the 
#         dispatcher.

#     Returns:
#         graphs.Adjacency: derived from 'item'.

#     """
#     if is_adjacency(item = item):
#         return item
#     else:
#         raise TypeError(
#             f'item cannot be converted because it is an unsupported type: '
#             f'{type(item).__name__}')

# @functools.singledispatch  
# def to_edges(item: object) -> graphs.Edges:
#     """Converts 'item' to an graphs.Edges.
    
#     Args:
#         item (object): item to convert to an graphs.Edges.

#     Raises:
#         TypeError: if 'item' is a type that is not registered.

#     Returns:
#         graphs.Edges: derived from 'item'.

#     """
#     if is_edges(item = item):
#         return item
#     else:
#         raise TypeError(
#             f'item cannot be converted because it is an unsupported type: '
#             f'{type(item).__name__}')

# @functools.singledispatch   
# def to_matrix(item: object) -> graphs.Matrix:
#     """Converts 'item' to a graphs.Matrix.
    
#     Args:
#         item (object): item to convert to a graphs.Matrix.

#     Raises:
#         TypeError: if 'item' is a type that is not registered.

#     Returns:
#         graphs.Matrix: derived from 'item'.

#     """
#     if is_matrix(item = item):
#         return item
#     else:
#         raise TypeError(
#             f'item cannot be converted because it is an unsupported type: '
#             f'{type(item).__name__}')
                