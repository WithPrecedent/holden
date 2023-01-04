"""
graphs: graphs with different internal storage formats
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
    Adjacency (base.Graph, camina.Dictionary): a graph stored as an adjacency 
        list.
    Edges (base.Graph, camina.Listing): a graph stored as an edge list.
    Matrix (base.Graph, camina.Listing): a graph stored as an adjacency matrix.
         
To Do:
    Add the remainder of the conversion methods between different forms
    Add private methods that currently raise NotImplementedError
    Integrate Kinds system when it is finished
    
"""
from __future__ import annotations
import collections
from collections.abc import (
    Hashable, MutableMapping, MutableSequence, Sequence, Set)
import copy
import dataclasses
from typing import Any, ClassVar, Optional, Type, TYPE_CHECKING, Union

import camina

from . import base
from . import check


""" Graph Form Base Classes """

@dataclasses.dataclass
class Adjacency(base.Graph, camina.Dictionary):
    """Base class for adjacency-list graphs.
    
    Args:
        contents (MutableMapping[Hashable, set[Hashable]]): keys are hashable 
            representations of nodes. Values are the nodes to which the key node
            are connected. In a directed graph, the key node is assumed to come
            before the value node in order. Defaults to a defaultdict that has a 
            set for its value type.
                                      
    """  
    contents: MutableMapping[Hashable, set[Hashable]] = dataclasses.field(
            default_factory = lambda: collections.defaultdict(set))

    """ Public Methods """   
    
    def _add(self, item: Hashable, *args: Any, **kwargs: Any) -> None:
        """Adds node to the stored graph.
                   
        Args:
            item (Hashable): node to add to the stored graph.
            
        """
        self.contents[item] = set()
        return
        
    def _connect(self, item: base.Edge, *args: Any, **kwargs: Any) -> None:
        """Adds edge to the stored graph.
        
        Args:
            item (Edge): edge to add to the stored graph.
            
        """
        self.contents[item[0]].add(item[1])
        return
      
    def _delete(self, item: Hashable, *args: Any, **kwargs: Any) -> None:
        """Deletes node from the stored graph.
          
        Args:
            item (Hashable): node to delete from 'contents'.
        
            
        """
        del self.contents[item]
        self.contents = {k: v.remove(item) for k, v in self.contents.items()}
        return
  
    def _disconnect(self, item: base.Edge, *args: Any, **kwargs: Any) -> None:
        """Removes edge from the stored graph.
        
        Args:
            item (Edge): edge to delete from the stored graph.
            
        """
        self.contents[item[0]].remove(item[1])  
        return

    def _merge(self, item: base.Graph, *args: Any, **kwargs: Any) -> None:
        """Combines 'item' with the stored graph.
        
        Args:
            item (Graph): another Graph object to add to the stored graph.
                
        """
        other = base.transform(
            item = item, 
            output = 'adjacency', 
            raise_same_error = False)
        for node, edges in other.items():
            if node in self:
                self[node].update(edges)
            else:
                self[node] = edges
        return
    
    def _subset(
        self, 
        include: Union[Hashable, Sequence[Hashable]] = None,
        exclude: Union[Hashable, Sequence[Hashable]] = None) -> Adjacency:
        """Returns a new graph without a subset of 'contents'.

        Args:
            include (Union[Hashable, Sequence[Hashable]]): nodes or edges which 
                should be included in the new graph.
            exclude (Union[Hashable, Sequence[Hashable]]): nodes or edges which 
                should not be included in the new graph.

        Returns:
           Adjacency: with only selected nodes and edges.
            
        """
        if include:
            excludables = [k for k in self.contents if k not in include]
        else:
            excludables = []
        excludables.extend([i for i in self.contents if i in exclude])
        new_graph = copy.deepcopy(self)
        for node in camina.iterify(excludables):
            new_graph.delete(node = node)
        return new_graph  
          
    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        """Returns whether 'instance' meets criteria to be a subclass.

        Args:
            instance (object): item to test as an instance.

        Returns:
            bool: whether 'instance' meets criteria to be a subclass.
            
        """
        return check.is_adjacency(item = instance)


