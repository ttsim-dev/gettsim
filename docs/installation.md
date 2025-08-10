# Installation

GETTSIM is available on [PyPi](https://pypi.org/project/gettsim/) and
[conda-forge](https://anaconda.org/conda-forge/gettsim). You can install GETTSIM using
your preferred package manager.

## Pixi

To install GETTSIM using pixi, first make sure that pixi is installed on your machine.
You can find the installation instructions [here](https://pixi.sh/latest/installation/).

With pixi available on your path, installing GETTSIM is as simple as typing

```shell-session
$ pixi add gettsim
```

## Conda / Mamba

Install the [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/)
or [mamba](https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html)
package manager.

In your shell, run

```shell-session
$ conda install -c conda-forge gettsim
```

or

```shell-session
$ mamba install -c conda-forge gettsim
```

## UV or Pip

Install the [uv](https://docs.astral.sh/uv/) or [pip](https://pip.pypa.io/en/stable/)
package manager.

In your shell, run

```shell-session
$ uv add gettsim
```

or

```shell-session
$ pip install gettsim
```

```{warning}
When installing GETTSIM via uv or pip, make sure
[`graphviz`](https://graphviz.org) is installed on your machine.
```

## Validate your installation

To validate the installation, start the Python interpreter and type

```python
import gettsim

gettsim.test()
```
