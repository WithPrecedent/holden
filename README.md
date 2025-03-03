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

This repository is under heavy construction.

<p align="center">
<img src="https://media.giphy.com/media/3ornjRyce6SukW8INi/giphy.gif" />
</p>

This package is named after the Roci's captain in *The Expanse*, James Holden, who was adept at furling his brow and recognizing connections. In a similar vein, **holden** offers users easy-to-use composite data structures without the overhead or complexity of larger graph packages. The included graphs are built for basic workflow design or analysis of conditional relationships. They are not designed for big data network analysis or similar large-scale projects (although nothing prevents you from using them in that manner). Rather, the goal of **holden** is to provide lightweight, turnkey, extensible composite data structures without all of the stuff you don't need in packages like [networkx](https://github.com/networkx/networkx). **holden** serves as the base for my [chrisjen](https://github.com/WithPrecedent/chrisjen) workflow package (similarly named for a character from The Expanse), but I have made **holden** available separately for easier integration into other uses.

## Why use holden?


## Simple

The basic building blocks provided are:
* `Composite`: the abstract base class for all types of a composite data structures
* `Graph`: subclass of Composite and the base class for all graph data structures
* `Edge`: an optional edge class which can be treated as a drop-in tuple replacement or extended for greater functionality
* `Node`: an optional vertex class which provides universal hashability and some other convenient functions
* `Forms`: a dictionary that automatically stores all direct Compisite subclasses to allow flexible subtype checking of and transformation between composite subtypes using its `classify` and `transform` methods

Out of the box, Graph has several subtypes with varying internal storage formats:
* `Adjacency`: an adjacency list using a `dict(Node, set(Node))` structure
* `Matrix`: an adjacency matrix that uses a `list[list[float | int]]` for mapping edges and a separate `list[str]` attribute that corresponds to the list of lists matrix
* `Edges`: an edge list structure that uses a `list[tuple[Node, Node]]` format

You can use **holden** without any regard to what is going on inside the graph. The methods and properties are the same regardless of which internal format is used. But the different forms are provided in case you want to utilize the advantages or avoid certain drawbacks of a particular form. Unless you want to design a different graph form, you should design subclasses to inherit from one of the
included forms and add mixins to expand functionality.

## Flexible

 Various traits can be added to graphs, nodes, and edges as mixins including:
* Weighted edges (`Weighted`)
* Abilty to create a graph from or convert any graph to any recognized form using properties with consistent syntax (`Fungible`)
* Directed graphs (`Directed`)
* Automatically names objects if a name is not passed (`Labeled`)
* Has methods to convert and export to other graph formats (`Exportable`)
* Ability to store node data internally for easy reuse separate from the graph structure (`Storage`)

**holden** provides transformation methods between all of the internal storage forms as well as functions to convert graphs into a set of paths (`Parallel`) or a single path (`Serial`). The transformation methods can be used as class properties or with functions using an easy-to-understand naming convention (e.g., adjacency_to_edges or edges_to_parallel).

**holden**'s framework supports a wide range of coding styles. You can create complex multiple inheritance structures with mixins galore or simpler, compositional objects. Even though the data structures are necessarily object-oriented, all of the tools to modify them are also available as functions, for those who prefer a more functional approaching to programming.

The package also uses structural subtyping that allows raw forms of the supported composite subtypes to be used and recognized as the same forms for which **holden** includes classes. So, for example, the is_adjacency function will recognize any object with a dict(Node, set(Node)) structure and isinstance(item, **holden**.Adjacency) will similarly return True for a raw adjacency list.


## Getting started

### Requirements

[TODO: List any OS or other restrictions and pre-installation dependencies]

### Installation

To install `holden`, use `pip`:

```sh
pip install holden
```

### Usage

[TODO: Describe common use cases, with possible example(s)]

## Contributing

Contributors are always welcome. Feel free to grab an [issue](https://www.github.com/WithPrecedent/holden/issues) to work on or make a suggested improvement. If you wish to contribute, please read the [Contribution Guide](https://www.github.com/WithPrecedent/holden/contributing.md) and [Code of Conduct](https://www.github.com/WithPrecedent/holden/code_of_conduct.md).

## Similar Projects

* [networkx](https://github.com/networkx/networkx): the market leader for python graphs. Offers greater flexibility and extensibility at the cost of substantial overhead.

## Acknowledgments

[TODO: Mention any people or organizations that warrant a special acknowledgment]

## License

Use of this repository is authorized under the [Apache Software License 2.0](https://www.github.com/WithPrecedent/holden/blog/main/LICENSE).

<p align="center">
<img src="https://media.giphy.com/media/3oKIPwyf0EBAGnAkWk/giphy.gif" />
</p>