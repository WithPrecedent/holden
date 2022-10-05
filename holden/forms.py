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
    is_adjacency
    is_edges
    is_matrix
    is_path
    is_paths
    Adjacency (amos.Dictionary, base.Graph): a graph stored as an adjacency 
        list.
    Edges (sequences.Listing, base.Graph): a graph stored as an edge list.
    Matrix (sequences.Listing, base.Graph): a graph stored as an adjacency 
        matrix.
    Path
    Paths
    adjacency_to_edges
    adjacency_to_matrix
    adjacency_to_path
    adjacency_to_paths
    edges_to_adjacency
    matrix_to_adjacency
    path_to_adjacency
    paths_to_adjacency
          
To Do:
    Add the remainder of the conversion methods between forms.
    Integrate Kinds system when it is finished.
    
"""
from __future__ import annotations
import abc
import collections
from collections.abc import (
    Collection, Hashable, MutableMapping, MutableSequence, Sequence, Set)
import contextlib
import dataclasses
import itertools
from typing import Any, ClassVar, Optional, Type, TYPE_CHECKING, Union

import amos

from . import base
from . import check
from . import convert


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
            all(isinstance(e, (Collection)) for e in connections)
            and all(base.is_node(item = i) for i in nodes))
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
        isinstance(item, Collection) 
        and not isinstance(item, str)
        and all(base.is_edge(item = i) for i in item))
    
def is_matrix(item: object) -> bool:
    """Returns whether 'item' is an adjacency matrix.

    Args:
        item (object): instance to test.

    Returns:
        bool: whether 'item' is an adjacency matrix.
        
    """
    if isinstance(item, Sequence) and len(item) == 2:
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


@dataclasses.dataclass
class Adjacency(amos.Dictionary, base.Graph):
    """Base class for adjacency-list graphs.
    
    Args:
        contents (MutableMapping[base.Node, Set[base.Node]]): keys 
            are nodes and values are sets of nodes (or hashable representations 
            of nodes). Defaults to a defaultdict that has a set for its value 
            type.
                                      
    """  
    contents: MutableMapping[base.Node, Set[base.Node]] = (
        dataclasses.field(
            default_factory = lambda: collections.defaultdict(set)))
   
    """ Properties """

    @property
    def adjacency(self) -> Adjacency:
        """Returns the stored graph as an Adjacency."""
        return self.contents

    @property
    def edges(self) -> Edges:
        """Returns the stored graph as an Edges."""
        return convert.adjacency_to_edges(item = self.contents)
         
    @property
    def matrix(self) -> Matrix:
        """Returns the stored graph as a Matrix."""
        return convert.adjacency_to_matrix(item = self.contents)

    @property
    def path(self) -> Path:
        """Returns the stored graph as a Path."""
        return convert.adjacency_to_path(item = self.contents)

    @property
    def paths(self) -> Paths:
        """Returns the stored graph as a Path."""
        return convert.adjacency_to_paths(item = self.contents)
                 
    """ Class Methods """
    
    @classmethod
    def from_adjacency(cls, item: Adjacency) -> Adjacency:
        """Creates an Adjacency instance from an Adjacency."""
        return cls(contents = item)
    
    @classmethod
    def from_edges(cls, item: Edges) -> Adjacency:
        """Creates an Adjacency instance from an Edges."""
        return cls(contents = convert.edges_to_adjacency(item = item))
        
    @classmethod
    def from_matrix(cls, item: Matrix) -> Adjacency:
        """Creates an Adjacency instance from a Matrix."""
        return cls(contents = convert.matrix_to_adjacency(item = item))
    
    @classmethod
    def from_path(cls, item: Path) -> Adjacency:
        """Creates an Edges instance from a Path."""
        return cls(contents = convert.path_to_adjacency(item = item))
    
    @classmethod
    def from_paths(cls, item: Paths) -> Adjacency:
        """Creates an Edges instance from a Path."""
        return cls(contents = convert.paths_to_adjacency(item = item))
                           
    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        """Returns whether 'instance' meets criteria to be a subclass.

        Args:
            instance (object): item to test as an instance.

        Returns:
            bool: whether 'instance' meets criteria to be a subclass.
            
        """
        return is_adjacency(item = instance)


@dataclasses.dataclass
class Edges(amos.Listing, base.Graph):
    """Base class for edge-list graphs.

    Args:
        contents (MutableSequence[base.Edge]): list of edges. Defaults to 
            an empty list.
                                      
    """   
    contents: MutableSequence[base.Edge] = dataclasses.field(
        default_factory = list)
   
    """ Properties """

    @property
    def adjacency(self) -> Adjacency:
        """Returns the stored graph as an Adjacency."""
        return convert.edges_to_adjacency(item = self.contents)

    @property
    def edges(self) -> Edges:
        """Returns the stored graph as an Edges."""
        return self.contents
     
    @property
    def matrix(self) -> Matrix:
        """Returns the stored graph as a Matrix."""
        return convert.edges_to_matrix(item = self.contents)

    @property
    def path(self) -> Path:
        """Returns the stored graph as a Path."""
        return convert.edges_to_path(item = self.contents)

    @property
    def paths(self) -> Paths:
        """Returns the stored graph as a Paths."""
        return convert.edges_to_paths(item = self.contents)
                             
    """ Class Methods """
    
    @classmethod
    def from_adjacency(cls, item: Adjacency) -> Edges:
        """Creates an Edges instance from an Adjacency."""
        return cls(contents = convert.adjacency_to_edges(item = item))
    
    @classmethod
    def from_edges(cls, item: Edges) -> Edges:
        """Creates an Edges instance from an Edges."""
        return cls(contents = item)
           
    @classmethod
    def from_matrix(cls, item: Matrix) -> Edges:
        """Creates an Edges instance from a Matrix."""
        return cls(contents = convert.matrix_to_edges(item = item))
    
    @classmethod
    def from_path(cls, item: Path) -> Edges:
        """Creates an Edges instance from a Path."""
        return cls(contents = convert.path_to_edges(item = item))
    
    @classmethod
    def from_paths(cls, item: Paths) -> Edges:
        """Creates an Edges instance from a Paths."""
        return cls(contents = convert.paths_to_edges(item = item))
                    
    """ Dunder Methods """
           
    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        """Returns whether 'instance' meets criteria to be a subclass.

        Args:
            instance (object): item to test as an instance.

        Returns:
            bool: whether 'instance' meets criteria to be a subclass.
            
        """
        return is_edges(item = instance)

   
@dataclasses.dataclass
class Matrix(amos.Listing, base.Graph):
    """Base class for adjacency-matrix graphs.
    
    Args:
        contents (Sequence[Sequence[int]]): a list of list of integers 
            indicating edges between nodes in the matrix. Defaults to an empty
            list.
        labels (Sequence[Hashable]): names of nodes in the matrix. 
            Defaults to an empty list.
                                      
    """  
    contents: MutableSequence[MutableSequence[int]] = dataclasses.field(
        default_factory = list)
    labels: MutableSequence[Hashable] = dataclasses.field(
        default_factory = list)
   
    """ Properties """

    @property
    def adjacency(self) -> Adjacency:
        """Returns the stored graph as an Adjacency."""
        return convert.matrix_to_adjacency(item = self.contents)

    @property
    def edges(self) -> Edges:
        """Returns the stored graph as an Edges."""
        return convert.matrix_to_edges(item = self.contents)
          
    @property
    def matrix(self) -> Matrix:
        """Returns the stored graph as a Matrix."""
        return self.contents

    @property
    def path(self) -> Path:
        """Returns the stored graph as a Path."""
        return convert.matrix_to_path(item = self.contents)

    @property
    def paths(self) -> Paths:
        """Returns the stored graph as a Paths."""
        return convert.matrix_to_paths(item = self.contents)
      
    """ Class Methods """
    
    @classmethod
    def from_adjacency(cls, item: Adjacency) -> Matrix:
        """Creates a Matrix instance from an Adjacency."""
        return cls(contents = convert.adjacency_to_matrix(item = item))
    
    @classmethod
    def from_edges(cls, item: Edges) -> Matrix:
        """Creates a Matrix instance from an Edges."""
        return cls(contents = convert.edges_to_matrix(item = item))
          
    @classmethod
    def from_matrix(cls, item: Matrix) -> Matrix:
        """Creates a Matrix instance from a Matrix."""
        return cls(contents = item[0], labels = item[1])
    
    @classmethod
    def from_path(cls, item: Path) -> Matrix:
        """Creates a Graph instance from a Path."""
        return cls(contents = convert.path_to_matrix(item = item))
    
    @classmethod
    def from_paths(cls, item: Paths) -> Matrix:
        """Creates a Graph instance from a Paths."""
        return cls(contents = convert.paths_to_matrix(item = item))
                          
    """ Dunder Methods """
        
    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        """Returns whether 'instance' meets criteria to be a subclass.

        Args:
            instance (object): item to test as an instance.

        Returns:
            bool: whether 'instance' meets criteria to be a subclass.
            
        """
        return is_matrix(item = instance)
    

    
# @to_edges.register # type: ignore
def adjacency_to_edges(item: Adjacency) -> Edges:
    """Converts 'item' to an Edges.
    
    Args:
        item (Adjacency): item to convert to an Edges.

    Returns:
        Edges: derived from 'item'.

    """ 
    edges = []
    for node, connections in item.items():
        for connection in connections:
            edges.append(tuple([node, connection]))
    return tuple(edges)

# @to_matrix.register # type: ignore 
def adjacency_to_matrix(item: Adjacency) -> Matrix:
    """Converts 'item' to a Matrix.
    
    Args:
        item (Adjacency): item to convert to a Matrix.

    Returns:
        Matrix: derived from 'item'.

    """ 
    names = list(item.keys())
    matrix = []
    for i in range(len(item)): 
        matrix.append([0] * len(item))
        for j in item[i]:
            matrix[i][j] = 1
    return tuple([matrix, names])    
   
    
# # @functools.singledispatch
# def to_adjacency(item: Any) -> Adjacency:
#     """Converts 'item' to an Adjacency.
    
