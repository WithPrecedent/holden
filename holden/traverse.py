"""
traverse: internal storage formats for graphs
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
    adjacency_to_serial
    adjacency_to_parallel
    edges_to_serial
    edges_to_parallel
    matrix_to_serial
    matrix_to_parallel
    serial_to_parallel
    parallel_to_serial
          
To Do:
    Add the remainder of the conversion methods between different forms
    Add private methods that currently raise NotImplementedError
    Integrate Kinds system when it is finished
    
"""
from __future__ import annotations
import collections
from collections.abc import (
    Collection, Hashable, MutableMapping, MutableSequence, Sequence, Set)
import copy
import dataclasses
# import functools
import itertools
from typing import Any, ClassVar, Optional, Type, TYPE_CHECKING, Union

import amos
import miller

from . import check
from . import composites
from . import workshop

if TYPE_CHECKING:
    from . import forms


# @to_parallel.register # type: ignore 
def adjacency_to_parallel(item: forms.Adjacency) -> composites.Parallel:
    """Converts 'item' to a Serial.
    
    Args:
        item (forms.Adjacency): item to convert to a Serial.

    Returns:
        Serial: derived from 'item'.

    """
    roots = workshop.get_roots_adjacency(item = item)
    endpoints = workshop.get_endpoints_adjacency(item = item)
    all_paths = []
    for start in roots:
        for end in endpoints:
            paths = walk_adjacency(item = item, start = start, stop = end)
            if paths:
                if all(isinstance(path, Hashable) for path in paths):
                    all_paths.append(paths)
                else:
                    all_paths.extend(paths)
    return all_paths

# @to_serial.register # type: ignore 
def adjacency_to_serial(item: forms.Adjacency) -> composites.Serial:
    """Converts 'item' to a Serial.
    
    Args:
        item (forms.Adjacency): item to convert to a Serial.

    Returns:
        Serial: derived from 'item'.

    """ 
    all_parallel = adjacency_to_parallel(item = item)
    if len(all_parallel) == 1:
        return all_parallel[0]
    else:
        return list(itertools.chain.from_iterable(all_parallel))

def walk_adjacency(
    item: forms.Adjacency, 
    start: Hashable, 
    stop: Hashable,
    path: Optional[Sequence[Hashable]] = None) -> Sequence[Hashable]:
    """Returns all paths in 'item' from 'start' to 'stop'.

    The code here is adapted from: https://www.python.org/doc/essays/graphs/
    
    Args:
        item (forms.Adjacency): item in which to find paths.
        start (Hashable): node to start paths from.
        stop (Hashable): node to stop paths.
        path (Optional[Sequence[Hashable]]): a path from 'start' to 'stop'. 
            Defaults to None. 

    Returns:
        Sequence[Hashable]: a list of possible paths (each path is a list nodes) 
            from 'start' to 'stop'.
        
    """            
    if path is None:
        path = []
    path = path + [start]
    if start == stop:
        return [path]
    if start not in item:
        return []
    paths = []
    for node in item[start]:
        if node not in path:
            new_paths = walk_adjacency(
                item = item,
                start = node, 
                stop = stop, 
                path = path)
            for new_path in new_paths:
                paths.append(new_path)
    return paths
 
# @to_parallel.register # type: ignore 
def edges_to_parallel(item: forms.Edges) -> composites.Parallel:
    """Converts 'item' to a Parallel.

    Args:
        item (forms.Edges): item to convert to a Parallel.

    Returns:
        Parallel: derived from 'item'.

    """
    raise NotImplementedError
   
# @to_serial.register # type: ignore 
def edges_to_serial(item: forms.Edges) -> composites.Serial:
    """Converts 'item' to a Serial.

    Args:
        item (forms.Edges): item to convert to a Serial.

    Returns:
        Serial: derived from 'item'.

    """
    raise NotImplementedError
 
# @to_parallel.register # type: ignore 
def matrix_to_parallel(item: forms.Matrix) -> composites.Parallel:
    """Converts 'item' to a Parallel.

    Args:
        item (forms.Matrix): item to convert to a Parallel.

    Returns:
        Parallel: derived from 'item'.

    """
    raise NotImplementedError
   
