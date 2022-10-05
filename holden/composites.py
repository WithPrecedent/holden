"""
composites: base types of composite data structures
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
    Graph (base.Composite, Protocol): base class for graphs. All subclasses must 
        have 'connect' and 'disconnect' methods for changing edges between nodes.
                  
To Do:
    Integrate Kinds system when it is finished.

    
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

if TYPE_CHECKING:
    from . import forms  
    from . import traits     


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
        and all(base.is_node(item = i) for i in item.keys())
        and all(is_tree(item = i) for i in item.values())) 
       
    
@dataclasses.dataclass # type: ignore
@runtime_checkable
class Graph(base.Composite, Protocol):
    """Base class for graph data structures.
    
    Args:
        contents (Collection[Any]): stored collection of nodes and/or edges.
                                      
    """  
    contents: Collection[Any]
   
    """ Required Subclass Properties """

    @abc.abstractproperty
    def adjacency(self) -> forms.Adjacency:
        """Returns the stored graph as an Adjacency."""
        pass

    @abc.abstractproperty
    def edges(self) -> forms.Edges:
        """Returns the stored graph as an Edges."""
        pass
           
    @abc.abstractproperty
    def matrix(self) -> forms.Matrix:
        """Returns the stored graph as a Matrix."""
        pass

    @abc.abstractproperty
    def path(self) -> forms.Path:
        """Returns the stored graph as a Path."""
        pass

    @abc.abstractproperty
    def paths(self) -> forms.Paths:
        """Returns the stored graph as a Path."""
        pass

    """ Required Subclass Methods """
    
    @abc.abstractclassmethod
    def from_adjacency(cls, item: forms.Adjacency) -> Graph:
        """Creates a Graph instance from an Adjacency."""
        pass
    
    @abc.abstractclassmethod
    def from_edges(cls, item: forms.Edges) -> Graph:
        """Creates a Graph instance from an Edges."""
        pass
        
    @abc.abstractclassmethod
    def from_matrix(cls, item: forms.Matrix) -> Graph:
        """Creates a Graph instance from a Matrix."""
        pass
              
    @abc.abstractclassmethod
    def from_path(cls, item: forms.Path) -> Graph:
        """Creates a Graph instance from a Path."""
        pass
              
    @abc.abstractclassmethod
    def from_paths(cls, item: forms.Paths) -> Graph:
        """Creates a Graph instance from a Paths."""
        pass


@dataclasses.dataclass # type: ignore
class Path(traits.Directed, forms.Path, base.Graph):
    """Path, directed path graph.
    
    Args:
        contents (MutableSequence[base.Node]): list of stored Node 
            instances. Defaults to an empty list.
          
    """
    contents: MutableSequence[base.Node] = dataclasses.field(
        default_factory = list)

    """ Properties """
    
    @property
    def endpoint(self) -> base.Node:
        """Returns the endpoint(s) of the stored graph."""
        return self.contents[-1]
    
    @property
    def root(self) -> base.Node:
        """Returns the root(s) of the stored graph."""
        return self.contents[0]
    
    """ Public Methods """
   
    def walk(
        self, 
        start: Optional[base.Node] = None,
        stop: Optional[base.Node] = None, 
        path: Optional[Path] = None,
        return_paths: bool = False, 
        *args: Any, 
        **kwargs: Any) -> Path:
        """Returns path in the stored composite object from 'start' to 'stop'.
        
        Args:
            start (Optional[base.Node]): base.Node to start paths from. Defaults to None.
                If it is None, 'start' should be assigned to one of the roots
                of the base.
            stop (Optional[base.Node]): base.Node to stop paths. Defaults to None. If it 
                is None, 'start' should be assigned to one of the roots of the 
                base.
            path (Optional[Path]): a path from 'start' to 'stop'. 
                Defaults to None. This parameter is used by recursive methods 
                for determining a path.
            return_paths (bool): whether to return a Paths instance 
                (True) or a Path instance (False). Defaults to True.

        Returns:
            Path
                            
        """
        if start is None and stop is None:
            return self.contents
        start = start or self.root
        stop = stop or self.endpoint
        index_start = self.contents.index(start)
        index_stop = self.contents.index(stop) + 1
        if index_stop > len(self.contents):
            return self.contents[index_start:]
        else:
            return self.contents[index_start:index_stop]
     

@dataclasses.dataclass # type: ignore
class Tree(amos.Hybrid, traits.Directed, base.Composite, Protocol):
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
    def children(self) -> MutableSequence[base.Node]:
        """Returns child nodes of this Node."""
        return self.contents
    
    @children.setter
    def children(self, value: MutableSequence[base.Node]) -> None:
        """Sets child nodes of this Node."""
        if amos.is_sequence(value):
            self.contents = value
        else:
            self.contents = [value]
        return

    @property
    def endpoint(self) -> Union[base.Node, base.Nodes]:
        """Returns the endpoint(s) of the stored graph."""
        if not self.contents:
            return self
        else:
            return self.contents[0].endpoint
 
    @property
    def root(self) -> Union[base.Node, base.Nodes]:
        """Returns the root(s) of the stored graph."""
        if self.parent is None:
            return self
        else:
            return self.parent.root  
                                
    """ Dunder Methods """
        
    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        """Returns whether 'instance' meets criteria to be a subclass.

        Args:
            instance (object): item to test as an instance.

        Returns:
            bool: whether 'instance' meets criteria to be a subclass.
            
        """
        return is_tree(item = instance)

    def __missing__(self) -> Tree:
        """Returns an empty tree if one does not exist.

        Returns:
            Tree: an empty instance of Tree.
            
        """
        return self.__class__()

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
        