#     Args:
#         item (Any): item to convert to an Adjacency.

#     Raises:
#         TypeError: if 'item' is a type that is not registered with the 
#         dispatcher.

#     Returns:
#         Adjacency: derived from 'item'.

#     """
#     if check.is_adjacency(item = item):
#         return item
#     else:
#         raise TypeError(
#             f'item cannot be converted because it is an unsupported type: '
#             f'{type(item).__name__}')

# @to_adjacency.register # type: ignore
def edges_to_adjacency(item: Edges) -> Adjacency:
    """Converts 'item' to an Adjacency.

    Args:
        item (Edges): item to convert to an Adjacency.

    Returns:
        Adjacency: derived from 'item'.

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
def matrix_to_adjacency(item: Matrix) -> Adjacency:
    """Converts 'item' to an Adjacency.

    Args:
        item (Matrix): item to convert to an Adjacency.

    Returns:
        Adjacency: derived from 'item'.

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


# # @to_adjacency.register # type: ignore 
# def tree_to_adjacency(item: Tree) -> Adjacency:
#     """Converts 'item' to an Adjacency.

#     Args:
#         item (Tree): item to convert to an Adjacency.

#     Returns:
#         Adjacency: derived from 'item'.

#     """
#     raise NotImplementedError
             
# # @to_adjacency.register # type: ignore 
# def nodes_to_adjacency(item: base.Nodes) -> Adjacency:
#     """Converts 'item' to an Adjacency.

