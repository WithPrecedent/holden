"""
graph: lightweight graph data structures
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
    Directed (Adjacency): a directed graph with unweighted edges.
        
To Do:
    Complete Network which will use an adjacency matrix for internal storage.
    
"""
from __future__ import annotations
import collections
from collections.abc import MutableMapping, MutableSequence, Sequence, Set
import copy
import dataclasses
import itertools
from typing import Any, Optional, Type, TYPE_CHECKING, Union

import amos

from . import base
from . import convert
from . import form
from . import trait
    

@dataclasses.dataclass # type: ignore
class Pipeline(trait.Directed, form.Linear, base.Graph):
    """Linear, directed pipeline graph.
    
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
        path: Optional[Pipeline] = None,
        return_pipelines: bool = False, 
        *args: Any, 
        **kwargs: Any) -> Pipeline:
        """Returns path in the stored composite object from 'start' to 'stop'.
        
        Args:
            start (Optional[base.Node]): base.Node to start paths from. Defaults to None.
                If it is None, 'start' should be assigned to one of the roots
                of the base.
            stop (Optional[base.Node]): base.Node to stop paths. Defaults to None. If it 
                is None, 'start' should be assigned to one of the roots of the 
                base.
            path (Optional[Pipeline]): a path from 'start' to 'stop'. 
                Defaults to None. This parameter is used by recursive methods 
                for determining a path.
            return_pipelines (bool): whether to return a Pipelines instance 
                (True) or a Pipeline instance (False). Defaults to True.

        Returns:
            Union[Pipeline, Pipelines]: path(s) through the 
                Composite object. If multiple paths are possible and 
                'return_pipelines' is False, this method should return a 
                Pipeline that includes all such paths appended to each other. If 
                multiple paths are possible and 'return_pipelines' is True, a 
                Pipelines instance with all of the paths should be returned. 
                Defaults to True.
                            
        """
        return self.contents
    
        
@dataclasses.dataclass
class System(form.Adjacency, trait.Directed, base.Graph):
    """Directed graph with unweighted edges stored as an adjacency list.
    
    Args:
        contents (MutableMapping[base.Node, Set[base.Node]]): keys 
            are nodes and values are sets of nodes (or hashable representations 
            of nodes). Defaults to a defaultdict that has a set for its value 
            format.
                  
    """  
    contents: MutableMapping[base.Node, Set[base.Node]] = (
        dataclasses.field(
            default_factory = lambda: collections.defaultdict(set)))
    
    """ Properties """

    @property
    def endpoint(self) -> Union[base.Node, base.Nodes]:
        """Returns the endpoint(s) of the stored graph."""
        return {k for k in self.contents.keys() if not self.contents[k]}
                    
    @property
    def root(self) -> Union[base.Node, base.Nodes]:
        """Returns the root(s) of the stored graph."""
        stops = list(itertools.chain.from_iterable(self.contents.values()))
        return {k for k in self.contents.keys() if k not in stops}
                      
    @property
    def nodes(self) -> set[base.Node]:
        """Returns all stored nodes in a set."""
        return set(self.contents.keys())

    @property
    def paths(self) -> base.Nodes:
        """Returns all paths through the stored as a list of nodes."""
        return self._find_all_paths(starts = self.root, stops = self.endpoint)
    
    @property
    def pipeline(self) -> base.Pipeline:
        """Returns stored graph as a pipeline."""
        pipeline = []
        for pipe in self.pipelines.values():
            pipeline.extend(pipe)
        return base.Pipeline(contents = pipeline)
    
    @property
    def pipelines(self) -> base.Pipelines:
        """Returns stored graph as pipelines."""
        all_paths = self.paths
        instances = [base.Pipeline(contents = p) for p in all_paths]
        pipelines = base.Pipelines()
        for instance in instances:
            pipelines.add(instance, name = 'path')
        return pipelines
            
    @property
    def tree(self) -> tree.Tree:
        """Returns the stored composite object as a tree.Tree."""
        raise NotImplementedError

    """ Class Methods """
    
    @classmethod
    def from_nodes(cls, item: base.Nodes) -> System:
        """Creates a System instance from a Nodes."""
        new_contents = convert.pipeline_to_adjacency(item = item)
        return cls(contents = new_contents)

    @classmethod
    def from_pipeline(cls, item: base.Pipeline) -> System:
        """Creates a System instance from a Pipeline."""
        new_contents = convert.pipeline_to_adjacency(item = item)
        return cls(contents = new_contents)
    
    @classmethod
    def from_pipelines(cls, item: base.Pipelines) -> System:
        """Creates a System instance from a Pipeline."""
        new_contents = convert.pipelines_to_adjacency(item = item)
        return cls(contents = new_contents)

    @classmethod
    def from_tree(cls, item: tree.Tree) -> System:
        """Creates a System instance from a Tree."""
        raise NotImplementedError
             
    """ Public Methods """

    def add(
        self, 
        node: base.Node,
        ancestors: base.Nodes = None,
        descendants: base.Nodes = None) -> None:
        """Adds 'node' to the stored graph.
        
        Args:
            node (base.Node): a node to add to the stored graph.
            ancestors (base.Nodes): node(s) from which 'node' should be 
                connected.
            descendants (base.Nodes): node(s) to which 'node' should be 
                connected.

        Raises:
            KeyError: if some nodes in 'descendants' or 'ancestors' are not in 
                the stored graph.
                
        """
        if descendants is None:
            self.contents[node] = set()
        # elif utilities.is_property(item = descendants, instance = self):
        #     self.contents = set(getattr(self, descendants))
        else:
            descendants = list(amos.iterify(item = descendants))
            descendants = [amos.namify(item = n) for n in descendants]
            missing = [n for n in descendants if n not in self.contents]
            if missing:
                raise KeyError(
                    f'descendants {str(missing)} are not in '
                    f'{self.__class__.__name__}')
            else:
                self.contents[node] = set(descendants)
        if ancestors is not None:  
            # if utilities.is_property(item = ancestors, instance = self):
            #     start = list(getattr(self, ancestors))
            # else:
            ancestors = list(amos.iterify(item = ancestors))
            missing = [n for n in ancestors if n not in self.contents]
            if missing:
                raise KeyError(
                    f'ancestors {str(missing)} are not in '
                    f'{self.__class__.__name__}')
            for start in ancestors:
                if node not in self[start]:
                    self.connect(start = start, stop = node)                 
        return 

    def append(self, item: base.Graph) -> None:
        """Appends 'item' to the endpoints of the stored graph.

        Appending creates an edge between every endpoint of this instance's
        stored graph and the every root of 'item'.

        Args:
            item (base.Graph): another Graph, 
                an adjacency list, an edge list, an adjacency matrix, or one or
                more nodes.
            
        Raises:
            TypeError: if 'item' is neither a Graph, Adjacency, Edges, Matrix,
                or base.Nodes type.
                
        """
        if isinstance(item, base.Graph):
            current_endpoints = list(self.endpoint)
            new_graph = self.create(item = item)
            self.merge(item = new_graph)
            for endpoint in current_endpoints:
                for root in new_graph.root:
                    self.connect(start = endpoint, stop = root)
        else:
            raise TypeError('item must be a Node, Nodes, or Composite type')
        return
  
    def connect(self, start: base.Node, stop: base.Node) -> None:
        """Adds an edge from 'start' to 'stop'.

        Args:
            start (base.Node): name of node for edge to start.
            stop (base.Node): name of node for edge to stop.
            
        Raises:
            ValueError: if 'start' is the same as 'stop'.
            
        """
        if start == stop:
            raise ValueError(
                'The start of an edge cannot be the same as the '
                'stop in a System because it is acyclic')
        elif start not in self:
            self.add(node = start)
        elif stop not in self:
            self.add(node = stop)
        if stop not in self.contents[start]:
            self.contents[start].add(amos.namify(item = stop))
        return

    def delete(self, node: base.Node) -> None:
        """Deletes node from graph.
        
        Args:
            node (base.Node): node to delete from 'contents'.
        
        Raises:
            KeyError: if 'node' is not in 'contents'.
            
        """
        try:
            del self.contents[node]
        except KeyError:
            raise KeyError(f'{node} does not exist in the graph')
        self.contents = {k: v.discard(node) for k, v in self.contents.items()}
        return

    def disconnect(self, start: base.Node, stop: base.Node) -> None:
        """Deletes edge from graph.

        Args:
            start (base.Node): starting node for the edge to delete.
            stop (base.Node): ending node for the edge to delete.
        
        Raises:
            KeyError: if 'start' is not a node in the stored graph..

        """
        try:
            self.contents[start].discard(stop)
        except KeyError:
            raise KeyError(f'{start} does not exist in the graph')
        return

    def merge(self, item: base.Graph) -> None:
        """Adds 'item' to this Graph.

        This method is roughly equivalent to a dict.update, just adding the
        new keys and values to the existing graph. It converts 'item' to an 
        adjacency list that is then added to the existing 'contents'.
        
        Args:
            item (base.Graph): another Graph, an adjacency 
                list, an edge list, an adjacency matrix, or one or more nodes.
            
        Raises:
            TypeError: if 'item' is neither a System, Adjacency, 
                Edges, Matrix, or base.Nodes type.
            
        """
        if isinstance(item, System):
            adjacency = item.adjacency
        elif isinstance(item, form.Adjacency):
            adjacency = item
        elif isinstance(item, form.Edges):
            adjacency = convert.edges_to_adjacency(item = item)
        elif isinstance(item, form.Matrix):
            adjacency = convert.matrix_to_adjacency(item = item)
        elif isinstance(item, (list, tuple, set)):
            adjacency = convert.pipeline_to_adjacency(item = item)
        elif isinstance(item, base.Node):
            adjacency = {item: set()}
        else:
            raise TypeError('item must be a Node, Nodes, or Composite type')
        self.contents.update(adjacency)
        return

    def prepend(self, item: base.Graph) -> None:
        """Prepends 'item' to the roots of the stored graph.

        Prepending creates an edge between every endpoint of 'item' and every
        root of this instance;s stored graph.

        Args:
            item (base.Graph): another Graph, an adjacency list, an 
                edge list, an adjacency matrix, or one or more nodes.
            
        Raises:
            TypeError: if 'item' is neither a System, Adjacency, Edges, Matrix, 
                or base.Nodes type.
                
        """
        if isinstance(item, base.Graph):
            current_roots = list(self.root)
            new_graph = self.create(item = item)
            self.merge(item = new_graph)
            for root in current_roots:
                for endpoint in new_graph.endpoints:
                    self.connect(start = endpoint, stop = root)
        else:
            raise TypeError(
                'item must be a System, Adjacency, Edges, Matrix, Pipeline, '
                'Pipelines, or Node type')
        return
      
    def subset(
        self, 
        include: Union[Any, Sequence[Any]] = None,
        exclude: Union[Any, Sequence[Any]] = None) -> System:
        """Returns a new System without a subset of 'contents'.
        
        All edges will be removed that include any nodes that are not part of
        the new subgraph.
        
        Any extra attributes that are part of a System (or a subclass) will be
        maintained in the returned subgraph.

        Args:
            include (Union[Any, Sequence[Any]]): nodes which should be included
                with any applicable edges in the new subgraph.
            exclude (Union[Any, Sequence[Any]]): nodes which should not be 
                included with any applicable edges in the new subgraph.

        Returns:
           System: with only key/value pairs with keys not in 'subset'.

        """
        if include is None and exclude is None:
            raise ValueError('Either include or exclude must not be None')
        else:
            if include:
                excludables = [k for k in self.contents if k not in include]
            else:
                excludables = []
            excludables.extend([i for i in self.contents if i in exclude])
            new_graph = copy.deepcopy(self)
            for node in amos.iterify(item = excludables):
                new_graph.delete(node = node)
        return new_graph
    
    def walk(
        self, 
        start: base.Node,
        stop: base.Node, 
        path: Optional[base.Pipeline] = None) -> base.Pipeline:
        """Returns all paths in graph from 'start' to 'stop'.

        The code here is adapted from: https://www.python.org/doc/essays/graphs/
        
        Args:
            start (base.Node): node to start paths from.
            stop (base.Node): node to stop paths.
            path (Pipeline): a path from 'start' to 'stop'. Defaults 
                to an empty list. 

        Returns:
            Pipeline: a list of possible paths (each path is a list 
                nodes) from 'start' to 'stop'.
            
        """
        if path is None:
            path = []
        path = path + [start]
        if start == stop:
            return [path]
        if start not in self.contents:
            return []
        paths = []
        for node in self.contents[start]:
            if node not in path:
                new_paths = self.walk(
                    start = node, 
                    stop = stop, 
                    path = path)
                for new_path in new_paths:
                    paths.append(new_path)
        return paths

    """ Private Methods """

    def _find_all_paths(
        self, 
        starts: base.Nodes, 
        stops: base.Nodes) -> base.Pipeline:
        """Returns all paths between 'starts' and 'stops'.

        Args:
            start (base.Nodes): starting point(s) for paths through the 
                System.
            ends (base.Nodes): ending point(s) for paths through the 
                System.

        Returns:
            base.Pipeline: list of all paths through the System from all 
                'starts' to all 'ends'.
            
        """
        all_paths = []
        for start in amos.iterify(item = starts):
            for end in amos.iterify(item = stops):
                paths = self.walk(start = start, stop = end)
                if paths:
                    if all(isinstance(path, base.Node) for path in paths):
                        all_paths.append(paths)
                    else:
                        all_paths.extend(paths)
        return all_paths


    
# @dataclasses.dataclass
# class Network(Graph):
#     """composites class for undirected graphs with unweighted edges.
    