# @to_serial.register # type: ignore 
def matrix_to_serial(item: forms.Matrix) -> composites.Serial:
    """Converts 'item' to a Serial.

    Args:
        item (forms.Matrix): item to convert to a Serial.

    Returns:
        Serial: derived from 'item'.

    """
    raise NotImplementedError

# @to_adjacency.register # type: ignore 
def parallel_to_adjacency(item: composites.Parallel) -> forms.Adjacency:
    """Converts 'item' to an forms.Adjacency.

    Args:
        item (Parallel): item to convert to an forms.Adjacency.

    Returns:
        forms.Adjacency: derived from 'item'.

    """
    adjacency = collections.defaultdict(set)
    for serial in item:
        pipe_adjacency = serial_to_adjacency(item = serial)
        for key, value in pipe_adjacency.items():
            if key in adjacency:
                for inner_value in value:
                    if inner_value not in adjacency:
                        adjacency[key].add(inner_value)
            else:
                adjacency[key] = value
    return adjacency  
    
# @to_edges.register # type: ignore 
def parallel_to_edges(item: composites.Parallel) -> forms.Edges:
    """Converts 'item' to an forms.Edges.

    Args:
        item (Parallel): item to convert to an forms.Edges.

    Returns:
        forms.Edges: derived from 'item'.

    """
    raise NotImplementedError
 
# @to_matrix.register # type: ignore 
def parallel_to_matrix(item: composites.Parallel) -> forms.Matrix:
    """Converts 'item' to a forms.Matrix.

    Args:
        item (Parallel): item to convert to a forms.Matrix.

    Returns:
        forms.Matrix: derived from 'item'.

    """
    raise NotImplementedError
   
# @to_serial.register # type: ignore 
def parallel_to_serial(item: composites.Parallel) -> composites.Serial:
    """Converts 'item' to a Serial.

    Args:
        item (Parallel): item to convert to a Serial.

    Returns:
        Serial: derived from 'item'.

    """
    raise NotImplementedError
    
# @to_adjacency.register # type: ignore 
def serial_to_adjacency(item: composites.Serial) -> forms.Adjacency:
    """Converts 'item' to an forms.Adjacency.

    Args:
        item (Serial): item to convert to an forms.Adjacency.

    Returns:
        forms.Adjacency: derived from 'item'.

    """
    if check.is_parallel(item = item):
        return parallel_to_adjacency(item = item)
    else:
        if not isinstance(item, (Collection)) or isinstance(item, str):
            item = [item]
        adjacency = collections.defaultdict(set)
        if len(item) == 1:
            adjacency.update({item[0]: set()})
        else:
            edges = list(amos.windowify(item, 2))
            for edge_pair in edges:
                if edge_pair[0] in adjacency:
                    adjacency[edge_pair[0]].add(edge_pair[1])
                else:
                    adjacency[edge_pair[0]] = {edge_pair[1]} 
        return adjacency
    
# @to_edges.register # type: ignore 
def serial_to_edges(item: composites.Serial) -> forms.Edges:
    """Converts 'item' to an forms.Edges.

    Args:
        item (Serial): item to convert to an forms.Edges.

    Returns:
        forms.Edges: derived from 'item'.

    """
    raise NotImplementedError
    
# @to_matrix.register # type: ignore 
def serial_to_matrix(item: composites.Serial) -> forms.Matrix:
    """Converts 'item' to a forms.Matrix.

    Args:
        item (Serial): item to convert to a forms.Matrix.

    Returns:
        forms.Matrix: derived from 'item'.

    """
    raise NotImplementedError
 
# @to_parallel.register # type: ignore 
def serial_to_parallel(item: composites.Serial) -> composites.Parallel:
    """Converts 'item' to a Parallel.

    Args:
        item (Serial): item to convert to a Parallel.

    Returns:
        Parallel: derived from 'item'.

    """
    raise NotImplementedError

                     