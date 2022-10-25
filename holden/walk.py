"""
forms: internal storage formats for graphs
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
    forms.Adjacency (amos.Dictionary, base.Graph): a graph stored as an adjacency 
        list.
    forms.Edges (sequences.Listing, base.Graph): a graph stored as an edge list.
    forms.Matrix (sequences.Listing, base.Graph): a graph stored as an adjacency 
        matrix.
    Serial
    Parallel
        is_adjacency
    is_edges
    is_matrix
    is_serial
    is_parallel
    transform
    to_adjacency
    to_edges
    to_matrix
    to_parallel
    to_serial
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
    Add the remainder of the conversion methods between different forms
    Add private methods that currently raise NotImplementedError
    Integrate Kinds system when it is finished
    
"""
from __future__ import annotations
import collections
from collections.abc import (
    Collection, Hashable, MutableMapping, MutableSequence, Sequence, Set)
import copy
import dataclasses
# import functools
import itertools
from typing import Any, ClassVar, Optional, Type, TYPE_CHECKING, Union

import amos
import miller

from . import base

if TYPE_CHECKING:
    from . import forms
   
# def transform(item: object, output: str) -> object:
#     """Will transform 'item' to another composite form.

#     Args:
#         item (object): item to convert.
#         output (str): lowercase name of form to convert 'item' to.

#     Raises:
#         TypeError: if 'output' has no corresponding converter function using the
#             format 'to_{name of form}'.
                
#     Returns:
#         object: converted 'item'.
        
#     """
#     transformer = 'to_' + output
#     try:
#         return locals()[transformer](item = item)
#     except KeyError:
#         raise TypeError(
#             f'item cannot be converted because {output} is not recognized.')
               
# @functools.singledispatch
# def to_adjacency(item: object) -> forms.Adjacency:
#     """Converts 'item' to an forms.Adjacency.
    
#     Args:
#         item (object): item to convert to an forms.Adjacency.

#     Raises:
#         TypeError: if 'item' is a type that is not registered with the 
#         dispatcher.

#     Returns:
#         forms.Adjacency: derived from 'item'.

#     """
#     if is_adjacency(item = item):
#         return item
#     else:
#         raise TypeError(
#             f'item cannot be converted because it is an unsupported type: '
#             f'{type(item).__name__}')

# @functools.singledispatch  
# def to_edges(item: object) -> forms.Edges:
#     """Converts 'item' to an forms.Edges.
    
#     Args:
#         item (object): item to convert to an forms.Edges.

#     Raises:
#         TypeError: if 'item' is a type that is not registered.

#     Returns:
#         forms.Edges: derived from 'item'.

#     """
#     if is_edges(item = item):
#         return item
#     else:
#         raise TypeError(
#             f'item cannot be converted because it is an unsupported type: '
#             f'{type(item).__name__}')

# @functools.singledispatch   
# def to_matrix(item: object) -> forms.Matrix:
#     """Converts 'item' to a forms.Matrix.
    
#     Args:
#         item (object): item to convert to a forms.Matrix.

#     Raises:
#         TypeError: if 'item' is a type that is not registered.

#     Returns:
#         forms.Matrix: derived from 'item'.

#     """
#     if is_matrix(item = item):
#         return item
#     else:
#         raise TypeError(
#             f'item cannot be converted because it is an unsupported type: '
#             f'{type(item).__name__}')

# @functools.singledispatch  
# def to_parallel(item: object) -> Parallel:
#     """Converts 'item' to a Parallel.
    
#     Args:
#         item (object): item to convert to a Parallel.

#     Raises:
#         TypeError: if 'item' is a type that is not registered.

#     Returns:
#         Parallel: derived from 'item'.

#     """
#     if is_parallel(item = item):
#         return item
#     else:
#         raise TypeError(
#             f'item cannot be converted because it is an unsupported type: '
#             f'{type(item).__name__}')

# @functools.singledispatch  
# def to_serial(item: object) -> Serial:
#     """Converts 'item' to a Serial.
    
#     Args:
#         item (object): item to convert to a Serial.

#     Raises:
#         TypeError: if 'item' is a type that is not registered.

#     Returns:
#         Serial: derived from 'item'.

#     """
#     if is_serial(item = item):
#         return item
#     else:
#         raise TypeError(
#             f'item cannot be converted because it is an unsupported type: '
#             f'{type(item).__name__}')
   
# @to_edges.register # type: ignore
def adjacency_to_edges(item: forms.Adjacency) -> forms.Edges:
    """Converts 'item' to an forms.Edges.
    
    Args:
        item (forms.Adjacency): item to convert to an forms.Edges.

    Returns:
        forms.Edges: derived from 'item'.

    """ 
    edges = []
    for node, connections in item.items():
        for connection in connections:
            edges.append(tuple([node, connection]))
    return tuple(edges)