#     Graph stores a directed acyclic graph (DAG) as an adjacency list. Despite 
#     being called an adjacency "list," the typical and most efficient way to 
#     store one is using a python dict. a piles Graph inherits from a Dictionary 
#     in order to allow use of its extra functionality over a plain dict.
    
#     Graph supports '+' and '+=' to be used to join two piles Graph instances. A
#     properly formatted adjacency list could also be the added object.
    
#     Graph internally supports autovivification where a list is created as a 
#     value for a missing key. This means that a Graph need not inherit from 
#     defaultdict.
    
#     Args:
#         contents (Adjacency): an adjacency list where the keys are nodes and the 
#             values are nodes which the key is connected to. Defaults to an empty 
#             dict.
                  
#     """  
#     contents: Matrix = dataclasses.field(default_factory = dict)
    
#     """ Properties """

#     @property
#     def adjacency(self) -> Adjacency:
#         """Returns the stored graph as an adjacency list."""
#         return matrix_to_adjacency(item = self.contents)

#     @property
#     def breadths(self) -> Pipeline:
#         """Returns all paths through the Graph using breadth-first search.
        
#         Returns:
#             Pipeline: returns all paths from 'roots' to 'endpoints' in a list 
#                 of lists of nodes.
                
#         """
#         return self._find_all_paths(
#             starts = self.root, 
#             ends = self.endpoint,
#             depth_first = False)

