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


def run(name, database, run_number=0,):
    """ Runs a selected test. """
    print(f'Running test {name} run {run_number}', flush=True)
    _tests[name].run(database, run_number)


def plot(name, database, show=False):
    """ Generates a selected test's plots. """
    _tests[name].plot(database, show)


def analyse(name, database):
    """ Analyse results for a selected test. """
    return _tests[name].analyse(database)


def results_writer_generator(name, date, path, identifier=None):
    """ Returns a ResultsDatabaseWriter. """
    return pfunk.ResultsDatabaseWriter(path, name, date, identifier)


from .optimisation import OptimisationLogistic
add(OptimisationLogistic(results_writer_generator, 'CMAES', 1.0))
add(OptimisationLogistic(results_writer_generator, 'XNES', 1.0))
add(OptimisationLogistic(results_writer_generator, 'SNES', 1.0))
add(OptimisationLogistic(results_writer_generator, 'PSO', 1.0))


from .optimisation import OptimisationFN
add(OptimisationFN(results_writer_generator, 'CMAES', 1.0))
add(OptimisationFN(results_writer_generator, 'XNES', 1.0))
add(OptimisationFN(results_writer_generator, 'SNES', 1.0))
add(OptimisationFN(results_writer_generator, 'PSO', 1.0))


from .optimisation import OptimisationBR
add(OptimisationBR(results_writer_generator, 'CMAES', 2.0))
add(OptimisationBR(results_writer_generator, 'XNES', 2.0))
add(OptimisationBR(results_writer_generator, 'SNES', 4.0))
add(OptimisationBR(results_writer_generator, 'PSO', 2.0))


from .mcmc_normal import MCMCNormal
# Single-chain methods
add(MCMCNormal(results_writer_generator, 'AdaptiveCovarianceMCMC', 1, 0.05))
add(MCMCNormal(
    results_writer_generator, 'HamiltonianMCMC', 1, 0.05, max_iter=1000))
add(MCMCNormal(results_writer_generator, 'MetropolisRandomWalkMCMC', 1, 0.2))
add(MCMCNormal(results_writer_generator, 'PopulationMCMC', 1, 1.0))
# Multi-chain methods
add(MCMCNormal(results_writer_generator, 'DifferentialEvolutionMCMC', 3, 0.1))
add(MCMCNormal(results_writer_generator, 'DreamMCMC', 3, 0.1))
add(MCMCNormal(results_writer_generator, 'EmceeHammerMCMC', 3, 0.1))


# issue 518 - turn off banana test for mcmc samplers
from .mcmc_banana import MCMCBanana
# Single-chain methods
add(MCMCBanana(results_writer_generator, 'AdaptiveCovarianceMCMC', 1, 1.0))
# Requires gradient
#add(MCMCBanana(results_writer_generator, 'HamiltonianMCMC', 1, 1.0))
add(MCMCBanana(results_writer_generator, 'MetropolisRandomWalkMCMC', 5, 1.0))
#add(MCMCBanana(results_writer_generator, 'PopulationMCMC', 1, 1.0, 50000))
# Multi-chain methods
#add(MCMCBanana(results_writer_generator, 'DifferentialEvolutionMCMC', 3, 1.0))
add(MCMCBanana(results_writer_generator, 'DreamMCMC', 4, 1.0))
add(MCMCBanana(results_writer_generator, 'EmceeHammerMCMC', 3, 1.0))


# issue 516 - turn off egg box test for mcmc samplers
# due to high difficulty of the problem
#from .mcmc_egg_box import MCMCEggBox
# Single-chain methods
#add(MCMCEggBox(results_writer_generator, 'AdaptiveCovarianceMCMC', 1, 1.0))
#add(MCMCEggBox(results_writer_generator, 'HamiltonianMCMC', 1, 1.0))
#add(MCMCEggBox(results_writer_generator, 'MetropolisRandomWalkMCMC', 1, 1.0))
#add(MCMCEggBox(results_writer_generator, 'PopulationMCMC', 1, 1.0))
# Multi-chain methods
#add(MCMCEggBox(results_writer_generator, 'DifferentialEvolutionMCMC', 6, 1.0))
#add(MCMCEggBox(results_writer_generator, 'DreamMCMC', 6, 1.0))


from .nested_normal import NestedNormal
add(NestedNormal(results_writer_generator, 'NestedEllipsoidSampler', 0.16))
add(NestedNormal(results_writer_generator, 'NestedRejectionSampler', 0.16))


from .nested_banana import NestedBanana
add(NestedBanana(results_writer_generator, 'NestedEllipsoidSampler', 0.1))
add(NestedBanana(results_writer_generator, 'NestedRejectionSampler', 1.0))


from .nested_egg_box import NestedEggBox
add(NestedEggBox(results_writer_generator, 'NestedEllipsoidSampler', 0.12))
add(NestedEggBox(results_writer_generator, 'NestedRejectionSampler', 0.12))

