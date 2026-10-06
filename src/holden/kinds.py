"""Type aliases for the raw forms of composite data structures.

Contents:
    RawAdjacency: type alias for a raw adjacency list.
    RawEdges: type alias for a raw edge list.
    RawMatrix: type alias for a raw adjacency matrix and its labels.
    RawParallel: type alias for a raw list of paths.
    RawSerial: type alias for a raw path.

"""

from __future__ import annotations

from collections.abc import Hashable
from typing import TypeAlias

RawAdjacency: TypeAlias = dict[Hashable, set[Hashable]]
RawEdges: TypeAlias = list[tuple[Hashable, Hashable]]
RawMatrix: TypeAlias = tuple[list[list[float]], list[Hashable]]
RawParallel: TypeAlias = list[list[Hashable]]
RawSerial: TypeAlias = list[Hashable]