#     @property
#     def depths(self) -> Pipeline:
#         """Returns all paths through the Graph using depth-first search.
        
#         Returns:
#             Pipeline: returns all paths from 'roots' to 'endpoints' in a list 
#                 of lists of nodes.
                
#         """
#         return self._find_all_paths(starts = self.root, 
#                                     ends = self.endpoint,
#                                     depth_first = True)
     
#     @property
#     def edges(self) -> Edges:
#         """Returns the stored graph as an edge list."""
#         return adjacency_to_edges(item = self.contents)

#     @property
#     def endpoints(self) -> list[base.Node]:
#         """Returns a list of endpoint nodes in the stored graph.."""
#         return [k for k in self.contents.keys() if not self.contents[k]]

#     @property
#     def matrix(self) -> Matrix:
#         """Returns the stored graph as an adjacency matrix."""
#         return adjacency_to_matrix(item = self.contents)
                      
#     @property
#     def nodes(self) -> dict[str, base.Node]:
#         """Returns a dict of node names as keys and nodes as values.
        
#         Because Graph allows various base.Node objects to be used as keys,
#         including the base.Nodes class, there isn't an obvious way to access already
#         stored nodes. This property creates a new dict with str keys derived
#         from the nodes (looking first for a 'name' attribute) so that a user
#         can access a node. 
        
#         This property is not needed if the stored nodes are all strings.
        
#         Returns:
#             Dict[str, base.Node]: keys are the name or has of nodes and the 
#                 values are the nodes themselves.
            
#         """
#         return {self.trait.namify(item = n): n for n in self.contents.keys()}
  
#     @property
#     def roots(self) -> list[base.Node]:
#         """Returns root nodes in the stored graph..

#         Returns:
#             list[base.Node]: root nodes.
            
#         """
#         stops = list(itertools.chain.from_iterable(self.contents.values()))
#         return [k for k in self.contents.keys() if k not in stops]
    
#     """ Class Methods """
    
#     @classmethod
#     def create(cls, item: Union[Adjacency, Edges, Matrix]) -> Graph:
#         """Creates an instance of a Graph from 'item'.
        
#         Args:
#             item (Union[Adjacency, Edges, Matrix]): an adjacency list, 
#                 adjacency matrix, or edge list which can used to create the
#                 stored graph.
                
#         Returns:
#             Graph: a Graph instance created compositesd on 'item'.
                
