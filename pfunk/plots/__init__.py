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
    """ Returns a sorted list of test names. """
    return sorted(_plots.keys())


def run(name):
    """ Runs a selected test. """
    _plots[name].run()


from .plot1 import Test1Plot
add(Test1Plot())

from .plot2 import Test2Plot
add(Test2Plot())

