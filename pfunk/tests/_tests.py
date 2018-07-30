#
# This module contains a dict of all available tests.
#
# This file is part of Pints Functional Testing.
#  Copyright (c) 2017-2018, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the Pints
#  functional testing software package.
#
import pfunk
from pfunk import FunctionalTestGroup as Group

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


from .test1 import Test1
add(Test1())

from .test2 import Test2
from .test3 import Test3
add(Group('test2_and_3', Test2(), Test3()))

from .opt_fn import OptimisationFitzhughNagumo
add(Group(
    'opt_fn_CMAES',
    OptimisationFitzhughNagumo('CMAES', 20),
    OptimisationFitzhughNagumo('CMAES', 40),
    OptimisationFitzhughNagumo('CMAES', 80),
    OptimisationFitzhughNagumo('CMAES', 120),
    OptimisationFitzhughNagumo('CMAES', 320),
))

add(Group(
    'opt_fn_XNES',
    OptimisationFitzhughNagumo('SNES', 20),
    OptimisationFitzhughNagumo('SNES', 40),
    OptimisationFitzhughNagumo('SNES', 80),
    OptimisationFitzhughNagumo('SNES', 120),
    OptimisationFitzhughNagumo('SNES', 320),
))

add(Group(
    'opt_fn_SNES',
    OptimisationFitzhughNagumo('XNES', 20),
    OptimisationFitzhughNagumo('XNES', 40),
    OptimisationFitzhughNagumo('XNES', 80),
    OptimisationFitzhughNagumo('XNES', 120),
    OptimisationFitzhughNagumo('XNES', 320),
))

add(Group(
    'opt_fn_PSO',
    OptimisationFitzhughNagumo('PSO', 20),
    OptimisationFitzhughNagumo('PSO', 40),
    OptimisationFitzhughNagumo('PSO', 80),
    OptimisationFitzhughNagumo('PSO', 120),
    OptimisationFitzhughNagumo('PSO', 320),
))
