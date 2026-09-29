"""Integration tests for the `holden` package as a whole."""

from __future__ import annotations

import pathlib

import holden

from .conftest import AnotherThing, EvenAnother, Something


def test_version() -> None:
    """Tests that the package has a version and an author."""
    assert isinstance(holden.__version__, str)
    assert holden.__version__.count('.') == 2
    assert holden.__author__


def test_public_names_are_importable() -> None:
    """Tests that everything in `__all__` is an attribute of the package."""
    assert holden.__all__
    for name in holden.__all__:
        assert hasattr(holden, name), name
    assert len(holden.__all__) == len(set(holden.__all__))


def test_expected_public_names() -> None:
    """Tests that the classes and functions in the README are available."""
    for name in (
            'Adjacency', 'Composite', 'Directed', 'Edge', 'Edges',
            'Exportable', 'Forms', 'Fungible', 'Graph', 'Labeled', 'Matrix',
            'Node', 'Parallel', 'Serial', 'Storage', 'System', 'Weighted',
            'classify', 'transform', 'is_adjacency', 'is_edges', 'is_matrix',
            'is_node', 'is_serial', 'is_parallel', 'adjacency_to_edges',
            'edges_to_parallel', 'to_dot', 'to_mermaid', 'walk', 'get_roots',
            'get_endpoints', 'set_base', 'get_base'):
        assert name in holden.__all__, name


def test_graph() -> None:
    """Tests constructing graphs from every raw form and by hand."""
    # Tests adjacency matrix constructor
    matrix = [[0, 0, 1], [1, 0, 0], [0, 0, 0]], ['scorpion', 'frog', 'river']
    workflow = holden.System.from_matrix(item = matrix)
    assert 'scorpion' in workflow['frog']
    assert 'river' not in workflow['frog']
    # Tests adjacency list constructor
    adjacency = {
        'grumpy': {'sleepy'},
        'doc': set(),
        'sneezy': {'grumpy', 'bashful'}}
    workflow = holden.System.from_adjacency(item = adjacency)
    assert 'sleepy' in workflow['grumpy']
    assert 'bashful' in workflow['sneezy']
    assert 'bashful' not in workflow['doc']
    # Tests edge list constructor
    edges = [
        ('camera', 'woman'),
        ('camera', 'man'),
        ('person', 'man'),
        ('tv', 'person')]
    workflow_edges = holden.System.from_edges(item = edges)
    assert 'woman' in workflow_edges['camera']
    assert 'man' in workflow_edges['camera']
    assert 'tv' not in workflow_edges['person']
    # Tests manual construction
    workflow = holden.System()
    workflow.add('bonnie')
    workflow.add('clyde')
    workflow.add('butch')
    workflow.add('sundance')
    workflow.add('henchman')
    workflow.connect(('bonnie', 'clyde'))
    workflow.connect(('butch', 'sundance'))
    workflow.connect(('bonnie', 'henchman'))
    workflow.connect(('sundance', 'henchman'))
    assert 'clyde' in workflow['bonnie']
    assert 'henchman' in workflow['bonnie']
    assert 'henchman' not in workflow['butch']
    # Tests paths
    all_paths = workflow.walk()
    assert ['butch', 'sundance', 'henchman'] in all_paths
    assert ['bonnie', 'clyde'] in all_paths
    assert ['bonnie', 'henchman'] in all_paths
    workflow.merge(item = workflow_edges)
    assert 'woman' in workflow
    # Tests labeled nodes
    new_workflow = holden.System()
    something = Something()
    another_thing = AnotherThing()
    even_another = EvenAnother()
    new_workflow.add(item = something)
    new_workflow.add(item = another_thing)
    new_workflow.add(item = even_another)
    new_workflow.connect(('something', 'another_thing'))
    assert 'another_thing' in new_workflow['something']
    assert 'something' in new_workflow
    assert 'not_there' not in new_workflow
    assert 'not_there' not in new_workflow.contents


def test_graph_again(tmp_path: pathlib.Path) -> None:
    """Tests a directed acyclic graph through its life."""
    edges = [('a', 'b'), ('c', 'd'), ('a', 'd'), ('d', 'e')]
    dag = holden.System.from_edges(item = edges)
    assert dag.walk() == [['a', 'b'], ['a', 'd', 'e'], ['c', 'd', 'e']]
    dag.add(item = 'cat')
    dag.connect(('e', 'cat'))
    adjacency = {
        'tree': {'house', 'yard'},
        'house': set(),
        'yard': set()}
    assert holden.is_adjacency(adjacency)
    another_dag = holden.System.from_adjacency(item = adjacency)
    dag.append(item = another_dag)
    assert dag['cat'] == {'tree'}
    paths = dag.walk()
    assert len(paths) == 6
    assert dag.endpoint == ['house', 'yard']
    assert dag.root == ['a', 'c']
    export_dot = tmp_path / 'dag.dot'
    holden.to_dot(item = dag, path = export_dot, name = 'dag')
    export_mermaid = tmp_path / 'dag.mermaid'
    holden.to_mermaid(item = dag, path = export_mermaid, name = 'dag')
    tests = pathlib.Path(__file__).parent
    assert export_dot.read_text() == (tests / 'dag.dot').read_text()
    assert export_mermaid.read_text() == (tests / 'dag.mermaid').read_text()
    assert dag.nodes == {
        'tree', 'b', 'c', 'a', 'yard', 'cat', 'd', 'house', 'e'}
    assert paths == [
        ['a', 'b', 'tree', 'house'],
        ['a', 'd', 'e', 'cat', 'tree', 'house'],
        ['a', 'b', 'tree', 'yard'],
        ['a', 'd', 'e', 'cat', 'tree', 'yard'],
        ['c', 'd', 'e', 'cat', 'tree', 'house'],
        ['c', 'd', 'e', 'cat', 'tree', 'yard']]
    path = dag.serial
    new_dag = holden.System.from_serial(item = path)
    assert new_dag['tree'] == dag['tree']
    another_dag = holden.System.from_parallel(item = paths)
    assert another_dag['tree'] == dag['tree']
    assert another_dag == dag


def test_path() -> None:
    """Tests a single path."""
    path = holden.Serial(['a', 'b', 'c'])
    assert path.walk() == [['a', 'b', 'c']]
    assert holden.System.from_serial(path).walk() == [['a', 'b', 'c']]
    assert path.adjacency.contents == {'a': {'b'}, 'b': {'c'}, 'c': set()}


def test_all_forms_describe_the_same_graph() -> None:
    """Tests that the same graph gives the same answers in every form."""
    edges = [('a', 'b'), ('c', 'd'), ('a', 'd'), ('d', 'e')]
    system = holden.System.from_edges(edges)
    forms = [
        holden.Adjacency(system.contents),
        system.edges,
        system.matrix,
        system.parallel]
    for form in forms:
        assert holden.get_roots(form) == ['a', 'c']
        assert holden.get_endpoints(form) == ['b', 'e']
        assert holden.walk(form) == system.walk()
        assert holden.utilities._rawify(holden.transform(
            form, 'adjacency', raise_same_error = False)) == system.contents
