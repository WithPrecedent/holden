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
class Something(holden.Node):
    
    pass


@dataclasses.dataclass
class AnotherThing(holden.Node):
    
    pass


@dataclasses.dataclass
class EvenAnother(holden.Node):
    
    pass


def test_graph():
    # Tests adjacency matrix constructor
    matrix = tuple([[[0, 0, 1], [1, 0, 0], [0, 0, 0]],
                    ['scorpion', 'frog', 'river']])
    workflow = holden.System.from_matrix(item = matrix)
    assert 'scorpion' in workflow['frog']
    assert 'river' not in workflow['frog']
    # Tests adjacency list constructor
    adjacency = {'grumpy': {'sleepy'},
                 'doc': {},
                 'sneezy': {'grumpy', 'bashful'}}
    workflow = holden.System.from_adjacency(item = adjacency)
    assert 'sleepy' in workflow['grumpy']
    assert 'bashful' in workflow['sneezy']
    assert 'bashful' not in workflow['doc']
    # Tests edge list constructor
    edges = [('camera', 'woman'), 
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
    workflow.connect('bonnie', 'clyde')
    workflow.connect('butch', 'sundance')
    workflow.connect('bonnie', 'henchman')
    workflow.connect('sundance', 'henchman')
    assert 'clyde' in workflow['bonnie']
    assert 'henchman' in workflow ['bonnie']
    assert 'henchman' not in workflow['butch']
    # Tests searches and paths
    # depth_search = workflow.search()
    # assert depth_search == ['bonnie', 'clyde', 'henchman']
    # breadth_search = workflow.search(depth_first = False)
    # print(breadth_search)
    # assert breadth_search == ['clyde', 'bonnie', 'henchman']
    all_paths = workflow.paths
    assert ['butch', 'sundance', 'henchman'] in all_paths
    assert ['bonnie', 'clyde'] in all_paths
    assert ['bonnie', 'henchman'] in all_paths
    workflow.merge(item = workflow_edges)
    new_workflow = holden.System()
    something = Something()
    another_thing = AnotherThing()
    even_another = EvenAnother()
    new_workflow.add(node = something)
    new_workflow.add(node = another_thing)
    new_workflow.add(node= even_another)
    new_workflow.connect('something', 'another_thing')
    assert 'another_thing' in new_workflow['something']
    assert 'another_thing' in new_workflow[something]
    assert another_thing in new_workflow[something]
    assert something in new_workflow
    return

def test_graph_again() -> None:
    edges = tuple([('a', 'b'), ('c', 'd'), ('a', 'd'), ('d', 'e')])
    dag = holden.System.create(item = edges)
    dag.add(node = 'cat')
    dag.add(node = 'dog', ancestors = 'e', descendants = ['cat'])
    assert dag['dog'] == {'cat'}
    assert dag['e'] == {'dog'}
    adjacency = {
        'tree': {'house', 'yard'},
        'house': set(),
        'yard': set()}
    assert holden.Adjacency.__instancecheck__(adjacency)
    another_dag = holden.System.create(item = adjacency)
    dag.append(item = another_dag)
    assert dag['cat'] == {'tree'}
    pipelines = dag.pipelines 
    assert len(pipelines) == 6
    assert dag.endpoint == {'house', 'yard'}
    assert dag.root == {'a', 'c'}
    assert dag.nodes == {
        'tree', 'b', 'c', 'a', 'yard', 'cat', 'd', 'house', 'dog', 'e'}
    pipeline = dag.pipeline
    new_dag = holden.System.from_pipeline(item = pipeline)
    assert new_dag['tree'] == dag['tree']
    another_dag = holden.System.from_pipelines(item = pipelines)
    assert another_dag['tree'] == dag['tree']
    return

def test_pipeline() -> None:
    
    return

def test_tree() -> None:
    
    return


if __name__ == '__main__':
    test_graph()
    test_graph_again()
    test_pipeline()
    test_tree()
    