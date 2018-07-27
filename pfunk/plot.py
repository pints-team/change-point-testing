#
# Fake test 1
#
# This file is part of Pints Functional Testing.
#  Copyright (c) 2017-2018, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the Pints
#  functional testing software package.
#
from __future__ import absolute_import, division
from __future__ import print_function, unicode_literals

import os
import re

import pfunk
import logging


class FunctionalTestPlot(object):
    """
    Abstract base class for functional test plots.
    """
    def __init__(self, plot_name):
        plot_name = str(plot_name)
        if pfunk.NAME_FORMAT.match(plot_name) is None:
            raise ValueError('Invalid plot name: ' + plot_name)
        self._plot_name = plot_name

    def name(self):
        return self._plot_name

    def run(self):
        raise NotImplementedError


class SingleTestPlot(FunctionalTestPlot):
    """
    Abstract base class for plots of a single test.
    """
    def __init__(self, plot_name, test_name):
        super(SingleTestPlot, self).__init__(plot_name)

        test_name = str(test_name)
        if pfunk.NAME_FORMAT.match(test_name) is None:
            raise ValueError('Invalid test name: ' + test_name)
        self._test_name = test_name

    def _run(self, results, plot_path):
        raise NotImplementedError

    def run(self):
        """
        Runs this test and logs the output.
        """
        # Create logger for _global_ console/file output
        log = logging.getLogger(__name__)
        log.info('Running plot: ' + self.name())

        # Load test results
        results = pfunk.io.find_test_results(self._test_name)

        # Create plot name
        date = pfunk.date()
        name = self.name()
        path = self._plot_name + '-' + date + '.png'
        plot_path = pfunk.io.unique_path(os.path.join(pfunk.DIR_PLOT, path))

        # Plot
        try:
            self._plot(results, plot_path)
        except Exception:
            log.error('Exception in plot: ' + self.name())
            raise

