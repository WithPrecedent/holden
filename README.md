[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) [![PyPI Latest Release](https://img.shields.io/pypi/v/holden.svg)](https://pypi.org/project/holden/) [![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) [![Documentation Status](https://readthedocs.org/projects/holden/badge/?version=latest)](http://holden.readthedocs.io/?badge=latest)

<p align="center">
<img src="https://media.giphy.com/media/3ornjRyce6SukW8INi/giphy.gif" />
</p>

This package is named after the Roci's captain in *The Expanse*, James Holden, who was adept at furling his brow and recognizing connections. In a similar vein, **holden** offers users easy-to-use composite data structures without the overhead or complexity of larger graph packages. The included graphs are built for basic workflow design or analysis of conditional relationships. They are not designed for big data network analysis or similar large-scale projects (although nothing prevents you from using them in that manner). Rather, the goal of **holden** is to provide lightweight, turnkey, extensible composite data structures without all of the stuff you don't need in packages like [networkx](https://github.com/networkx/networkx). **holden** serves as the base for my [chrisjen](https://github.com/WithPrecedent/chrisjen) workflow package (similarly named for a character from The Expanse), but I have made **holden** available separately for easier integration into other uses.

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

## Contributing

The project is highly internally documented so that users and developers can make **holden** work with their projects. It is designed for Python coders at all levels. Beginners should be able to follow the readable code and internal documentation to understand how it works. More advanced users should find complex and tricky problems addressed through efficient code.

I hope you find **holden** useful and feel free to contribute, leave suggestions, or report bugs.

<p align="center">
<img src="https://media.giphy.com/media/3oKIPwyf0EBAGnAkWk/giphy.gif" />
</p>

## Similar Projects
* [networkx](https://github.com/networkx/networkx): the market leader for python graphs. Offers greater flexibility and extensibility at the cost of substantial overhead.