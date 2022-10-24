"""
base: base classes for composite data structures
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
    Graph (amos.Bunch, Protocol): base class for composite data structures. 
        Provides some common functionality and requires subclass methods.
    Edge (Sequence): base class for an edge in a graph. Many graphs will not
        require edge instances, but the class is made available for more complex 
        graphs and type checking.
    # Node (amos.Proxy): wrapper for items that can be stored in a Graph or other
    #     data structure.  
    # Nodes (amos.Bunch): any collection of Node instances. This is primarily
    #     intended for easy type checking of any arbitrary group of objects to 
    #     make sure they meet the requirements of being a Node (real or virtual) 
    #     instance.
    is_graph
    is_edge
    is_node
    # is_nodes
    # to_node

                 
To Do:
    Integrate Kinds system when it is finished.

    
"""
from __future__ import annotations
import abc
# import collections
from collections.abc import Collection, Hashable, Sequence
import contextlib
import dataclasses
import inspect
from typing import (
    Any, Optional, Protocol, runtime_checkable, Type, TYPE_CHECKING, Union)

import amos 
import miller


""" Base Classes for Graph Data Structures """
      
@dataclasses.dataclass
@runtime_checkable
class Graph(amos.Bunch, Protocol):
    """Base class for holden graphs.
    
    Args:
        contents (Collection[Any]): stored collection of nodes and/or edges.
                                     
    """  
    contents: Collection[Any]
             
    """ Required Subclass Methods """
    
    def _add(self, item: Hashable, *args: Any, **kwargs: Any) -> None:
        """Adds node to the stored graph.
 
        Subclasses must provide their own specific methods for adding a single
        node. The provided 'add' method offers all of the error checking and
        the ability to add multiple nodes at once. Subclasses just need to 
        provide the mechanism for adding a single node without worrying about
        validation or error-checking.
                   
        Args:
            item (Hashable): node to add to the stored graph.
                
        """
        raise NotImplementedError

    def _connect(self, item: Edge, *args: Any, **kwargs: Any) -> None:
        """Adds edge to the stored graph.

        Subclasses must provide their own specific methods for adding a single
        edge. The provided 'connect' method offers all of the error checking and
        the ability to add multiple edges at once. Subclasses just need to 
        provide the mechanism for adding a single edge without worrying about
        validation or error-checking.
        
        Args:
            item (Edge): edge to add to the stored graph.
            
        """
        raise NotImplementedError
      
    def _delete(self, item: Hashable, *args: Any, **kwargs: Any) -> None:
        """Deletes node from the stored graph.

        Subclasses must provide their own specific methods for deleting a single
        node. The provided 'delete' method offers all of the error checking and
        the ability to delete multiple nodes at once. Subclasses just need to 
        provide the mechanism for deleting a single node without worrying about
        validation or error-checking.
                
        Args:
            item (Hashable): node to delete from 'contents'.
            
        """
        raise NotImplementedError
  
    def _disconnect(self, item: Edge, *args: Any, **kwargs: Any) -> None:
        """Removes edge from the stored graph.

        Subclasses must provide their own specific methods for deleting a single
        edge. The provided 'disconnect' method offers all of the error checking 
        and the ability to delete multiple edges at once. Subclasses just need 
        to provide the mechanism for deleting a single edge without worrying 
        about validation or error-checking.
        
        Args:
            item (Edge): edge to delete from the stored graph.
            
        """
        raise NotImplementedError  

    def _merge(self, item: Graph, *args: Any, **kwargs: Any) -> None:
        """Combines 'item' with the stored graph.

        Subclasses must provide their own specific methods for merging with
        another graph. The provided 'merge' method offers all of the error 
        checking. Subclasses just need to provide the mechanism for merging 
        ithout worrying about validation or error-checking.
        
        Args:
            item (Graph): another Graph object to add to the stored graph.
                
        """
        raise NotImplementedError
    
    def _subset(
        self, 
        include: Union[Hashable, Sequence[Hashable]] = None,
        exclude: Union[Hashable, Sequence[Hashable]] = None) -> Graph:
        """Returns a new Graph without a subset of 'contents'.

        Subclasses must provide their own specific methods for deleting a single
        edge. Subclasses just need to provide the mechanism for returning a
        subset without worrying about validation or error-checking.
        
        Args:
            include (Union[Hashable, Sequence[Hashable]]): nodes or edges which 
                should be included in the new graph.
            exclude (Union[Hashable, Sequence[Hashable]]): nodes or edges which 
                should not be included in the new graph.

        Returns:
           Graph: with only selected nodes and edges.
            
        """
        raise NotImplementedError  
         
    """ Public Methods """

    def add(self, item: Hashable, *args: Any, **kwargs: Any) -> None:
        """Adds node to the stored graph.
                   
        Args:
            item (Hashable): node to add to the stored graph.
            
        Raises:
            TypeError: if 'item' is not a node type.
            ValueError: if 'item' is already in the stored graph.
            
        """
        if not is_node(item = item):
            raise TypeError(f'{item} is not a node type')
        elif item in self.contents:
            raise ValueError(f'{item} already in the graph') 
        else:  
            self._add(item, *args, **kwargs)
        return
        
    def connect(self, item: Edge, *args: Any, **kwargs: Any) -> None:
        """Adds edge to the stored graph.
        
        Args:
            item (Edge): edge to add to the stored graph.
            
        Raises:
            ValueError: if the ends of the item are the same or if one of the
                edge ends does not currently exist in the stored graph.
            
        """
        if not is_edge(item = item):
            raise TypeError(f'{item} is not an edge type') 
        elif item[0] == item[1]:
            raise ValueError(
                'The starting point of an edge cannot be the same as the '
                'ending point')
        elif item[0] not in self:
            raise ValueError(f'{item[0]} is not in the graph')
        elif item[1] not in self:
            raise ValueError(f'{item[1]} is not in the graph')
        else:
            self._connect(item, *args, **kwargs)
        return                         
  
    def delete(self, item: Hashable, *args: Any, **kwargs: Any) -> None:
        """Deletes node from the stored graph.

        Subclasses must provide their own specific methods for deleting a single
        node. The provided 'delete' method offers all of the error checking and
        the ability to delete multiple nodes at once. Subclasses just need to 
        provide the mechanism for deleting a single node without worrying about
        validation or error-checking.
                
        Args:
            item (Hashable): node to delete from 'contents'.
        
        Raises:
            KeyError: if 'item' is not in 'contents'.
            TypeError: if 'item' is not in 'contents'.
            
        """
        if not is_node(item = item):
            raise TypeError(f'{item} is not a node type')
        try:
            self._delete(item, *args **kwargs)
        except KeyError:
            raise KeyError(f'{item} does not exist in the graph')
        return
    
    def disconnect(self, item: Edge, *args: Any, **kwargs: Any) -> None:
        """Removes edge from the stored graph.
        
        Args:
            item (Edge): edge to delete from the stored graph.
            
        Raises:
            ValueError: if the edge does not exist in the stored graph.
            
        """
        if not is_edge(item = item):
            raise TypeError(f'{item} is not an edge type') 
        elif item[0] == item[1]:
            raise ValueError(
                'The starting point of an edge cannot be the same as the '
                'ending point')
        else:
            try:
                self._disconnect(item, *args, **kwargs)
            except (KeyError, ValueError):
                raise ValueError(
                    f'The edge ({item[0]}, {item[1]}) is not in the graph')
        return     

    def merge(self, item: Graph, *args: Any, **kwargs: Any) -> None:
        """Adds 'item' to this Graph.

        This method is roughly equivalent to a dict.update, just adding 'item'
        to the existing stored graph while maintaining its structure.
        
        Args:
            item (base.Graph): another Graph, an adjacency 
                list, an edge list, an adjacency matrix, or one or more nodes.
            
        Raises:
            TypeError: if 'item' is not compatible graph type.
            
        """
        if not is_graph(item = item):
            raise TypeError(f'{item} is not a compatible graph type') 
        else:
            self._merge(item, *args, **kwargs)
        return
        
    def subset(
        self, 
        include: Union[Hashable, Sequence[Hashable]] = None,
        exclude: Union[Hashable, Sequence[Hashable]] = None) -> Graph:
        """Returns a new Graph without a subset of 'contents'.
        
        All edges will be removed that include any nodes that are not part of
        the new subgraph.
        
        Any extra attributes that are part of a Graph (or a subclass) should 
        be maintained in the returned subgraph.

        Args:
            include (Union[Hashable, Sequence[Hashable]]): nodes or edges which 
                should be included in the new graph.
            exclude (Union[Hashable, Sequence[Hashable]]): nodes or edges which 
                should not be included in the new graph.

        Raises:
            ValueError: if include and exclude are none or if any item in
                include or exclude is not in the stored graph.

        Returns:
           Graph: with only selected nodes and edges.

        """
        if include is None and exclude is None:
            raise ValueError('Either include or exclude must not be None')
        if not all(i for i in include if i in self.contents):
            raise ValueError('Some values in include are not in the graph')
        if not all(i for i in exclude if i in self.contents):
            raise ValueError('Some values in exclude are not in the graph')
        return self._subset(include, exclude)
                      
    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        """Returns whether 'instance' meets criteria to be a subclass.

        Args:
            instance (object): item to test as an instance.

        Returns:
            bool: whether 'instance' meets criteria to be a subclass.
            
        """
        return is_graph(item = instance)

       
