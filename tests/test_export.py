"""Tests for `holden.export`."""

from __future__ import annotations

import pathlib

import pytest

import holden
from holden import export

DOT = 'digraph dag {\na -> b\na -> d\nc -> d\nd -> e\n}\n'
MERMAID = (
    '---\ntitle: dag\n---\nflowchart LR\n'
    '    a(a) --> b(b)\n    a(a) --> d(d)\n    c(c) --> d(d)\n'
    '    d(d) --> e(e)\n')
DATA = pathlib.Path(__file__).parent


def test_to_dot_directed(edges: list[tuple[str, str]]) -> None:
    """Tests `to_dot` for a directed graph."""
    system = holden.System.from_edges(edges)
    assert export.to_dot(system, name = 'dag') == DOT


def test_to_dot_undirected(
        adjacency: dict[str, set[str]],
        edges: list[tuple[str, str]],
        matrix: tuple[list[list[int]], list[str]]) -> None:
    """Tests that raw forms are exported as undirected graphs."""
    expected = 'graph dag {\na -- b\na -- d\nc -- d\nd -- e\n}\n'
    for item in (adjacency, edges, matrix, holden.Edges(edges)):
        assert export.to_dot(item, name = 'dag') == expected


def test_to_dot_default_name() -> None:
    """Tests the default name."""
    assert export.to_dot({'a': {'b'}, 'b': set()}) == (
        'graph holden {\na -- b\n}\n')


def test_to_dot_settings() -> None:
    """Tests global settings."""
    dot = export.to_dot(
        holden.Serial(['a', 'b']),
        name = 'path',
        settings = {'rankdir': 'LR', 'size': '"4,4"'})
    assert dot == 'digraph path {\nrankdir=LR;\nsize="4,4";\na -> b\n}\n'


def test_to_dot_quotes_identifiers() -> None:
    """Tests that identifiers that dot cannot read are quoted."""
    dot = export.to_dot(
        [('two words', 'has"quote'), ('1', '-2.5'), ('a_b', 'end')],
        name = 'my graph')
    assert dot == (
        'graph "my graph" {\n'
        '"two words" -- "has\\"quote"\n'
        '1 -- -2.5\n'
        'a_b -- end\n'
        '}\n')


def test_to_dot_isolated_nodes() -> None:
    """Tests that nodes without edges are included."""
    dot = export.to_dot({'a': {'b'}, 'b': set(), 'c': set()}, name = 'x')
    assert dot == 'graph x {\na -- b\nc\n}\n'
    assert export.to_dot({}, name = 'x') == 'graph x {\n}\n'


def test_to_dot_is_deterministic() -> None:
    """Tests that sets do not change the order of the output."""
    system = holden.System({'a': {'z', 'y', 'x', 'b'}})
    assert export.to_dot(system, name = 'x') == (
        'digraph x {\na -> b\na -> x\na -> y\na -> z\n}\n')


def test_to_dot_saves_file(tmp_path: pathlib.Path) -> None:
    """Tests writing to a `str` path and to a `pathlib.Path`."""
    system = holden.System.from_edges([('a', 'b')])
    result = export.to_dot(system, path = tmp_path / 'one.dot', name = 'one')
    assert (tmp_path / 'one.dot').read_text() == result
    export.to_dot(system, path = str(tmp_path / 'two.dot'), name = 'two')
    assert (tmp_path / 'two.dot').read_text().startswith('digraph two')
    assert b'\r' not in (tmp_path / 'one.dot').read_bytes()


def test_to_mermaid_directed(edges: list[tuple[str, str]]) -> None:
    """Tests `to_mermaid` for a directed graph."""
    system = holden.System.from_edges(edges)
    assert export.to_mermaid(system, name = 'dag') == MERMAID


def test_to_mermaid_undirected(edges: list[tuple[str, str]]) -> None:
    """Tests that raw forms are exported with lines instead of arrows."""
    mermaid = export.to_mermaid(edges, name = 'dag')
    assert mermaid == MERMAID.replace('-->', '--')


def test_to_mermaid_default_name() -> None:
    """Tests the default name."""
    assert export.to_mermaid([('a', 'b')]).startswith('---\ntitle: holden\n')


def test_to_mermaid_settings() -> None:
    """Tests global settings, including nested ones."""
    mermaid = export.to_mermaid(
        [('a', 'b')],
        name = 'x',
        settings = {'theme': 'dark', 'flowchart': {'curve': 'basis'}})
    assert mermaid == (
        '---\ntitle: x\nconfig:\n  theme: dark\n  flowchart:\n'
        '    curve: basis\n---\nflowchart LR\n    a(a) -- b(b)\n')


def test_to_mermaid_special_identifiers() -> None:
    """Tests nodes that cannot be used as mermaid identifiers."""
    mermaid = export.to_mermaid(
        [('two words', 'end'), ('a-b', 'a_b'), ('say "hi"', 'a b')],
        name = 'x')
    lines = mermaid.splitlines()[4:]
    assert lines == [
        '    two_words("two words") -- end_(end)',
        '    a_b("a-b") -- a_b_1(a_b)',
        '    say__hi_("say #quot;hi#quot;") -- a_b_2("a b")']


def test_to_mermaid_isolated_nodes() -> None:
    """Tests that nodes without edges are included."""
    mermaid = export.to_mermaid({'a': {'b'}, 'b': set(), 'c': set()})
    assert mermaid.endswith('flowchart LR\n    a(a) -- b(b)\n    c(c)\n')


def test_to_mermaid_saves_file(tmp_path: pathlib.Path) -> None:
    """Tests writing to a file."""
    system = holden.System.from_edges([('a', 'b')])
    result = export.to_mermaid(system, path = tmp_path / 'one.mmd',
        name = 'one')
    assert (tmp_path / 'one.mmd').read_text() == result


def test_exports_match_committed_files(tmp_path: pathlib.Path) -> None:
    """Tests the exports of the larger graph that is saved in the tests."""
    dag = holden.System.from_edges(
        [('a', 'b'), ('c', 'd'), ('a', 'd'), ('d', 'e')])
    dag.add('cat')
    dag.connect(('e', 'cat'))
    dag.append(holden.System({'tree': {'house', 'yard'}, 'house': set(),
                              'yard': set()}))
    dot = export.to_dot(dag, path = tmp_path / 'dag.dot', name = 'dag')
    mermaid = export.to_mermaid(
        dag, path = tmp_path / 'dag.mermaid', name = 'dag')
    assert dot == (DATA / 'dag.dot').read_text()
    assert mermaid == (DATA / 'dag.mermaid').read_text()


def test_exports_of_all_forms_agree(
        adjacency: dict[str, set[str]],
        edges: list[tuple[str, str]],
        matrix: tuple[list[list[int]], list[str]]) -> None:
    """Tests that every form produces the same export."""
    expected = export.to_mermaid(adjacency)
    for item in (
            edges,
            matrix,
            holden.Edges(edges),
            holden.Matrix(matrix[0], matrix[1]),
            holden.Adjacency(adjacency)):
        assert export.to_mermaid(item) == expected


def test_export_rejects_unrecognized_items() -> None:
    """Tests that an item that is not a composite raises an error."""
    with pytest.raises(TypeError):
        export.to_dot('a')
    with pytest.raises(TypeError):
        export.to_mermaid(5)
