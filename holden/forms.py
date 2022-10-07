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
    is_serial
    is_parallel
    Adjacency (amos.Dictionary, base.Graph): a graph stored as an adjacency 
        list.
    Edges (sequences.Listing, base.Graph): a graph stored as an edge list.
    Matrix (sequences.Listing, base.Graph): a graph stored as an adjacency 
        matrix.
    Serial
    Parallel
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
    Integrate Kinds system when it is finished
    
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

def is_parallel(item: object) -> bool:
    """Returns whether 'item' is sequence of parallel.

    Args:
        item (object): instance to test.

    Returns:
        bool: whether 'item' is a sequence of parallel.
    
    """
    return (
        isinstance(item, Sequence)
        and all(base.is_serial(item = i) for i in item))

def is_serial(item: object) -> bool:
    """Returns whether 'item' is a serial.

    Args:
        item (object): instance to test.

    Returns:
        bool: whether 'item' is a serial.
    
    """
    return (
        isinstance(item, Sequence)
        and not isinstance(item, str)
        and all(base.is_node(item = i) for i in item))


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
        return adjacency_to_edges(item = self.contents)
         
    @property
    def matrix(self) -> Matrix:
        """Returns the stored graph as a Matrix."""
        return adjacency_to_matrix(item = self.contents)

    @property
    def parallel(self) -> Parallel:
        """Returns the stored graph as a Serial."""
        return adjacency_to_parallel(item = self.contents)
     
    @property
    def serial(self) -> Serial:
        """Returns the stored graph as a Serial."""
        return adjacency_to_serial(item = self.contents)
            
    """ Class Methods """
    
    @classmethod
    def from_adjacency(cls, item: Adjacency) -> Adjacency:
        """Creates an Adjacency instance from an Adjacency."""
        return cls(contents = item)
    
    @classmethod
    def from_edges(cls, item: Edges) -> Adjacency:
        """Creates an Adjacency instance from an Edges."""
        return cls(contents = edges_to_adjacency(item = item))
        
    @classmethod
    def from_matrix(cls, item: Matrix) -> Adjacency:
        """Creates an Adjacency instance from a Matrix."""
        return cls(contents = matrix_to_adjacency(item = item))
    
    @classmethod
    def from_parallel(cls, item: Parallel) -> Adjacency:
        """Creates an Edges instance from a Serial."""
        return cls(contents = parallel_to_adjacency(item = item))
      
    @classmethod
    def from_serial(cls, item: Serial) -> Adjacency:
        """Creates an Edges instance from a Serial."""
        return cls(contents = serial_to_adjacency(item = item))
                         
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
        contents (MutableSequence[base.Edge]): Listing of edges. Defaults to 
            an empty list.
                                      
    """   
    contents: MutableSequence[base.Edge] = dataclasses.field(
        default_factory = list)
   
    """ Properties """

    @property
    def adjacency(self) -> Adjacency:
        """Returns the stored graph as an Adjacency."""
        return edges_to_adjacency(item = self.contents)

    @property
    def edges(self) -> Edges:
        """Returns the stored graph as an Edges."""
        return self.contents
     
    @property
    def matrix(self) -> Matrix:
        """Returns the stored graph as a Matrix."""
        return edges_to_matrix(item = self.contents)

    @property
    def parallel(self) -> Parallel:
        """Returns the stored graph as a Parallel."""
        return edges_to_parallel(item = self.contents)
 
    @property
    def serial(self) -> Serial:
        """Returns the stored graph as a Serial."""
        return edges_to_serial(item = self.contents)
                            
    """ Class Methods """
    
    @classmethod
    def from_adjacency(cls, item: Adjacency) -> Edges:
        """Creates an Edges instance from an Adjacency."""
        return cls(contents = adjacency_to_edges(item = item))
    
    @classmethod
    def from_edges(cls, item: Edges) -> Edges:
        """Creates an Edges instance from an Edges."""
        return cls(contents = item)
           
    @classmethod
    def from_matrix(cls, item: Matrix) -> Edges:
        """Creates an Edges instance from a Matrix."""
        return cls(contents = matrix_to_edges(item = item))
    
    @classmethod
    def from_parallel(cls, item: Parallel) -> Edges:
        """Creates an Edges instance from a Parallel."""
        return cls(contents = parallel_to_edges(item = item))
    
    @classmethod
    def from_serial(cls, item: Serial) -> Edges:
        """Creates an Edges instance from a Serial."""
        return cls(contents = serial_to_edges(item = item))
                    
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
        return matrix_to_adjacency(item = self.contents)

    @property
    def edges(self) -> Edges:
        """Returns the stored graph as an Edges."""
        return matrix_to_edges(item = self.contents)
          
    @property
    def matrix(self) -> Matrix:
        """Returns the stored graph as a Matrix."""
        return self.contents

    @property
    def parallel(self) -> Parallel:
        """Returns the stored graph as a Parallel."""
        return matrix_to_parallel(item = self.contents)
 
    @property
    def serial(self) -> Serial:
        """Returns the stored graph as a Serial."""
        return matrix_to_serial(item = self.contents)
     
    """ Class Methods """
    
    @classmethod
    def from_adjacency(cls, item: Adjacency) -> Matrix:
        """Creates a Matrix instance from an Adjacency."""
        return cls(contents = adjacency_to_matrix(item = item))
    
    @classmethod
    def from_edges(cls, item: Edges) -> Matrix:
        """Creates a Matrix instance from an Edges."""
        return cls(contents = edges_to_matrix(item = item))
          
    @classmethod
    def from_matrix(cls, item: Matrix) -> Matrix:
        """Creates a Matrix instance from a Matrix."""
        return cls(contents = item[0], labels = item[1])
    
    @classmethod
    def from_parallel(cls, item: Parallel) -> Matrix:
        """Creates a Graph instance from a Parallel."""
        return cls(contents = parallel_to_matrix(item = item))
     
    @classmethod
    def from_serial(cls, item: Serial) -> Matrix:
        """Creates a Graph instance from a Serial."""
        return cls(contents = serial_to_matrix(item = item))
                         
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
    
   
@dataclasses.dataclass
class Parallel(amos.Listing, base.Graph):
    """Base class for a list of serial graphs.
    
    Args:
        contents (MutableSequence[Serial]): Listing of Serial instances. 
            Defaults to an empty list.
                                      
    """   
    contents: MutableSequence[Serial] = dataclasses.field(
        default_factory = list)
                                
    """ Properties """

    @property
    def adjacency(self) -> Adjacency:
        """Returns the stored graph as an Adjacency."""
        return parallel_to_adjacency(item = self.contents)

    @property
    def edges(self) -> Edges:
        """Returns the stored graph as an Edges."""
        return parallel_to_edges(item = self.contents)
          
    @property
    def matrix(self) -> Matrix:
        """Returns the stored graph as a Matrix."""
        return parallel_to_matrix(item = self.contents)

    @property
    def parallel(self) -> Parallel:
        """Returns the stored graph as a Parallel."""
        return self.contents

    @property
    def serial(self) -> Serial:
        """Returns the stored graph as a Serial."""
        return parallel_to_serial(item = self.contents)
    
    """ Class Methods """
    
    @classmethod
    def from_adjacency(cls, item: Adjacency) -> Parallel:
        """Creates a Parallel instance from an Adjacency."""
        return cls(contents = adjacency_to_parallel(item = item))
    
    @classmethod
    def from_edges(cls, item: Edges) -> Serial:
        """Creates a Parallel instance from an Edges."""
        return cls(contents = edges_to_parallel(item = item))
        
    @classmethod
    def from_matrix(cls, item: Matrix) -> Serial:
        """Creates a Parallel instance from a Matrix."""
        return cls(contents = matrix_to_parallel(item = item))
    
    @classmethod
    def from_parallel(cls, item: Parallel) -> Serial:
        """Creates a Parallel instance from a Parallel."""
        return cls(contents = item)
     
    @classmethod
    def from_serial(cls, item: Serial) -> Serial:
        """Creates a Parallel instance from a Serial."""
        return cls(contents = item)
                    
    """ Dunder Methods """
        
    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        """Returns whether 'instance' meets criteria to be a subclass.

        Args:
            instance (object): item to test as an instance.

        Returns:
            bool: whether 'instance' meets criteria to be a subclass.
            
        """
        return is_parallel(item = instance)
     
    
@dataclasses.dataclass
class Serial(amos.Hybrid, base.Graph):
    """Base class for serial graphs.
    
    Args:
        contents (MutableSequence[base.Node]): list of nodes. Defaults to 
            an empty list.
                                      
    """   
    contents: MutableSequence[base.Node] = dataclasses.field(
        default_factory = list)
                                
    """ Properties """

    @property
    def adjacency(self) -> Adjacency:
        """Returns the stored graph as an Adjacency."""
        return serial_to_adjacency(item = self.contents)

    @property
    def edges(self) -> Edges:
        """Returns the stored graph as an Edges."""
        return serial_to_edges(item = self.contents)
          
    @property
    def matrix(self) -> Matrix:
        """Returns the stored graph as a Matrix."""
        return serial_to_matrix(item = self.contents)

    @property
    def parallel(self) -> Parallel:
        """Returns the stored graph as a Parallel."""
        return serial_to_parallel(item = self.contents)

    @property
    def serial(self) -> Serial:
        """Returns the stored graph as a Serial."""
        return self.contents
    
    """ Class Methods """
    
    @classmethod
    def from_adjacency(cls, item: Adjacency) -> Serial:
        """Creates a Serial instance from an Adjacency."""
        return cls(contents = adjacency_to_serial(item = item))
    
    @classmethod
    def from_edges(cls, item: Edges) -> Serial:
        """Creates a Serial instance from an Edges."""
        return cls(contents = edges_to_serial(item = item))
        
    @classmethod
    def from_matrix(cls, item: Matrix) -> Serial:
        """Creates a Serial instance from a Matrix."""
        return cls(contents = matrix_to_serial(item = item))
    
    @classmethod
    def from_parallel(cls, item: Parallel) -> Serial:
        """Creates a Serial instance from a Serial."""
        return cls(contents = parallel_to_serial(item = item))
     
    @classmethod
    def from_serial(cls, item: Serial) -> Serial:
        """Creates a Serial instance from a Serial."""
        return cls(contents = item)
                    
    """ Dunder Methods """
        
    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        """Returns whether 'instance' meets criteria to be a subclass.

        Args:
            instance (object): item to test as an instance.

        Returns:
            bool: whether 'instance' meets criteria to be a subclass.
            
        """
        return is_serial(item = instance)

    
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

# @to_serial.register # type: ignore 
def adjacency_to_serial(item: Adjacency) -> Serial:
    """Converts 'item' to a Serial.
    
    Args:
        item (Adjacency): item to convert to a Serial.

    Returns:
        Serial: derived from 'item'.

    """ 
    all_parallel = adjacency_to_parallel(item = item)
    if len(all_parallel) == 1:
        return all_parallel[0]
    else:
        return itertools.chain(all_parallel)  

# @to_parallel.register # type: ignore 
def adjacency_to_parallel(item: Adjacency) -> Serial:
    """Converts 'item' to a Serial.
    
    Args:
        item (Adjacency): item to convert to a Serial.

    Returns:
        Serial: derived from 'item'.

    """ 
    pass

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
    
# @to_matrix.register # type: ignore 
def edges_to_matrix(item: Edges) -> Matrix:
    """Converts 'item' to a Matrix.

    Args:
        item (Edges): item to convert to a Matrix.

    Returns:
        Matrix: derived from 'item'.

    """
    raise NotImplementedError
 
# @to_parallel.register # type: ignore 
def edges_to_parallel(item: Edges) -> Parallel:
    """Converts 'item' to a Parallel.

    Args:
        item (Edges): item to convert to a Parallel.

    Returns:
        Parallel: derived from 'item'.

    """
    raise NotImplementedError
   
# @to_serial.register # type: ignore 
def edges_to_serial(item: Edges) -> Serial:
    """Converts 'item' to a Serial.

    Args:
        item (Edges): item to convert to a Serial.

    Returns:
        Serial: derived from 'item'.

    """
    raise NotImplementedError

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
    
# @to_edges.register # type: ignore 
def matrix_to_edges(item: Matrix) -> Edges:
    """Converts 'item' to an Edges.

    Args:
        item (Matrix): item to convert to an Edges.

    Returns:
        Edges: derived from 'item'.

    """
    raise NotImplementedError
 
# @to_parallel.register # type: ignore 
def matrix_to_parallel(item: Matrix) -> Parallel:
    """Converts 'item' to a Parallel.

    Args:
        item (Matrix): item to convert to a Parallel.

    Returns:
        Parallel: derived from 'item'.

    """
    raise NotImplementedError
   
# @to_serial.register # type: ignore 
def matrix_to_serial(item: Matrix) -> Serial:
    """Converts 'item' to a Serial.

    Args:
        item (Matrix): item to convert to a Serial.

    Returns:
        Serial: derived from 'item'.

    """
    raise NotImplementedError

# @to_adjacency.register # type: ignore 
def parallel_to_adjacency(item: Parallel) -> Adjacency:
    """Converts 'item' to an Adjacency.

    Args:
        item (Parallel): item to convert to an Adjacency.

    Returns:
        Adjacency: derived from 'item'.

    """
    adjacency = collections.defaultdict(set)
    for _, serial in item.items():
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
def parallel_to_edges(item: Parallel) -> Edges:
    """Converts 'item' to an Edges.

    Args:
        item (Parallel): item to convert to an Edges.

    Returns:
        Edges: derived from 'item'.

    """
    raise NotImplementedError
 
# @to_matrix.register # type: ignore 
def parallel_to_matrix(item: Parallel) -> Matrix:
    """Converts 'item' to a Matrix.

    Args:
        item (Parallel): item to convert to a Matrix.

    Returns:
        Matrix: derived from 'item'.

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
def serial_to_adjacency(item: Serial) -> Adjacency:
    """Converts 'item' to an Adjacency.

    Args:
        item (Serial): item to convert to an Adjacency.

    Returns:
        Adjacency: derived from 'item'.

    """
    if is_parallel(item = item):
        return parallel_to_adjacency(item = item)
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
    
# @to_edges.register # type: ignore 
def serial_to_edges(item: Serial) -> Edges:
    """Converts 'item' to an Edges.

    Args:
        item (Serial): item to convert to an Edges.

    Returns:
        Edges: derived from 'item'.

    """
    raise NotImplementedError
    
# @to_matrix.register # type: ignore 
def serial_to_matrix(item: Serial) -> Matrix:
    """Converts 'item' to a Matrix.

    Args:
        item (Serial): item to convert to a Matrix.

    Returns:
        Matrix: derived from 'item'.

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
# def to_serial(item: Any) -> Serial:
#     """Converts 'item' to a Serial.
    
#     Args:
#         item (Any): item to convert to a Serial.

#     Raises:
#         TypeError: if 'item' is a type that is not registered.

#     Returns:
#         Serial: derived from 'item'.

#     """
#     if check.is_serial(item = item):
#         return item
#     else:
#         raise TypeError(
#             f'item cannot be converted because it is an unsupported type: '
#             f'{type(item).__name__}')
                     