@dataclasses.dataclass(frozen = True, order = True)
class Edge(Sequence):
    """Base class for an edge in a graph structure.
    
    If a subclass adds other attributes, it is important that they are not 
    declared as dataclass fields to allow indexing to work properly.
    
    Edges are not required for most of the base graph classes in amos. But
    they can be used by subclasses of those base classes for more complex data
    structures.
    
    Args:
        start (Hashable): starting point for the edge.
        stop (Hashable): stopping point for the edge.
        
    """
    start: Hashable
    stop: Hashable

    """ Dunder Methods """
        
    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        """Returns whether 'instance' meets criteria to be a subclass.

        Args:
            instance (object): item to test as an instance.

        Returns:
            bool: whether 'instance' meets criteria to be a subclass.
            
        """
        return is_edge(item = instance)
    
    def __getitem__(self, index: int) -> Hashable:
        """Allows Edge subclass to be accessed by index.
        
        Args:
            index (int): the number of the field in the dataclass based on 
                order.
        
        Raises:
            IndexError: if 'index' is greater than 1.
        
        Returns:
            Hashable: contents of field identified by 'index'.
                 
        """
        if index > 1:
            raise IndexError('Index out of bounds - edges are only two points')
        else:
            return getattr(self, dataclasses.fields(self)[index].name)
    
    def __len__(self) -> int:
        """Returns length of 2.
        
        Returns:
            int: 2
            
        """
        return 2


