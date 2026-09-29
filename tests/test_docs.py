"""Tests that the python examples in the documentation run without error."""

from __future__ import annotations

import pathlib
import re
import sys
import types

import pytest

from holden import check, workshop

DOCS = pathlib.Path(__file__).parents[1] / 'docs'


@pytest.mark.parametrize('name', ['tutorial', 'advanced', 'recipes'])
def test_doc_examples_run(name: str) -> None:
    """Executes all of the python code blocks of a documentation page."""
    text = (DOCS / f'{name}.md').read_text(encoding = 'utf-8')
    blocks = re.findall(r'```python\n(.*?)```', text, flags = re.DOTALL)
    assert blocks
    module = types.ModuleType(f'docs_{name}')
    sys.modules[module.__name__] = module
    try:
        for block in blocks:
            exec(compile(block, f'{name}.md', 'exec'), module.__dict__)  # noqa: S102
    finally:
        del sys.modules[module.__name__]
        for module_name, function in (
                (check, 'is_bag'),
                (workshop, 'bag_to_adjacency'),
                (workshop, 'adjacency_to_bag')):
            if hasattr(module_name, function):
                delattr(module_name, function)


@pytest.mark.parametrize('name', ['tutorial', 'advanced', 'recipes'])
def test_doc_pages_are_not_empty(name: str) -> None:
    """Tests that every page of the guide has text and examples."""
    text = (DOCS / f'{name}.md').read_text(encoding = 'utf-8')
    assert len(text.splitlines()) > 20
    assert text.startswith('# ')
