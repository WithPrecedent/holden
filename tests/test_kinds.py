"""Tests for `holden.kinds`."""

from __future__ import annotations

from holden import kinds


def test_raw_forms_are_defined() -> None:
    """Tests that every raw form has a type alias."""
    for name in (
            'RawAdjacency', 'RawEdges', 'RawMatrix', 'RawParallel',
            'RawSerial'):
        assert hasattr(kinds, name)
