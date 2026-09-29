"""Tests that every example in the README works as documented."""

from __future__ import annotations

import doctest
import pathlib
import re


def test_readme_examples() -> None:
    """Runs all of the python code blocks in the README as doctests."""
    path = pathlib.Path(__file__).parents[1] / 'README.md'
    text = path.read_text(encoding = 'utf-8')
    blocks = re.findall(r'```python\n(.*?)```', text, flags = re.DOTALL)
    assert blocks
    parser = doctest.DocTestParser()
    test = parser.get_doctest('\n'.join(blocks), {}, 'README', str(path), 0)
    assert test.examples
    runner = doctest.DocTestRunner()
    runner.run(test)
    results = runner.summarize(verbose = False)
    assert results.failed == 0
    assert results.attempted == len(test.examples)


def test_readme_has_no_placeholders() -> None:
    """Tests that the README does not have any unfinished sections."""
    path = pathlib.Path(__file__).parents[1] / 'README.md'
    text = path.read_text(encoding = 'utf-8')
    assert '[TODO' not in text
    assert 'under heavy construction' not in text
