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
    Parallel (camina.Listing, traits.Directed, base.Composite):
    Serial (camina.Hybrid, traits.Directed, base.Composite):
                  
To Do:
    Complete Tree class and related functions
    Integrate Kinds system when it is finished
  
"""
from __future__ import annotations
from collections.abc import Hashable, MutableSequence, Sequence
import copy
import dataclasses
from typing import Any, Optional, Union

import camina

from . import base
from . import check
from . import report
from . import traits
from . import traverse

    
@dataclasses.dataclass
class Parallel(camina.Listing, traits.Directed, base.Composite):
    """Base class for a list of serial composites.
    
    Args:
        contents (MutableSequence[Serial]): Listing of Serial instances. 
            Defaults to an empty list.
                                      
    """   
    contents: MutableSequence[Serial] = dataclasses.field(
        default_factory = list)
                                
    """ Properties """
    
    @property
    def endpoint(self) -> MutableSequence[Hashable]:
        """Returns the endpoints of the stored composite."""
        return report.get_endpoints_parallel(item = self)
                    
    @property
    def root(self) -> MutableSequence[Hashable]:
        """Returns the roots of the stored composite."""
        return report.get_roots_parallel(item = self)

    """ Public Methods """
    
    def walk(
        self, 
        start: Optional[Hashable] = None, 
        stop: Optional[Hashable] = None) -> Parallel:
        """Returns all paths in graph from 'start' to 'stop'.
        
        Args:
            start (Hashable): node to start paths from.
            stop (Hashable): node to stop paths.
            
        Returns:
            Paralle: a list of possible paths (each path is a list nodes) from 
                'start' to 'stop'.
            
        """
        if start is None:
            root = self.root
        else:
            root = camina.listify(start)
        if stop is None:
            endpoint = self.endpoint
        else:
            endpoint = self.camina.listify(stop)
        return traverse.walk_parallel(
            item = self, 
            start = root, 
            stop = endpoint) 
    
    """ Private Methods """   
    
    def _add(self, item: Hashable, *args: Any, **kwargs: Any) -> None:
        """Adds node to the stored composite.
                   
        Args:
            item (Hashable): node to add to the stored composite.
            
        """
        self.contents.append(item)
        return
      
    def _delete(self, item: Hashable, *args: Any, **kwargs: Any) -> None:
        """Deletes node from the stored composite.
                
        Args:
            item (Hashable): node to delete from 'contents'.
        
            
        """
        del self.contents[item]
        return

    def _merge(self, item: base.Composite, *args: Any, **kwargs: Any) -> None:
        """Combines 'item' with the stored composite.

        Subclasses must provide their own specific methods for merging with
        another composite. The provided 'merge' method offers all of the error 
        checking. Subclasses just need to provide the mechanism for merging 
        ithout worrying about validation or error-checking.
        
        Args:
            item (base.Composite): another Composite object to add to the 
                stored composite.
                
        """
        other = base.transform(
            item = item, 
            output = 'parallel', 
            raise_same_error = False)
        for serial in other:
            self.contents.append(serial)
        return
    
    def _subset(
        self, 
        include: Union[Hashable, Sequence[Hashable]] = None,
        exclude: Union[Hashable, Sequence[Hashable]] = None) -> Parallel:
        """Returns a new composite without a subset of 'contents'.

        Subclasses must provide their own specific methods for deleting a single
        edge. Subclasses just need to provide the mechanism for returning a
        subset without worrying about validation or error-checking.
        
        Args:
            include (Union[Hashable, Sequence[Hashable]]): nodes or edges which 
                should be included in the new composite.
            exclude (Union[Hashable, Sequence[Hashable]]): nodes or edges which 
                should not be included in the new composite.

        Returns:
           Parallel: with only selected nodes and edges.
            
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
class Serial(camina.Hybrid, traits.Directed, base.Composite):
    """Base class for serial composites.
    
    Args:
        contents (MutableSequence[Hashable]): list of nodes. Defaults to 
            an empty list.
                                      
    """   
    contents: MutableSequence[Hashable] = dataclasses.field(
        default_factory = list)
                   
    """ Properties """

    @property
    def endpoint(self) -> MutableSequence[Hashable]:
        """Returns the endpoints of the stored composite."""
        return report.get_endpoints_serial(item = self)
                    
    @property
    def root(self) -> MutableSequence[Hashable]:
        """Returns the roots of the stored composite."""
        return report.get_roots_serial(item = self)

    """ Public Methods """
    
    def walk(
        self, 
        start: Optional[Hashable] = None, 
        stop: Optional[Hashable] = None) -> Parallel:
        """Returns all paths in graph from 'start' to 'stop'.
        
        Args:
            start (Hashable): node to start paths from.
            stop (Hashable): node to stop paths.
            
        Returns:
            Paralle: a list of possible paths (each path is a list nodes) from 
                'start' to 'stop'.
            
        """
        if start is None:
            start = self.root[0]
        if stop is None:
            stop = self.endpoint[0]
        return traverse.walk_serial(item = self, start = start, stop = stop) 
        
    """ Private Methods """   
    
    def _add(self, item: Hashable, *args: Any, **kwargs: Any) -> None:
        """Adds node to the stored composite.
                   
        Args:
            item (Hashable): node to add to the stored composite.
            
        """
        self.contents.append(item)
        return
      
    def _delete(self, item: Hashable, *args: Any, **kwargs: Any) -> None:
        """Deletes node from the stored composite.
                
        Args:
            item (Hashable): node to delete from 'contents'.
        
            
        """
        del self.contents[item]
        return

    def _merge(self, item: base.Composite, *args: Any, **kwargs: Any) -> None:
        """Combines 'item' with the stored composite.

        Subclasses must provide their own specific methods for merging with
        another composite. The provided 'merge' method offers all of the error 
        checking. Subclasses just need to provide the mechanism for merging 
        ithout worrying about validation or error-checking.
        
        Args:
            item (base.Composite): another Composite object to add to the 
                stored composite.
                
        """
        other = base.transform(
            item = item, 
            output = 'serial', 
            raise_same_error = False)
        self.contents.extend(other)
        return
    
    def _subset(
        self, 
        include: Union[Hashable, Sequence[Hashable]] = None,
        exclude: Union[Hashable, Sequence[Hashable]] = None) -> Serial:
        """Returns a new composite without a subset of 'contents'.

        Subclasses must provide their own specific methods for deleting a single
        edge. Subclasses just need to provide the mechanism for returning a
        subset without worrying about validation or error-checking.
        
        Args:
            include (Union[Hashable, Sequence[Hashable]]): nodes or edges which 
                should be included in the new composite.
            exclude (Union[Hashable, Sequence[Hashable]]): nodes or edges which 
                should not be included in the new composite.

        Returns:
           Serial: with only selected nodes and edges.
            
        """
        if include:
            new_serial = [i for i in self.contents if i in include]  
        else:
            new_serial = copy.deepcopy(self.contents)
        if exclude:
            new_serial = [i for i in self.contents if i not in exclude]
        return self.__class__(contents = new_serial)
                        
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
# class Tree(camina.Hybrid, traits.Directed, base.Composite):
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
#         if camina.is_sequence(value):
#             self.contents = value
#         else:
#             self.contents = [value]
#         return

#     @property
#     def endpoint(self) -> Union[Hashable, Collection[Hashable]]:
#         """Returns the endpoint(s) of the stored composite."""
#         if not self.contents:
#             return self
#         else:
#             return self.contents[0].endpoint
 
#     @property
#     def root(self) -> Union[Hashable, Collection[Hashable]]:
#         """Returns the root(s) of the stored composite."""
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
# def to_tree(item: Any) -> graphs.Tree:
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
# def matrix_to_tree(item: graphs.Matrix) -> graphs.Tree:
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
        