@dataclasses.dataclass
class Node(Hashable):
    """Vertex wrapper to provide hashability to any object.
    
    Node acts a basic wrapper for any item stored in a graph structure.
    
    Args:
        contents (Optional[Any]): any stored item(s). Defaults to None.
            
    """
    contents: Optional[Any] = None

    """ Initialization Methods """
    
    def __init_subclass__(cls, *args: Any, **kwargs: Any):
        """Forces subclasses to use the same hash methods as Node.
        
        This is necessary because dataclasses, by design, do not automatically 
        inherit the hash and equivalance dunder methods from their super 
        classes.
        
        """
        # Calls other '__init_subclass__' methods for parent and mixin classes.
        with contextlib.suppress(AttributeError):
            super().__init_subclass__(*args, **kwargs) # type: ignore
        # Copies hashing related methods to a subclass.
        cls.__hash__ = Node.__hash__ # type: ignore
        cls.__eq__ = Node.__eq__ # type: ignore
        cls.__ne__ = Node.__ne__ # type: ignore
                
    """ Dunder Methods """
    
    @classmethod
    def __subclasshook__(cls, subclass: Type[Any]) -> bool:
        """Returns whether 'subclass' is a virtual or real subclass.

        Args:
            subclass (Type[Any]): item to test as a subclass.

        Returns:
            bool: whether 'subclass' is a real or virtual subclass.
            
        """
        return is_node(item = subclass)
               
    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        """Returns whether 'instance' meets criteria to be a subclass.

        Args:
            instance (object): item to test as an instance.

        Returns:
            bool: whether 'instance' meets criteria to be a subclass.
            
        """
        return is_node(item = instance)
    
    def __hash__(self) -> int:
        """Makes Node hashable so that it can be used as a key in a dict.

        Rather than using the object ID, this method prevents two Nodes with
        the same name from being used in a graph object that uses a dict as
        its base storage type.
        
        Returns:
            int: hashable of 'name'.
            
        """
        return hash(self)