#         """
#         if is_adjacency_list(item = item):
#             return cls.from_adjacency(adjacency = item)
#         elif is_adjacency_matrix(item = item):
#             return cls.from_matrix(matrix = item)
#         elif is_edge_list(item = item):
#             return cls.from_adjacency(edges = item)
#         else:
#             raise TypeError(
#                 f'create requires item to be an adjacency list, adjacency '
#                 f'matrix, or edge list')
           
#     @classmethod
#     def from_adjacency(cls, adjacency: Adjacency) -> Graph:
#         """Creates a Graph instance from an adjacency list.
        
#         'adjacency' should be formatted with nodes as keys and values as lists
#         of names of nodes to which the node in the key is connected.

#         Args:
#             adjacency (Adjacency): adjacency list used to 
#                 create a Graph instance.

#         Returns:
#             Graph: a Graph instance created compositesd on 'adjacent'.
              
#         """
#         return cls(contents = adjacency)
    
#     @classmethod
#     def from_edges(cls, edges: Edges) -> Graph:
#         """Creates a Graph instance from an edge list.

#         'edges' should be a list of tuples, where the first item in the tuple
#         is the node and the second item is the node (or name of node) to which
#         the first item is connected.
        
#         Args:
#             edges (Edges): Edge list used to create a Graph 
#                 instance.
                
#         Returns:
#             Graph: a Graph instance created compositesd on 'edges'.

#         """
#         return cls(contents = edges_to_adjacency(item = edges))
    
#     @classmethod
#     def from_matrix(cls, matrix: Matrix) -> Graph:
#         """Creates a Graph instance from an adjacency matrix.

#         Args:
#             matrix (Matrix): adjacency matrix used to create a Graph instance. 
#                 The values in the matrix should be 1 (indicating an edge) and 0 
#                 (indicating no edge).
 
#         Returns:
#             Graph: a Graph instance created compositesd on 'matrix'.
                        
#         """
#         return cls(contents = matrix_to_adjacency(item = matrix))
    
#     @classmethod
#     def from_pipeline(cls, pipeline: Pipeline) -> Graph:
#         """Creates a Graph instance from a Pipeline.

#         Args:
#             pipeline (Pipeline): serial pipeline used to create a Graph
#                 instance.
 
#         Returns:
#             Graph: a Graph instance created compositesd on 'pipeline'.
                        
#         """
#         return cls(contents = pipeline_to_adjacency(item = pipeline))
       
#     """ Public Methods """
    
#     def add(self, 
#             node: base.Node,
#             ancestors: base.Nodes = None,
#             descendants: base.Nodes = None) -> None:
#         """Adds 'node' to 'contents' with no corresponding edges.
        
#         Args:
#             node (base.Node): a node to add to the stored graph.
#             ancestors (base.Nodes): node(s) from which node should be connected.
#             descendants (base.Nodes): node(s) to which node should be connected.

#         """
#         if descendants is None:
#             self.contents[node] = []
#         elif descendants in self:
#             self.contents[node] = amos.iterify(item = descendants)
#         else:
#             missing = [n for n in descendants if n not in self.contents]
#             raise KeyError(f'descendants {missing} are not in the stored graph.')
#         if ancestors is not None:  
#             if (isinstance(ancestors, base.Node) and ancestors in self
#                     or (isinstance(ancestors, (list, tuple, set)) 
#                         and all(isinstance(n, base.Node) for n in ancestors)
#                         and all(n in self.contents for n in ancestors))):
#                 start = ancestors
#             elif (hasattr(self.__class__, ancestors) 
#                     and isinstance(getattr(type(self), ancestors), property)):
#                 start = getattr(self, ancestors)
#             else:
#                 missing = [n for n in ancestors if n not in self.contents]
#                 raise KeyError(f'ancestors {missing} are not in the stored graph.')
#             for starting in amos.iterify(item = start):
#                 if node not in [starting]:
#                     self.connect(start = starting, stop = node)                 
#         return 

#     def append(self, 
#                item: Union[Graph, Adjacency, Edges, Matrix, base.Nodes]) -> None:
#         """Adds 'item' to this Graph.

#         Combining creates an edge between every endpoint of this instance's
#         Graph and the every root of 'item'.

#         Args:
#             item (Union[Graph, Adjacency, Edges, Matrix, base.Nodes]): another 
#                 Graph to join with this one, an adjacency list, an edge list, an
#                 adjacency matrix, or base.Nodes.
            
#         Raises:
#             TypeError: if 'item' is neither a Graph, Adjacency, Edges, Matrix,
#                 or base.Nodes type.
            
#         """
#         if isinstance(item, Graph):
#             if self.contents:
#                 current_endpoints = self.endpoint
#                 self.contents.update(item.contents)
#                 for endpoint in current_endpoints:
#                     for root in item.root:
#                         self.connect(start = endpoint, stop = root)
#             else:
#                 self.contents = item.contents
#         elif isinstance(item, Adjacency):
#             self.append(item = self.from_adjacency(adjacecny = item))
#         elif isinstance(item, Edges):
#             self.append(item = self.from_edges(edges = item))
#         elif isinstance(item, Matrix):
#             self.append(item = self.from_matrix(matrix = item))
#         elif isinstance(item, base.Nodes):
#             if isinstance(item, (list, tuple, set)):
#                 new_graph = Graph()
#                 edges = more_itertools.windowed(item, 2)
#                 for edge_pair in edges:
#                     new_graph.add(node = edge_pair[0], descendants = edge_pair[1])
#                 self.append(item = new_graph)
#             else:
#                 self.add(node = item)
#         else:
#             raise TypeError(
#                 'item must be a Graph, Adjacency, Edges, Matrix, or base.Nodes '
#                 'type')
#         return
  
#     def connect(self, start: base.Node, stop: base.Node) -> None:
#         """Adds an edge from 'start' to 'stop'.

