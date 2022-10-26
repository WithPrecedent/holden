"""
composites: base types of other composite data structures
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

                  
To Do:
    Complete Tree class and related functions
    Integrate Kinds system when it is finished

    
"""
from __future__ import annotations
import abc
from collections.abc import (
    Collection, Hashable, MutableMapping, MutableSequence, Sequence)
import contextlib
import dataclasses
from typing import (
    Any, Optional, Protocol, runtime_checkable, Type, TYPE_CHECKING, Union)

import amos

from . import base
from . import check
from . import traits
from . import traverse

if TYPE_CHECKING:
    from . import forms  

    
@dataclasses.dataclass
class Parallel(amos.Listing, traits.Directed):
    """Base class for a list of serial graphs.
    
    Args:
        contents (MutableSequence[Serial]): Listing of Serial instances. 
            Defaults to an empty list.
                                      
    """   
    contents: MutableSequence[Serial] = dataclasses.field(
        default_factory = list)
                                
    """ Properties """
    
    @property
    def endpoint(self) -> MutableSequence[Hashable]:
        """Returns the endpoints of the stored graph."""
        return [p[-1] for p in self.contents]
                    
    @property
    def root(self) -> MutableSequence[Hashable]:
        """Returns the roots of the stored graph."""
        return [p[0] for p in self.contents]
    
    @property
    def adjacency(self) -> forms.Adjacency:
        """Returns the stored graph as an Adjacency."""
        return traverse.parallel_to_adjacency(item = self.contents)

    @property
    def edges(self) -> forms.Edges:
        """Returns the stored graph as an Edges."""
        return traverse.parallel_to_edges(item = self.contents)
          
    @property
    def matrix(self) -> forms.Matrix:
        """Returns the stored graph as a Matrix."""
        return traverse.parallel_to_matrix(item = self.contents)

    @property
    def parallel(self) -> Parallel:
        """Returns the stored graph as a Parallel."""
        return self.contents

    @property
    def serial(self) -> Serial:
        """Returns the stored graph as a Serial."""
        return traverse.parallel_to_serial(item = self.contents)
    
    """ Class Methods """
    
    @classmethod
    def from_adjacency(cls, item: forms.Adjacency) -> Parallel:
        """Creates a Parallel instance from an Adjacency."""
        return cls(contents = traverse.adjacency_to_parallel(item = item))
    
    @classmethod
    def from_edges(cls, item: forms.Edges) -> Serial:
        """Creates a Parallel instance from an Edges."""
        return cls(contents = traverse.edges_to_parallel(item = item))
        
    @classmethod
    def from_matrix(cls, item: forms.Matrix) -> Serial:
        """Creates a Parallel instance from a Matrix."""
        return cls(contents = traverse.matrix_to_parallel(item = item))
    
    @classmethod
    def from_parallel(cls, item: Parallel) -> Serial:
        """Creates a Parallel instance from a Parallel."""
        return cls(contents = item)
     
    @classmethod
    def from_serial(cls, item: Serial) -> Serial:
        """Creates a Parallel instance from a Serial."""
        return cls(contents = item)

    """ Private Methods """   
    
    def _add(self, item: Hashable, *args: Any, **kwargs: Any) -> None:
        """Adds node to the stored graph.
                   
        Args:
            item (Hashable): node to add to the stored graph.
            
        """
        self.contents.append(item)
        return
        
    def _connect(self, item: base.Edge, *args: Any, **kwargs: Any) -> None:
        """Adds edge to the stored graph.
        
        Args:
            item (Edge): edge to add to the stored graph.
            
        """
        raise NotImplementedError(
            'Parallel graphs cannot connect edges because it changes the form')
      
    def _delete(self, item: Hashable, *args: Any, **kwargs: Any) -> None:
        """Deletes node from the stored graph.
                
        Args:
            item (Hashable): node to delete from 'contents'.
        
            
        """
        del self.contents[item]
        return
    
    def _disconnect(self, item: base.Edge, *args: Any, **kwargs: Any) -> None:
        """Removes edge from the stored graph.
        
        Args:
            item (Edge): edge to delete from the stored graph.
            
        """
        raise NotImplementedError(
            'Parallel graphs cannot disconnect edges because it changes the '
            'form')

    def _merge(self, item: base.Graph, *args: Any, **kwargs: Any) -> None:
        """Combines 'item' with the stored graph.

        Subclasses must provide their own specific methods for merging with
        another graph. The provided 'merge' method offers all of the error 
        checking. Subclasses just need to provide the mechanism for merging 
        ithout worrying about validation or error-checking.
        
        Args:
            item (Graph): another Graph object to add to the stored graph.
                
        """
        form = base.classify(item = item)
        if form == 'parallel':
            other = item
        else:
            transformer = globals()[f'{form}_to_parallel']
            other = transformer(item = item)
        for serial in other.contents:
            self.contents.append(serial)
        return
    
    def _subset(
        self, 
        include: Union[Hashable, Sequence[Hashable]] = None,
        exclude: Union[Hashable, Sequence[Hashable]] = None) -> forms.Adjacency:
        """Returns a new graph without a subset of 'contents'.

        Subclasses must provide their own specific methods for deleting a single
        edge. Subclasses just need to provide the mechanism for returning a
        subset without worrying about validation or error-checking.
        
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
        return check.is_parallel(item = instance)
     
    
@dataclasses.dataclass
class Serial(amos.Hybrid, traits.Directed):
    """Base class for serial graphs.
    
    Args:
        contents (MutableSequence[Hashable]): list of nodes. Defaults to 
            an empty list.
                                      
    """   
    contents: MutableSequence[Hashable] = dataclasses.field(
        default_factory = list)
                   
    """ Properties """

    @property
    def endpoint(self) -> MutableSequence[Hashable]:
        """Returns the endpoints of the stored graph."""
        return [self.contents[-1]]
                    
    @property
    def root(self) -> MutableSequence[Hashable]:
        """Returns the roots of the stored graph."""
        return [self.contents[0]]
    
    @property
    def adjacency(self) -> forms.Adjacency:
        """Returns the stored graph as an Adjacency."""
        return traverse.serial_to_adjacency(item = self.contents)

    @property
    def edges(self) -> forms.Edges:
        """Returns the stored graph as an Edges."""
        return traverse.serial_to_edges(item = self.contents)
          
    @property
    def matrix(self) -> forms.Matrix:
        """Returns the stored graph as a Matrix."""
        return traverse.serial_to_matrix(item = self.contents)

    @property
    def parallel(self) -> Parallel:
        """Returns the stored graph as a Parallel."""
        return traverse.serial_to_parallel(item = self.contents)

    @property
    def serial(self) -> Serial:
        """Returns the stored graph as a Serial."""
        return self.contents
    
    """ Class Methods """
    
    @classmethod
    def from_adjacency(cls, item: forms.Adjacency) -> Serial:
        """Creates a Serial instance from an Adjacency."""
        return cls(contents = traverse.adjacency_to_serial(item = item))
    
    @classmethod
    def from_edges(cls, item: forms.Edges) -> Serial:
        """Creates a Serial instance from an Edges."""
        return cls(contents = traverse.edges_to_serial(item = item))
        
    @classmethod
    def from_matrix(cls, item: forms.Matrix) -> Serial:
        """Creates a Serial instance from a Matrix."""
        return cls(contents = traverse.matrix_to_serial(item = item))
    
    @classmethod
    def from_parallel(cls, item: Parallel) -> Serial:
        """Creates a Serial instance from a Serial."""
        return cls(contents = traverse.parallel_to_serial(item = item))
     
    @classmethod
    def from_serial(cls, item: Serial) -> Serial:
        """Creates a Serial instance from a Serial."""
        return cls(contents = item)

    """ Private Methods """   
    
    def _add(self, item: Hashable, *args: Any, **kwargs: Any) -> None:
        """Adds node to the stored graph.
                   
        Args:
            item (Hashable): node to add to the stored graph.
            
        """
        self.contents.append(item)
        return
        
    def _connect(self, item: base.Edge, *args: Any, **kwargs: Any) -> None:
        """Adds edge to the stored graph.
        
        Args:
            item (Edge): edge to add to the stored graph.
            
        """
        raise NotImplementedError(
            'Serial graphs cannot connect edges because it changes the form')
      
    def _delete(self, item: Hashable, *args: Any, **kwargs: Any) -> None:
        """Deletes node from the stored graph.
                
        Args:
            item (Hashable): node to delete from 'contents'.
        
            
        """
        del self.contents[item]
        return
    
    def _disconnect(self, item: base.Edge, *args: Any, **kwargs: Any) -> None:
        """Removes edge from the stored graph.
        
        Args:
            item (Edge): edge to delete from the stored graph.
            
        """
        raise NotImplementedError(
            'Serial graphs cannot disconnect edges because it changes the form')

    def _merge(self, item: base.Graph, *args: Any, **kwargs: Any) -> None:
        """Combines 'item' with the stored graph.

        Subclasses must provide their own specific methods for merging with
        another graph. The provided 'merge' method offers all of the error 
        checking. Subclasses just need to provide the mechanism for merging 
        ithout worrying about validation or error-checking.
        
        Args:
            item (Graph): another Graph object to add to the stored graph.
                
        """
        form = base.classify(item = item)
        if form == 'serial':
            other = item
        else:
            transformer = globals()[f'{form}_to_serial']
            other = transformer(item = item)
        self.contents.extend(other)
        return
    
    def _subset(
        self, 
        include: Union[Hashable, Sequence[Hashable]] = None,
        exclude: Union[Hashable, Sequence[Hashable]] = None) -> Serial:
        """Returns a new graph without a subset of 'contents'.

        Subclasses must provide their own specific methods for deleting a single
        edge. Subclasses just need to provide the mechanism for returning a
        subset without worrying about validation or error-checking.
        
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
        return check.is_serial(item = instance)      