# @dataclasses.dataclass
# @runtime_checkable
# class Nodes(amos.Bunch, Protocol):
#     """Collection of Nodes.
    
#     Nodes are not guaranteed to be in order. 

#     Args:
#         contents (Optional[Any]): any stored item(s). Defaults to None.
            
#     """
#     contents: Optional[Collection[Node]] = None
    
#     """ Dunder Methods """ 
    
#     @classmethod
#     def __instancecheck__(cls, instance: object) -> bool:
#         """Returns whether 'instance' meets criteria to be a subclass.

#         Args:
#             instance (object): item to test as an instance.

#         Returns:
#             bool: whether 'instance' meets criteria to be a subclass.
            
#         """
#         return is_nodes(item = instance)


""" Base Class Type Checkers """

def is_graph(item: Union[Type[Any], object]) -> bool:
    """Returns whether 'item' is a graph.

    Args:
        item (object): instance to test.

    Returns:
        bool: whether 'item' is a graph.
    
    """
    return miller.has_methods(
        item = item, 
        methods = ['add', 'connect', 'delete', 'disconnect', 'merge'])

def is_edge(item: object) -> bool:
    """Returns whether 'item' is an edge.

    Args:
        item (object): instance to test.

    Returns:
        bool: whether 'item' is an edge.
        
    """
    return (
        miller.is_sequence(item)
        and len(item) == 2
        and is_node(item = item[0])
        and is_node(item = item[1]))
      
def is_node(item: Union[object, Type[Any]]) -> bool:
    """Returns whether 'item' is a node.

    Args:
        item (Union[object, Type[Any]]): instance or class to test.

    Returns:
        bool: whether 'item' is a node.
    
    """
    if inspect.isclass(item):
        return issubclass(item, Hashable)
    else:
        return isinstance(item, Hashable)

def is_nodes(item: object) -> bool:
    """Returns whether 'item' is a collection of nodes.

    Args:
        item (object): instance to test.

    Returns:
        bool: whether 'item' is a collection of nodes.
    
    """
    return (
        isinstance(item, Collection) and all(is_node(item = i) for i in item))

# """ Base Class Converters """

# def to_node(
#     item: Union[Type[Any], object], 
#     base: Optional[Type[Node]] = Node) -> Node:
#     """Converts 'item' into a Node, if it is not already a Node instance.

#     Args:
#         item (Union[Type[Any], object]): class or instance to transform into a  
#             Node.
#         base (Optional[Type[Node]]): base class to wrap 'item' in if 'item'
#              is not a Node.

#     Returns:
#         Node: a Node or Node subclass instance.
        
#     """
#     if is_node(item = item):
#         return item
#     else:
#         return base(contents = item)    
          