#         Args:
#             start (base.Node): name of node for edge to start.
#             stop (base.Node): name of node for edge to stop.
            
#         Raises:
#             ValueError: if 'start' is the same as 'stop'.
            
#         """
#         if start == stop:
#             raise ValueError(
#                 'The start of an edge cannot be the same as the stop')
#         else:
#             if stop not in self.contents:
#                 self.add(node = stop)
#             if start not in self.contents:
#                 self.add(node = start)
#             if stop not in self.contents[start]:
#                 self.contents[start].append(self.trait.namify(item = stop))
#         return

#     def delete(self, node: base.Node) -> None:
#         """Deletes node from graph.
        
#         Args:
#             node (base.Node): node to delete from 'contents'.
        
#         Raises:
#             KeyError: if 'node' is not in 'contents'.
            
#         """
#         try:
#             del self.contents[node]
#         except KeyError:
#             raise KeyError(f'{node} does not exist in the graph')
#         self.contents = {
#             k: v.remove(node) for k, v in self.contents.items() if node in v}
#         return

#     def disconnect(self, start: base.Node, stop: base.Node) -> None:
#         """Deletes edge from graph.

#         Args:
#             start (base.Node): starting node for the edge to delete.
#             stop (base.Node): ending node for the edge to delete.
        
#         Raises:
#             KeyError: if 'start' is not a node in the stored graph..
#             ValueError: if 'stop' does not have an edge with 'start'.

#         """
#         try:
#             self.contents[start].remove(stop)
#         except KeyError:
#             raise KeyError(f'{start} does not exist in the graph')
#         except ValueError:
#             raise ValueError(f'{stop} is not connected to {start}')
#         return

#     def merge(self, item: Union[Graph, Adjacency, Edges, Matrix]) -> None:
#         """Adds 'item' to this Graph.

#         This method is roughly equivalent to a dict.update, just adding the
#         new keys and values to the existing graph. It converts the supported
#         formats to an adjacency list that is then added to the existing 
#         'contents'.
        
#         Args:
#             item (Union[Graph, Adjacency, Edges, Matrix]): another Graph to 
#                 add to this one, an adjacency list, an edge list, or an
#                 adjacency matrix.
            
#         Raises:
#             TypeError: if 'item' is neither a Graph, Adjacency, Edges, or 
#                 Matrix type.
            
#         """
#         if isinstance(item, Graph):
#             item = item.contents
#         elif isinstance(item, Adjacency):
#             pass
#         elif isinstance(item, Edges):
#             item = self.from_edges(edges = item).contents
#         elif isinstance(item, Matrix):
#             item = self.from_matrix(matrix = item).contents
#         else:
#             raise TypeError(
#                 'item must be a Graph, Adjacency, Edges, or Matrix type to '
#                 'update')
#         self.contents.update(item)
#         return
  
#     def subgraph(self, 
#                  include: Union[Any, Sequence[Any]] = None,
#                  exclude: Union[Any, Sequence[Any]] = None) -> Graph:
#         """Returns a new Graph without a subset of 'contents'.
        
#         All edges will be removed that include any nodes that are not part of
#         the new subgraph.
        
#         Any extra attributes that are part of a Graph (or a subclass) will be
#         maintained in the returned subgraph.

#         Args:
#             include (Union[Any, Sequence[Any]]): nodes which should be included
#                 with any applicable edges in the new subgraph.
#             exclude (Union[Any, Sequence[Any]]): nodes which should not be 
#                 included with any applicable edges in the new subgraph.

#         Returns:
#             Graph: with only key/value pairs with keys not in 'subset'.

#         """
#         if include is None and exclude is None:
#             raise ValueError('Either include or exclude must not be None')
#         else:
#             if include:
#                 excludables = [k for k in self.contents if k not in include]
#             else:
#                 excludables = []
#             excludables.extend([i for i in self.contents if i not in exclude])
#             new_graph = copy.deepcopy(self)
#             for node in amos.iterify(item = excludables):
#                 new_graph.delete(node = node)
#         return new_graph

#     def walk(self, 
#              start: base.Node, 
#              stop: base.Node, 
#              path: Pipeline = None,
#              depth_first: bool = True) -> Pipeline:
#         """Returns all paths in graph from 'start' to 'stop'.

#         The code here is adapted from: https://www.python.org/doc/essays/graphs/
        
#         Args:
#             start (base.Node): node to start paths from.
#             stop (base.Node): node to stop paths.
#             path (Pipeline): a path from 'start' to 'stop'. Defaults to an 
#                 empty list. 

#         Returns:
#             Pipeline: a list of possible paths (each path is a list 
#                 nodes) from 'start' to 'stop'.
            
#         """
#         if path is None:
#             path = []
#         path = path + [start]
#         if start == stop:
#             return [path]
#         if start not in self.contents:
#             return []
#         if depth_first:
#             method = self._depth_first_search
#         else:
#             method = self._breadth_first_search
#         paths = []
#         for node in self.contents[start]:
#             if node not in path:
#                 new_paths = self.walk(
#                     start = node, 
#                     stop = stop, 
#                     path = path,
#                     depth_first = depth_first)
#                 for new_path in new_paths:
#                     paths.append(new_path)
#         return paths

#     def _all_paths_bfs(self, start, stop):
#         """

#         """
#         if start == stop:
#             return [start]
#         visited = {start}
#         queue = collections.deque([(start, [])])
#         while queue:
#             current, path = queue.popleft()
#             visited.add(current)
#             for connected in self[current]:
#                 if connected == stop:
#                     return path + [current, connected]
#                 if connected in visited:
#                     continue
#                 queue.append((connected, path + [current]))
#                 visited.add(connected)   
#         return []

#     def _breadth_first_search(self, node: base.Node) -> Pipeline:
#         """Returns a breadth first search path through the Graph.

