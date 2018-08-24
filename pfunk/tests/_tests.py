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
    if not isinstance(test, pfunk.FunctionalTest):
        raise ValueError('All tests must extend FunctionalTest.')
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
    return _tests[name].analyse()


from .optimisation import OptimisationLogistic
add(OptimisationLogistic('CMAES'))
add(OptimisationLogistic('XNES'))
add(OptimisationLogistic('SNES'))
add(OptimisationLogistic('PSO'))

from .optimisation import OptimisationFN
add(OptimisationFN('CMAES'))
add(OptimisationFN('XNES'))
add(OptimisationFN('SNES'))
add(OptimisationFN('PSO'))

from .optimisation import OptimisationBR
add(OptimisationBR('CMAES'))
add(OptimisationBR('XNES'))
add(OptimisationBR('SNES'))
add(OptimisationBR('PSO'))

from .sampling_normal import SamplingNormal
add(SamplingNormal('AdaptiveCovarianceMCMC', 1))
add(SamplingNormal('MetropolisRandomWalkMCMC', 1))
add(SamplingNormal('DifferentialEvolutionMCMC', 3))
add(SamplingNormal('PopulationMCMC', 1))

from .sampling_banana import SamplingBanana
add(SamplingBanana('AdaptiveCovarianceMCMC', 1))
add(SamplingBanana('MetropolisRandomWalkMCMC', 1))
add(SamplingBanana('DifferentialEvolutionMCMC', 3))
add(SamplingBanana('PopulationMCMC', 1))

from .sampling_egg_box import SamplingEggBox
add(SamplingEggBox('AdaptiveCovarianceMCMC', 1))
add(SamplingEggBox('MetropolisRandomWalkMCMC', 1))
add(SamplingEggBox('DifferentialEvolutionMCMC', 3))
add(SamplingEggBox('PopulationMCMC', 1))

