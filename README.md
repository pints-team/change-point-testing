# Pints Functional Testing

This repository will be used to house functional tests of Pints algorithms, that go beyond unit testing, and typically take longer to run.

## How does it work?

Preliminary design

- Test
    - Instance of a Test class. Probably some tests will be specific, others will be instances of the same class. For example, we could use a similar test for several optimisation methods / problems.
    - Each _instance_ should have a unique name
    
- When run, each test should produce:
    - a log (e.g. the method's `log_to_file`)
    - a file with lots of output, in some yet-to-be-determined format. Example entries include datetime, name of the test, the random seed used, the commit hash of the current pints version

- Plotting
    - We should add a script that (uses a library that) can read these 2nd files, and create plots of various quantities, over time.

- Warnings / reporting
    - Eventually, if everything works well, we can build something that emails us if the results drop and stay low for a couple of runs. Instead of emailing we could also just use the cmd line return value to indicate a failure.
    - I think it'd be best to have this analysis separate from the running of the tests, so for them a failure would be an exception occurring.
 
- Travis
    - Travis is for testing. This is testing, so should be ok? Can't see anything in the user agreement that says this would be wrong (bitcoing mining is explicitly not allowed).
    - We need to add a list of tests, and then a file somewhere saying which test was last run, plus a script that will then start on the next test. This way, every time the script is run the next test is started.
    
- Pints
    - We should probably have a local pints in this project, and git pull before every test is run. There's several git python packages. [GitPython](https://github.com/gitpython-developers/GitPython/graphs/contributors) currently seems best, and is what we're using for the web lab.
 
- Seeding
    - Before running each test, we should generate a random seed, and then use this to seed the random generator. This means that we can reproduce the 
    
- Infra
    - Don't think this should be pip-installable, but a requirements.txt would be nice so that we can install dependencies using `pip install -r requirements.txt`.
    
- Storing data
    - I'd like to do everything disk based (inlcuding the current 'status') etc. This makes it easy to do things in a distributed way! For example, we could run a few tests offline
    
- Timing
    - We should log evaluations, and iterations, but _not_ run-time.
    - Two reasons: 1. Benchmarking is very hard, and we can't benchmark on testing machines (which are slow and whose performance varies hugely over time). 2. It'd stop us from being able to add data from different machines.
