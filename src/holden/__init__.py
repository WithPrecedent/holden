"""Lightweight, easy-to-use, flexible composite data structures."""

from __future__ import annotations

__version__ = "0.2.0"

__author__: str = "Corey Rayburn Yung"

from . import (
    applications,
    base,
    check,
    composites,
    export,
    graphs,
    options,
    report,
    traits,
    traverse,
    workshop,
)
from .applications import *  # noqa: F403
from .base import *  # noqa: F403
from .check import *  # noqa: F403
from .composites import *  # noqa: F403
from .export import *  # noqa: F403
from .graphs import *  # noqa: F403
from .options import *  # noqa: F403
from .report import *  # noqa: F403
from .traits import *  # noqa: F403
from .traverse import *  # noqa: F403
from .workshop import *  # noqa: F403

__all__: list[str] = [  # noqa: PLE0604
    *applications.__all__,
    *base.__all__,
    *check.__all__,
    *composites.__all__,
    *export.__all__,
    *graphs.__all__,
    *options.__all__,
    *report.__all__,
    *traits.__all__,
    *traverse.__all__,
    *workshop.__all__,
]
