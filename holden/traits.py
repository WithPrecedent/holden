"""
traits: characteristics of graphs
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
    Directed (Protocol): a directed graph with unweighted edges.
        
To Do:

    
"""
from __future__ import annotations
import abc
import contextlib
import dataclasses
from typing import (
    Any, Optional, Protocol, runtime_checkable, Type, TYPE_CHECKING, Union)

import amos

if TYPE_CHECKING:
    from . import base
    
    
@dataclasses.dataclass
class Directed(Protocol):
    """Base class for directed graph data structures."""  
    
    """ Required Subclass Properties """
        
    @abc.abstractproperty
    def endpoint(self) -> Union[base.Node, base.Nodes]:
        """Returns the endpoint(s) of the stored graph."""
        pass
 
    @abc.abstractproperty
    def root(self) -> Union[base.Node, base.Nodes]:
        """Returns the root(s) of the stored graph."""
        pass
    
    @abc.abstractclassmethod
    def from_path(cls, item: Path) -> Path:
        """Creates a Paths instance from a Path."""
        return cls(contents = item)
    
    @abc.abstractclassmethod
    def from_paths(cls, item: Paths) -> Path:
        """Creates a Paths instance from a Paths."""
        return cls(contents = convert.paths_to_paths(item = item))
            
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def append(
        self, 
        item: Union[base.Node, base.Graph], 
        *args: Any, 
        **kwargs: Any) -> None:
        """Appends 'item' to the endpoint(s) of the stored graph.

        Args:
            item (Union[base.Node, base.Graph]): a Node or Graph to 
                add to the stored graph.
                
        """
        pass
    
    @abc.abstractmethod
    def prepend(
        self, 
        item: Union[base.Node, base.Graph], 
        *args: Any, 
        **kwargs: Any) -> None:
        """Prepends 'item' to the root(s) of the stored graph.

        Args:
            item (Union[base.Node, base.Graph]): a Node or Graph to 
                add to the stored graph.
                
        """
        pass
    
    @abc.abstractmethod
    def walk(
        self, 
        start: Optional[base.Node] = None,
        stop: Optional[base.Node] = None, 
        path: Optional[base.Path] = None,
        *args: Any, 
        **kwargs: Any) -> base.Path:
        """Returns path in the stored graph from 'start' to 'stop'.
        
        Args:
            start (Optional[base.Node]): Node to start paths from. 
                Defaults to None. If it is None, 'start' should be assigned to 
                'root'.
            stop (Optional[base.Node]): Node to stop paths at. 
                Defaults to None. If it is None, 'start' should be assigned to 
                'endpoint'.
            path (Optional[base.Path]): a path from 'start' to 'stop'. 
                Defaults to None. This parameter is used for recursively
                determining a path.

        Returns:
            base.Path: path(s) through the graph. 
                            
        """
        pass
    
    """ Dunder Methods """

    def __add__(self, other: base.Graph) -> None:
        """Adds 'other' to the stored graph using 'append'.

        Args:
            other (Union[base.Graph]): another graph to add to the current 
                one.
            
        """
        self.append(item = other)     
        return 

    def __radd__(self, other: base.Graph) -> None:
        """Adds 'other' to the stored graph using 'prepend'.

        Args:
            other (Union[base.Graph]): another graph to add to the current 
                one.
            
        """
        self.prepend(item = other)     
        return 

 
@dataclasses.dataclass
@runtime_checkable
class Labeled(Protocol):
    """Mixin for labeling parts of a composite object. 

    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a composite object.
            Defaults to None.
        contents (Optional[Any]): any stored item(s). Defaults to None.
            
    """
    name: Optional[str] = None
    contents: Optional[Any] = None
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes instance."""
        # To support usage as a mixin, it is important to call other base class 
        # '__post_init__' methods, if they exist.
        with contextlib.suppress(AttributeError):
            super().__post_init__(*args, **kwargs) # type: ignore
        self.name = self.name or self._namify()

    
    """ Private Methods """
    
    def _namify(self) -> str:
        """Returns str name of an instance.
        
        By default, if 'contents' is None, 'none' will be returned. Otherwise, 
        amos.namify will be called based on the value of the 'contents'
        attribute and its return value will be returned. 
        
        For different naming rules, subclasses should override this method, 
        which is automatically called when an instance is initialized.
        
        Returns:
            str: str label for part of a composite data structute.
            
        """
        if self.contents is None:
            return 'none'
        else:
            return amos.namify(item = self.contents)
                               
    """ Dunder Methods """
    
    def __hash__(self) -> int:
        """Makes Node hashable based on 'name.'
        
        Returns:
            int: hashable of 'name'.
            
        """
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        """Determines equality based on 'name' attribute.

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
        """Determines inequality based on 'name' attribute.

        Args:
            other (object): other object to test for equivalance.
           
        Returns:
            bool: whether 'name' is not the same as 'other.name'.
            
        """
        return not(self == other)
 