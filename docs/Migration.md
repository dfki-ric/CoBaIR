# Migrating from 4.x to 5.0

CoBaIR 5.0 splits the library into a config model and the inference, brings the web GUI and renames the package
to lowercase `cobair`. **Code written for 4.x keeps working in 5.x**, it only shows `DeprecationWarning`s.
The deprecated names are removed in 6.0.0
([#199](https://github.com/dfki-ric/CoBaIR/issues/199)).

## Install
5.0 needs **Python ≥ 3.10**. The dependencies are split into extras:

| 4.x | 5.0 |
|---|---|
| `pip install CoBaIR` | `pip install "cobair[infer]"` for the inference, `"cobair[all]"` for everything |
| `python start_configurator.py` | `pip install "cobair[qt]"`, then `cobair-qt` |
| | **new:** `pip install "cobair[web]"`, then `cobair-web` (Python ≥ 3.11) |

`pip install cobair` alone installs only the config model (`cobair.model`, needs only pyyaml).

## Imports and API

| 4.x (deprecated) | 5.0 |
|---|---|
| `import CoBaIR` | `import cobair` |
| `from CoBaIR.bayes_net import BayesNet` | `from cobair.model import Config` and `from cobair.infer import Inference` |
| `load_config(path)` | `Config.load(path)` |
| `BayesNet(config)` | `config = Config.from_dict(config)`, `inference = Inference(config)` |
| `bayes_net.add_context(...)`, `edit_context`, `del_context`, `add_intention`, `edit_intention`, `del_intention`, `change_context_apriori_value`, `change_influence_value`, `add_combined_influence`, `del_combined_influence`, `change_decision_threshold` | the same methods on `Config` |
| `bayes_net.validate_config()` (warnings) | `config.validate()` returns the problems as list, `config.valid` |
| `bayes_net.save(path)` | `config.save(path)` |
| `bayes_net.infer(evidence)` | `Inference(config).infer(evidence)` |
| `bayes_net.bind_discretization_function(...)` | `inference.bind_discretization_function(...)` |
| `from CoBaIR.configurator import Configurator` | `from cobair.qt import Configurator` |

Example:

```python
# 4.x
from CoBaIR.bayes_net import BayesNet, load_config
net = BayesNet(load_config('my_scenario.yml'))
intention, threshold, probabilities = net.infer({'speech commands': 'pickup'})

# 5.0
from cobair.model import Config
from cobair.infer import Inference
inference = Inference(Config.load('my_scenario.yml'))
intention, threshold, probabilities = inference.infer({'speech commands': 'pickup'})
```

`Inference.infer` returns a named tuple `(intention, decision_threshold, probabilities)`, so the 4.x unpacking
works unchanged. An `Inference` works on a copy of the config: create a new one after editing the config.

## Config files
The YAML format is **compatible in both directions**: 5.0 reads 4.x files, and 4.x reads files written by 5.0.
Files written by 5.0 start with a comment and the keys `format_version` and `created_with`, which 4.x ignores.
Contexts, instantiations and intentions keep their order instead of being sorted alphabetically.

## Changed behaviour
These were bugs in 4.x. If your code relied on them, check the results:

- Editing or deleting a context no longer deletes **all combined influences**. Renaming a context renames it in the
  combined influences.
- **All combinations** of a context tuple count in the inference, 4.x only used the first one.
  `del_combined_influence` removes only the given combination.
- **Discretization functions** run for every evidence value that is not an instantiation. In 4.x they only ran for
  unhashable values, so e.g. a float for a bool context was ignored with a warning.
- Renaming a context to the name of another context raises a `ValueError` instead of overwriting it.
- Apriori probabilities are checked to sum up to 1 with a small tolerance, so `0.1 + 0.2 + 0.7` is valid.
  Integers (e.g. a decision threshold of `0`) count as numbers.
