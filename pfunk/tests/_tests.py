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


def rwg(name, date, path, identifier=None):
    """ Generator that returns a ResultsDatabaseWriter. """
    return pfunk.ResultsDatabaseWriter(path, name, date, identifier)


# All optimisers
from .optimisation import OptimisationLogistic
add(OptimisationLogistic(rwg, 'CMAES', 1.0))
add(OptimisationLogistic(rwg, 'NelderMead', 1.0))
add(OptimisationLogistic(rwg, 'PSO', 1.0))
add(OptimisationLogistic(rwg, 'SNES', 1.0))
add(OptimisationLogistic(rwg, 'XNES', 1.0))


# Global optimisers
from .optimisation import OptimisationFN
add(OptimisationFN(rwg, 'CMAES', 1.0))
add(OptimisationFN(rwg, 'PSO', 1.0))
add(OptimisationFN(rwg, 'SNES', 1.0))
add(OptimisationFN(rwg, 'XNES', 1.0))


# Global optimisers
from .optimisation import OptimisationBR
add(OptimisationBR(rwg, 'CMAES', 2.0))
add(OptimisationBR(rwg, 'PSO', 2.0))
add(OptimisationBR(rwg, 'SNES', 4.0))
add(OptimisationBR(rwg, 'XNES', 2.0))


# All MCMC methods
from .mcmc_normal import MCMCNormal
add(MCMCNormal(rwg, 'DifferentialEvolutionMCMC', 3, 0.2))
add(MCMCNormal(rwg, 'DreamMCMC', 3, 0.1))
add(MCMCNormal(rwg, 'EmceeHammerMCMC', 3, 0.1))
add(MCMCNormal(rwg, 'HaarioACMC', 1, 0.05))
add(MCMCNormal(rwg, 'HaarioBardenetACMC', 1, 0.05))
add(MCMCNormal(rwg, 'HamiltonianMCMC', 1, 0.05, max_iter=1000))
add(MCMCNormal(rwg, 'MALAMCMC', 1, 0.1))
add(MCMCNormal(rwg, 'MetropolisRandomWalkMCMC', 1, 0.2))
add(MCMCNormal(rwg, 'PopulationMCMC', 1, 1.0))
add(MCMCNormal(rwg, 'RaoBlackwellACMC', 1, 0.05))
add(MCMCNormal(rwg, 'RelativisticMCMC', 1, 1.0))
add(MCMCNormal(rwg, 'SliceDoublingMCMC', 1, 0.01))
add(MCMCNormal(rwg, 'SliceStepoutMCMC', 1, 0.01))


# All MCMC methods?
#   issue 518 - turn off banana test for mcmc samplers
#   michael - have re-enabled these to see what happens
from .mcmc_banana import MCMCBanana
add(MCMCBanana(rwg, 'DifferentialEvolutionMCMC', 4, 1.0))
add(MCMCBanana(rwg, 'DreamMCMC', 4, 1.0))
add(MCMCBanana(rwg, 'EmceeHammerMCMC', 4, 1.0))
add(MCMCBanana(rwg, 'HaarioACMC', 1, 1.0))
add(MCMCBanana(rwg, 'HaarioBardenetACMC', 1, 1.0))
add(MCMCBanana(rwg, 'HamiltonianMCMC', 1, 1.0))
add(MCMCBanana(rwg, 'MALAMCMC', 1, 1.0))
add(MCMCBanana(rwg, 'MetropolisRandomWalkMCMC', 1, 1.0))
add(MCMCBanana(rwg, 'PopulationMCMC', 1, 1.5, max_iter=50000))
add(MCMCBanana(rwg, 'RaoBlackwellACMC', 1, 1.0))
add(MCMCBanana(rwg, 'RelativisticMCMC', 1, 1.0))
add(MCMCBanana(rwg, 'SliceDoublingMCMC', 1, 1.0))
add(MCMCBanana(rwg, 'SliceStepoutMCMC', 1, 1.0))


# Nested samplers
from .nested_normal import NestedNormal
add(NestedNormal(rwg, 'NestedEllipsoidSampler', 0.16))
add(NestedNormal(rwg, 'NestedRejectionSampler', 0.16))


# Nested samplers
from .nested_banana import NestedBanana
add(NestedBanana(rwg, 'NestedEllipsoidSampler', 0.1))
add(NestedBanana(rwg, 'NestedRejectionSampler', 1.0))


# Nested samplers
from .nested_egg_box import NestedEggBox
add(NestedEggBox(rwg, 'NestedEllipsoidSampler', 0.12))
add(NestedEggBox(rwg, 'NestedRejectionSampler', 0.12))