""" Type Checkers """

    
# @dataclasses.dataclass # type: ignore
# class Tree(amos.Hybrid, traits.Directed, base.Graph):
#     """Base class for an tree data structures.
    
#     The Tree class uses a Hybrid instead of a linked list for storing children
#     nodes to allow easier access of nodes further away from the root. For
#     example, a user might use 'a_tree["big_branch"]["small_branch"]["a_leaf"]' 
#     to access a desired node instead of 'a_tree[2][0][3]' (although the latter
#     access technique is also supported).

#     Args:
#         contents (MutableSequence[Node]): list of stored Tree or other 
#             Node instances. Defaults to an empty list.
#         name (Optional[str]): name of Tree node. Defaults to None.
#         parent (Optional[Tree]): parent Tree, if any. Defaults to None.
#         default_factory (Optional[Any]): default value to return or default 
#             function to call when the 'get' method is used. Defaults to None. 
              
#     """
#     contents: MutableSequence[Hashable] = dataclasses.field(
#         default_factory = list)
#     name: Optional[str] = None
#     parent: Optional[Tree] = None
#     default_factory: Optional[Any] = None
                    
#     """ Properties """
        
#     @property
#     def children(self) -> MutableSequence[Hashable]:
#         """Returns child nodes of this Node."""
#         return self.contents
    
