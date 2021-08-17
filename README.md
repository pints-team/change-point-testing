[![Build Status](https://dev.azure.com/OxfordRSE/pints-functional-testing/_apis/build/status/pints-team.functional-testing?branchName=master)](https://dev.azure.com/OxfordRSE/pints-functional-testing/_build/latest?definitionId=1&branchName=master)
[![Results](badge-results.svg)](https://www.cs.ox.ac.uk/projects/PINTS/functional-testing)

# Pints Change Point Testing

This repository is used to code that will become a change point detection module, used to see if the statistical properties of a piece of software change over time. It will be used to make sure [PINTS](https://github.com/pints-team/pints) functions reliably.

The information here is out of date. This will be rewritten at some point: https://github.com/pints-team/change-point-testing/issues/38

[Old test results can be viewed here](https://www.cs.ox.ac.uk/projects/PINTS/functional-testing) (or by clicking the blue badge above).


## Installation

- Functional testing requires Python 3.4 or later
- When cloning, make sure to add the `--recursive` switch
- To install, use `python3 -m pip install -r requirements.txt`. This makes sure you have all the dependencies you know.

```
git clone git@github.com:pints-team/functional-testing.git --recursive
```
## Running tests

- To see a list of available tests, use `./funk list`.
- Use `./funk run test_name` to run a test.
  - This will store results in a database (default `./results.db`).
- Use `./funk run --next` to run the next test in line. This is determined by looking at the result files and seeing which test hasn't been run for the longest time.
- Use `./funk run test_name --show` to show the resulting plot as well

## Adding tests

- Add a test to the `tests` module, and then add it to `tests.py` so that the framework can find it.
- Write any results (int, floats, strings, or numpy arrays) to the result object.
- Write any pints logs to the given log path (e.g. `opt.set_log_to_file(log_path)`).

Some details:
- The internal pints repo is reloaded before every test is run, and the version number and commit hash are automatically added to the results object.
- The numpy random generator is seeded before every tests is run, and the seed is automatically added to the results object.
- If the test passes successfully, please set `status=passed` in the results object.

## Creating plots, running analysis

- Use `./funk plot test_name` to run a plot, or `./funk plot --all` to run all plots
- Use `./funk analyse test_name` to check if a test passed or failed, or `./funk analyse --all` to check all tests

