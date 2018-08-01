#
# This module contains a dict of all available tests.
#
# This file is part of Pints Functional Testing.
#  Copyright (c) 2017-2018, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the Pints
#  functional testing software package.
#
import pfunk

_tests = {}


def add(test):
    """ Adds a test to the list of available tests. """
    if not isinstance(test, pfunk.AbstractFunctionalTest):
        raise ValueError('All tests must extend AbstractFunctionalTest.')
    _tests[test.name()] = test


def tests():
    """ Returns a sorted list of test names. """
    return sorted(_tests.keys())


def run(name):
    """ Runs a selected test. """
    _tests[name].run()


def plot(name, show):
    """ Generates a selected test's plots. """
    _tests[name].plot(show)


def analyse(name):
    """ Analyse results for a selected test. """
    _tests[name].analyse()


from .test1 import Test1
add(Test1())


from .opt_fn import OptimisationFitzhughNagumo
add(OptimisationFitzhughNagumo('CMAES', 100))