# @to_matrix.register # type: ignore 
def adjacency_to_matrix(item: forms.Adjacency) -> forms.Matrix:
    """Converts 'item' to a forms.Matrix.
    
    Args:
        item (forms.Adjacency): item to convert to a forms.Matrix.

    Returns:
        forms.Matrix: derived from 'item'.

    """ 
    names = list(item.keys())
    matrix = []
    for i in range(len(item)): 
        matrix.append([0] * len(item))
        for j in item[i]:
            matrix[i][j] = 1
    return tuple([matrix, names])    

# @to_parallel.register # type: ignore 
def adjacency_to_parallel(item: forms.Adjacency) -> Serial:
    """Converts 'item' to a Serial.
    
    Args:
        item (forms.Adjacency): item to convert to a Serial.

    Returns:
        Serial: derived from 'item'.

    """
    roots = get_roots_adjacency(item = item)
    endpoints = get_endpoints_adjacency(item = item)
    all_paths = []
    for start in roots:
        for end in endpoints:
            paths = walk_adjacency(item = item, start = start, stop = end)
            if paths:
                if all(isinstance(path, Hashable) for path in paths):
                    all_paths.append(paths)
                else:
                    all_paths.extend(paths)
    return all_paths

# @to_serial.register # type: ignore 
def adjacency_to_serial(item: forms.Adjacency) -> Serial:
    """Converts 'item' to a Serial.
    
    Args:
        item (forms.Adjacency): item to convert to a Serial.

    Returns:
        Serial: derived from 'item'.

    """ 
    all_parallel = adjacency_to_parallel(item = item)
    if len(all_parallel) == 1:
        return all_parallel[0]
    else:
        return list(itertools.chain.from_iterable(all_parallel))

def walk_adjacency(
    item: forms.Adjacency, 
    start: Hashable, 
    stop: Hashable,
    path: Optional[Sequence[Hashable]] = None) -> Sequence[Hashable]:
    """Returns all paths in 'item' from 'start' to 'stop'.

    The code here is adapted from: https://www.python.org/doc/essays/graphs/
    
    Args:
        item (forms.Adjacency): item in which to find paths.
        start (Hashable): node to start paths from.
        stop (Hashable): node to stop paths.
        path (Optional[Sequence[Hashable]]): a path from 'start' to 'stop'. 
            Defaults to None. 

    Returns:
        Sequence[Hashable]: a list of possible paths (each path is a list nodes) 
            from 'start' to 'stop'.
        
    """            
    if path is None:
        path = []
    path = path + [start]
    if start == stop:
        return [path]
    if start not in item:
        return []
    paths = []
    for node in item[start]:
        if node not in path:
            new_paths = walk_adjacency(
                item = item,
                start = node, 
                stop = stop, 
                path = path)
            for new_path in new_paths:
                paths.append(new_path)
    return paths
    
# @to_adjacency.register # type: ignore
def edges_to_adjacency(item: forms.Edges) -> forms.Adjacency:
    """Converts 'item' to an forms.Adjacency.

    Args:
        item (forms.Edges): item to convert to an forms.Adjacency.

    Returns:
        forms.Adjacency: derived from 'item'.

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
def edges_to_matrix(item: forms.Edges) -> forms.Matrix:
    """Converts 'item' to a forms.Matrix.

    Args:
        item (forms.Edges): item to convert to a forms.Matrix.

    Returns:
        forms.Matrix: derived from 'item'.

    """
    raise NotImplementedError
 
# @to_parallel.register # type: ignore 
def edges_to_parallel(item: forms.Edges) -> Parallel:
    """Converts 'item' to a Parallel.

    Args:
        item (forms.Edges): item to convert to a Parallel.

    Returns:
        Parallel: derived from 'item'.

    """
    raise NotImplementedError
   
# @to_serial.register # type: ignore 
def edges_to_serial(item: forms.Edges) -> Serial:
    """Converts 'item' to a Serial.

    Args:
        item (forms.Edges): item to convert to a Serial.

    Returns:
        Serial: derived from 'item'.

    """
    raise NotImplementedError

# @to_adjacency.register # type: ignore 
def matrix_to_adjacency(item: forms.Matrix) -> forms.Adjacency:
    """Converts 'item' to an forms.Adjacency.

    Args:
        item (forms.Matrix): item to convert to an forms.Adjacency.

    Returns:
        forms.Adjacency: derived from 'item'.

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
def matrix_to_edges(item: forms.Matrix) -> forms.Edges:
    """Converts 'item' to an forms.Edges.

    Args:
        item (forms.Matrix): item to convert to an forms.Edges.

    Returns:
        forms.Edges: derived from 'item'.

    """
    raise NotImplementedError
 