#         Args:
#             node (base.Node): node to start the search from.

#         Returns:
#             Pipeline: nodes in a path through the Graph.
            
#         """        
#         visited = set()
#         queue = [node]
#         while queue:
#             vertex = queue.pop(0)
#             if base. not in visited:
#                 visited.add(vertex)
#                 queue.extend(set(self[vertex]) - visited)
#         return list(visited)
       
#     def _depth_first_search(self, 
#         node: base.Node, 
#         visited: list[base.Node]) -> Pipeline:
#         """Returns a depth first search path through the Graph.

#         Args:
#             node (base.Node): node to start the search from.
#             visited (list[base.Node]): list of visited nodes.

#         Returns:
#             Pipeline: nodes in a path through the Graph.
            
#         """  
#         if node not in visited:
#             visited.append(node)
#             for edge in self[node]:
#                 self._depth_first_search(node = edge, visited = visited)
#         return visited
  
#     def _find_all_paths(self, 
#         starts: Union[base.Node, Sequence[base.Node]],
#         stops: Union[base.Node, Sequence[base.Node]],
#         depth_first: bool = True) -> Pipeline:
#         """[summary]

#         Args:
#             start (Union[base.Node, Sequence[base.Node]]): starting points for 
#                 paths through the Graph.
#             ends (Union[base.Node, Sequence[base.Node]]): endpoints for paths 
#                 through the Graph.

#         Returns:
#             Pipeline: list of all paths through the Graph from all
#                 'starts' to all 'ends'.
            
#         """
#         all_paths = []
#         for start in amos.iterify(item = starts):
#             for end in amos.iterify(item = stops):
#                 paths = self.walk(
#                     start = start, 
#                     stop = end,
#                     depth_first = depth_first)
#                 if paths:
#                     if all(isinstance(path, base.Node) for path in paths):
#                         all_paths.append(paths)
#                     else:
#                         all_paths.extend(paths)
#         return all_paths
            
#     """ Dunder Methods """

#     def __add__(self, other: Graph) -> None:
#         """Adds 'other' Graph to this Graph.

#         Adding another graph uses the 'merge' method. Read that method's 
#         docstring for further details about how the graphs are added 
#         together.
        
#         Args:
#             other (Graph): a second Graph to join with this one.
            
#         """
#         self.merge(graph = other)        
#         return

#     def __iadd__(self, other: Graph) -> None:
#         """Adds 'other' Graph to this Graph.

#         Adding another graph uses the 'merge' method. Read that method's 
#         docstring for further details about how the graphs are added 
#         together.
        
#         Args:
#             other (Graph): a second Graph to join with this one.
            
#         """
#         self.merge(graph = other)        
#         return

#     def __contains__(self, nodes: base.Nodes) -> bool:
#         """[summary]

#         Args:
#             nodes (base.Nodes): [description]

#         Returns:
#             bool: [description]
            
#         """
#         if isinstance(nodes, (list, tuple, set)):
#             return all(n in self.contents for n in nodes)
#         elif isinstance(nodes, base.Node):
#             return nodes in self.contents
#         else:
#             return False   
        
#     def __getitem__(self, key: base.Node) -> Any:
#         """Returns value for 'key' in 'contents'.

#         Args:
#             key (base.Node): key in 'contents' for which a value is sought.

#         Returns:
#             Any: value stored in 'contents'.

#         """
#         return self.contents[key]

#     def __setitem__(self, key: base.Node, value: Any) -> None:
#         """sets 'key' in 'contents' to 'value'.

#         Args:
#             key (base.Node): key to set in 'contents'.
#             value (Any): value to be paired with 'key' in 'contents'.

#         """
#         self.contents[key] = value
#         return

#     def __delitem__(self, key: base.Node) -> None:
#         """Deletes 'key' in 'contents'.

#         Args:
#             key (base.Node): key in 'contents' to delete the key/value pair.

#         """
#         del self.contents[key]
#         return

#     def __missing__(self) -> list:
#         """Returns an empty list when a key doesn't exist.

#         Returns:
#             list: an empty list.

#         """
#         return []
    
#     def __str__(self) -> str:
#         """Returns prettier summary of the Graph.

#         Returns:
#             str: a formatted str of class information and the contained 
#                 adjacency list.
            
#         """
#         new_line = '\n'
#         tab = '    '
#         summary = [f'{new_line}piles {self.__class__.__name__}']
#         summary.append('adjacency list:')
#         for node, edges in self.contents.items():
#             summary.append(f'{tab}{node}: {str(edges)}')
#         return new_line.join(summary) 

# Changer: Type[Any] = Callable[[base.Node], None]
# Finder: Type[Any] = Callable[[base.Node], Optional[base.Node]]




# @dataclasses.dataclass # type: ignore
# class Categorizer(Tree):
#     """composites class for an tree data structures.
        
#     Args:
#         contents (MutableSequence[base.Node]): list of stored Node 
#             instances (including other Trees). Defaults to an empty list.
#         name (Optional[str]): name of Tree node which should match a parent 
#             tree's key name corresponding to this Tree node. All nodes in a Tree
#             must have unique names. The name is used to make all Tree nodes 
#             hashable and capable of quick comparison. Defaults to None, but it
#             should not be left as None when added to a Tree.
#         parent (Optional[Tree]): parent Tree, if any. Defaults to None.
        
#     """
#     contents: MutableSequence[base.Node] = dataclasses.field(
#         default_factory = list)
#     name: Optional[str] = None
#     parent: Optional[Tree] = None 
    
#     """ Properties """
        
#     @property
#     def branches(self) -> list[Tree]:
#         """Returns all stored Tree nodes in a list."""
#         return self.nodes - self.leaves
    
#     @property
#     def children(self) -> dict[str, base.Node]:
#         """[summary]

#         Returns:
#             dict[str, base.Node]: [description]
#         """
#         return self.contents
    
