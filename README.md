[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) [![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) [![Documentation Status](https://readthedocs.org/projects/holden/badge/?version=latest)](http://holden.readthedocs.io/?badge=latest)

![](https://media.giphy.com/media/3ornjRyce6SukW8INi/giphy.gif)

The goal of holden is provide lightweight, turnkey, extensible composite data structures.

Out of the box, it provides graph structures with internal storage in the following formats:
* Adjacency list (Adjacency)
* Adjacency matrix (Matrix)
* Edge list (Edges)

It supports directed graphs and weighted edges. It provides transformation methods for all the internal storage forms as well as functions to convert graphs into a set of paths (Parallel) or a single path (Serial).

holden's framework supports a wide range of coding styles. You can create complex multiple inheritance structures with mixins galore or simpler, compositional objects. Even though the data structures are necessarily object-oriented, all of the tools to modify them are also available as functions, for those who prefer a more funcitonal approaching to programming.

The project is also highly documented so that users and developers and make holden work with their projects. It is designed for Python coders at all levels. Beginners should be able to follow the readable code and internal documentation to understand how it works. More advanced users should find complex and tricky problems addressed through efficient code.
