"""Concrete lightweight graph data structures.

Contents:
    System: a directed graph with unweighted edges with an internal adjacency
        list structure.

To Do:
    Complete Network which will use an adjacency matrix for internal storage.

"""

from __future__ import annotations

import dataclasses

from . import graphs, traits

__all__: list[str] = ["System"]


@dataclasses.dataclass
class System(
    traits.Directed, graphs.Adjacency, traits.Fungible, traits.Exportable
):
    """Directed graph with unweighted edges stored as an adjacency list.

    A System combines the `Adjacency` form with the `Directed`, `Fungible`, and
    `Exportable` traits. So, it can find roots, endpoints, and paths; be
    converted to and created from every other form of composite data structure;
    and be exported to dot and mermaid formats.

    Args:
        contents: keys are nodes and values are sets of nodes (or hashable
            representations of nodes). Defaults to an empty `dict`.

    """
