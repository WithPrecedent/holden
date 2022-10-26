"""
test_holden: unit tests for holden data structures
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2022, Corey Rayburn Yung
License: Apache-2.0

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
    
    
"""
import dataclasses

import holden


@dataclasses.dataclass
class Something(holden.Labeled, holden.Node):
    
    name = 'something'


@dataclasses.dataclass
class AnotherThing(holden.Labeled, holden.Node):
    
    name = 'another_thing'


@dataclasses.dataclass
class EvenAnother(holden.Labeled, holden.Node):
    
    name = 'even_another'


def test_graph():
    # Tests adjacency matrix constructor
    matrix = tuple(
        [[[0, 0, 1], [1, 0, 0], [0, 0, 0]],
        ['scorpion', 'frog', 'river']])
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
    assert 'henchman' in workflow ['bonnie']
    assert 'henchman' not in workflow['butch']
    # Tests searches and parallel
    # depth_search = workflow.search()
    # assert depth_search == ['bonnie', 'clyde', 'henchman']
    # breadth_search = workflow.search(depth_first = False)
    # print(breadth_search)
    # assert breadth_search == ['clyde', 'bonnie', 'henchman']
    all_paths = workflow.walk()
    assert ['butch', 'sundance', 'henchman'] in all_paths
    assert ['bonnie', 'clyde'] in all_paths
    assert ['bonnie', 'henchman'] in all_paths
    workflow.merge(item = workflow_edges)
    new_workflow = holden.System()
    something = Something()
    another_thing = AnotherThing()
    even_another = EvenAnother()
    new_workflow.add(item = something)
    new_workflow.add(item = another_thing)
    new_workflow.add(item = even_another)
    new_workflow.connect(('something', 'another_thing'))
    # assert 'another_thing' in new_workflow['something']
    assert 'another_thing' in new_workflow['something']
    assert 'something' in new_workflow
    return

def test_graph_again() -> None:
    edges = [('a', 'b'), ('c', 'd'), ('a', 'd'), ('d', 'e')]
    dag = holden.System.from_edges(item = edges)
    assert dag.walk() == [['a', 'b'], ['a', 'd', 'e'], ['c', 'd', 'e']]
    dag.add(item = 'cat')
    dag.connect(('e', 'cat'))
    # dag.add(item = 'dog', ancestors = 'e', descendants = ['cat'])
    # assert dag['dog'] == {'cat'}
    # assert dag['e'] == {'dog'}
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
    # assert dag.walk() == [
    #     ['a', 'd', 'e', 'cat', 'tree', 'house'], 
    #     ['a', 'b', 'tree', 'house'], 
    #     ['a', 'd', 'e', 'cat', 'tree', 'yard'], 
    #     ['a', 'b', 'tree', 'yard'], 
    #     ['c', 'd', 'e', 'cat', 'tree', 'house'], 
    #     ['c', 'd', 'e', 'cat', 'tree', 'yard']]
    
    # assert dag.nodes == {
    #     'tree', 'b', 'c', 'a', 'yard', 'cat', 'd', 'house', 'dog', 'e'}
    # path = dag.serial
    # new_dag = holden.System.from_serial(item = path)
    # assert new_dag['tree'] == dag['tree']
    # another_dag = holden.System.from_parallel(item = paths)
    # assert another_dag['tree'] == dag['tree']
    return

def test_path() -> None:
    
    return

def test_tree() -> None:
    
    return


if __name__ == '__main__':
    test_graph()
    test_graph_again()
    test_path()
    test_tree()
    