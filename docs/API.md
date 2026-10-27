# API

CoBaIR is split into the config model and the inference:

- `cobair.model` describes a scenario (contexts, intentions, influences, decision threshold), validates it,
  reads and writes config files and computes the conditional probability tables. It only needs `pyyaml`.
- `cobair.infer` infers the intentions for given evidence with the two-layer Bayesian net.
  It needs the `[infer]` extra: `pip install "cobair[infer]"`.

```python
from cobair.model import Config
from cobair.infer import Inference

config = Config.load('small_example.yml')
config.change_influence_value('pick up tool', 'speech commands', 'pickup', 5)
print(config.validate())  # [] if the config is valid

inference = Inference(config)  # create a new Inference after editing the config
intention, decision_threshold, probabilities = inference.infer({'speech commands': 'pickup'})
```

## cobair.model

::: cobair.model

## cobair.infer

::: cobair.infer

## Deprecated: cobair.bayes_net

The 4.x API `BayesNet`, `load_config`, `config_to_default_dict` and `default_to_regular` still works in 5.x,
but raises a `DeprecationWarning` and will be removed in 6.0.0.

::: cobair.bayes_net
