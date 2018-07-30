# Pints Functional Testing

This repository will be used to house functional tests of [Pints](https://github.com/pints-team/pints) algorithms, that go beyond unit testing, and typically take longer to run.

**Note: As this is part of the Pints project, GitHub project management features (e.g. issues) have been disabled for this repo. For tickets and discussion, please see [https://github.com/pints-team/pints](The main pints repository on GitHub).**

**At the moment, there is no service that runs these tests, even though we are setting it up so that we can start using one soon. However, it's perfectly possible for everyone to run tests locally and then commit the results to the git repo.**

## Urgent to-do

- [x] Result file reader and writer
- [x] Test class
- [x] Example test
- [x] List of tests, test last run file reading/writing
- [x] Analysis class: reads several results for 1 test
- [x] Plot based on analysis class
- [ ] Add a functional test and plot for 1 optimiser
- [ ] Add functional tests and plots for all optimisers
- [ ] Add a functional test and plot for 1 sampler
- [ ] Add functional tests and plots for all samplers

## How it works

### Running tests

- Use `./funk -t test_name` to run a test.
- This will create a result file in `results`, and possibly a log file in `logs`.
- To see a list of tests, use `./funk --list`.
- Use `./funk --next` to run the next test in line. This is determined by looking at the result files and seeing which test hasn't been run for the longest time.

### Adding tests

- Add a test to the `tests` module, and then add it to `tests.py` so that the framework can find it.
- Write any results (int, floats, strings, or numpy arrays) to the result object.
- Write any pints logs to the given log path (e.g. `opt.set_log_to_file(log_path)`).

Some details:
- The internal pints repo is reloaded before every test is run, and the version number and commit hash are automatically added to the results object.
- The numpy random generator is seeded before every tests is run, and the seed is automatically added to the results object.
- If the test passes successfully, please set `status=passed` in the results object.

### Creating plots

- Use `./funk -p plot_name` to run a plot.
- This will create a file in `plots`.
- To see a list of plots, use `./funk --plots`.

### Adding plots

- Add a plot to the `plots` module, and then add it to `plots.py` so that the framework can find it
- For plots of a single test, a results object will be passed in that provides access to all logged entries of a particular result. For example, if the test stores a value `x` the result object for plotting can be used as `result[x]` to obtain a tuple `times, values` where `times` are all the times where `x` was logged and `values` are all logged `x` values.

### Installing

- To install, use `pip install -r requirements`. This makes sure you have all the dependencies you know.


## To-do

- Reporting
    - Eventually, if everything works well, we can build something that emails us if the results drop and stay low for a couple of runs. Instead of emailing we could also just use the cmd line return value to indicate a failure.
    - I think it'd be best to have this analysis separate from the running of the tests, so for them a failure would be an exception occurring.
    
- Travis
    - Travis is for testing. This is testing, so should be ok? Can't see anything in the user agreement that says this would be wrong (bitcoing mining is explicitly not allowed).   
    
- Storing data
    - I'd like to do everything disk based (inlcuding the current 'status') etc. This makes it easy to do things in a distributed way! For example, we could run a few tests offline
    - **We need to use GitPython to git pull the test repo itself before every run (tricky?), and then commit the `results` and `logs` after each run.
    
- Timing
    - We should log evaluations, and iterations, but _not_ run-time.
    - Two reasons: 1. Benchmarking is very hard, and we can't benchmark on testing machines (which are slow and whose performance varies hugely over time). 2. It'd stop us from being able to add data from different machines.

