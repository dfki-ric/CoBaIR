# CoBaIR

CoBaIR is a python library for **Co**ntext **Ba**sed **I**ntention **R**ecognition. 
It provides the means to infer an intention from given context. 
An intention is a binary value e.g. `repair pipe` that can either be present or not. Only one intention can be present at a time.
Context on the otherhand can have multiple discrete instantiations e.g. `weather:sunny|cloudy|raining`.
If context values are continuous, discretizer functions can be used to create discrete values.
From the infered intention in a HRI scenario the robot can perform corresponding actions to help the human with a specific task.

## Publications
For a more in-depth explanation consult the following papers:
- [Concept Paper](https://www.dfki.de/fileadmin/user_upload/import/12351_lubitz_kimmi_cobabir_2022_-_Adrian_Lubitz.pdf)



## Install 
```bash
pip install CoBaIR
```
You can install the library from your local copy after cloning this repo with pip using `pip install .` 
or istall the the `develop` branch with `pip install git+https://github.com/dfki-ric/CoBaIR.git@develop`

### Known Issues
On some Linux Distros there seems to be a problem with a shared library. [This Solutions](https://stackoverflow.com/questions/71010343/cannot-load-swrast-and-iris-drivers-in-fedora-35/72200748#72200748) suggests to `export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6
` which works on Ubuntu 22.04.

## Use the Graphical User Interface
To make the configuration of a scenario easier we provide a Graphical User Interface(GUI). The GUI can be started with
```bash
python start_configurator.py
```
if you want to start the GUI with a loaded config use
```bash
python start_configurator.py -f config.yml
```


## Documentation
The Documentation can be accessed on https://dfki-ric.github.io/CoBaIR/

## Bayesian Approach
In the bayesian approach CoBaIR uses a two-layer Bayesian Net of the following structure.
![two-layer Bayesian Net](docs/images/2layerbayesian.svg)

## Config Format
Configs will be saved in yml files. For convenience the is a configurator which can be started with

```bash
python start_configurator.py
```

### Bayesian Approach
The configuration file for a two layer bayesian net for context based intention recognition follows the given format:

```yaml
# List of contexts. Contexts can have different discrete instantiations. 
# Number of instantiations must be larger than 1.
# For all discrete instantiations a prior probability must be given(sum for one context must be 1)
contexts:
  context 1:
    instantiation 1 : float
      .
    instantiation m_1 : float
  context n:
    instantiation 1 : float
      .
    instantiation m_n : float
# List of intentions. Intentions are always binary(either present or not)
# For every intention the context variables and their influence on the intention is given
# [very high, high, medium, low, very low, no] => [5, 4, 3, 2, 1, 0]
intentions: 
  intention 1:
    context 1:
        instantiation 1: int # one out of [5, 4, 3, 2, 1, 0]
        .
        instantiation m_1: int # one out of [5, 4, 3, 2, 1, 0]
    context n:
        instantiation 1: int # one out of [5, 4, 3, 2, 1, 0]
        .
        instantiation m_n: int # one out of [5, 4, 3, 2, 1, 0]
  intention p:
    context 1:
        instantiation 1: int # one out of [5, 4, 3, 2, 1, 0]
        .
        instantiation m_1: int # one out of [5, 4, 3, 2, 1, 0]
    context n:
        instantiation 1: int # one out of [5, 4, 3, 2, 1, 0]
        .
        instantiation m_n: int # one out of [5, 4, 3, 2, 1, 0]
# decision_threshold is a float value between 0 and 1 which decides 
# when an intention should be considered in inference.
# Probability must be greater than decision_threshold.
decision_threshold: float

```
# How to contribute
If you find any Bugs or want to contribute/suggest a new feature you can create a Merge Request / Pull Request or contact me directly via adrian.lubitz@dfki.de

## Run tests
Tests are implemented with [pytest](https://docs.pytest.org/en/7.1.x/).
To install test dependencies you need to run 

```bash
pip install -r requirements/test_requirements.txt
```
Then you can run 
```bash
python -m pytest tests/
```
You can as well see the test report for a specific commit in gitlab under [pipeline->Tests](hhttps://git.hb.dfki.de/kimmi_sf/implementation/CoBaIR/-/pipelines/39889/test_report)

### Coverage
If you want to see coverage for the tests you can run

```bash
coverage run -m pytest tests/
```

Use 

```bash
coverage report
```
or 


```bash
coverage html
```

You can as well see the coverage for a specific job in gitlab under [jobs](https://git.hb.dfki.de/kimmi_sf/implementation/CoBaIR/-/jobs)

To show results of the coverage analysis.
## Build docu
Documentation is implemented with the [material theme](https://squidfunk.github.io/mkdocs-material/) for [mkdocs](https://www.mkdocs.org/).

### Dependencies
Install all dependencies for building the docu with 
```bash
pip install -r requirements/doc_requirements.txt
```
### Build
Build the docu with 
```bash
mkdocs build
```
The documentation will be in the `site` folder.

# Authors
Adrian Lubitz & Arunima Gopikrishnan

## Funding
CoBaIR is currently developed in the [Robotics Group](https://robotik.dfki-bremen.de/de/ueber-uns/universitaet-bremen-arbeitsgruppe-robotik.html) of the [University of Bremen](https://www.uni-bremen.de/), together with the [Robotics Innovation Center](https://robotik.dfki-bremen.de/en/startpage.html) of the **German Research Center for Artificial Intelligence** (DFKI) in **Bremen**.
CoBaIR has been funded by the German Federal Ministry for Economic Affairs and Energy and the [German Aerospace Center](https://www.dlr.de/DE/Home/home_node.html) (DLR).
CoBaIR been used and/or developed in the [KiMMI-SF](https://robotik.dfki-bremen.de/en/research/projects/kimmi-sf/) project.

<p align="center">
<img src="https://raw.githubusercontent.com/oarriaga/altamira-data/master/images/funding_partners.png" width="1200">
</p>