# @to_parallel.register # type: ignore 
def matrix_to_parallel(item: forms.Matrix) -> Parallel:
    """Converts 'item' to a Parallel.

    Args:
        item (forms.Matrix): item to convert to a Parallel.

    Returns:
        Parallel: derived from 'item'.

    """
    raise NotImplementedError
   
# @to_serial.register # type: ignore 
def matrix_to_serial(item: forms.Matrix) -> Serial:
    """Converts 'item' to a Serial.

    Args:
        item (forms.Matrix): item to convert to a Serial.

    Returns:
        Serial: derived from 'item'.

    """
    raise NotImplementedError

# @to_adjacency.register # type: ignore 
def parallel_to_adjacency(item: Parallel) -> forms.Adjacency:
    """Converts 'item' to an forms.Adjacency.

    Args:
        item (Parallel): item to convert to an forms.Adjacency.

    Returns:
        forms.Adjacency: derived from 'item'.

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
def parallel_to_edges(item: Parallel) -> forms.Edges:
    """Converts 'item' to an forms.Edges.

    Args:
        item (Parallel): item to convert to an forms.Edges.

    Returns:
        forms.Edges: derived from 'item'.

    """
    raise NotImplementedError
 
# @to_matrix.register # type: ignore 
def parallel_to_matrix(item: Parallel) -> forms.Matrix:
    """Converts 'item' to a forms.Matrix.

    Args:
        item (Parallel): item to convert to a forms.Matrix.

    Returns:
        forms.Matrix: derived from 'item'.

    """
    raise NotImplementedError
   
# @to_serial.register # type: ignore 
def parallel_to_serial(item: Parallel) -> Serial:
    """Converts 'item' to a Serial.

    Args:
        item (Parallel): item to convert to a Serial.

    Returns:
        Serial: derived from 'item'.

    """
    raise NotImplementedError
    
# @to_adjacency.register # type: ignore 
def serial_to_adjacency(item: Serial) -> forms.Adjacency:
    """Converts 'item' to an forms.Adjacency.

    Args:
        item (Serial): item to convert to an forms.Adjacency.

    Returns:
        forms.Adjacency: derived from 'item'.

    """
    if is_parallel(item = item):
        return parallel_to_adjacency(item = item)
    else:
        if not isinstance(item, (Collection)) or isinstance(item, str):
            item = [item]
        adjacency = collections.defaultdict(set)
        if len(item) == 1:
            adjacency.update({item[0]: set()})
        else:
            edges = list(amos.windowify(item, 2))
            for edge_pair in edges:
                if edge_pair[0] in adjacency:
                    adjacency[edge_pair[0]].add(edge_pair[1])
                else:
                    adjacency[edge_pair[0]] = {edge_pair[1]} 
        return adjacency
    
# @to_edges.register # type: ignore 
def serial_to_edges(item: Serial) -> forms.Edges:
    """Converts 'item' to an forms.Edges.

    Args:
        item (Serial): item to convert to an forms.Edges.

    Returns:
        forms.Edges: derived from 'item'.

    """
    raise NotImplementedError
    
# @to_matrix.register # type: ignore 
def serial_to_matrix(item: Serial) -> forms.Matrix:
    """Converts 'item' to a forms.Matrix.

    Args:
        item (Serial): item to convert to a forms.Matrix.

    Returns:
        forms.Matrix: derived from 'item'.

    """
    raise NotImplementedError
 
# @to_parallel.register # type: ignore 
def serial_to_parallel(item: Serial) -> Parallel:
    """Converts 'item' to a Parallel.

    Args:
        item (Serial): item to convert to a Parallel.

    Returns:
        Parallel: derived from 'item'.

    """
    raise NotImplementedError


# # # @to_adjacency.register # type: ignore 
# def tree_to_adjacency(item: Tree) -> forms.Adjacency:
#     """Converts 'item' to an forms.Adjacency.

#     Args:
#         item (Tree): item to convert to an forms.Adjacency.

#     Returns:
#         forms.Adjacency: derived from 'item'.

#     """
#     raise NotImplementedError
             
# # # @to_adjacency.register # type: ignore 
# def nodes_to_adjacency(item: Collection[Hashable]) -> forms.Adjacency:
#     """Converts 'item' to an forms.Adjacency.

#     Args:
#         item (Collection[Hashable]): item to convert to an forms.Adjacency.

#     Returns:
#         forms.Adjacency: derived from 'item'.

#     """
#     adjacency = collections.defaultdict(set)
#     return adjacency.update((k, set()) for k in item)
                     