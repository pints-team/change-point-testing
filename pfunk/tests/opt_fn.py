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

import pfunk
import matplotlib.pyplot as plt


class OptimisationFitzhughNagumo(pfunk.FunctionalTest):
    """
    Runs an optimisation on the Fitzhugh-Nagumo toy model, with a
    user-specified maximum number of iterations.

    Arguments:

    ``method``
        A *string* indicating the method to use, e.g. 'CMAES'. (Must be a
        string, because we shouldn't import pints before we start testing.)
    ``max_iterations``
        The maximum number of iterations to run (> 0).

    """

    def __init__(self, method, max_iterations):

        # Can't check method here, don't want to import pints
        self._method = str(method)

        # Check number of iterations
        max_iterations = int(max_iterations)
        if not max_iterations > 0:
            raise ValueError('Maximum number of iterations must be > 0.')
        self._max_iterations = max_iterations

        # Create name and initialise
        name = 'opt_fn_' + method + '_' + str(max_iterations)
        super(OptimisationFitzhughNagumo, self).__init__(name)

    def _run(self, result, log_path):

        import pints
        import pints.toy
        import numpy as np

        # Store method and iterations
        result['method'] = self._method
        result['max_iterations'] = self._max_iterations

        # Get method class
        method = getattr(pints, self._method)

        # Create a model
        model = pints.toy.FitzhughNagumoModel()

        # Run a simulation
        true_parameters = [0.1, 0.5, 3]
        times = np.linspace(0, 20, 200)
        values = model.simulate(true_parameters, times)

        # Add some noise
        sigma = 0.5
        noisy = values + np.random.normal(0, sigma, values.shape)

        # Create problem
        problem = pints.MultiOutputProblem(model, times, noisy)
        score = pints.SumOfSquaresError(problem)

        # Evaluate at true parameters
        ftrue = score(true_parameters)

        # Select boundaries
        boundaries = pints.RectangularBoundaries([0, 0, 0], [10, 10, 10])

        # Select a random starting point
        x0 = boundaries.sample(1)[0]

        # Create an optimisation problem
        opt = pints.Optimisation(
            score, x0, boundaries=boundaries, method=method)

        # Log to file
        opt.set_log_to_screen(False)
        opt.set_log_to_file(log_path)

        # Set max iterations
        opt.set_max_iterations(self._max_iterations)

        # Run
        xbest, fbest = opt.run()

        # Store solution
        result['xbest'] = xbest
        result['fbest'] = fbest

        # Store solution, relative to likelihood at 'true' solution
        result['fbest_relative'] = fbest / ftrue

        # Store status
        result['status'] = 'done'

    def _analyse(self, results):
        return pfunk.assert_not_deviated_from(1.0, 1.0, results, 'fbest_relative')

    def _plot(self, results):
        fig = plt.figure()
        plt.title('FN Optimisation with ' + self._method + 'and max iterations ' + str(self._max_iterations))

        plt.xlabel('Run')
        plt.ylabel('Score relative to f(true)')

        commits, mean, std = pfunk.gather_statistics_per_commit(results, 'fbest_relative')

        plt.errorbar(commits, mean, yerr=std)
        fig.autofmt_xdate()

        return fig
