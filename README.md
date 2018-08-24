# Pints Functional Testing

This repository is used to house functional tests of [Pints](https://github.com/pints-team/pints) algorithms, that go beyond unit testing, and typically take longer to run.

[Results are visible here](https://github.com/pints-team/functional-testing-results).

GitHub project management features (e.g. issues) have been disabled for this repo. For tickets and discussion, please see [The main pints repository on GitHub](https://github.com/pints-team/pints).



## How it works

### Running tests

- To see a list of available tests, use `./funk list`.
- Use `./funk test test_name` to run a test.
- This will create a result file in `results`, and possibly a log file in `logs`.
- Use `./funk test --next` to run the next test in line. This is determined by looking at the result files and seeing which test hasn't been run for the longest time.
- Use `./funk test test_name --show` to show the resulting plot as well

### Adding tests

- Add a test to the `tests` module, and then add it to `tests.py` so that the framework can find it.
- Write any results (int, floats, strings, or numpy arrays) to the result object.
- Write any pints logs to the given log path (e.g. `opt.set_log_to_file(log_path)`).

Some details:
- The internal pints repo is reloaded before every test is run, and the version number and commit hash are automatically added to the results object.
- The numpy random generator is seeded before every tests is run, and the seed is automatically added to the results object.
- If the test passes successfully, please set `status=passed` in the results object.

### Creating plots, running analysis

- Use `./funk plot test_name` to run a plot, or `./funk plot --all` to run all plots
- Use `./funk analyse test_name` to check if a test passed or failed, or `./funk analyse --all` to check all tests


### Installing

- When cloning, make sure to add the `--recursive` switch
- To install, use `python3 -m pip install -r requirements`. This makes sure you have all the dependencies you know.
