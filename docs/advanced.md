# Advanced User Guide

This guide explains how **holden** is put together and how to extend it. Every example on this page is run by the test suite.

## Structural subtyping

The `is_{form}` functions in `holden.check` look at the structure of an object rather than its class. So, a plain `dict` of `set` values is an adjacency list, even if it was not created by **holden**.

| Form | Raw structure | Checker |
| --- | --- | --- |
| `adjacency` | `dict[Node, set[Node]]` | `is_adjacency` |
| `edges` | `list[tuple[Node, Node]]` | `is_edges` |
| `matrix` | `tuple[list[list[float]], list[Node]]` of a matrix and labels | `is_matrix` |
| `parallel` | `list[list[Node]]` | `is_parallel` |
| `serial` | `list[Node]` | `is_serial` |

```python
import dataclasses

import holden

raw = {"a": {"b"}, "b": set()}
assert holden.is_adjacency(raw)
assert isinstance(raw, holden.Adjacency)  # a raw structure is an instance
assert not isinstance(raw, holden.Edges)
assert isinstance(holden.System(raw), holden.Adjacency)
```

Some raw structures can match more than one form. An empty `list` is a valid edge list, path list, and path. `holden.classify` checks the forms in this order: `adjacency`, `edges`, `matrix`, `parallel`, `serial`, and then any forms that you have registered.

```python
assert holden.classify([]) == "edges"
```

Only the classes for registered forms (see below) accept raw structures in `isinstance`. A subclass, such as `System`, only has instances that were created from it.

```python
assert not isinstance(raw, holden.System)
```

### Add your own checker

`add_checker` adds a function to `holden.check`, so that `classify` can use it. The name must be `is_{form}`, where `form` is the name of a registered form.

```python
@dataclasses.dataclass
class Bag(holden.Composite):
    """Unordered collection of nodes."""

    contents: set = dataclasses.field(default_factory=set)

    @property
    def nodes(self):
        return set(self.contents)

    def _add(self, item, **kwargs):
        self.contents.add(item)

    def _delete(self, item, **kwargs):
        self.contents.discard(item)

    def _merge(self, item, **kwargs):
        self.contents.update(item)

    def _subset(self, include=None, exclude=None):
        return self.__class__(set(self._selected(self.contents, include, exclude)))


holden.add_checker("is_bag", lambda item: isinstance(item, set))
assert holden.classify({"a", "b"}) == "bag"
```

## The registry of forms

`holden.Forms` is a registry. Every class that inherits directly from `Composite` (or, for graphs, from `Graph`) is added to it when the class is created. The key is the snake case name of the class. Subclasses of those classes, like `System`, are not registered.

```python
assert holden.Forms.registry["bag"] is Bag
assert holden.Forms.registry["adjacency"] is holden.Adjacency
assert "system" not in holden.Forms.registry
```

A registered form is used by `classify` (for classes) and by `Forms.transform` (which returns an instance of the registered class).

To use your own class for a form, subclass the form and call `holden.set_base`.

```python
@dataclasses.dataclass
class LoggedEdges(holden.Edges):
    """Edge list that could do something useful when it is used."""


original = holden.get_base("edges")
holden.set_base("edges", LoggedEdges)
try:
    system = holden.System.from_edges([("a", "b")])
    assert type(system.edges) is LoggedEdges
finally:
    holden.set_base("edges", original)
assert type(system.edges) is holden.Edges
```

## Writing a form

A composite data structure needs the `nodes` property and the `_add`, `_delete`, `_merge`, and `_subset` methods. Graphs also need `_connect` and `_disconnect`. The public methods (`add`, `delete`, `merge`, `subset`, `connect`, and `disconnect`) do all of the error checking, so the private methods only have to do the work for the way that the data is stored. The `Bag` above is a complete example.

```python
bag = Bag()
bag.add("a")
bag.add("b")
assert bag.nodes == {"a", "b"}
assert "a" in bag
bag.delete("a")
assert bag.subset(include="b").contents == {"b"}
bag.merge({"c", "d"})
assert bag.nodes == {"b", "c", "d"}
```

`_selected(nodes, include, exclude)` is a helper for `_subset`. It returns the nodes that are in `include` (unless `include` is `None`) and not in `exclude`.

Because `Bag` does not have edges, it is not a graph. To make a graph, inherit directly from `Graph` and provide the connection methods. A graph that can only store nodes that are part of an edge (such as an edge list) should set `_implicit_nodes = True`. Then `connect` creates the nodes that are missing instead of raising an error.

Conversions to and from a new form need transformers. `add_transformer` adds a function to `holden.workshop`, where `transform` looks for `{source}_to_{output}` functions. Only a conversion to and from one form (usually `adjacency`) is required if you add every conversion that you need.

```python
def bag_to_adjacency(item):
    return {node: set() for node in item}


def adjacency_to_bag(item):
    return set(item)


holden.add_transformer("bag_to_adjacency", bag_to_adjacency)
holden.add_transformer("adjacency_to_bag", adjacency_to_bag)
assert holden.transform({"a", "b"}, "adjacency") == {"a": set(), "b": set()}
assert holden.transform({"a": {"b"}, "b": set()}, "bag") == {"a", "b"}
assert isinstance(holden.Forms.transform({"a"}, "adjacency"), holden.Adjacency)
```

## Traits

Traits are mixins. Put them in front of the form in the list of base classes. `Directed` must be before the form so that the `+` operators of `Directed` are used.