#     @property
#     def is_leaf(self) -> bool:
#         """[summary]

#         Returns:
#             bool: [description]
#         """
#         return not self.children
    
#     @property
#     def is_root(self) -> bool:
#         """[summary]

#         Returns:
#             bool: [description]
#         """
#         return self.parent is None
    
#     @property
#     def leaves(self) -> list[base.Node]:
#         """Returns all stored leaf nodes in a list."""
#         matches = []
#         for node in self.nodes:
#             if not hasattr(node, 'is_leaf') or node.is_leaf:
#                 matches.append(node)
#         return matches
     
#     @property
#     def nodes(self) -> list[base.Node]:
#         """Returns all stored nodes in a list."""
#         return depth_first_search(tree = self.contents)

#     @property
#     def root(self) -> Tree:
#         """
#         """
#         composites = [n.is_root for n in self.nodes]
#         if len(composites) > 1:
#             raise ValueError('The tree is broken - it has more than 1 root')
#         elif len(composites) == 0:
#             raise ValueError('The tree is broken - it has no root')
#         else:
#             return composites[0]
    
#     """ Public Methods """
    
#     def add(
#         self, 
#         item: Union[base.Node, Sequence[base.Node]],
#         parent: Optional[str] = None) -> None:
#         """Adds node(s) in item to 'contents'.
        
#         In adding the node(s) to the stored tree, the 'parent' attribute for the
#         node(s) is set to this Tree instance.

#         Args:
#             item (Union[base.Node, Sequence[base.Node]]): node(s) to 
#                 add to the 'contents' attribute.

#         Raises:
#             ValueError: if 'item' already is in the stored tree or if 'parent'
#                 is not in the tree.
                            
#         """
#         if parent is None:
#             parent_node = self
#         else:
#             parent_node = self.get(item = parent)
#         if parent_node is None:
#             raise ValueError(
#                 f'Cannot add {item.name} because parent node {parent} is not '
#                 f'in the tree')
#         if isinstance(item, Sequence) and not isinstance(item, str):
#             for node in item:
#                 self.add(item = node)
#         elif item in self.nodes:
#             raise ValueError(
#                 f'Cannot add {item.name} because it is already in the tree')
#         else:
#             item.parent = parent_node
#             parent_node.contents.append(item)
#         return
    
#     def find(self, finder: Finder, **kwargs: Any) -> Optional[base.Node]:
#         """Finds first matching node in Tree using 'finder'.

#         Args:
#             finder (Callable[[base.Node], Optional[base.Node]]): 
#                 function or other callable that returns a node if it meets 
#                 certain criteria or otherwise returns None.
#             kwargs: keyword arguments to pass to 'finder' when examing each
#                 node.

#         Returns:
#             Optional[base.Node]: matching Node or None if no matching node 
#                 is found.
            
#         """                  
#         for node in self.nodes:
#             comparison = finder(self, **kwargs)
#             if comparison:
#                 return node
#         return None
            
#     def find_add(
#         self, 
#         finder: Finder, 
#         item: base.Node, 
#         **kwargs: Any) -> None:
#         """Finds first matching node in Tree using 'finder'.

#         Args:
#             finder (Callable[[base.Node], Optional[base.Node]]): 
#                 function or other callable that returns a node if it meets 
#                 certain criteria or otherwise returns None.
#             item (base.Node): node to add to the 'contents' attribute of 
#                 the first node that meets criteria in 'finder'.
#             kwargs: keyword arguments to pass to 'finder' when examing each
#                 node.

#         Raises:
#             ValueError: if no matching node is found by 'finder'.

#         Returns:
#             Optional[base.Node]: matching Node or None if no matching node 
#                 is found.
            
#         """  
#         node = self.find(finder = finder, **kwargs)
#         if node:
#             node.add(item = item)
#         else:
#             raise ValueError(
#                 'item could not be added because no matching node was found by '
#                 'finder')
#         return
    
#     def find_all(self, finder: Finder, **kwargs: Any) -> list[base.Node]:
#         """Finds all matching nodes in Tree using 'finder'.

#         Args:
#             finder (Callable[[base.Node], Optional[base.Node]]): 
#                 function or other callable that returns a node if it meets 
#                 certain criteria or otherwise returns None.
#             kwargs: keyword arguments to pass to 'finder' when examing each
#                 node.

#         Returns:
#             list[base.Node]: matching nodes or an empty list if no 
#                 matching node is found.
            
#         """              
#         found = []     
#         for node in self.nodes:
#             comparison = finder(self, **kwargs)
#             if comparison:
#                 found.append(node)
#         return found
            
#     def find_change(
#         self, 
#         finder: Finder, 
#         changer: Changer, 
#         **kwargs: Any) -> None:
#         """Finds matching nodes in Tree using 'finder' and applies 'changer'.

#         Args:
#             finder (Callable[[base.Node], Optional[base.Node]]): 
#                 function or other callable that returns a node if it meets 
#                 certain criteria or otherwise returns None.
#             changer (Callable[[base.Node], None]): function or other 
#                 callable that modifies the found node.
#             kwargs: keyword arguments to pass to 'finder' when examing each
#                 node.

#         Raises:
#             ValueError: if no matching node is found by 'finder'.
            
#         """  
#         nodes = self.find_all(finder = finder, **kwargs)
#         if nodes:
#             for node in nodes:
#                 changer(node)
#         else:
#             raise ValueError(
#                 'changer could not be applied because no matching node was '
#                 'found by finder')
#         return
    
#     def get(self, item: str) -> Optional[base.Node]:
#         """Finds first matching node in Tree match 'item'.

#         Args:
#             item (str): 

#         Returns:
#             Optional[base.Node]: matching Node or None if no matching node 
#                 is found.
            
#         """                  
#         for node in self.nodes:
#             if node.name == item:
#                 return node
#         return self.__missing__()
                                    
