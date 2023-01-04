"""
traits: characteristics of graphs, edges, and nodes
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
    Directed (abc.ABC): a directed graph with unweighted edges.
    Exportable (abc.ABC):
    Fungible (abc.ABC):
    Labeled (abc.ABC):    
    Storage (abc.ABC):
    Weighted (abc.ABC):
    
To Do:

    
"""
from __future__ import annotations
import abc
from collections.abc import Collection, Hashable
import contextlib
import dataclasses
import pathlib
from typing import Any, Optional, Type, TYPE_CHECKING, Union

import camina

from . import base
from . import export

if TYPE_CHECKING:
    from . import composites
    from . import graphs
    
    
@dataclasses.dataclass
class Directed(abc.ABC):
    """Base class for directed graph data structures.
    
    Args:
        contents (Collection[Any]): stored collection of nodes and/or edges.
                                      
    """  
    contents: Collection[Any]
    
    """ Required Subclass Properties """
        
    @abc.abstractproperty
    def endpoint(self) -> Union[Hashable, Collection[Hashable]]:
        """Returns the endpoint(s) of the stored composite."""
        pass
 
    @abc.abstractproperty
    def root(self) -> Union[Hashable, Collection[Hashable]]:
        """Returns the root(s) of the stored composite."""
        pass
            
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def append(
        self, 
        item: Union[Hashable, base.Graph], 
        *args: Any, 
        **kwargs: Any) -> None:
        """Appends 'item' to the endpoint(s) of the stored composite.

        Args:
            item (Union[Hashable, base.Graph]): a Node or Graph to 
                add to the stored composite.
                
        """
        pass
    
    @abc.abstractmethod
    def prepend(
        self, 
        item: Union[Hashable, base.Graph], 
        *args: Any, 
        **kwargs: Any) -> None:
        """Prepends 'item' to the root(s) of the stored composite.

        Args:
            item (Union[Hashable, base.Graph]): a Node or Graph to 
                add to the stored composite.
                
        """
        pass
    
    @abc.abstractmethod
    def walk(
        self, 
        start: Optional[Hashable] = None,
        stop: Optional[Hashable] = None, 
        path: Optional[base.Path] = None,
        *args: Any, 
        **kwargs: Any) -> base.Path:
        """Returns path in the stored composite from 'start' to 'stop'.
        
        Args:
            start (Optional[Hashable]): Node to start paths from. 
                Defaults to None. If it is None, 'start' should be assigned to 
                'root'.
            stop (Optional[Hashable]): Node to stop paths at. 
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
        """Adds 'other' to the stored composite using 'append'.

        Args:
            other (Union[base.Graph]): another graph to add to the current 
                one.
            
        """
        self.append(item = other)     
        return 

    def __radd__(self, other: base.Graph) -> None:
        """Adds 'other' to the stored composite using 'prepend'.

        Args:
            other (Union[base.Graph]): another graph to add to the current 
                one.
            
        """
        self.prepend(item = other)     
        return 
   
   
@dataclasses.dataclass # type: ignore
class Exportable(abc.ABC):
    """Mixin for exporting graphs to other formats."""  
   
    """ Public Methods """
        
    def to_dot(
        self,
        path: Optional[str | pathlib.Path] = None,
        name: Optional[str] = None,
        settings: Optional[dict[str, Any]] = None) -> str:
        """Converts the stored composite to a dot format.

        Args:
            path (Optional[str | pathlib.Path]): path to export 'item' to. 
                Defaults to None.
            name (Optional[str]): name of 'item' to put in the dot str. Defaults 
                to None.
            settings (Optional[dict[str, Any]]): any global settings to add to 
                the dot graph. Defaults to None.

        Returns:
            str: composite object in graphviz dot format.

        """
        name = name or camina.namify(self)
        return export.to_dot(
            item = self, 
            path = path, 
            name = name, 
            settings = settings)
        
    
@dataclasses.dataclass # type: ignore
class Fungible(abc.ABC):
    """Mixin requirements for graphs that can be internally transformed."""  
   
    """ Properties """

    @property
    def adjacency(self) -> graphs.Adjacency:
        """Returns the stored composite as an Adjacency."""
        return base.transform(
            item = self, 
            output = 'adjacency', 
            raise_same_error = False)
        
    @property
    def edges(self) -> graphs.Edges:
        """Returns the stored composite as an Edges."""
        return base.transform(
            item = self, 
            output = 'edges', 
            raise_same_error = False)
           
    @property
    def matrix(self) -> graphs.Matrix:
        """Returns the stored composite as a Matrix."""
        return base.transform(
            item = self, 
            output = 'matrix', 
            raise_same_error = False)
     
    @property
    def parallel(self) -> composites.Parallel:
        """Returns the stored composite as a Parallel."""
        return base.transform(
            item = self, 
            output = 'parallel', 
            raise_same_error = False)
            
    @property
    def serial(self) -> composites.Serial:
        """Returns the stored composite as a Serial."""
        return base.transform(
            item = self, 
            output = 'serial', 
            raise_same_error = False)

    """ Class Methods """
    
    @classmethod
    def from_adjacency(cls, item: graphs.Adjacency) -> Fungible:
        """Creates a composite data structure from an Adjacency."""
        return cls(contents = base.transform(
            item = item, 
            output = base.classify(cls),
            raise_same_error = False))
    
    @classmethod
    def from_edges(cls, item: graphs.Edges) -> Fungible:
        """Creates a composite data structure from an Edges."""
        return cls(contents = base.transform(
            item = item, 
            output = base.classify(cls), 
            raise_same_error = False))
        
    @classmethod
    def from_matrix(cls, item: graphs.Matrix) -> Fungible:
        """Creates a composite data structure from a Matrix."""
        return cls(contents = base.transform(
            item = item, 
            output = base.classify(cls), 
            raise_same_error = False))
        
    @classmethod
    def from_parallel(cls, item: composites.Parallel) -> Fungible:
        """Creates a composite data structure from a Parallel."""
        return cls(contents = base.transform(
            item = item, 
            output = base.classify(cls), 
            raise_same_error = False)) 
        
    @classmethod
    def from_serial(cls, item: composites.Serial) -> Fungible:
        """Creates a composite data structure from a Serial."""
        return cls(contents = base.transform(
            item = item, 
            output = base.classify(cls), 
            raise_same_error = False))      
           
 
@dataclasses.dataclass
class Labeled(abc.ABC):
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
        camina.namify will be called based on the value of the 'contents'
        attribute and its return value will be returned. 
        
        For different naming rules, subclasses should override this method, 
        which is automatically called when an instance is initialized.
        
        Returns:
            str: str label for part of a composite data structute.
            
        """
        if self.contents is None:
            return 'none'
        else:
            return camina.namify(self.contents)
                               
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

    # def __ne__(self, other: object) -> bool:
    #     """Determines inequality based on 'name' attribute.

    #     Args:
    #         other (object): other object to test for equivalance.
           
    #     Returns:
    #         bool: whether 'name' is not the same as 'other.name'.
            
    #     """
    #     return not(self == other)
 

@dataclasses.dataclass
class Storage(abc.ABC):
    """Mixin for storage of nodes in a Library with the composite object.
    
    Args:
        contents (Collection[Any]): stored collection of nodes and/or edges.
                                      
    """  
    contents: Collection[Any]
    nodes: camina.Library = dataclasses.field(default_factory = camina.Library)
 

@dataclasses.dataclass
class Weighted(abc.ABC):
    """Mixin for weighted nodes.
    
    Args:
        weight (Optional[float]): the weight of the object. Defaults to 1.0.
                  
    """  
    weight: Optional[float] = 1.0   

    """ Dunder Methods """  
        
    def __len__(self) -> float:
        """Returns 'weight'.
        
        Returns:
            float: weight of the edge.
            
        """
        return self.weight