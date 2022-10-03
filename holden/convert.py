"""
convert: functions that convert types
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

All tools should follow one of two form. For conversion of a known type
to another type, the function name should be:
    f'{item type}_to_{output type}'
For a conversion from an unknown type to another type, the function name should
be:
    f'to_{output type}'
     
Contents:
    to_adjacency
    edges_to_adjacency
    matrix_to_adjacency
    linear_to_adjacency
    linears_to_adjacency
    tree_to_adjacency
    nodes_to_adjacency
    to_edges
    adjacency_to_edges
    to_matrix
    adjacency_to_matrix
    to_tree
    matrix_to_tree  
    
ToDo:
    Add more flexible tools.
    
"""
from __future__ import annotations
import ast
import collections
from collections.abc import Collection

import inspect
from typing import Any, Callable, Optional, Type, TYPE_CHECKING, Union

import amos

if TYPE_CHECKING:
    from . import base
    from . import form
    from . import check


def to_node(
    item: Union[Type[Any], object]) -> Union[Type[base.Node], base.Node]:
    """Converts a class or object into a Node for a composite data structure.
    
    Currently, the method supports any object but only python dataclass types 
    for classes. And those dataclasses should not have a '__post_init__' 
    method - it will be overwritten by 'nodify'.

    Args:
        item (Union[Type[Any], object]): class or instance to transform into a  
            Node.

    Returns:
        Union[Type[base.Node], base.Node]: a Node class or instance.
        
    """
    item.__hash__ = Node.__hash__ # type: ignore
    item.__eq__ = Node.__eq__ # type: ignore
    item.__ne__ = Node.__ne__ # type: ignore
    if inspect.isclass(item):
        item.__post_init__ = Node.__post_init__ # type: ignore
    else:
        if not hasattr(item, 'name') or not item.name:
            item.name = amos.namify(item = item)
    return item

# # @functools.singledispatch
# def to_adjacency(item: Any) -> form.Adjacency:
#     """Converts 'item' to an Adjacency.
    
#     Args:
#         item (Any): item to convert to an Adjacency.

#     Raises:
#         TypeError: if 'item' is a type that is not registered with the 
#         dispatcher.

#     Returns:
#         form.Adjacency: derived from 'item'.

#     """
#     if check.is_adjacency(item = item):
#         return item
#     else:
#         raise TypeError(
#             f'item cannot be converted because it is an unsupported type: '
#             f'{type(item).__name__}')

# @to_adjacency.register # type: ignore
def edges_to_adjacency(item: form.Edges) -> form.Adjacency:
    """Converts 'item' to an Adjacency.

    Args:
        item (form.Edges): item to convert to an Adjacency.

    Returns:
        form.Adjacency: derived from 'item'.

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

# @to_adjacency.register # type: ignore 
def matrix_to_adjacency(item: form.Matrix) -> form.Adjacency:
    """Converts 'item' to an Adjacency.

    Args:
        item (form.Matrix): item to convert to an Adjacency.

    Returns:
        form.Adjacency: derived from 'item'.

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

# @to_adjacency.register # type: ignore 
def linear_to_adjacency(item: form.Linear) -> form.Adjacency:
    """Converts 'item' to an Adjacency.

    Args:
        item (form.Linear): item to convert to an Adjacency.

    Returns:
        form.Adjacency: derived from 'item'.

    """
    if check.is_linears(item = item):
        return linears_to_adjacency(item = item)
    else:
        if not isinstance(item, (Collection)) or isinstance(item, str):
            item = [item]
        adjacency = collections.defaultdict(set)
        if len(item) == 1:
            adjacency.update({item: set()})
        else:
            edges = amos.windowify(item, 2)
            for edge_pair in edges:
                if edge_pair[0] in adjacency:
                    adjacency[edge_pair[0]].add(edge_pair[1])
                else:
                    adjacency[edge_pair[0]] = {edge_pair[1]}
        return adjacency

# @to_adjacency.register # type: ignore 
def linears_to_adjacency(item: form.Linear) -> form.Adjacency:
    """Converts 'item' to an Adjacency.

    Args:
        item (form.Linear): item to convert to an Adjacency.

    Returns:
        form.Adjacency: derived from 'item'.

    """
    adjacency = collections.defaultdict(set)
    for _, linear in item.items():
        pipe_adjacency = linear_to_adjacency(item = linear)
        for key, value in pipe_adjacency.items():
            if key in adjacency:
                for inner_value in value:
                    if inner_value not in adjacency:
                        adjacency[key].add(inner_value)
            else:
                adjacency[key] = value
    return adjacency

