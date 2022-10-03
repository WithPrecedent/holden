"""
check: functions that check passed item and give a boolean result
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
    is_node: returns whether an item is a node.
    is_nodes: returns whether an item is a collection of nodes.
    is_edge: returns whether an item is an edge.
    is_composite: returns whether an item is a composite data structure.
    is_adjacency: returns whether an item is an adjacency list.
    is_matrix: returns whether an item is an adjacency matrix.
    is_edges: returns whether an item is a colleciton of edges.
    is_graph: returns whether an item is a graph.
    is_linear: returns whether an item is a linear path of nodes.
    is_linears: returns whether an item is a collection of linears.
    is_tree: returns whether an item is a tree.
    is_forest: returns whether an item is a collection of tree.

To Do:

    Add support for Kinds once that system is complete.
    
"""
from __future__ import annotations
from collections.abc import (
    Collection, Hashable, MutableMapping, MutableSequence, Sequence, Set)
import inspect
import itertools
from typing import Any, Optional, Type, Union


def is_node(item: object) -> bool:
    """Returns whether 'item' is a node.

    Args:
        item (object): instance to test.

    Returns:
        bool: whether 'item' is a node.
    
    """
    if inspect.isclass(item):
        return hasattr(item, '__hash__') and hasattr(item, 'name')
    return isinstance(item, Hashable) and hasattr(item, 'name')

def is_nodes(item: object) -> bool:
    """Returns whether 'item' is a collection of nodes.

    Args:
        item (object): instance to test.

    Returns:
        bool: whether 'item' is a collection of nodes.
    
    """
    return isinstance(item, Collection) and all(is_node(item = i) for i in item)

def is_edge(item: object) -> bool:
    """Returns whether 'item' is an edge.

    Args:
        item (object): instance to test.

    Returns:
        bool: whether 'item' is an edge.
        
    """
    return (
        isinstance(item, tuple) 
        and len(item) == 2
        and is_node(item = item[0])
        and is_node(item = item[1]))

def is_composite(item: object) -> bool:
    """Returns whether 'item' is a collection of node connections.

    Args:
        item (object): instance to test.

    Returns:
        bool: whether 'item' is a collection of node connections.
        
    """
    return (
        is_adjacency(item = item)
        or is_edges(item = item)
        or is_graph(item = item)
        or is_matrix(item = item)
        or is_tree(item = item))

def is_adjacency(item: object) -> bool:
    """Returns whether 'item' is an adjacency list.

    Args:
        item (object): instance to test.

    Returns:
        bool: whether 'item' is an adjacency list.
        
    """
    if isinstance(item, MutableMapping):
        connections = list(item.values())
        nodes = list(itertools.chain(item.values()))
        return (
            all(isinstance(e, (Set)) for e in connections)
            and all(isinstance(n, (Set, Hashable)) for n in nodes))
    else:
        return False

def is_matrix(item: object) -> bool:
    """Returns whether 'item' is an adjacency matrix.

    Args:
        item (object): instance to test.

    Returns:
        bool: whether 'item' is an adjacency matrix.
        
    """
    if isinstance(item, tuple) and len(item) == 2:
        matrix = item[0]
        labels = item[1]
        connections = list(itertools.chain(matrix))
        return (
            isinstance(matrix, MutableSequence)
            and isinstance(labels, Sequence) 
            and not isinstance(labels, str)
            and all(isinstance(i, MutableSequence) for i in matrix)
            and all(isinstance(n, Hashable) for n in labels)
            and all(isinstance(e, int) for e in connections))
    else:
        return False

def is_edges(item: object) -> bool:
    """Returns whether 'item' is an edge list.

    Args:
        item (object): instance to test.

    Returns:
        bool: whether 'item' is an edge list.
    
    """
        
    return (
        isinstance(item, Sequence) 
        and not isinstance(item, str)
        and all(is_edge(item = i) for i in item))

def is_graph(item: object) -> bool:
    """Returns whether 'item' is a graph.

    Args:
        item (object): instance to test.

    Returns:
        bool: whether 'item' is a graph.
    
    """
        
    return (
        is_adjacency(item = item) 
        or is_matrix(item = item)
        or is_edges(item = item))

def is_linear(item: object) -> bool:
    """Returns whether 'item' is a linear.

    Args:
        item (object): instance to test.

    Returns:
        bool: whether 'item' is a linear.
    
    """
    return (
        isinstance(item, Sequence)
        and not isinstance(item, str)
        and all(is_node(item = i) for i in item))

def is_linears(item: object) -> bool:
    """Returns whether 'item' is a sequence of linears.

    Args:
        item (object): instance to test.

    Returns:
        bool: whether 'item' is a sequence of linears.
    
    """
    return (
        isinstance(item, Sequence)
        and not isinstance(item, str)
        and all(is_linear(item = i) for i in item)) 

def is_tree(item: object) -> bool:
    """Returns whether 'item' is a tree.

    Args:
        item (object): instance to test.

    Returns:
        bool: whether 'item' is a tree.
    
    """
    return (
        isinstance(item, MutableSequence)
        and all(isinstance(i, (MutableSequence, Hashable)) for i in item)) 
    
def is_forest(item: object) -> bool:
    """Returns whether 'item' is a dict of tree.

    Args:
        item (object): instance to test.

    Returns:
        bool: whether 'item' is a dict of tree.
    
    """
    return (
        isinstance(item, MutableMapping)
        and all(isinstance(i, Hashable) for i in item.keys())
        and all(is_tree(item = i) for i in item.values())) 
