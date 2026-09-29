# Recipes

Short solutions to common problems. Every example on this page is run by the test suite.

## Run steps of a workflow in order

Store the callables for each step in a `Storage` graph and walk the graph.

```python
import dataclasses

import holden


@dataclasses.dataclass
class Workflow(holden.Storage, holden.System):
    """Graph of step names with the functions that carry them out."""

    def run(self, value):
        for path in self.walk():
            result = value
            for name in path:
                result = self.retrieve(name)(result)
            yield path, result


workflow = Workflow.from_edges([("double", "add_one"), ("double", "square")])
workflow.store("double", lambda x: x * 2)
workflow.store("add_one", lambda x: x + 1)
workflow.store("square", lambda x: x**2)

assert dict((tuple(path), result) for path, result in workflow.run(3)) == {
    ("double", "add_one"): 7,
    ("double", "square"): 36}
```

## Use objects as nodes

Any hashable object can be a node. Frozen dataclasses are hashable by their values.

```python
@dataclasses.dataclass(frozen=True)
class Task:
    name: str
    hours: int = 1


design = Task("design", 4)
build = Task("build", 8)
ship = Task("ship")
plan = holden.System.from_edges([(design, build), (build, ship)])
assert plan.root == [design]
assert sum(task.hours for task in plan.walk()[0]) == 13
```

If your objects are not hashable (or should be compared by something other than their values), subclass `Node`. It makes the object hashable using all of its fields, even if they include unhashable values such as a `list`.

```python
@dataclasses.dataclass
class Step(holden.Node):
    pass


first = Step(["a", "list"])
assert first == Step(["a", "list"])
assert first in {Step(["a", "list"])}
```

## Refer to nodes by name

`Labeled` nodes are hashed and compared by their name. You can then use a plain `str` anywhere a node is expected.

```python
@dataclasses.dataclass
class Job(holden.Labeled, holden.Node):
    pass


jobs = holden.System()
jobs.add(Job(name="extract", contents="extract.py"))
jobs.add(Job(name="load", contents="load.py"))
jobs.connect(("extract", "load"))

assert "load" in jobs["extract"]
assert jobs.root[0].contents == "extract.py"
```

If a subclass sets a `name` class attribute, that is the default name.

```python
@dataclasses.dataclass
class Transform(holden.Labeled, holden.Node):
    name = "transform"


assert Transform().name == "transform"
assert Transform(name="custom").name == "custom"
```

## Convert between forms

Use the properties of a graph, the `from_{form}` class methods, or the functions that are named for the forms.

```python
edges = [("a", "b"), ("b", "c")]
adjacency = holden.edges_to_adjacency(edges)
matrix = holden.adjacency_to_matrix(adjacency)

assert adjacency == {"a": {"b"}, "b": {"c"}, "c": set()}
assert matrix == ([[0, 1, 0], [0, 0, 1], [0, 0, 0]], ["a", "b", "c"])
assert holden.matrix_to_serial(matrix) == ["a", "b", "c"]
assert holden.transform(matrix, "edges") == edges
```

`holden.Forms.transform` does the same thing but returns an instance of the class for the form instead of a raw structure.

```python
graph = holden.Forms.transform(edges, "matrix")
assert isinstance(graph, holden.Matrix)
assert graph.labels == ["a", "b", "c"]
```

## Check what you have been given

```python
assert holden.classify({"a": {"b"}, "b": set()}) == "adjacency"
assert holden.classify([("a", "b")]) == "edges"
assert holden.classify(([[0]], ["a"])) == "matrix"
assert holden.classify([["a", "b"], ["c"]]) == "parallel"
assert holden.classify(["a", "b"]) == "serial"
assert holden.classify(holden.System()) == "adjacency"

try:
    holden.classify("not a graph")
except TypeError:
    pass
else:
    raise AssertionError("classify should have raised a TypeError")
```

## Get a reproducible export

The output of `to_dot` and `to_mermaid` is in a stable order even though the connections of a node are stored in a `set`. Nodes that do not have any edges are included.

```python
graph = holden.System({"a": {"z", "y", "x"}, "lonely": set()})
assert graph.to_dot(name="g") == "\n".join([
    "digraph g {",
    "a -> x",
    "a -> y",
    "a -> z",
    "lonely",
    "}",
    ""])
```

## Find the leaves of a graph that is too big to print

```python
big = holden.System.from_edges([(i, i + 1) for i in range(500)])
assert big.root == [0]
assert big.endpoint == [500]
assert len(big.walk()[0]) == 501
```

## Combine graphs of different forms

`merge` accepts any form. So, you can combine data from different sources without converting it first.

```python
combined = holden.System()
combined.merge([("a", "b")])  # an edge list
combined.merge({"b": {"c"}, "c": set()})  # an adjacency list
combined.merge(([[0, 1], [0, 0]], ["c", "d"]))  # an adjacency matrix
combined.merge(["d", "e"])  # a single path

assert combined.walk() == [["a", "b", "c", "d", "e"]]
```
