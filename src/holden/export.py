"""Functions to export composite data structures to other formats.

Contents:


To Do:


"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from . import base, traits

if TYPE_CHECKING:
    import pathlib

_LINE_BREAK = '\n'
_DIRECTED_LINK = '->'
_UNDIRECTED_LINK = '--'

def to_dot(
    item: base.Composite,
    path: str | pathlib.Path | None = None,
    name: str = 'holden',
    settings: dict[str, Any] | None = None) -> str:
    """Converts 'item' to a dot format.

    Args:
        item: item to convert to a dot format.
        path: path to export 'item' to. Defaults to None.
        name: name of 'item' to put in the dot str. Defaults to 'holden'.
        settings: any global settings to add to the dot graph. Defaults to None.

    Returns:
        Composite object in graphviz dot format.

    """
    edges = base.transform(
        item = item,
        output = 'edges',
        raise_same_error = False)
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

def to_mermaid(
    item: base.Composite,
    path: str | pathlib.Path | None = None,
    name: str = 'holden',
    settings: dict[str, Any] | None = None) -> str:
    """Converts 'item' to a mermaid format.

    Args:
        item: item to convert to a mermaid format.
        path: path to export 'item' to. Defaults to None.
        name: name of 'item' to put in the mermaid str. Defaults to 'holden'.
        settings: any global settings to add to the mermaid graph. Defaults to
            None.

    Returns:
        Composite object in mermaid format.

    """
    raise NotImplementedError('mermaid export is not yet supported')
