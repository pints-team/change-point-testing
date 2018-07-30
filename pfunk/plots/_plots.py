#
# This module contains a dict of all available plots.
#
# This file is part of Pints Functional Testing.
#  Copyright (c) 2017-2018, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the Pints
#  functional testing software package.
#
import pfunk

_plots = {}


def add(plot):
    """ Adds a plot to the list of available plots. """
    if not isinstance(plot, pfunk.FunctionalTestPlot):
        raise ValueError('Only FunctionalTestPlot objects can be added.')
    _plots[plot.name()] = plot


def plots():
    """ Returns a sorted list of plot names. """
    return sorted(_plots.keys())


def run(name, show=False):
    """ Runs a selected plot. """
    _plots[name].run(show)


from .plot1 import Test1Plot
add(Test1Plot())

from .plot2 import Test2Plot
add(Test2Plot())

from .opt_fn_plot import OptimisationFitzhughNagumo
add(OptimisationFitzhughNagumo('CMAES', [20, 40, 80, 160, 320]))
add(OptimisationFitzhughNagumo('XNES', [20, 40, 80, 160, 320]))
add(OptimisationFitzhughNagumo('SNES', [20, 40, 80, 160, 320]))
add(OptimisationFitzhughNagumo('PSO', [20, 40, 80, 160, 320]))