# @to_adjacency.register # type: ignore 
def tree_to_adjacency(item: form.Tree) -> form.Adjacency:
    """Converts 'item' to an Adjacency.

    Args:
        item (form.Tree): item to convert to an Adjacency.

    Returns:
        form.Adjacency: derived from 'item'.

    """
    raise NotImplementedError
             
# @to_adjacency.register # type: ignore 
def nodes_to_adjacency(item: base.Nodes) -> form.Adjacency:
    """Converts 'item' to an Adjacency.

    Args:
        item (base.Nodes): item to convert to an Adjacency.

    Returns:
        form.Adjacency: derived from 'item'.

    """
    adjacency = collections.defaultdict(set)
    return adjacency.update((k, set()) for k in item)

# @functools.singledispatch  
def to_edges(item: Any) -> form.Edges:
    """Converts 'item' to an Edges.
    
    Args:
        item (Any): item to convert to an Edges.

    Raises:
        TypeError: if 'item' is a type that is not registered.

    Returns:
        form.Edges: derived from 'item'.

    """
    if check.is_edges(item = item):
        return item
    else:
        raise TypeError(
            f'item cannot be converted because it is an unsupported type: '
            f'{type(item).__name__}')
    
# @to_edges.register # type: ignore
def adjacency_to_edges(item: form.Adjacency) -> form.Edges:
    """Converts 'item' to an Edges.
    
    Args:
        item (form.Adjacency): item to convert to an Edges.

    Returns:
        form.Edges: derived from 'item'.

    """ 
    edges = []
    for node, connections in item.items():
        for connection in connections:
            edges.append(tuple([node, connection]))
    return tuple(edges)

# @functools.singledispatch   
def to_matrix(item: Any) -> form.Matrix:
    """Converts 'item' to a Matrix.
    
    Args:
        item (Any): item to convert to a Matrix.

    Raises:
        TypeError: if 'item' is a type that is not registered.

    Returns:
        form.Matrix: derived from 'item'.

    """
    if check.is_matrix(item = item):
        return item
    else:
        raise TypeError(
            f'item cannot be converted because it is an unsupported type: '
            f'{type(item).__name__}')

# @to_matrix.register # type: ignore 
def adjacency_to_matrix(item: form.Adjacency) -> form.Matrix:
    """Converts 'item' to a Matrix.
    
    Args:
        item (form.Adjacency): item to convert to a Matrix.

    Returns:
        form.Matrix: derived from 'item'.

    """ 
    names = list(item.keys())
    matrix = []
    for i in range(len(item)): 
        matrix.append([0] * len(item))
        for j in item[i]:
            matrix[i][j] = 1
    return tuple([matrix, names])    

# @functools.singledispatch  
def to_linear(item: Any) -> form.Linear:
    """Converts 'item' to a Linear.
    
    Args:
        item (Any): item to convert to a Linear.

    Raises:
        TypeError: if 'item' is a type that is not registered.

    Returns:
        form.Linear: derived from 'item'.

    """
    if check.is_tree(item = item):
        return item
    else:
        raise TypeError(
            f'item cannot be converted because it is an unsupported type: '
            f'{type(item).__name__}')
       
# @functools.singledispatch 
def to_tree(item: Any) -> form.Tree:
    """Converts 'item' to a Tree.
    
    Args:
        item (Any): item to convert to a Tree.

    Raises:
        TypeError: if 'item' is a type that is not registered.

    Returns:
        form.Tree: derived from 'item'.

    """
    if check.is_tree(item = item):
        return item
    else:
        raise TypeError(
            f'item cannot be converted because it is an unsupported type: '
            f'{type(item).__name__}')

# @to_tree.register # type: ignore 
def matrix_to_tree(item: form.Matrix) -> form.Tree:
    """Converts 'item' to a Tree.
    
    Args:
        item (form.Matrix): item to convert to a Tree.

    Raises:
        TypeError: if 'item' is a type that is not registered.

    Returns:
        form.Tree: derived from 'item'.

    """
    tree = {}
    for node in item:
        children = item[:]
        children.remove(node)
        tree[node] = matrix_to_tree(children)
    return tree
