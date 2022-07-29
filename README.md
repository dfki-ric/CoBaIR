[![pipeline status](https://git.hb.dfki.de/kimmi_sf/implementation/CoBaIR/badges/develop/pipeline.svg)](https://git.hb.dfki.de/kimmi_sf/implementation/CoBaIR/-/commits/develop)
[![coverage report](https://git.hb.dfki.de/kimmi_sf/implementation/CoBaIR/badges/develop/coverage.svg)](https://git.hb.dfki.de/kimmi_sf/implementation/CoBaIR/-/commits/develop)
[![Latest Release](https://git.hb.dfki.de/kimmi_sf/implementation/CoBaIR/-/badges/release.svg)](https://git.hb.dfki.de/kimmi_sf/implementation/CoBaIR/-/releases)

# CoBaIR

CoBaIR is a python lib for **Co**ntext **Ba**sed **I**ntention **R**ecognition. 
It provides the means to infer an intention from given context. 
An intention is a binary value e.g. `repair pipe` that can either be present or not. Only one intention can be present at a time.
Context on the otherhand is can have multiple discrete instantiations e.g. `weather:sunny|cloudy|raining`.
If context values are continuous, discretizer functions can be used to create discrete values.
From the infered intention in a HRI scenario the robot can perform corresponding actions to help the human with a specific task.


## Documentation
The Documentation can be accessed via the VPN on http://bob.dfki.uni-bremen.de/apis/kimmi_sf/implementation/CoBaIR/latest

## Bayesian Approach
In the bayesian approach CoBaIR uses a two-layer Bayesian Net of the following structure.
![two-layer Bayesian Net](docs/images/2layerbayesian.svg)


## Install dependencies
You need to install all dependencies from the `requirements.txt` with `pip install -r requirements.txt`.



## Config Format
Configs will be saved in yml files. For convenience the is a configurator which can be started with

```bash
python start_configurator.py
```

### Bayesian Approach
The configuration file for a two layer bayesian net for context based intention recognition follows the given format:

```yaml
# List of contexts. Contexts can have different discrete instantiations. 
# Number of instantiations must be larger than 2.
# For all discrete instantiations a prior probability must be given(sum for one context must be 1)
contexts:
  context 1:
    instantiation 1 : float
    instantiation 2 : float
      .
      .
      .
    instantiation m_1 : float
  context 2:
    instantiation 1 : float
    instantiation 2 : float
      .
      .
      .
    instantiation m_2 : float
    .
    .
    .
  context n:
    instantiation 1 : float
    instantiation 2 : float
      .
      .
      .
    instantiation m_n : float



# List of intentions. Intentions are always binary(either present or not)
# For every intention the context variables and their influence on the intention is given
# [very high, high, medium, low, very low, no] => [5, 4, 3, 2, 1, 0]
intentions: 
  intention 1:
    context 1:
        instantiation 1: [5, 4, 3, 2, 1, 0]
        instantiation 2: [5, 4, 3, 2, 1, 0]
        .
        .
        .
        instantiation m_1: [5, 4, 3, 2, 1, 0]
    context 2:
        instantiation 1: [5, 4, 3, 2, 1, 0]
        instantiation 2: [5, 4, 3, 2, 1, 0]
        .
        .
        .
        instantiation m_1: [5, 4, 3, 2, 1, 0]
        .
        .
        .
    context n:
        instantiation 1: [5, 4, 3, 2, 1, 0]
        instantiation 2: [5, 4, 3, 2, 1, 0]
        .
        .
        .
        instantiation m_n: [5, 4, 3, 2, 1, 0]
  intention 2:
    context 1:
        instantiation 1: [5, 4, 3, 2, 1, 0]
        instantiation 2: [5, 4, 3, 2, 1, 0]
        .
        .
        .
        instantiation m_1: [5, 4, 3, 2, 1, 0]
    context 2:
        instantiation 1: [5, 4, 3, 2, 1, 0]
        instantiation 2: [5, 4, 3, 2, 1, 0]
        .
        .
        .
        instantiation m_1: [5, 4, 3, 2, 1, 0]
        .
        .
        .
    context n:
        instantiation 1: [5, 4, 3, 2, 1, 0]
        instantiation 2: [5, 4, 3, 2, 1, 0]
        .
        .
        .
        instantiation m_n: [5, 4, 3, 2, 1, 0]
    .
    .
    .
  intention p:
    context 1:
        instantiation 1: [5, 4, 3, 2, 1, 0]
        instantiation 2: [5, 4, 3, 2, 1, 0]
        .
        .
        .
        instantiation m_1: [5, 4, 3, 2, 1, 0]
    context 2:
        instantiation 1: [5, 4, 3, 2, 1, 0]
        instantiation 2: [5, 4, 3, 2, 1, 0]
        .
        .
        .
        instantiation m_1: [5, 4, 3, 2, 1, 0]
        .
        .
        .
    context n:
        instantiation 1: [5, 4, 3, 2, 1, 0]
        instantiation 2: [5, 4, 3, 2, 1, 0]
        .
        .
        .
        instantiation m_n: [5, 4, 3, 2, 1, 0]

```


### CPT Values
In the default approach of creating a CPT(Conditional Probability Table) you would need to determine

 n<sub>v</sub>(i, j c, n) = &sum;<sub>j</sub> c<sub>j</sub> + i * &prod;<sub>i</sub> n<sub>i</sub> &prod;<sub>j</sub> c<sub>j</sub>


 values. Where n<sub>v</sub> is the number of values which needs to be determined, c is the number of possible instantiations for a context i is the number of intentions and n is the number of possible instantiations for Intentions.

 While in the optimized version the product is replaced with a sum resulting in the following:

 n<sub>v</sub>(i, j, c) = (i+1)&sum;<sub>j</sub> c<sub>j</sub>

This is possible due to the following assumptions:

- **Intentions are binary**: we just need to care about the positive case and the negative case can be assumed as counterposibility.
- **Context has a meaning on its own for intentions**: Therefor we set a percentage influence value v<sub>i, j, n</sub> for every context-intention-tuple (C<sub>i,j</sub>, I<sub>n</sub>) and calculate the conditional probabilities of the conditional probability tables(CPTs) as the average of all influence values for the given context.

This is the optimal case. The second assumption may not be true for every intention.

## Run tests
Tests are implemented with [pytest](https://docs.pytest.org/en/7.1.x/).
To install test dependencies you need to run 

```bash
pip install -r test_requirements.txt
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
pip install -r doc_requirements.txt
```
### Build
Build the docu with 
```bash
mkdocs build
```
The documentation will be in the `site` folder.

# Authors
Adrian Lubitz & Arunima Gopikrishnan
