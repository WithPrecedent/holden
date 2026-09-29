# holden

| | |
| --- | --- |
| Version | [![PyPI Latest Release](https://img.shields.io/pypi/v/holden.svg?style=for-the-badge&color=steelblue&label=PyPI&logo=PyPI&logoColor=yellow)](https://pypi.org/project/holden/) [![GitHub Latest Release](https://img.shields.io/github/v/tag/WithPrecedent/holden?style=for-the-badge&color=navy&label=GitHub&logo=github)](https://github.com/WithPrecedent/holden/releases)
| Status | [![Build Status](https://img.shields.io/github/actions/workflow/status/WithPrecedent/holden/ci.yml?branch=main&style=for-the-badge&color=cadetblue&label=Tests&logo=pytest)](https://github.com/WithPrecedent/holden/actions/workflows/ci.yml?query=branch%3Amain) [![Development Status](https://img.shields.io/badge/Development-Active-seagreen?style=for-the-badge&logo=git)](https://www.repostatus.org/#active) [![Project Stability](https://img.shields.io/pypi/status/holden?style=for-the-badge&logo=pypi&label=Stability&logoColor=yellow)](https://pypi.org/project/holden/)
| Documentation | [![Hosted By](https://img.shields.io/badge/Hosted_by-Github_Pages-blue?style=for-the-badge&color=navy&logo=github)](https://WithPrecedent.github.io/holden)
| Tools | [![Documentation](https://img.shields.io/badge/MkDocs-magenta?style=for-the-badge&color=deepskyblue&logo=markdown&labelColor=gray)](https://squidfunk.github.io/mkdocs-material/) [![Linter](https://img.shields.io/endpoint?style=for-the-badge&url=https://raw.githubusercontent.com/charliermarsh/Ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/Ruff) [![Dependency Manager](https://img.shields.io/badge/PDM-mediumpurple?style=for-the-badge&logo=affinity&labelColor=gray)](https://PDM.fming.dev) [![Pre-commit](https://img.shields.io/badge/pre--commit-darkolivegreen?style=for-the-badge&logo=pre-commit&logoColor=white&labelColor=gray)](https://github.com/TezRomacH/python-package-template/blob/master/.pre-commit-config.yaml) [![CI](https://img.shields.io/badge/GitHub_Actions-navy?style=for-the-badge&logo=githubactions&labelColor=gray&logoColor=white)](https://github.com/features/actions) [![Editor Settings](https://img.shields.io/badge/Editor_Config-paleturquoise?style=for-the-badge&logo=editorconfig&labelColor=gray)](https://editorconfig.org/) [![Repository Template](https://img.shields.io/badge/snickerdoodle-bisque?style=for-the-badge&logo=cookiecutter&labelColor=gray)](https://www.github.com/WithPrecedent/holden) [![Dependency Maintainer](https://img.shields.io/badge/dependabot-navy?style=for-the-badge&logo=dependabot&logoColor=white&labelColor=gray)](https://github.com/dependabot)
| Compatibility | [![Compatible Python Versions](https://img.shields.io/pypi/pyversions/holden?style=for-the-badge&color=steelblue&label=Python&logo=python&logoColor=yellow)](https://pypi.python.org/pypi/holden/) [![Linux](https://img.shields.io/badge/Linux-lightseagreen?style=for-the-badge&logo=linux&labelColor=gray&logoColor=white)](https://www.linux.org/) [![MacOS](https://img.shields.io/badge/MacOS-snow?style=for-the-badge&logo=apple&labelColor=gray)](https://www.apple.com/macos/) [![Windows](https://img.shields.io/badge/windows-blue?style=for-the-badge&logo=Windows&labelColor=gray&color=orangered)](https://www.microsoft.com/en-us/windows?r=1)
| Stats | [![PyPI Download Rate (per month)](https://img.shields.io/pypi/dm/holden?style=for-the-badge&color=steelblue&label=Downloads%20💾&logo=pypi&logoColor=yellow)](https://pypi.org/project/holden) [![GitHub Stars](https://img.shields.io/github/stars/WithPrecedent/holden?style=for-the-badge&color=navy&label=Stars%20⭐&logo=github)](https://github.com/WithPrecedent/holden/stargazers) [![GitHub Contributors](https://img.shields.io/github/contributors/WithPrecedent/holden?style=for-the-badge&color=navy&label=Contributors%20🙋&logo=github)](https://github.com/WithPrecedent/holden/graphs/contributors) [![GitHub Issues](https://img.shields.io/github/issues/WithPrecedent/holden?style=for-the-badge&color=navy&label=Issues%20📘&logo=github)](https://github.com/WithPrecedent/holden/graphs/contributors) [![GitHub Forks](https://img.shields.io/github/forks/WithPrecedent/holden?style=for-the-badge&color=navy&label=Forks%20🍴&logo=github)](https://github.com/WithPrecedent/holden/forks)
| | |

-----

## What is holden?

<p align="center">
<img src="https://media.giphy.com/media/3ornjRyce6SukW8INi/giphy.gif" />
</p>

This package is named after the Roci's captain in *The Expanse*, James Holden, who was adept at furling his brow and recognizing connections. In a similar vein, **holden** offers users easy-to-use composite data structures without the overhead or complexity of larger graph packages. The included graphs are built for basic workflow design or analysis of conditional relationships. They are not designed for big data network analysis or similar large-scale projects (although nothing prevents you from using them in that manner). Rather, the goal of **holden** is to provide lightweight, turnkey, extensible composite data structures without all of the stuff you don't need in packages like [networkx](https://github.com/networkx/networkx). **holden** serves as the base for my [chrisjen](https://github.com/WithPrecedent/chrisjen) workflow package (similarly named for a character from The Expanse), but I have made **holden** available separately for easier integration into other uses.

## Why use holden?


## Simple

The basic building blocks provided are:
* `Composite`: the abstract base class for all types of composite data structures
* `Graph`: subclass of `Composite` and the base class for all graph data structures
* `Edge`: an optional edge class which can be treated as a drop-in `tuple` replacement or extended for greater functionality
* `Node`: an optional vertex class which provides universal hashability and some other convenient functions
* `Forms`: a registry that automatically stores all direct `Composite` subclasses to allow flexible subtype checking of and transformation between composite subtypes using its `classify` and `transform` methods

Out of the box, `Graph` has several subtypes with varying internal storage formats:
* `Adjacency`: an adjacency list using a `dict[Node, set[Node]]` structure
* `Matrix`: an adjacency matrix that uses a `list[list[float | int]]` for mapping edges and a separate `list[Node]` attribute (`labels`) that corresponds to the rows and columns of the matrix
* `Edges`: an edge list structure that uses a `list[tuple[Node, Node]]` format

Paths through a graph are stored in two other composite data structures:
* `Serial`: a single path, stored as a `list[Node]`
* `Parallel`: a collection of paths, stored as a `list[list[Node]]`

`System` is a ready-to-use directed graph that is stored as an adjacency list. It combines the `Adjacency` form with the traits described below.

You can use **holden** without any regard to what is going on inside the graph. The methods and properties are the same regardless of which internal format is used. But the different forms are provided in case you want to utilize the advantages or avoid certain drawbacks of a particular form. Unless you want to design a different graph form, you should design subclasses to inherit from one of the
included forms and add mixins to expand functionality.

## Flexible

 Various traits can be added to graphs, nodes, and edges as mixins including:
* Weighted edges (`Weighted`)
* Ability to create a graph from or convert any graph to any recognized form using properties and class methods with consistent syntax (`Fungible`)
* Directed graphs with roots, endpoints, paths, and `+` for joining graphs (`Directed`)
* Automatically names objects if a name is not passed (`Labeled`)
* Has methods to convert and export to other graph formats (`Exportable`)
* Ability to store node data internally for easy reuse separate from the graph structure (`Storage`)

**holden** provides transformation methods between all of the internal storage forms as well as functions to convert graphs into a set of paths (`Parallel`) or a single path (`Serial`). The transformation methods can be used as class properties or with functions using an easy-to-understand naming convention (e.g., `adjacency_to_edges` or `edges_to_parallel`).

**holden**'s framework supports a wide range of coding styles. You can create complex multiple inheritance structures with mixins galore or simpler, compositional objects. Even though the data structures are necessarily object-oriented, all of the tools to modify them are also available as functions, for those who prefer a more functional approach to programming.

The package also uses structural subtyping that allows raw forms of the supported composite subtypes to be used and recognized as the same forms for which **holden** includes classes. So, for example, the `is_adjacency` function will recognize any object with a `dict[Node, set[Node]]` structure and `isinstance(item, holden.Adjacency)` will similarly return `True` for a raw adjacency list.


## Getting started

### Requirements

**holden** requires Python 3.11 or later. It runs on Linux, macOS, and Windows. Its only dependencies are [bunches](https://github.com/WithPrecedent/bunches) (the base classes for its collections) and [wonka](https://github.com/WithPrecedent/wonka) (the base class for its registry). Both are installed automatically by `pip`.

### Installation

To install `holden`, use `pip`:

```sh
pip install holden
```

### Usage

#### Build a graph

A `System` can be created from any raw form of a graph: an edge list, an adjacency list, an adjacency matrix, a list of paths, or a single path. Nodes can be any hashable object, but the examples here use strings.

```python
import holden
edges = [("a", "b"), ("c", "d"), ("a", "d"), ("d", "e")]
dag = holden.System.from_edges(edges)
dag["a"] == {"b", "d"}  # True
dag.nodes == {"a", "b", "c", "d", "e"}  # True
"c" in dag  # True
"z" in dag  # False
```

A graph can also be built by hand. Nodes must be added before they are connected and an edge cannot connect a node to itself.

```python
workflow = holden.System()
for step in ("load", "clean", "model", "report"):
    workflow.add(step)
workflow.connect(("load", "clean"))
workflow.connect(("clean", "model"))
workflow.connect(("model", "report"))
workflow.walk()  # [['load', 'clean', 'model', 'report']]
workflow.disconnect(("model", "report"))
workflow.delete("report")
workflow.endpoint  # ['model']
```

`add`, `delete`, `connect`, `disconnect`, `merge`, and `subset` work the same way for every form of graph. Each one raises an informative error (`TypeError`, `ValueError`, or `KeyError`) if it is passed something that does not make sense.

```python
dag.merge({"e": {"f"}, "f": set()})
dag["e"] == {"f"}  # True
smaller = dag.subset(exclude=["f", "e"])
smaller.nodes == {"a", "b", "c", "d"}  # True
# Raises ValueError: The starting point of an edge cannot be the same as the ending point
dag.connect(("a", "a"))
```

#### Find roots, endpoints, and paths

A directed graph has roots (nodes with nothing pointing at them), endpoints (nodes that point at nothing), and paths from roots to endpoints. `walk` returns every path. A start and/or a stop can be passed to limit the paths.

```python
dag.root  # ['a', 'c']
dag.endpoint  # ['b', 'f']
dag.walk("c")  # [['c', 'd', 'e', 'f']]
dag.walk("a", "f")  # [['a', 'd', 'e', 'f']]
```

Graphs can be joined with `append` and `prepend` (or `+` and `+=`). Appending connects every endpoint of the graph to every root of the joined graph. A single node can also be appended or prepended.

```python
pipeline = holden.System.from_edges([("load", "clean")])
pipeline.append("model")
pipeline.prepend("download")
pipeline.walk()  # [['download', 'load', 'clean', 'model']]
pipeline += holden.System.from_edges([("report", "email")])
pipeline.endpoint  # ['email']
```

#### Change the form

Every graph can be viewed in every other form using the properties of the `Fungible` trait. Each property returns an instance of the class for that form. The `from_{form}` class methods create a new graph from any raw form or instance.

```python
dag = holden.System.from_edges(edges)
dag.edges.contents  # [('a', 'b'), ('a', 'd'), ('c', 'd'), ('d', 'e')]
dag.matrix.labels  # ['a', 'b', 'c', 'd', 'e']
dag.matrix.contents[0]  # [0, 1, 0, 1, 0]
dag.parallel.contents  # [['a', 'b'], ['a', 'd', 'e'], ['c', 'd', 'e']]
dag.serial.contents  # ['a', 'b', 'a', 'd', 'e', 'c', 'd', 'e']
same_dag = holden.System.from_matrix(dag.matrix)
same_dag == dag  # True
```

A `Serial` is a single path. When a graph has one path, the `Serial` is that path. When a graph has more than one path, its paths are joined end to end (as shown above). A `Parallel` keeps the paths separate.

If you prefer functions, every conversion is also available as a function that takes and returns raw structures. The names are `{form}_to_{form}`.

```python
holden.adjacency_to_edges({"a": {"b"}, "b": set()})  # [('a', 'b')]
holden.edges_to_matrix([("a", "b")])  # ([[0, 1], [0, 0]], ['a', 'b'])
holden.matrix_to_parallel(([[0, 1], [0, 0]], ["a", "b"]))  # [['a', 'b']]
holden.transform([("a", "b"), ("b", "c")], "serial")  # ['a', 'b', 'c']
```

#### Use raw structures

Because **holden** uses structural subtyping, you can ask about the form of any object. The `is_{form}` functions check the structure and `classify` returns the name of the form.

```python
raw = {"a": {"b"}, "b": set()}
holden.is_adjacency(raw)  # True
holden.is_edges(raw)  # False
holden.classify(raw)  # 'adjacency'
isinstance(raw, holden.Adjacency)  # True
isinstance([("a", "b")], holden.Edges)  # True
isinstance(raw, holden.Edges)  # False
```

An edge is a `tuple` of two nodes (or an `Edge`). Lists are used for paths.

```python
holden.is_edge(("a", "b"))  # True
holden.is_edge(["a", "b"])  # False
holden.Edge("a", "b") == ("a", "b")  # True
```

#### Export a graph

The `Exportable` trait (part of `System`) exports to [Graphviz](https://graphviz.org/) `dot` and [mermaid](https://mermaid.js.org/) formats. Both return a `str` and, if a `path` is passed, save a file.

```python
print(dag.to_dot(name="dag"), end="")
# Output:
# digraph dag {
# a -> b
# a -> d
# c -> d
# d -> e
# }

print(dag.to_mermaid(name="dag"), end="")
# Output:
# ---
# title: dag
# ---
# flowchart LR
#     a(a) --> b(b)
#     a(a) --> d(d)
#     c(c) --> d(d)
#     d(d) --> e(e)
```

Rendered, the two exports look like this:

<p align="center">
<img src="https://raw.githubusercontent.com/WithPrecedent/holden/main/docs/img/export_graphviz.png" alt="Graphviz rendering of the dag" height="260" />
&nbsp;&nbsp;&nbsp;&nbsp;
<img src="https://raw.githubusercontent.com/WithPrecedent/holden/main/docs/img/export_mermaid.png" alt="Mermaid rendering of the dag" height="260" />
</p>

The functions `holden.to_dot` and `holden.to_mermaid` do the same for any form of graph, including raw structures.

#### Name nodes and store data

The `Labeled` trait gives nodes a `name`. Labeled nodes are hashed and compared by name, so the name can be used anywhere the node could be.

```python
import dataclasses

@dataclasses.dataclass
class Step(holden.Labeled, holden.Node):
    pass

flow = holden.System()
flow.add(Step(name="load"))
flow.add(Step(name="clean"))
flow.connect(("load", "clean"))
"clean" in flow["load"]  # True
flow.root[0].name  # 'load'
```

The `Storage` trait stores data for nodes in a `library`, so the graph itself can be made of lightweight labels.

```python
@dataclasses.dataclass
class Workflow(holden.Storage, holden.System):
    pass

workflow = Workflow.from_edges([("load", "clean")])
workflow.store("load", "load_data.py")
workflow.retrieve("load")  # 'load_data.py'
```

#### Build your own

Any direct subclass of `Composite` is added to `Forms`. Any subclass of a form (such as `Adjacency`) inherits the behavior of that form and can add traits as mixins. See the [advanced user guide](https://WithPrecedent.github.io/holden/advanced) for details.

```python
@dataclasses.dataclass
class Pipeline(holden.Directed, holden.Edges, holden.Fungible):
    pass

pipeline = Pipeline.from_adjacency({"load": {"clean"}, "clean": set()})
pipeline.contents  # [('load', 'clean')]
pipeline.walk()  # [['load', 'clean']]
```

An `Edges` graph only stores nodes that are part of an edge, so `connect` (rather than `add`) is used to build one up. All of the other forms store nodes on their own.

## Contributing

Contributors are always welcome. Feel free to grab an [issue](https://www.github.com/WithPrecedent/holden/issues) to work on or make a suggested improvement. If you wish to contribute, please read the [Contribution Guide](https://www.github.com/WithPrecedent/holden/contributing.md) and [Code of Conduct](https://www.github.com/WithPrecedent/holden/code_of_conduct.md).

## Similar Projects

* [networkx](https://github.com/networkx/networkx): the market leader for python graphs. Offers greater flexibility and extensibility at the cost of substantial overhead.

## Acknowledgments

**holden** is named for James Holden and his crew from *The Expanse* by James S. A. Corey (the pen name of Daniel Abraham and Ty Franck). The graph algorithms for finding paths are adapted from [Python Patterns - Implementing Graphs](https://www.python.org/doc/essays/graphs/) by Guido van Rossum, and the sliding window function is adapted from [more-itertools](https://github.com/more-itertools/more-itertools).

## License

Use of this repository is authorized under the [Apache Software License 2.0](https://www.github.com/WithPrecedent/holden/blog/main/LICENSE).

<p align="center">
<img src="https://media.giphy.com/media/3oKIPwyf0EBAGnAkWk/giphy.gif" />
</p>
