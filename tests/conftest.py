"""Shared fixtures and helper classes for unit tests."""

from __future__ import annotations

import dataclasses
from collections.abc import Iterator

import pytest

import holden


@dataclasses.dataclass
class Something(holden.Labeled, holden.Node):
    """Labeled node with a default name."""

    name = 'something'


@dataclasses.dataclass
class AnotherThing(holden.Labeled, holden.Node):
    """Labeled node with a different default name."""

    name = 'another_thing'


@dataclasses.dataclass
class EvenAnother(holden.Labeled, holden.Node):
    """Labeled node with a third default name."""

    name = 'even_another'


@pytest.fixture(autouse = True)
def _reset_registry() -> Iterator[None]:
    """Restores the `Forms` registry after each test."""
    registry = dict(holden.Forms.registry)
    yield
    holden.Forms.registry.clear()
    holden.Forms.registry.update(registry)


@pytest.fixture
def edges() -> list[tuple[str, str]]:
    """Returns a raw edge list for a small directed acyclic graph."""
    return [('a', 'b'), ('c', 'd'), ('a', 'd'), ('d', 'e')]


@pytest.fixture
def adjacency() -> dict[str, set[str]]:
    """Returns a raw adjacency list equivalent to the `edges` fixture."""
    return {'a': {'b', 'd'}, 'b': set(), 'c': {'d'}, 'd': {'e'}, 'e': set()}


@pytest.fixture
def matrix() -> tuple[list[list[int]], list[str]]:
    """Returns a raw adjacency matrix equivalent to the `edges` fixture."""
    return (
        [
            [0, 1, 0, 1, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0],
            [0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0]],
        ['a', 'b', 'c', 'd', 'e'])
