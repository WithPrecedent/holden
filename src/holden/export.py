"""Functions to export composite data structures to other formats.

Contents:
    to_dot: exports a composite object to a dot (Graphviz) file.
    to_mermaid: exports a composite object to a mermaid file.

To Do:
    Add different shapes to mermaid flowchart.
    Add excalidraw support.

"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from . import base, traits, utilities

if TYPE_CHECKING:
    import pathlib

_LINE_BREAK = '\n'
_DOT_ARROW = '->'
_MERMAID_ARROW = '-->'
_CONNECTOR = '--'
_INDENT = '    '
_YAML_INDENT = '  '
_MERMAID_FRONTMATTER = '---'


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
        link = _DOT_ARROW
    else:
        dot = 'graph '
        link = _CONNECTOR
    dot = dot + name + ' {\n'
    if settings is not None:
        for key, value in settings.items():
            dot = f'{dot}{key}={value};{_LINE_BREAK}'
    for edge in edges:
        dot = f'{dot}{edge[0]} {link} {edge[1]}{_LINE_BREAK}'
    dot = dot + '}'
    if path is not None:
        _save_file(dot, path)
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
    edges = base.transform(
        item = item,
        output = 'edges',
        raise_same_error = False)
    link = _MERMAID_ARROW if isinstance(item, traits.Directed) else _CONNECTOR
    code = ''
    code = _add_mermaid_settings(code, name, settings)
    code = f'{code}flowchart LR{_LINE_BREAK}'
    for edge in edges:
        code = f'{code}{_INDENT}{edge[0]}({edge[0]}) {link} {edge[1]}({edge[1]}){_LINE_BREAK}'
    if path is not None:
        _save_file(code, path)
    return code

def _add_mermaid_settings(
    code: str,
    name: str,
    settings: dict[str, Any] | None) -> str:
    """Adds mermaid settings to `code`.

    Args:
        code (str): _description_
        name: title of flowchart.
        settings (dict[str, Any]): _description_

    Returns:
        str: _description_
    """
    code = f'{_MERMAID_FRONTMATTER}{_LINE_BREAK}'
    code = f'{code}title: {name}{_LINE_BREAK}'
    if settings is not None:
        code = f'{code}config:{_LINE_BREAK}'
        for key, value in settings.items():
            code = {f'{code}{_YAML_INDENT}{key}: {value}{_LINE_BREAK}'}
    return f'{code}{_MERMAID_FRONTMATTER}{_LINE_BREAK}'

def _save_file(item: str, path: pathlib.Path | str) -> None:
    """Saves file to disk.

    Args:
        item: `str` item to save to disk.
        path: path to save `item` to.

    """
    path = utilities._pathlibify(path)
    with open(path, 'w') as a_file:
        a_file.write(item)
    a_file.close()
    return