| Trait | Adds |
| --- | --- |
| `Directed` | `root`, `endpoint`, `walk`, `append`, `prepend`, `+`, `+=`, and reflected `+` |
| `Exportable` | `to_dot` and `to_mermaid` |
| `Fungible` | properties for every form and `from_{form}` class methods |
| `Labeled` | a `name` that is used for hashing and equality |
| `Storage` | a `library` with `store`, `retrieve`, and `discard` |
| `Weighted` | a `weight` and `float()` |

```python
@dataclasses.dataclass
class Network(
        holden.Directed, holden.Fungible, holden.Exportable, holden.Matrix):
    """Directed graph that is stored as an adjacency matrix."""


network = Network.from_edges([("a", "b"), ("b", "c")])
assert isinstance(network.contents, list)
assert network.labels == ["a", "b", "c"]
assert network.walk() == [["a", "b", "c"]]
assert network.to_dot(name="network").startswith("digraph network")
```

`System` is a class with `Directed`, `Fungible`, and `Exportable` on top of `Adjacency`. `Serial` and `Parallel` also include them.

### Weighted edges and nodes

`Edge` subclasses can add fields. They are still edges: only the start and stop are used for indexing, unpacking, and `len`.

```python
@dataclasses.dataclass(frozen=True)
class WeightedEdge(holden.Edge):
    weight: float = 1.0


edge = WeightedEdge("a", "b", 2.5)
assert tuple(edge) == ("a", "b")
edges = holden.Edges()
edges.connect(edge)
assert edges.nodes == {"a", "b"}
```

`Weighted` adds the weight to something that is not a frozen dataclass, such as a `Node`.

```python
@dataclasses.dataclass
class WeightedNode(holden.Weighted, holden.Node):
    pass


assert float(WeightedNode("a", weight=2)) == 2.0
```

A `Matrix` stores the weight of an edge as the value in the matrix. Any value that is not zero is an edge, and `connect` does not overwrite a value that is already there.

```python
weighted = holden.Matrix([[0, 4.5], [0, 0]], ["a", "b"])
weighted.connect(("a", "b"))
assert weighted.contents[0][1] == 4.5
assert holden.matrix_to_adjacency(weighted) == {"a": {"b"}, "b": set()}
```

## Paths

`Serial` and `Parallel` store paths instead of graphs. A `Serial` is a single path. A `Parallel` is several paths.

```python
serial = holden.Serial(["load", "clean", "model"])
assert serial.root == ["load"]
assert serial.endpoint == ["model"]
assert serial.walk("clean") == [["clean", "model"]]
assert serial[0] == "load"
assert serial[1:] == ["clean", "model"]
assert serial["clean"] == "clean"  # access by name is inherited from `bunches`

parallel = holden.Parallel([["a", "b"], ["a", "c"]])
assert parallel.root == ["a"]
assert parallel.endpoint == ["b", "c"]
assert parallel.nodes == {"a", "b", "c"}
```

Appending to a `Parallel` follows the meaning of appending to a graph: every path is followed by every path of the appended item.

```python
parallel.append([["x"], ["y"]])
assert parallel.contents == [
    ["a", "b", "x"], ["a", "b", "y"], ["a", "c", "x"], ["a", "c", "y"]]
```

Converting a graph to a `Serial` follows the paths from its roots to its endpoints. If there is only one path, that path is returned. If there is more than one, the paths are joined end to end. Converting to a `Parallel` returns the paths themselves.

```python
dag = holden.System.from_edges([("a", "b"), ("a", "c")])
assert dag.parallel.contents == [["a", "b"], ["a", "c"]]
assert dag.serial.contents == ["a", "b", "a", "c"]
assert holden.System.from_edges([("a", "b"), ("b", "c")]).serial.contents == [
    "a", "b", "c"]
```

Graphs that have cycles have no roots on the cycle, so paths that need to start on a cycle are not found. A path never visits the same node twice.

## Functional style

Everything that the classes do can also be done with functions that take and return raw structures.

| Module | Functions |
| --- | --- |
| `holden.check` | `is_adjacency`, `is_composite`, `is_edge`, `is_edges`, `is_graph`, `is_matrix`, `is_node`, `is_nodes`, `is_parallel`, `is_serial` |
| `holden.workshop` | `{form}_to_{form}` transformers |
| `holden.report` | `get_roots`, `get_endpoints`, and `get_roots_{form}` and `get_endpoints_{form}` for each form |
| `holden.traverse` | `walk` and `walk_{form}` for each form |
| `holden.export` | `to_dot` and `to_mermaid` |

```python
adjacency = {"a": {"b", "c"}, "b": set(), "c": set()}
assert holden.get_roots(adjacency) == ["a"]
assert holden.get_endpoints_adjacency(adjacency) == ["b", "c"]
assert holden.walk(adjacency) == [["a", "b"], ["a", "c"]]
assert holden.walk_adjacency(adjacency, "a", "c") == [["a", "c"]]
```

## Determinism

The connections of a node in an adjacency list are stored in a `set`, which does not have a stable order between python sessions. Every function in **holden** that iterates over a `set` (the conversions, `walk`, and the exporters) sorts by the `str` of each node so that its output is reproducible. Nodes that are the keys of a `dict` keep their order of insertion.

## Performance

**holden** is designed for clarity and small graphs, not for speed. `walk` finds every path, so the number of paths that it returns can grow exponentially with the size of the graph. `walk_adjacency` uses a loop rather than recursion, so the depth of a path is not limited by the recursion limit of python.
