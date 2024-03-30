"""Functions to export composite data structures to other formats.

Contents:

           
To Do:

    
"""
from __future__ import annotations
import pathlib
from typing import Any, Callable, Optional

from . import base
from . import traits


_LINE_BREAK = '\n'
_DIRECTED_LINK = '->'
_UNDIRECTED_LINK = '--'

def to_dot(
    item: base.Composite, 
    path: Optional[str | pathlib.Path] = None,
    name: Optional[str] = None,
    settings: Optional[dict[str, Any]] = None) -> str:
    """Converts 'item' to a dot format.

    Args:
        item (base.Composite): item to convert to a dot format.
        path (Optional[str | pathlib.Path]): path to export 'item' to. Defaults
            to None.
        name (Optional[str]): name of 'item' to put in the dot str. Defaults to
            None.
        settings (Optional[dict[str, Any]]): any global settings to add to the
            dot graph. Defaults to None.

    Returns:
        str: composite object in graphviz dot format.

    """
    edges = base.transform(
        item = item, 
        output = 'edges', 
        raise_same_error = False)
    name = name or 'holden'
    if isinstance(item, traits.Directed):
        dot = 'digraph '
        link = _DIRECTED_LINK
    else:
        dot = 'graph '
        link = _UNDIRECTED_LINK
    dot = dot +  name + ' {\n'
    if settings is not None:
        for key, value in settings.items():
            dot = f'{dot}{key}={value};{_LINE_BREAK}'
    for edge in edges:
        dot = f'{dot}{edge[0]} {link} {edge[1]}{_LINE_BREAK}'
    dot = dot + '}'
    if path is not None:
        with open(path, 'w') as a_file:
            a_file.write(dot)
        a_file.close()
    return dot
 