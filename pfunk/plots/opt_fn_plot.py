#
# Fake plot for fake test 2
#
# This file is part of Pints Functional Testing.
#  Copyright (c) 2017-2018, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the Pints
#  functional testing software package.
#
from __future__ import absolute_import, division
from __future__ import print_function, unicode_literals

import matplotlib.pyplot as plt

import pfunk


class OptimisationFitzhughNagumoByDate(pfunk.MultiTestPlot):
    """
    Plot for Fitzhugh-Nagumo optimiser tests.
    """
    def __init__(self, method, max_iterations):

        self._method = str(method)
        self._max_iterations = [int(x) for x in max_iterations]

        plot_name = 'opt_fn_' + method
        test_names = [plot_name + '_' + str(i) for i in max_iterations]

        super(OptimisationFitzhughNagumoByDate, self).__init__(
            plot_name, test_names)

    def _run(self, results, plot_path, show):

        n = len(self._max_iterations)

        plt.figure()
        plt.title('FN Optimisation with ' + self._method)

        for i, r in enumerate(results):
            maxi = self._max_iterations[i]

            plt.suptitle('Max iterations: ' + str(maxi))
            #plt.subplot(n, 1, 1 + i)
            plt.xlabel('Run')
            plt.ylabel('Score relative to f(best)')

            dates, scores = r['date', 'fbest_relative']
            plt.plot(dates, scores, 'o:', label='max ' + str(maxi))

        plt.legend()
        plt.savefig(plot_path)

        if show:
            plt.show()