#     @children.setter
#     def children(self, value: MutableSequence[Hashable]) -> None:
#         """Sets child nodes of this Node."""
#         if amos.is_sequence(value):
#             self.contents = value
#         else:
#             self.contents = [value]
#         return

#     @property
#     def endpoint(self) -> Union[Hashable, Collection[Hashable]]:
#         """Returns the endpoint(s) of the stored graph."""
#         if not self.contents:
#             return self
#         else:
#             return self.contents[0].endpoint
 
#     @property
#     def root(self) -> Union[Hashable, Collection[Hashable]]:
#         """Returns the root(s) of the stored graph."""
#         if self.parent is None:
#             return self
#         else:
#             return self.parent.root  
                                
#     """ Dunder Methods """
        
#     @classmethod
#     def __instancecheck__(cls, instance: object) -> bool:
#         """Returns whether 'instance' meets criteria to be a subclass.

#         Args:
#             instance (object): item to test as an instance.

#         Returns:
#             bool: whether 'instance' meets criteria to be a subclass.
            
#         """
#         return is_tree(item = instance)

#     def __missing__(self) -> Tree:
#         """Returns an empty tree if one does not exist.

#         Returns:
#             Tree: an empty instance of Tree.
            
#         """
#         return self.__class__()


# def is_tree(item: object) -> bool:
#     """Returns whether 'item' is a tree.

#     Args:
#         item (object): instance to test.

#     Returns:
#         bool: whether 'item' is a tree.
    
#     """
#     return (
#         isinstance(item, MutableSequence)
#         and all(isinstance(i, (MutableSequence, Hashable)) for i in item)) 
    
# def is_forest(item: object) -> bool:
#     """Returns whether 'item' is a dict of tree.

#     Args:
#         item (object): instance to test.

#     Returns:
#         bool: whether 'item' is a dict of tree.
    
#     """
#     return (
#         isinstance(item, MutableMapping)
#         and all(base.is_node(item = i) for i in item.keys())
#         and all(is_tree(item = i) for i in item.values())) 


# # @functools.singledispatch 
# def to_tree(item: Any) -> forms.Tree:
#     """Converts 'item' to a Tree.
    
#     Args:
#         item (Any): item to convert to a Tree.

#     Raises:
#         TypeError: if 'item' is a type that is not registered.

#     Returns:
#         form.Tree: derived from 'item'.

#     """
#     if check.is_tree(item = item):
#         return item
#     else:
#         raise TypeError(
#             f'item cannot be converted because it is an unsupported type: '
#             f'{type(item).__name__}')

# # @to_tree.register # type: ignore 
# def matrix_to_tree(item: forms.Matrix) -> forms.Tree:
#     """Converts 'item' to a Tree.
    
#     Args:
#         item (form.Matrix): item to convert to a Tree.

#     Raises:
#         TypeError: if 'item' is a type that is not registered.

#     Returns:
#         form.Tree: derived from 'item'.

#     """
#     tree = {}
#     for node in item:
#         children = item[:]
#         children.remove(node)
#         tree[node] = matrix_to_tree(children)
#     return tree
        