#     Args:
#         item (base.Nodes): item to convert to an Adjacency.

#     Returns:
#         Adjacency: derived from 'item'.

#     """
#     adjacency = collections.defaultdict(set)
#     return adjacency.update((k, set()) for k in item)

# # @functools.singledispatch  
# def to_edges(item: Any) -> Edges:
#     """Converts 'item' to an Edges.
    
#     Args:
#         item (Any): item to convert to an Edges.

#     Raises:
#         TypeError: if 'item' is a type that is not registered.

#     Returns:
#         Edges: derived from 'item'.

#     """
#     if check.is_edges(item = item):
#         return item
#     else:
#         raise TypeError(
#             f'item cannot be converted because it is an unsupported type: '
#             f'{type(item).__name__}')


# # @functools.singledispatch   
# def to_matrix(item: Any) -> Matrix:
#     """Converts 'item' to a Matrix.
    
#     Args:
#         item (Any): item to convert to a Matrix.

#     Raises:
#         TypeError: if 'item' is a type that is not registered.

#     Returns:
#         Matrix: derived from 'item'.

#     """
#     if check.is_matrix(item = item):
#         return item
#     else:
#         raise TypeError(
#             f'item cannot be converted because it is an unsupported type: '
#             f'{type(item).__name__}')


# # @functools.singledispatch  
# def to_path(item: Any) -> Path:
#     """Converts 'item' to a Path.
    
#     Args:
#         item (Any): item to convert to a Path.

#     Raises:
#         TypeError: if 'item' is a type that is not registered.

#     Returns:
#         Path: derived from 'item'.

#     """
#     if check.is_path(item = item):
#         return item
#     else:
#         raise TypeError(
#             f'item cannot be converted because it is an unsupported type: '
#             f'{type(item).__name__}')
                     