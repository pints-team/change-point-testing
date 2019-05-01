#
# This module contains a dict of all available tests.
#
# This file is part of Pints Functional Testing.
#  Copyright (c) 2017-2019, University of Oxford.
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
add(OptimisationLogistic('CMAES', 1.0))
add(OptimisationLogistic('XNES', 1.0))
add(OptimisationLogistic('SNES', 1.0))
add(OptimisationLogistic('PSO', 1.0))


from .optimisation import OptimisationFN
add(OptimisationFN('CMAES', 1.0))
add(OptimisationFN('XNES', 1.0))
add(OptimisationFN('SNES', 1.0))
add(OptimisationFN('PSO', 1.0))


from .optimisation import OptimisationBR
add(OptimisationBR('CMAES', 2.0))
add(OptimisationBR('XNES', 2.0))
add(OptimisationBR('SNES', 4.0))
add(OptimisationBR('PSO', 2.0))


from .mcmc_normal import MCMCNormal
# Single-chain methods
add(MCMCNormal('AdaptiveCovarianceMCMC', 1, 0.05))
add(MCMCNormal('HamiltonianMCMC', 1, 0.05, max_iter=1000))
add(MCMCNormal('MetropolisRandomWalkMCMC', 1, 0.2))
add(MCMCNormal('PopulationMCMC', 1, 1.0))
# Multi-chain methods
add(MCMCNormal('DifferentialEvolutionMCMC', 3, 0.1))
add(MCMCNormal('DreamMCMC', 3, 0.1))
add(MCMCNormal('EmceeHammerMCMC', 3, 0.1))


# issue 518 - turn off banana test for mcmc samplers
from .mcmc_banana import MCMCBanana
# Single-chain methods
add(MCMCBanana('AdaptiveCovarianceMCMC', 1, 1.0))
#add(MCMCBanana('HamiltonianMCMC', 1, 1.0))  # Requires gradient
add(MCMCBanana('MetropolisRandomWalkMCMC', 5, 1.0))
#add(MCMCBanana('PopulationMCMC', 1, 1.0, 50000))
# Multi-chain methods
# add(MCMCBanana('DifferentialEvolutionMCMC', 3, 1.0))
add(MCMCBanana('DreamMCMC', 4, 1.0))
add(MCMCBanana('EmceeHammerMCMC', 3, 1.0))


# issue 516 - turn off egg box test for mcmc samplers
# due to high difficulty of the problem
#from .mcmc_egg_box import MCMCEggBox
# Single-chain methods
#add(MCMCEggBox('AdaptiveCovarianceMCMC', 1, 1.0))
#add(MCMCEggBox('HamiltonianMCMC', 1, 1.0))  # Requires gradient
#add(MCMCEggBox('MetropolisRandomWalkMCMC', 1, 1.0))
#add(MCMCEggBox('PopulationMCMC', 1, 1.0))
# Multi-chain methods
#add(MCMCEggBox('DifferentialEvolutionMCMC', 6, 1.0))
#add(MCMCEggBox('DreamMCMC', 6, 1.0))


from .nested_normal import NestedNormal
add(NestedNormal('NestedEllipsoidSampler', 0.16))
add(NestedNormal('NestedRejectionSampler', 0.16))


from .nested_banana import NestedBanana
add(NestedBanana('NestedEllipsoidSampler', 0.1))
add(NestedBanana('NestedRejectionSampler', 1.0))


from .nested_egg_box import NestedEggBox
add(NestedEggBox('NestedEllipsoidSampler', 0.12))
add(NestedEggBox('NestedRejectionSampler', 0.12))

