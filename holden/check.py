"""
check: functions that type check graph forms using structural subtyping
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
    add_checker
    is_adjacency
    is_edges
    is_matrix
          
To Do:

    
"""
from __future__ import annotations
from collections.abc import (
    Collection, Hashable, MutableMapping, MutableSequence, Sequence, Set)
import itertools
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from . import base


def add_checker(name: str, item: Callable[[base.Graph]]) -> None:
    """Adds a checker to the local namespace.
    
    This allows the function to be found by the 'classify' function.

    Args:
        name (str): name of the checker function. It needs to be in the 
            'is_{form}' format.
        item (Callable[[base.Graph]]): callable checker which should have a
            single parameter, item which should be a base.Graph type.
        
    """
    globals()[name] = item
    return

def is_adjacency(item: object) -> bool:
    """Returns whether 'item' is an adjacency list.

    Args:
        item (object): instance to test.

    Returns:
        bool: whether 'item' is an adjacency list.
        
    """
    if isinstance(item, MutableMapping):
        connections = list(item.values())
        nodes = list(itertools.chain.from_iterable(item.values()))
        return (
            all(isinstance(e, set) for e in connections)
            and all(base.is_node(item = i) for i in nodes))
    else:
        return False

def is_edges(item: object) -> bool:
    """Returns whether 'item' is an edge list.

    Args:
        item (object): instance to test.

    Returns:
        bool: whether 'item' is an edge list.
    
    """
        
    return (
        isinstance(item, MutableSequence) 
        and all(base.is_edge(item = i) for i in item))
    
def is_matrix(item: object) -> bool:
    """Returns whether 'item' is an adjacency matrix.

    Args:
        item (object): instance to test.

    Returns:
        bool: whether 'item' is an adjacency matrix.
        
    """
    if isinstance(item, Sequence) and len(item) == 2:
        matrix = item[0]
        labels = item[1]
        connections = list(itertools.chain(matrix))
        return (
            isinstance(matrix, MutableSequence)
            and isinstance(labels, MutableSequence) 
            and all(isinstance(i, MutableSequence) for i in matrix)
            and all(isinstance(n, Hashable) for n in labels)
            and all(isinstance(c, int) for c in connections))
    else:
        return False
