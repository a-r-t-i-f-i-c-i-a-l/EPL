# EPL

**E**xplanatory **P**attern **L**earning is a new approach to symbolic machine learning and knowledge represenation. It aims to model the experiences of an AI agent in a world as patterns to be abstracted. It is based in part on the notion of image schemata from cognitive linguistics. This repository contains a reference proof-of-concept implementation of EPL.

# Requirements

```
numpy,
textworld,
matplotlib
```

# Code

The main parts of code are in `hypotheses.py` and `agent.py`. `agent` contains the definitions of `VariablePlaceholders` and `Action` types. `hypotheses` does the bulk of the actual learning and reasoning.

Aside from this, we provide Python scripts for training and testing EPL, testing Language Models (namely GPT-3 and T0pp), as well as creating fine tune data for GPT-3 and calculating and plotting metrics.

# Tests

In order to train and test EPL, use `train_test_epl.py`. Execute

```python train_test_epl.py```

In order to test a language model, you will need an API key (from BigScience for T0pp and from OpenAI for GPT-3). Use

```python test_language_models.py```

to get a list of command-line switches.

In order to create your own fine tune data for GPT-3, use

```python create_gpt3_fine_tune_data.py```

In order to calculate the metrics and plot the results, use

```python plot_calculate_results.py`.``
