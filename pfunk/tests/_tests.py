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


def plot(name, show=False):
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

from .mcmc_normal import MCMCNormal
add(MCMCNormal('AdaptiveCovarianceMCMC', 1, 0.05))
add(MCMCNormal('MetropolisRandomWalkMCMC', 1, 0.05))
add(MCMCNormal('DifferentialEvolutionMCMC', 3, 0.05))
add(MCMCNormal('DreamMCMC', 3, 0.05))
add(MCMCNormal('PopulationMCMC', 1, 1.0))

from .mcmc_banana import MCMCBanana
add(MCMCBanana('AdaptiveCovarianceMCMC', 1))
add(MCMCBanana('MetropolisRandomWalkMCMC', 1))
add(MCMCBanana('DifferentialEvolutionMCMC', 3))
add(MCMCBanana('DreamMCMC', 3))
add(MCMCBanana('PopulationMCMC', 1))

from .mcmc_egg_box import MCMCEggBox
add(MCMCEggBox('AdaptiveCovarianceMCMC', 4))
add(MCMCEggBox('MetropolisRandomWalkMCMC', 4))
add(MCMCEggBox('DifferentialEvolutionMCMC', 4))
add(MCMCEggBox('DreamMCMC', 4))
add(MCMCEggBox('PopulationMCMC', 1))

from .nested_normal import NestedNormal
add(NestedNormal('NestedEllipsoidSampler'))
add(NestedNormal('NestedRejectionSampler'))

from .nested_banana import NestedBanana
add(NestedBanana('NestedEllipsoidSampler'))
add(NestedBanana('NestedRejectionSampler'))

from .nested_egg_box import NestedEggBox
add(NestedEggBox('NestedEllipsoidSampler'))
add(NestedEggBox('NestedRejectionSampler'))
