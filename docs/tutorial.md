# Tutorial

This tutorial builds a small workflow graph step by step and shows the most common things that **holden** can do with it. Every example on this page is run by the test suite, so you can copy any of them as they are.

## Nodes and edges

A **node** is any hashable object. The simplest nodes are strings or numbers. An **edge** is a `tuple` of two nodes, where the first node comes before the second.

```python
import holden

edge = ("load", "clean")
assert holden.is_node("load")
assert holden.is_edge(edge)
assert not holden.is_edge(["load", "clean"])  # lists are used for paths
```

If you want an edge that has attributes, or that is a drop-in replacement for a `tuple`, use `Edge`.

```python
edge = holden.Edge("load", "clean")
start, stop = edge
assert (start, stop) == ("load", "clean")
assert edge == ("load", "clean")
assert edge[0] == "load"
```

## Creating a graph

`System` is a directed graph that stores its nodes in an adjacency list (a `dict` where each key is a node and each value is a `set` of the nodes it points to). Create one by adding nodes and connecting them.

```python
workflow = holden.System()
workflow.add("load")
workflow.add("clean")
workflow.add("model")
workflow.connect(("load", "clean"))
workflow.connect(("clean", "model"))

assert workflow["load"] == {"clean"}
assert workflow.nodes == {"load", "clean", "model"}
assert "clean" in workflow
```

The methods check what you give them and raise an error that says what is wrong.

```python
import pytest

with pytest.raises(ValueError):
    workflow.add("load")  # already in the graph
with pytest.raises(ValueError):
    workflow.connect(("load", "missing"))  # 'missing' is not a node
with pytest.raises(ValueError):
    workflow.connect(("load", "load"))  # an edge cannot loop back
with pytest.raises(KeyError):
    workflow.delete("missing")
with pytest.raises(TypeError):
    workflow.add(["not", "hashable"])
```

You can also create a graph from data that you already have. Use the `from_{form}` class methods with an edge list, an adjacency list, an adjacency matrix, a list of paths, or a single path.

```python
from_edges = holden.System.from_edges([("a", "b"), ("b", "c")])
from_adjacency = holden.System.from_adjacency(
    {"a": {"b"}, "b": {"c"}, "c": set()})
from_matrix = holden.System.from_matrix(
    ([[0, 1, 0], [0, 0, 1], [0, 0, 0]], ["a", "b", "c"]))
from_parallel = holden.System.from_parallel([["a", "b", "c"]])
from_serial = holden.System.from_serial(["a", "b", "c"])

assert from_edges == from_adjacency == from_matrix
assert from_edges == from_parallel == from_serial
```

## Changing a graph

`delete` removes a node and every edge that includes it. `disconnect` removes only an edge.

```python
workflow.add("report")
workflow.connect(("model", "report"))
workflow.disconnect(("model", "report"))
assert workflow["model"] == set()
workflow.delete("report")
assert "report" not in workflow
```

`merge` adds another graph (of any form) to the graph. It works like `dict.update`, keeping the connections that already exist.

```python
workflow.merge([("model", "score"), ("model", "plot")])
assert workflow["model"] == {"score", "plot"}
```

`subset` returns a new graph with only some of the nodes. Any edge that includes a node that is not kept is dropped. The original graph is not changed.

```python
small = workflow.subset(include=["load", "clean"])
assert small.nodes == {"load", "clean"}
assert small["clean"] == set()
without_plot = workflow.subset(exclude="plot")
assert "plot" not in without_plot
assert "plot" in workflow
```

## Roots, endpoints, and paths

A **root** is a node that no other node points to. An **endpoint** is a node that points to no other node. A **path** goes from a root to an endpoint.

```python
assert workflow.root == ["load"]
assert workflow.endpoint == ["score", "plot"]
assert workflow.walk() == [
    ["load", "clean", "model", "score"],
    ["load", "clean", "model", "plot"]]
```

Pass `start` and/or `stop` to `walk` to look for paths between particular nodes.

```python
assert workflow.walk("clean", "score") == [["clean", "model", "score"]]
assert workflow.walk(stop="plot") == [["load", "clean", "model", "plot"]]
assert workflow.walk("plot", "load") == []
```

Paths never visit a node twice, so a graph with a cycle will not cause an endless loop.

## Joining graphs

`append` connects every endpoint of a graph to every root of another graph (or to a single node). `prepend` connects every endpoint of the other graph to every root of the graph. The `+` and `+=` operators use `append`.

```python
pipeline = holden.System.from_edges([("load", "clean")])
pipeline.append("model")
assert pipeline.walk() == [["load", "clean", "model"]]
pipeline.prepend("download")
assert pipeline.walk() == [["download", "load", "clean", "model"]]

report = holden.System.from_edges([("score", "publish")])
pipeline += report
assert pipeline.walk() == [
    ["download", "load", "clean", "model", "score", "publish"]]
```

## Other forms

The way that a graph is stored inside is called its **form**. **holden** has three forms of graph: `Adjacency`, `Edges`, and `Matrix`; and two forms of paths: `Serial` and `Parallel`. Every graph has a property for each form.

```python
dag = holden.System.from_edges([("a", "b"), ("c", "d"), ("a", "d")])

assert dag.edges.contents == [("a", "b"), ("a", "d"), ("c", "d")]
assert dag.matrix.labels == ["a", "b", "c", "d"]
assert dag.matrix.contents == [
    [0, 1, 0, 1], [0, 0, 0, 0], [0, 0, 0, 1], [0, 0, 0, 0]]
assert dag.parallel.contents == [["a", "b"], ["a", "d"], ["c", "d"]]
assert dag.adjacency is dag
```

The properties return instances of `Edges`, `Matrix`, `Parallel`, and `Serial`, so they can be used like any other composite data structure.

```python
matrix = dag.matrix
matrix.add("e")
matrix.connect(("d", "e"))
assert holden.System.from_matrix(matrix).endpoint == ["b", "e"]
assert dag.nodes == {"a", "b", "c", "d"}  # dag is not changed
```

## Exporting

Graphs can be exported to [Graphviz](https://graphviz.org/) `dot` and [mermaid](https://mermaid.js.org/) flowcharts.

```python
assert dag.to_dot(name="dag") == "\n".join([
    "digraph dag {",
    "a -> b",
    "a -> d",
    "c -> d",
    "}",
    ""])
assert dag.to_mermaid(name="dag").splitlines()[:4] == [
    "---", "title: dag", "---", "flowchart LR"]
```

Pass a `path` to also save the file. `to_dot` and `to_mermaid` are also functions that work on any form of graph, including raw lists and dicts.

```python
import pathlib
import tempfile

with tempfile.TemporaryDirectory() as folder:
    path = pathlib.Path(folder) / "dag.dot"
    holden.to_dot([("a", "b")], path=path, name="raw")
    assert path.read_text() == "graph raw {\na -- b\n}\n"
```

## Next steps

* The [recipes](recipes.md) show how to solve some common problems.
* The [advanced user guide](advanced.md) explains structural subtyping, traits, custom forms, and how to extend **holden**.
* The API reference has the details of every class and function.
