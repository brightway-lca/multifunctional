# multifunctional

[![PyPI](https://img.shields.io/pypi/v/multifunctional.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/multifunctional.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/multifunctional)][pypi status]
[![License](https://img.shields.io/pypi/l/multifunctional)][license]

[![Read the documentation at https://multifunctional.readthedocs.io/](https://img.shields.io/readthedocs/multifunctional/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/brightway-lca/multifunctional/actions/workflows/python-test.yml/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/brightway-lca/multifunctional/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi status]: https://pypi.org/project/multifunctional/
[read the docs]: https://multifunctional.readthedocs.io/
[tests]: https://github.com/brightway-lca/multifunctional/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/brightway-lca/multifunctional
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

Handling multifunctional activities in the Brightway LCA software framework.

## Installation

You can install _multifunctional_ via [pip] from [PyPI]:

```console
$ pip install multifunctional
```

It is also available on `anaconda` using `mamba` or `conda` at the `cmutel` channel:

```console
mamba install -c conda-forge -c cmutel multifunctional
```

## Usage

Multifunctional activities can lead to linear algebra problems which don't have exactly one solution. Therefore, we commonly need to apply a handling function to either partition such activities, or otherwise manipulate their data such that they allow for the creation of a square and non-singular technosphere matrix.

This library is designed around the following workflow:

Users create and register a `multifunctional.MultifunctionalDatabase`. Registering this database must include the database metadata key `default_allocation`, which refers to an allocation strategy function present in `multifunctional.allocation_strategies`.

```python
import multifunctional
mf_db = multifunctional.MultifunctionalDatabase("emojis FTW")
mf_db.register(default_allocation="price")
```

Multifunctional process(es) are created and written to the `MultifunctionalDatabase`. A multifunctional process is any process with multiple "functional" edges, either outputs (e.g. products) and/or input (e.g. wastes). Each functional edge must be labelled `functional=True`. This labeling can be done manually or via a classification function.

```python
mf_data = {
    ("emojis FTW", "😼"): {
        "type": "product",
        "name": "meow",
        "unit": "kg",
    },
    ("emojis FTW", "🐶"): {
        "type": "product",
        "name": "woof",
        "unit": "kg",
    },
    ("emojis FTW", "1"): {
        "name": "process - 1",
        "location": "somewhere",
        "exchanges": [
            {
                "functional": True,
                "type": "production",
                "input": ("emojis FTW", "😼"),
                "amount": 4,
                "properties": {
                    "price": 7,
                    "mass": 6,
                },
            },
            {
                "functional": True,
                "type": "technosphere",
                "input": ("emojis FTW", "🐶"),
                "amount": 6,
                "properties": {
                    "price": 12,
                    "mass": 4,
                },
            },
        ],
    }
}
```

Allocation can be done manually before writing the data to the database; if not done manually, it will be done automatically upon calling `.write()`

LCA calculations can then be done as normal. See `dev/basic_example.ipynb` for a simple example.

### Substitution

You don't need to use library for substitution, that already works natively in Brightway. Just produce a product which another process also produces (i.e. has the same database name and code), and the production amount of the other process will be reduced as needed to meet the functional unit demand.

We will eventually have a plan for including substitution in parallel with allocation.

### Classifying functional edges

There is currently no built-in functionality to determine if an edge is functional based on its attributes - instead we rely on the label `functional` being manually specified. You can write a function to iterate over datasets and label the functional edges in whatever fashion you choose.

### Built-in allocation functions

`multifunctional` includes the following built-in property-based allocation functions:

* `price`: Does economic allocation based on the property "price" in each functional edge.
* `mass`: Does economic allocation based on the property "mass" in each functional edge.
* `manual_allocation`: Does allocation based on the property "manual_allocation" in each functional edge. Doesn't normalize by amount of production exchange.
* `equal`: Splits burdens equally among all functional edges.

Property-based allocation assumes that each functional edge has a `properties` dictionary, and this dictionary has the relevant key with a corresponding numeric value. For example, for `price` allocation, each functional edge needs to have `'properties' = {'price': some_number}`.

### Custom property-based allocation functions

To create new property-based allocation functions, add an entry to `allocation_strategies` using the function `property_allocation`:

```python
import multifunctional as mf
mf.allocation_strategies['<label in function dictionary>'] = property_allocation(property_label='<property string>')
```

Additions to `allocation_strategies` are not persisted, so they need to be added each time you start a new Python interpreter or Jupyter notebook.

### Custom single-factor allocation functions

To create custom allocation functions which apply a single allocation factor to all nonfunctional inputs and outputs, pass a function to `multifunctional.allocation.generic_allocation`. This function needs to accept the following input arguments:

* edge_data (dict): Data on functional edge
* node: An instance of `multifunctional.MaybeMultifunctionalProcess`
* strategy_label: An optional string to label the allocation strategy used

The custom function should return a number.

The custom function needs to be curried and added to `allocation_strategies`. You can follow this example:

```python
import multifunctional as mf
from functools import partial

def allocation_factor(edge_data: dict, node: mf.MaybeMultifunctionalProcess) -> float:
   """Nonsensical allocation factor generation"""
   if edge_data.get("unit") == "kg":
      return 1.2
   elif "silly" in node["name"]:
      return 4.2
   else:
      return 7

mf.allocation_strategies['silly'] = partial(
   mf.generic_allocation,
   func=allocation_factor,
   strategy_label="something silly"
)
```

### Other custom allocation functions

To have complete control over allocation, add your own function to `allocation_strategies`. This function should take an input of *either* `multifunctional.MaybeMultifunctionalProcess` or a plain data dictionary, and return a list of data dictionaries *including the original input process*. These dictionaries can follow the [normal `ProcessWithReferenceProduct` data schema](https://github.com/brightway-lca/bw_interface_schemas/blob/5fb1d40587aec2a4bb2248505550fc883a91c355/bw_interface_schemas/lci.py#L83), but the result datasets need to also include the following:

* `mf_parent_key`: Integer database id of the source multifunctional process
* `type`: One of "readonly_process", "process", or "multifunctional"

Furthermore, the code of the allocated processes (`mf_allocated_process_code`) must be written to each functional edge (and that edge saved so this data is persisted). See the code in `multifunctional.allocation.generic_allocation` for an example.

## Technical notes

### Process-specific allocation strategies

Individual processes can override the default database allocation by specifying their own `default_allocation`:

```python
import bw2data
node = bw2data.get(database="emojis FTW", code="1")
node["default_allocation"] = "mass"
node.save()
```

### Specifying `code` values for allocated processes

When allocating a multifunctional process to separate monofunctional processes, we need to generate `code` values for each monofunctional process. This can be done by specifying `desired_code` for the functional exchange.  See `dev/basic_example.ipynb` for a simple example.

When writing a multifunctional process, we need to create artificial edges to allocated processes which don't exist yet. You can't therefore directly specify the `code` of such an edge.

### Separate `product` nodes

By default, the allocation function creates chimaera process+product nodes. However, we recommend distinguishing products and processes as best practice, and this is supported by `multifunctional`. You will need to create the `product` nodes yourself; they can be in the same multifunctional database, or in another database.

To create a functional link to a `product` node in the same database, you should specify an exchange `input` to the desired product. See `dev/split_products.ipynb` for a simple example. The product can be in the mutifunctional database, but doesn't have to be.

## How does it work?

Recent Brightway versions allow users to specify which graph nodes types should be used when building matrices, and which types can be ignored. We create a multifunctional process node with the type `multifunctional`, which will be ignored when creating processed datapackages. However, in our database class `MultifunctionalDatabase` we change the function which creates these processed datapackages to load the multifunctional processes, perform whatever strategy is needed to handle multifunctionality, and then use the results of those handling strategies (e.g. monofunctional processes) in the processed datapackage.

We also tell `MultifunctionalDatabase` to load a new `ReadOnlyProcessWithReferenceProduct` process class instead of the standard `Activity` class when interacting with the database. This new class is read only because the data is generated from the multifunctional process itself - if updates are needed, either that input process or the allocation function should be modified.

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide][Contributor Guide].

## License

Distributed under the terms of the [BSD 3 Clause license][License],
_multifunctional_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue][Issue Tracker] along with a detailed description.


<!-- github-only -->

[command-line reference]: https://multifunctional.readthedocs.io/en/latest/usage.html
[License]: https://github.com/brightway-lca/multifunctional/blob/main/LICENSE
[Contributor Guide]: https://github.com/brightway-lca/multifunctional/blob/main/CONTRIBUTING.md
[Issue Tracker]: https://github.com/brightway-lca/multifunctional/issues


## Building the Documentation

You can build the documentation locally by installing the documentation Conda environment:

```bash
conda env create -f docs/environment.yml
```

activating the environment

```bash
conda activate sphinx_multifunctional
```

and [running the build command](https://www.sphinx-doc.org/en/master/man/sphinx-build.html#sphinx-build):

```bash
sphinx-build docs _build/html --builder=html --jobs=auto --write-all; open _build/html/index.html
```
