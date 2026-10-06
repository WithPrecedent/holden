"""Tests that every example in the README works as documented."""

from __future__ import annotations

import ast
import contextlib
import io
import pathlib
import re


def _run_block(source: str, namespace: dict) -> int:
    """Runs a README code block and checks the results in its comments.

    A comment at the end of an expression's line is the expected `repr` of the
    expression. Comment lines after a statement that begin with `# Output:` are
    its expected printed output. A `# Raises Error: message` comment on the line
    before a statement is the exception it is expected to raise.

    Args:
        source: The code block.
        namespace: The names shared by the code blocks.

    Returns:
        The number of results that were checked.

    """
    lines = source.splitlines()
    checked = 0
    for node in ast.parse(source).body:
        first = node.lineno - 1
        last = node.end_lineno
        code = '\n'.join(lines[first:last])
        raises = None
        if first and (
            match := re.match(r'# Raises (\w+): (.*)', lines[first - 1])):
            raises = match.groups()
        expected_output = None
        trailing = []
        for line in lines[last:]:
            if not line.startswith('#'):
                break
            trailing.append(line[2:])
        if trailing and trailing[0] == 'Output:':
            expected_output = trailing[1:]
        buffer = io.StringIO()
        try:
            with contextlib.redirect_stdout(buffer):
                if isinstance(node, ast.Expr):
                    value = eval(
                        compile(ast.Expression(node.value), 'README', 'eval'),
                            namespace)
                else:
                    exec(compile(ast.Module([node], []), 'README', 'exec'),
                        namespace)
                    value = None
        except Exception as error:
            assert raises is not None, f'Unexpected {error!r} in: {code}'
            assert (type(error).__name__, str(error)) == raises, code
            checked += 1
            continue
        assert raises is None, f'Expected {raises[0]} from: {code}'
        if expected_output is not None:
            assert buffer.getvalue().splitlines() == expected_output, code
            checked += 1
        elif isinstance(node, ast.Expr) and '  # ' in lines[last - 1]:
            expected = lines[last - 1].rsplit('  # ', 1)[1]
            assert repr(value) == expected, code
            checked += 1
    return checked


def test_readme_examples() -> None:
    """Runs all of the python code blocks in the README and checks results."""
    path = pathlib.Path(__file__).parents[1] / 'README.md'
    text = path.read_text(encoding = 'utf-8')
    blocks = re.findall(r'```python\n(.*?)```', text, flags = re.DOTALL)
    assert blocks
    namespace: dict = {}
    checked = sum(_run_block(block, namespace) for block in blocks)
    assert checked > 0


def test_readme_has_no_placeholders() -> None:
    """Tests that the README does not have any unfinished sections."""
    path = pathlib.Path(__file__).parents[1] / 'README.md'
    text = path.read_text(encoding = 'utf-8')
    assert '[TODO' not in text
    assert 'under heavy construction' not in text
