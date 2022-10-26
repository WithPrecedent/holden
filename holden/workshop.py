"""
workshop: functions to change the internal storage format for a graph
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
    edges_to_adjacency
    edges_to_matrix
    matrix_to_adjacency
    matrix_to_edges
           
To Do:
    Implement edges_to_matrix function.
    
"""
from __future__ import annotations
import collections
from collections.abc import (
    Collection, Hashable, MutableMapping, MutableSequence, Sequence, Set)
# import functools
import itertools
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from . import base
    from . import forms


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
    matrix = item[0]
    labels = item[1]
    edges = []
    for i in enumerate(matrix):
        for j in enumerate(matrix):
            if matrix[i][j] > 0:
                edges.append((labels[i], labels[j]))
    return edges

""" Introspection Tools """

def get_endpoints_adjacency(item: forms.Adjacency) -> MutableSequence[Hashable]:
    """Returns the endpoints in 'item'."""
    return [k for k in item.keys() if not item[k]]

def get_roots_adjacency(item: forms.Adjacency) -> MutableSequence[Hashable]:
    """Returns the roots in 'item'."""
    stops = list(itertools.chain.from_iterable(item.values()))
    return [k for k in item.keys() if k not in stops]  

""" 
These are functions design to implement a dispatch system for the form
tranformers. However, functools.singledispatch has some shortcomings. If a new
dispatch system is developed in amos or the functools decorator is improved,
these functions may be restored to allow more flexible function calls.

"""          
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
                