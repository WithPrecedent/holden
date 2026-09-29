"""Functions to export composite data structures to other formats.

Contents:
    to_dot: exports a composite object to a dot (Graphviz) file.
    to_mermaid: exports a composite object to a mermaid file.

To Do:
    Add different shapes to mermaid flowchart.
    Add excalidraw support.

"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from . import base, report, traits, utilities

if TYPE_CHECKING:
    import pathlib
    from collections.abc import Hashable

__all__: list[str] = ["to_dot", "to_mermaid"]

_LINE_BREAK = "\n"
_DOT_ARROW = "->"
_MERMAID_ARROW = "-->"
_CONNECTOR = "--"
_INDENT = "    "
_YAML_INDENT = "  "
_MERMAID_FRONTMATTER = "---"
_DOT_ID = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|-?(\.[0-9]+|[0-9]+(\.[0-9]*)?)")
_NOT_WORD = re.compile(r"\W")
# Words that cannot be used as the identifier of a mermaid node.
_MERMAID_RESERVED = frozenset({"end"})


def to_dot(
    item: Any,
    path: str | pathlib.Path | None = None,
    name: str = "holden",
    settings: dict[str, Any] | None = None,
) -> str:
    """Converts `item` to a dot format.

    Args:
        item: composite data structure or raw form to convert to a dot format.
            If `item` is a `Directed` composite data structure, a directed
            graph is created. Otherwise, an undirected graph is created.
        path: path to export `item` to. Defaults to `None`.
        name: name of `item` to put in the dot `str`. Defaults to "holden".
        settings: any global settings to add to the dot graph. Defaults to
            `None`.

    Returns:
        Composite object in graphviz dot format.

    """
    adjacency = base._to_raw(item, "adjacency")
    if isinstance(item, traits.Directed):
        dot = "digraph "
        link = _DOT_ARROW
    else:
        dot = "graph "
        link = _CONNECTOR
    lines = [f"{dot}{_dot_id(name)} {{"]
    if settings is not None:
        lines.extend(f"{key}={value};" for key, value in settings.items())
    lines.extend(
        f"{_dot_id(start)} {link} {_dot_id(stop)}"
        for start, stop in _edges(adjacency)
    )
    lines.extend(_dot_id(node) for node in _isolated(adjacency))
    code = _LINE_BREAK.join(lines) + _LINE_BREAK + "}" + _LINE_BREAK
    if path is not None:
        _save_file(code, path)
    return code


def to_mermaid(
    item: Any,
    path: str | pathlib.Path | None = None,
    name: str = "holden",
    settings: dict[str, Any] | None = None,
) -> str:
    """Converts `item` to a mermaid format.

    Args:
        item: composite data structure or raw form to convert to a mermaid
            format. If `item` is a `Directed` composite data structure, the
            edges are arrows. Otherwise, the edges are lines.
        path: path to export `item` to. Defaults to `None`.
        name: name of `item` to put in the mermaid `str`. Defaults to "holden".
        settings: any global settings to add to the mermaid graph. A nested
            `dict` is written as nested yaml. Defaults to `None`.

    Returns:
        Composite object in mermaid format.

    """
    adjacency = base._to_raw(item, "adjacency")
    link = _MERMAID_ARROW if isinstance(item, traits.Directed) else _CONNECTOR
    ids: dict[Hashable, str] = {}
    lines = [
        f"{_INDENT}{_mermaid_node(start, ids)} {link} {_mermaid_node(stop, ids)}"
        for start, stop in _edges(adjacency)
    ]
    lines.extend(
        f"{_INDENT}{_mermaid_node(node, ids)}" for node in _isolated(adjacency)
    )
    code = _add_mermaid_settings(name, settings)
    code = f"{code}flowchart LR{_LINE_BREAK}"
    code += "".join(f"{line}{_LINE_BREAK}" for line in lines)
    if path is not None:
        _save_file(code, path)
    return code


def _add_mermaid_settings(name: str, settings: dict[str, Any] | None) -> str:
    """Creates the mermaid front matter.

    Args:
        name: title of flowchart.
        settings: any global settings to add to the mermaid graph.

    Returns:
        The front matter of a mermaid file as a `str`.

    """
    lines = [_MERMAID_FRONTMATTER, f"title: {name}"]
    if settings is not None:
        lines.append("config:")
        lines.extend(_yaml_lines(settings, _YAML_INDENT))
    lines.append(_MERMAID_FRONTMATTER)
    return _LINE_BREAK.join(lines) + _LINE_BREAK


def _dot_id(node: Hashable) -> str:
    """Returns `node` as an identifier that is valid in a dot file.

    Args:
        node: node to convert.

    Returns:
        `str` of `node`, in double quotes if it is not a valid dot identifier.

    """
    text = _label(node)
    if _DOT_ID.fullmatch(text):
        return text
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _edges(
    adjacency: dict[Hashable, set[Hashable]],
) -> list[tuple[Hashable, Hashable]]:
    """Returns the edges of an adjacency list in a deterministic order.

    Args:
        adjacency: raw adjacency list.

    Returns:
        List of edges.

    """
    return [
        (start, stop)
        for start, stops in adjacency.items()
        for stop in utilities._stabilize(stops)
    ]


def _isolated(adjacency: dict[Hashable, set[Hashable]]) -> list[Hashable]:
    """Returns the nodes of an adjacency list that have no edges.

    Args:
        adjacency: raw adjacency list.

    Returns:
        List of nodes that no node connects to and that do not connect to any
            node.

    """
    stops: set[Hashable] = set()
    for connections in adjacency.values():
        stops.update(connections)
    return [
        node
        for node in report._nodes_adjacency(adjacency)
        if not adjacency.get(node) and node not in stops
    ]


def _label(node: Hashable) -> str:
    """Returns the text that represents a node in an exported file.

    Args:
        node: node to label.

    Returns:
        The `name` of `node`, if it has a `str` name. Otherwise, the `str` of
            `node`.

    """
    name = getattr(node, "name", None)
    return name if isinstance(name, str) else str(node)


def _mermaid_node(node: Hashable, ids: dict[Hashable, str]) -> str:
    """Returns the mermaid syntax for a node.

    Args:
        node: node to convert.
        ids: mapping of the nodes that have already been converted to their
            mermaid identifiers. It is updated with `node`, if necessary.

    Returns:
        The identifier and (in parentheses) label of the node.

    """
    text = _label(node)
    if node not in ids:
        identifier = _NOT_WORD.sub("_", text) or "_"
        if identifier.lower() in _MERMAID_RESERVED:
            identifier = f"{identifier}_"
        used = set(ids.values())
        candidate, count = identifier, 1
        while candidate in used:
            candidate = f"{identifier}_{count}"
            count += 1
        ids[node] = candidate
    if _NOT_WORD.search(text) is None:
        label = text
    else:
        label = '"' + text.replace('"', "#quot;") + '"'
    return f"{ids[node]}({label})"


def _save_file(item: str, path: pathlib.Path | str) -> None:
    """Saves file to disk.

    Args:
        item: `str` item to save to disk.
        path: path to save `item` to.

    """
    path = utilities._pathlibify(path)
    with path.open("w", encoding="utf-8", newline="\n") as a_file:
        a_file.write(item)


def _yaml_lines(settings: dict[str, Any], indent: str) -> list[str]:
    """Returns `settings` as lines of yaml.

    Args:
        settings: settings to convert.
        indent: indentation to put in front of each line.

    Returns:
        Lines of yaml. Nested `dict` values are indented further.

    """
    lines = []
    for key, value in settings.items():
        if isinstance(value, dict):
            lines.append(f"{indent}{key}:")
            lines.extend(_yaml_lines(value, indent + _YAML_INDENT))
        else:
            lines.append(f"{indent}{key}: {value}")
    return lines