#     def walk(self, depth_first: bool = True) -> base.Pipeline:
#         """Returns all paths in tree from 'start' to 'stop'.
        
#         Args:
#             depth_first (bool): whether to search through the stored tree depth-
#                 first (True) or breadth_first (False). Defaults to True.
                
#         """
#         if depth_first:
#             return depth_first_search(tree = self.contents)
#         else:
#             raise NotImplementedError(
#                 'breadth first search is not yet implemented')
#             # return breadth_first_search(tree = self.contents)

#     """ Dunder Methods """

#     def __add__(self, other: base.Graph) -> None:
#         """Adds 'other' to the stored tree using the 'append' method.

#         Args:
#             other (base.Graph): another Composite or supported
#                 raw data structure.
            
#         """
#         self.append(item = other)     
#         return 

#     def __radd__(self, other: base.Graph) -> None:
#         """Adds 'other' to the stored tree using the 'prepend' method.

#         Args:
#             other (base.Graph): another Composite or supported
#                 raw data structure.
            
#         """
#         self.prepend(item = other)     
#         return 

#     def __missing__(self) -> dict[str, Tree]:
#         """[summary]

#         Returns:
#             dict[str, Tree]: [description]
            
#         """
#         return {}
    
#     def __hash__(self) -> int:
#         """[summary]

#         Returns:
#             int: [description]
            
#         """
#         return hash(self.name)

#     def __eq__(self, other: Any) -> bool:
#         """[summary]

#         Args:
#             other (Any): [description]

#         Returns:
#             bool: [description]
            
#         """
#         if hasattr(other, 'name'):
#             return other.name == self.name
#         else:
#             return False
        
#     def __ne__(self, other: Any) -> bool:
#         """[summary]

#         Args:
#             other (Any): [description]

#         Returns:
#             bool: [description]
            
#         """
#         return not self.__eq__(other = other)


# def breadth_first_search(
#     tree: Tree, 
#     visited: Optional[list[Tree]] = None) -> base.Pipeline:
#     """Returns a breadth first search path through 'tree'.

#     Args:
#         tree (Tree): tree to search.
#         visited (Optional[list[Tree]]): list of visited nodes. Defaults to None.

#     Returns:
#         base.Pipeline: nodes in a path through 'tree'.
        
#     """         
#     visited = visited or []
#     if hasattr(tree, 'is_root') and tree.is_root:
#         visited.append(tree)
#     if hasattr(tree, 'children') and tree.children:
#         visited.extend(tree.children)
#         for child in tree.children:
#             visited.extend(breadth_first_search(tree = child, visited = visited))
#     return visited
                
                     
# def depth_first_search(
#     tree: Tree, 
#     visited: Optional[list[Tree]] = None) -> base.Pipeline:
#     """Returns a depth first search path through 'tree'.

#     Args:
#         tree (Tree): tree to search.
#         visited (Optional[list[Tree]]): list of visited nodes. Defaults to None.

#     Returns:
#         base.Pipeline: nodes in a path through 'tree'.
        
#     """  
#     visited = visited or []
#     visited.append(tree)
#     if hasattr(tree, 'children') and tree.children:
#         for child in tree.children:
#             visited.extend(depth_first_search(tree = child, visited = visited))
#     return visited

 
# @dataclasses.dataclass # type: ignore
# class Pipelines(sequence.Hybrid, base.Composite):
#     """Base class a collection of Pipeline instances.
        
#     Args:
#         contents (MutableSequence[base.Node]): list of stored Pipeline instances. 
#             Defaults to an empty list.

#     """
#     contents: MutableSequence[Pipeline] = dataclasses.field(
#         default_factory = list)

#     """ Properties """

#     def endpoint(self) -> Pipeline:
#         """Returns the endpoint of the stored composite object."""
#         return self.contents[list(self.contents.keys())[-1]]

#     def root(self) -> Pipeline:
#         """Returns the root of the stored composite object."""
#         self.contents[list(self.contents.keys())[0]]
    
#     """ Public Methods """
  
#     def merge(item: base.Composite, *args: Any, **kwargs: Any) -> None:
#         """Combines 'item' with the stored composite object.

#         Args:
#             item (Composite): another Composite object to add to the stored 
#                 composite object.
                
#         """
#         pass

#     def walk(
#         self, 
#         start: Optional[base.Node] = None,
#         stop: Optional[base.Node] = None, 
#         path: Optional[Pipeline] = None,
#         return_pipelines: bool = True, 
#         *args: Any, 
#         **kwargs: Any) -> Union[Pipeline, Pipelines]:
#         """Returns path in the stored composite object from 'start' to 'stop'.
        
#         Args:
#             start (Optional[base.Node]): base.Node to start paths from. Defaults to None.
#                 If it is None, 'start' should be assigned to one of the roots
#                 of the base.
#             stop (Optional[base.Node]): base.Node to stop paths. Defaults to None. If it 
#                 is None, 'start' should be assigned to one of the roots of the 
#                 base.
#             path (Optional[Pipeline]): a path from 'start' to 'stop'. 
#                 Defaults to None. This parameter is used by recursive methods 
#                 for determining a path.
#             return_pipelines (bool): whether to return a Pipelines instance 
#                 (True) or a Pipeline instance (False). Defaults to True.

#         Returns:
#             Union[Pipeline, Pipelines]: path(s) through the 
#                 Composite object. If multiple paths are possible and 
#                 'return_pipelines' is False, this method should return a 
#                 Pipeline that includes all such paths appended to each other. If 
#                 multiple paths are possible and 'return_pipelines' is True, a 
#                 Pipelines instance with all of the paths should be returned. 
#                 Defaults to True.
                            
#         """
#         return self.items()
        
#     """ Dunder Methods """
        
#     @classmethod
#     def __instancecheck__(cls, instance: object) -> bool:
#         return check.is_pipelines(item = instance)
 