@dataclasses.dataclass
class Edges(base.Graph, camina.Listing):
    """Base class for edge-list graphs.

    Args:
        contents (MutableSequence[base.Edge]): Listing of edges. Defaults to 
            an empty list.
                                      
    """   
    contents: MutableSequence[base.Edge] = dataclasses.field(
        default_factory = list)

    """ Private Methods """   
    
    def _add(self, item: base.Edge, *args: Any, **kwargs: Any) -> None:
        """Adds edge to the stored graph.
                   
        Args:
            item (base.Edge): edge to add to the stored graph.
            
        """
        self.contents.append(item)
        return
            
    def _connect(self, item: base.Edge, *args: Any, **kwargs: Any) -> None:
        """Adds edge to the stored graph.
        
        Args:
            item (Edge): edge to add to the stored graph.
            
        """
        self.contents.append(item)
        return

    def _delete(self, item: base.Edge, *args: Any, **kwargs: Any) -> None:
        """Removes edge from the stored graph.
        
        Args:
            item (Edge): edge to delete from the stored graph.
            
        """
        self.contents.remove(item) 
        return    
            
    def _disconnect(self, item: base.Edge, *args: Any, **kwargs: Any) -> None:
        """Removes edge from the stored graph.
        
        Args:
            item (Edge): edge to delete from the stored graph.
            
        """
        self.contents.remove(item) 
        return    

    def _merge(self, item: base.Graph, *args: Any, **kwargs: Any) -> None:
        """Combines 'item' with the stored graph.
        
        Args:
            item (Graph): another Graph object to add to the stored graph.
                
        """
        other = base.transform(
            item = item, 
            output = 'edges', 
            raise_same_error = False)
        self.contents.extend(other)
        return
    
    def _subset(
        self, 
        include: Union[Hashable, Sequence[Hashable]] = None,
        exclude: Union[Hashable, Sequence[Hashable]] = None) -> Adjacency:
        """Returns a new graph without a subset of 'contents'.

        Args:
            include (Union[Hashable, Sequence[Hashable]]): nodes or edges which 
                should be included in the new graph.
            exclude (Union[Hashable, Sequence[Hashable]]): nodes or edges which 
                should not be included in the new graph.

        Returns:
           Adjacency: with only selected nodes and edges.
            
        """
        raise NotImplementedError 
                              
    """ Dunder Methods """
           
    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        """Returns whether 'instance' meets criteria to be a subclass.

        Args:
            instance (object): item to test as an instance.

        Returns:
            bool: whether 'instance' meets criteria to be a subclass.
            
        """
        return check.is_edges(item = instance)

   
@dataclasses.dataclass
class Matrix(base.Graph, camina.Listing):
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

    """ Private Methods """   
    
    def _add(self, item: base.Edge, *args: Any, **kwargs: Any) -> None:
        """Adds edge to the stored graph.
                   
        Args:
            item (base.Edge): edge to add to the stored graph.
            
        """
        raise NotImplementedError
            
    def _connect(self, item: base.Edge, *args: Any, **kwargs: Any) -> None:
        """Adds edge to the stored graph.
        
        Args:
            item (Edge): edge to add to the stored graph.
            
        """
        raise NotImplementedError

    def _delete(self, item: base.Edge, *args: Any, **kwargs: Any) -> None:
        """Removes edge from the stored graph.
        
        Args:
            item (Edge): edge to delete from the stored graph.
            
        """
        raise NotImplementedError   
            
    def _disconnect(self, item: base.Edge, *args: Any, **kwargs: Any) -> None:
        """Removes edge from the stored graph.
        
        Args:
            item (Edge): edge to delete from the stored graph.
            
        """
        raise NotImplementedError   

    def _merge(self, item: base.Graph, *args: Any, **kwargs: Any) -> None:
        """Combines 'item' with the stored graph.
        
        Args:
            item (Graph): another Graph object to add to the stored graph.
                
        """
        other = base.transform(
            item = item, 
            output = 'matrix', 
            raise_same_error = False)
        new_matrix = other[0]
        length = len(self.contents)
        for row in enumerate(new_matrix):
            for column in enumerate(row):
                self.contents[row + length][column + length] = (
                    new_matrix[row][column])
        self.labels.extend(other[1])
        return
    
    def _subset(
        self, 
        include: Union[Hashable, Sequence[Hashable]] = None,
        exclude: Union[Hashable, Sequence[Hashable]] = None) -> Adjacency:
        """Returns a new graph without a subset of 'contents'.

        Args:
            include (Union[Hashable, Sequence[Hashable]]): nodes or edges which 
                should be included in the new graph.
            exclude (Union[Hashable, Sequence[Hashable]]): nodes or edges which 
                should not be included in the new graph.

        Returns:
           Adjacency: with only selected nodes and edges.
            
        """
        raise NotImplementedError 
                             
    """ Dunder Methods """
        
    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        """Returns whether 'instance' meets criteria to be a subclass.

        Args:
            instance (object): item to test as an instance.

        Returns:
            bool: whether 'instance' meets criteria to be a subclass.
            
        """
        return check.is_matrix(item = instance)
