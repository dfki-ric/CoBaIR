# CoBaBIR

CoBaBIR is a python lib for **Co**ntext **Ba**sed **B**ayesian **I**ntention **R**ecognition.
It uses a two-layer Bayesian Net of the following structure.
![two-layer Bayesian Net](docs/images/2layerbayesian.svg)


## Install dependencies
You need to install all dependencies from the `requirements.txt` with `pip install -r requirements.txt`.



## Config Format
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

 n<sub>v</sub>(i, c) = &sum;<sub>j</sub> c<sub>j</sub> + i * &prod;<sub>j</sub> c<sub>j</sub>


 values. Where n<sub>v</sub> is the number of values which needs to be determined, c is the number of possible instantiations for a context and i is the number of intentions.

 While in the optimized version the product is replaced with a sum resulting in the following:

 n<sub>v</sub>(i, c) = (i+1)&sum;<sub>j</sub> c<sub>j</sub>


## Run tests
Tests are implemented with [unittest](https://docs.python.org/3/library/unittest.html) and can be executed with:

```bash
python -m unittest discover -s tests
```