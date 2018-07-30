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
import numpy as np

import pfunk


class OptimisationFitzhughNagumoByCommit(pfunk.MultiTestPlot):
    """
    Plot for Fitzhugh-Nagumo optimiser tests.
    """
    def __init__(self, method, max_iterations):

        self._method = str(method)
        self._max_iterations = [int(x) for x in max_iterations]

        plot_name = 'opt_fn_by_commit_' + method

        test_name = 'opt_fn_' + method
        test_names = [test_name + '_' + str(i) for i in max_iterations]

        super(OptimisationFitzhughNagumoByCommit, self).__init__(
            plot_name, test_names)

    def _run(self, results, plot_path, show):

        n = len(self._max_iterations)

        fig = plt.figure()
        plt.title('FN Optimisation with ' + self._method)

        for i, r in enumerate(results):
            maxi = self._max_iterations[i]

            plt.xlabel('Run')
            plt.ylabel('Score relative to f(true)')

            # Fetch commits and scores
            commits, scores = r['pints_commit', 'fbest_relative']

            # Gather per commit
            x = []
            xinv = {}
            y = []
            for i, commit in enumerate(commits):
                if commit in xinv:
                    xinv[commit]
                    y[xinv[commit]].append(scores[i])
                else:
                    xinv[commit] = len(x)
                    x.append(commit)
                    y.append([scores[i]])
            mean = []
            std = []
            for values in y:
                mean.append(np.mean(values))
                std.append(np.std(values))

            plt.errorbar(x, mean, yerr=std, label='max iter ' + str(maxi))

        fig.autofmt_xdate()

        plt.legend()
        plt.savefig(plot_path)

        if show:
            plt.show()
