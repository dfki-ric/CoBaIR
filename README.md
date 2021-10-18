# Bayesian Net for Intention Recognition

Module for context based intention recognition with bayes net.

## Install dependencies
You need to install all dependencies from the `requirements.txt` with `pip install -r requirements.txt`.
## Run test
`python small_example_from_yaml.py`

you can also run `small_example_from_yaml.py` in interactive mode and dynamically change the evidence in the last cell.
This example automatically loads the file `small_example.yaml`. If you wish to load another file you need to specify it in `small_example_from_yaml.py`.

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

