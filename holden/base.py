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
    Composite (amos.Bunch, Protocol): base class for composite data structures. 
        Requires 'append', 'delete', 'merge', 'prepend', and 'walk' methods.
    Edge (Sequence): base class for an edge in a graph. Many graphs will not
        require edge instances, but the class is made available for more complex 
        graphs and type checking.
    Graph (Composite, Protocol): base class for graphs. All subclasses must have 
        'connect' and 'disconnect' methods for changing edges between nodes.
    Node (amos.Proxy): wrapper for items that can be stored in a Graph or other
        data structure.  
    Nodes (amos.Bunch): any collection of Node instances. This is primarily
        intended for easy type checking of any arbitrary group of objects to 
        make sure they meet the requirements of being a Node (real or virtual) 
        instance.
                  
To Do:
    Integrate Kinds system when it is finished.
    Restore 'beautify' str representations once those are finished.

    
"""
from __future__ import annotations
import abc
from collections.abc import Collection, Hashable, Sequence
import contextlib
import dataclasses
from typing import (
    Any, Optional, Protocol, runtime_checkable, Type, TYPE_CHECKING)

import amos

from . import check

if TYPE_CHECKING:
    from . import form
        
        
@dataclasses.dataclass
@runtime_checkable
class Composite(amos.Bunch, Protocol):
    """Base class for composite data structures.
    
    Args:
        contents (Collection[Any]): stored collection of nodes and/or edges.
                                     
    """  
    contents: Collection[Any]
    
                 
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def connect(self, start: Hashable, stop: Hashable) -> None:
        """Creates a new edge in the stored graph.

        Args:
            start (Hashable): starting node for the new edge.
            stop (Hashable): ending node for the new edge.
        
        Raises:
            KeyError: if 'start' or 'stop' are not a nodes in the stored graph.

        """
        pass  
    
    @abc.abstractmethod
    def disconnect(self, start: Hashable, stop: Hashable) -> None:
        """Deletes edge from the stored graph.

        Args:
            start (Hashable): starting node for the edge to delete.
            stop (Hashable): ending node for the edge to delete.
        
        Raises:
            KeyError: if 'start' or 'stop' are not a nodes in the stored graph.

        """
        pass  
  
    @abc.abstractmethod
    def merge(self, item: Composite, *args: Any, **kwargs: Any) -> None:
        """Combines 'item' with the stored composite object.

        Args:
            item (Composite): another Composite object to add to the stored 
                composite object.
                
        """
        pass
            
    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        """Returns whether 'instance' meets criteria to be a subclass.

        Args:
            instance (object): item to test as an instance.

        Returns:
            bool: whether 'instance' meets criteria to be a subclass.
            
        """
        return check.is_composite(item = instance)
      
      
@dataclasses.dataclass(frozen = True, order = True)
class Edge(Sequence):
    """Base class for an edge in a composite structure.
    
    If a subclass adds other attributes, it is important that they are not 
    declared as dataclass fields to allow indexing to work properly.
    
    Edges are not required for most of the base composite classes in amos. But
    they can be used by subclasses of those base classes for more complex data
    structures.
    
    Args:
        start (Node): starting point for the edge.
        stop (Node): stopping point for the edge.
        
    """
    start: Node
    stop: Node

    """ Dunder Methods """
        
    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        """Returns whether 'instance' meets criteria to be a subclass.

        Args:
            instance (object): item to test as an instance.

        Returns:
            bool: whether 'instance' meets criteria to be a subclass.
            
        """
        return check.is_edge(item = instance)
    
    def __getitem__(self, index: int) -> Node:
        """Allows Edge subclass to be accessed by index.
        
        Args:
            index (int): the number of the field in the dataclass based on 
                order.
        
        Returns:
            Node: contents of field identified by 'index'.
                 
        """
        return getattr(self, dataclasses.fields(self)[index].name)
    
    def __len__(self) -> int:
        """Returns length based on the number of fields.
        
        Returns:
            int: number of fields.
            
        """
        return len(dataclasses.fields(self))
        

@dataclasses.dataclass # type: ignore
@runtime_checkable
class Graph(Composite, Protocol):
    """Base class for graph data structures.
    
    Args:
        contents (Collection[Any]): stored collection of nodes and/or edges.
                                      
    """  
    contents: Collection[Any]
   
    """ Required Subclass Properties """

    @abc.abstractproperty
    def adjacency(self) -> form.Adjacency:
        """Returns the stored graph as an Adjacency."""
        pass

    @abc.abstractproperty
    def edges(self) -> form.Edges:
        """Returns the stored graph as an Edges."""
        pass

    @abc.abstractproperty
    def linear(self) -> form.Linear:
        """Returns the stored graph as a Linear."""
        pass
           
    @abc.abstractproperty
    def matrix(self) -> form.Matrix:
        """Returns the stored graph as a Matrix."""
        pass
           
    @property
    def tree(self) -> form.Tree:
        """Returns the stored graph as a Tree."""
        pass     
     
    """ Required Subclass Methods """
    
    @abc.abstractclassmethod
    def from_adjacency(cls, item: form.Adjacency) -> Graph:
        """Creates a Graph instance from an Adjacency."""
        pass
    
    @abc.abstractclassmethod
    def from_edges(cls, item: form.Edges) -> Graph:
        """Creates a Graph instance from an Edges."""
        pass
    
    @abc.abstractclassmethod
    def from_linear(cls, item: form.Linear) -> Graph:
        """Creates a Graph instance from a Linear."""
        pass
        
    @abc.abstractclassmethod
    def from_matrix(cls, item: form.Matrix) -> Graph:
        """Creates a Graph instance from a Matrix."""
        pass
            
    @classmethod
    def from_tree(cls, item: form.Tree) -> Graph:
        """Creates an Edges instance from a Tree."""
        pass
            
    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        """Returns whether 'instance' meets criteria to be a subclass.

        Args:
            instance (object): item to test as an instance.

        Returns:
            bool: whether 'instance' meets criteria to be a subclass.
            
        """
        return check.is_graph(item = instance)
 
 
@dataclasses.dataclass
class Node(amos.Proxy):
    """Vertex wrapper to provide hashability to any object.
    
    Node acts a basic wrapper for any item stored in a composite structure.
    
    Args:
        contents (Optional[Any]): any stored item(s). Defaults to None.
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a composite object.
            Defaults to None.
            
    """
    contents: Optional[Any] = None
    name: Optional[str] = None

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
   
    def __post_init__(self) -> None:
        """Initializes instance."""
        # To support usage as a mixin, it is important to call other base class 
        # '__post_init__' methods, if they exist.
        with contextlib.suppress(AttributeError):
            super().__post_init__(*args, **kwargs) # type: ignore
        self.name = self.name or amos.namify(item = self)
                
    """ Dunder Methods """
    
    @classmethod
    def __subclasshook__(cls, subclass: Type[Any]) -> bool:
        """Returns whether 'subclass' is a virtual or real subclass.

        Args:
            subclass (Type[Any]): item to test as a subclass.

        Returns:
            bool: whether 'subclass' is a real or virtual subclass.
            
        """
        return check.is_node(item = subclass)
               
    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        """Returns whether 'instance' meets criteria to be a subclass.

        Args:
            instance (object): item to test as an instance.

        Returns:
            bool: whether 'instance' meets criteria to be a subclass.
            
        """
        return check.is_node(item = instance)
    
    def __hash__(self) -> int:
        """Makes Node hashable so that it can be used as a key in a dict.

        Rather than using the object ID, this method prevents two Nodes with
        the same name from being used in a composite object that uses a dict as
        its base storage type.
        
        Returns:
            int: hashable of 'name'.
            
        """
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        """Makes Node hashable so that it can be used as a key in a dict.

        Args:
            other (object): other object to test for equivalance.
            
        Returns:
            bool: whether 'name' is the same as 'other.name'.
            
        """
        try:
            return str(self.name) == str(other.name) # type: ignore
        except AttributeError:
            return str(self.name) == other

    def __ne__(self, other: object) -> bool:
        """Completes equality test dunder methods.

        Args:
            other (object): other object to test for equivalance.
           
        Returns:
            bool: whether 'name' is not the same as 'other.name'.
            
        """
        return not(self == other)


@dataclasses.dataclass
@runtime_checkable
class Nodes(amos.Bunch, Protocol):
    """Collection of Nodes.
    
    Nodes are not guaranteed to be in order. 

    Args:
        contents (Optional[Any]): any stored item(s). Defaults to None.
            
    """
    contents: Optional[Collection[Node]] = None
    
    """ Dunder Methods """ 
    
    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        """Returns whether 'instance' meets criteria to be a subclass.

        Args:
            instance (object): item to test as an instance.

        Returns:
            bool: whether 'instance' meets criteria to be a subclass.
            
        """
        return check.is_nodes(item = instance)
    