"""
form: internal storage formats for graphs
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
    Adjacency (mapping.Dictionary, base.Graph): a graph stored as an adjacency 
        list.
    Edges (sequences.Listing, base.Graph): a graph stored as an edge list.
    Matrix (sequences.Listing, base.Graph): a graph stored as an adjacency 
        matrix.
          
To Do:
    Integrate Kinds system when it is finished.
    
"""
from __future__ import annotations
import abc
import collections
from collections.abc import (
    Collection, Hashable, MutableMapping, MutableSequence, Sequence, Set)
import contextlib
import dataclasses
from typing import Any, ClassVar, Optional, Type, TYPE_CHECKING, Union

from . import base
from . import mapping
from . import sequence
from . import check
from . import convert


@dataclasses.dataclass
class Adjacency(mapping.Dictionary, base.Graph):
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
    def linear(self) -> Linear:
        """Returns the stored graph as a Linear."""
        return convert.adjacency_to_linear(item = self.contents)
              
    @property
    def matrix(self) -> Matrix:
        """Returns the stored graph as a Matrix."""
        return convert.adjacency_to_matrix(item = self.contents)
           
    @property
    def tree(self) -> Tree:
        """Returns the stored graph as a Tree."""
        return convert.adjacency_to_tree(item = self.contents)
            
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
    def from_linear(cls, item: Linear) -> Adjacency:
        """Creates an Edges instance from a Linear."""
        return cls(contents = convert.linear_to_adjacency(item = item))
            
    @classmethod
    def from_matrix(cls, item: Matrix) -> Adjacency:
        """Creates an Adjacency instance from a Matrix."""
        return cls(contents = convert.matrix_to_adjacency(item = item))
             
    @classmethod
    def from_tree(cls, item: Tree) -> Adjacency:
        """Creates an Adjacency instance from a Tree."""
        return cls(contents = convert.tree_to_adjacency(item = item))
                   
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
class Edges(sequence.Listing, base.Graph):
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
    def linear(self) -> Linear:
        """Returns the stored graph as a Linear."""
        return convert.edges_to_linear(item = self.contents)
           
    @property
    def matrix(self) -> Matrix:
        """Returns the stored graph as a Matrix."""
        return convert.edges_to_matrix(item = self.contents)
           
    @property
    def tree(self) -> Tree:
        """Returns the stored graph as a Tree."""
        return convert.edges_to_tree(item = self.contents)
            
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
    def from_linear(cls, item: Linear) -> Edges:
        """Creates an Edges instance from a Linear."""
        return cls(contents = convert.linear_to_edges(item = item))
            
    @classmethod
    def from_matrix(cls, item: Matrix) -> Edges:
        """Creates an Edges instance from a Matrix."""
        return cls(contents = convert.matrix_to_edges(item = item))
             
    @classmethod
    def from_tree(cls, item: Tree) -> Edges:
        """Creates an Edges instance from a Tree."""
        return cls(contents = convert.tree_to_edges(item = item))
                
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
class Linear(sequence.Hybrid, base.Graph):
    """Base class for linear graphs.
    
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
        return convert.matrix_to_adjacency(item = self.contents)

    @property
    def edges(self) -> Edges:
        """Returns the stored graph as an Edges."""
        return convert.matrix_to_edges(item = self.contents)

    @property
    def linear(self) -> Linear:
        """Returns the stored graph as a Linear."""
        return self.contents
           
    @property
    def matrix(self) -> Matrix:
        """Returns the stored graph as a Matrix."""
        return convert.linear_to_matrix(item = self.contents)
           
    @property
    def tree(self) -> Tree:
        """Returns the stored graph as a Tree."""
        return convert.linear_to_tree(item = self.contents)
            
    """ Class Methods """
    
    @classmethod
    def from_adjacency(cls, item: Adjacency) -> Linear:
        """Creates a Linear instance from an Adjacency."""
        return cls(contents = convert.adjacency_to_linear(item = item))
    
    @classmethod
    def from_edges(cls, item: Edges) -> Linear:
        """Creates a Linear instance from an Edges."""
        return cls(contents = convert.edges_to_linear(item = item))
    
    @classmethod
    def from_linear(cls, item: Linear) -> Linear:
        """Creates a Linear instance from a Linear."""
        return cls(contents = item)
            
    @classmethod
    def from_matrix(cls, item: Matrix) -> Linear:
        """Creates a Linear instance from a Matrix."""
        return cls(contents = convert.matrix_to_linear(item = item))
             
    @classmethod
    def from_tree(cls, item: Tree) -> Linear:
        """Creates a Linear instance from a Tree."""
        return cls(contents = convert.tree_to_linear(item = item))
                    
    """ Dunder Methods """
        
    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        """Returns whether 'instance' meets criteria to be a subclass.

        Args:
            instance (object): item to test as an instance.

        Returns:
            bool: whether 'instance' meets criteria to be a subclass.
            
        """
        return check.is_linear(item = instance)
       
    
@dataclasses.dataclass
class Matrix(sequence.Listing, base.Graph):
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
    def linear(self) -> Linear:
        """Returns the stored graph as a Linear."""
        return convert.matrix_to_linear(item = self.contents)
           
    @property
    def matrix(self) -> Matrix:
        """Returns the stored graph as a Matrix."""
        return self.contents
           
    @property
    def tree(self) -> Tree:
        """Returns the stored graph as a Tree."""
        return convert.matrix_to_tree(item = self.contents)
         
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
    def from_linear(cls, item: Linear) -> Matrix:
        """Creates a Graph instance from a Linear."""
        return cls(contents = convert.linear_to_matrix(item = item))
            
    @classmethod
    def from_matrix(cls, item: Matrix) -> Matrix:
        """Creates a Matrix instance from a Matrix."""
        return cls(contents = item[0], labels = item[1])
             
    @classmethod
    def from_tree(cls, item: Tree) -> Matrix:
        """Creates a Matrix instance from a Tree."""
        return cls(contents = convert.tree_to_matrix(item = item))
               
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


@dataclasses.dataclass # type: ignore
class Tree(sequence.Hybrid, base.Graph, base.Node):
    """Base class for an tree data structures.
    
    The Tree class uses a Hybrid instead of a linked list for storing children
    nodes to allow easier access of nodes further away from the root. For
    example, a user might use 'a_tree["big_branch"]["small_branch"]["a_leaf"]' 
    to access a desired node instead of 'a_tree[2][0][3]' (although the latter
    access technique is also supported).

    Args:
        contents (MutableSequence[Node]): list of stored Tree or other 
            Node instances. Defaults to an empty list.
        name (Optional[str]): name of Tree node. Defaults to None.
        parent (Optional[Tree]): parent Tree, if any. Defaults to None.
        default_factory (Optional[Any]): default value to return or default 
            function to call when the 'get' method is used. Defaults to None. 
              
    """
    contents: MutableSequence[base.Node] = dataclasses.field(
        default_factory = list)
    name: Optional[str] = None
    parent: Optional[Tree] = None
    default_factory: Optional[Any] = None
                    
    """ Properties """

    @property
    def adjacency(self) -> Adjacency:
        """Returns the stored graph as an Adjacency."""
        return convert.tree_to_adjacency(item = self.contents)

    @property
    def edges(self) -> Edges:
        """Returns the stored graph as an Edges."""
        return convert.tree_to_edges(item = self.contents)

    @property
    def linear(self) -> Linear:
        """Returns the stored graph as a Linear."""
        return convert.tree_to_linear(item = self.contents)
           
    @property
    def matrix(self) -> Matrix:
        """Returns the stored graph as a Matrix."""
        return convert.tree_to_matrix(item = self.contents)
           
    @property
    def tree(self) -> Tree:
        """Returns the stored graph as a Tree."""
        return self.contents
        
    @property
    def children(self) -> MutableSequence[base.Node]:
        """Returns child nodes of this Node."""
        return self.contents
    
    @children.setter
    def children(self, value: MutableSequence[base.Node]) -> None:
        """Sets child nodes of this Node."""
        self.contents = value
        return

    # @property
    # def endpoint(self) -> Union[base.Node, base.Nodes]:
    #     """Returns the endpoint(s) of the stored graph."""
    #     if not self.contents:
    #         return self
    #     else:
    #         return self.contents[0].endpoint
 
    # @property
    # def root(self) -> Union[base.Node, base.Nodes]:
    #     """Returns the root(s) of the stored graph."""
    #     if self.parent is None:
    #         return self
    #     else:
    #         return self.parent.root  
                   
    """ Class Methods """
    
    @classmethod
    def from_adjacency(cls, item: Adjacency) -> Tree:
        """Creates a Tree instance from an Adjacency."""
        return cls(contents = convert.adjacency_to_tree(item = item))
    
    @classmethod
    def from_edges(cls, item: Edges) -> Tree:
        """Creates a Tree instance from an Edges."""
        return cls(contents = convert.edges_to_tree(item = item))
    
    @classmethod
    def from_linear(cls, item: Linear) -> Tree:
        """Creates a Tree instance from a Linear."""
        return cls(contents = convert.linear_to_tree(item = item))
            
    @classmethod
    def from_matrix(cls, item: Matrix) -> Tree:
        """Creates a Tree instance from a Matrix."""
        return cls(contents = convert.matrix_to_tree(item = item))
            
    @classmethod
    def from_tree(cls, item: Tree) -> Tree:
        """Creates a Tree instance from a Tree."""
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
        return check.is_tree(item = instance)

    def __missing__(self) -> Tree:
        """Returns an empty tree if one does not exist.

        Returns:
            Tree: an empty instance of Tree.
            
        """
        return self.__class__()
        