#
# Fake test 1
#
# This file is part of Pints Functional Testing.
#  Copyright (c) 2017-2019, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the Pints
#  functional testing software package.
#
from __future__ import absolute_import, division
from __future__ import print_function, unicode_literals

import pfunk
from scipy import stats


class Optimisation(pfunk.FunctionalTest):
    """
    Runs an optimisation and tracks convergence and relative best position.

    Arguments:

    ``method``
        A *string* indicating the method to use, e.g. 'CMAES'. (Must be a
        string, because we shouldn't import pints before we start testing.)
    ``max_iterations``
        The maximum number of iterations to run (> 0).

    """

    def __init__(self, method, pass_threshold):

        # Can't check method here, don't want to import pints
        self._method = str(method)
        self._pass_threshold = float(pass_threshold)

        # Create name and initialise
        name = 'opt_' + self._problem_name() + '_' + method
        super(Optimisation, self).__init__(name)

    def _problem(self):
        """
        Returns a tuple ``(score, xtrue, x0, sigma0, boundaries)``.
        """
        raise NotImplementedError

    def _run(self, result):

        import pints
        import numpy as np

        # Store method and iterations
        result['method'] = self._method

        # Get method class
        method = getattr(pints, self._method)

        # Get problem
        score, xtrue, x0, sigma0, boundaries = self._problem()

        # Evaluate at true parameters
        ftrue = score(xtrue)

        # Create optimiser
        optimiser = method(x0, sigma0, boundaries)

        # Count iterations and function evaluations
        iterations = 0
        evaluations = 0
        unchanged_iterations = 0

        # Create parallel evaluator
        n_workers = pints.ParallelEvaluator.cpu_count()
        if isinstance(optimiser, pints.PopulationBasedOptimiser):
            n_workers = min(n_workers, optimiser.population_size())
        evaluator = pints.ParallelEvaluator(score, n_workers=n_workers)

        # Keep track of best position and score
        fbest = float('inf')

        # Start searching
        evals = []
        frels = []

        running = True
        while running:
            xs = optimiser.ask()
            fs = evaluator.evaluate(xs)
            optimiser.tell(fs)

            # Check if new best found
            fnew = optimiser.fbest()
            if fnew < fbest:
                # Check if this counts as a significant change
                if np.abs(fnew - fbest) < 1e-9:
                    unchanged_iterations += 1
                else:
                    unchanged_iterations = 0

                # Update best position
                fbest = fnew
            else:
                unchanged_iterations += 1

            # Update iteration and evaluation count
            iterations += 1
            evaluations += len(fs)

            # Log evaluations and relative score
            evals.append(evaluations)
            frels.append(fbest / ftrue)

            # Maximum number of iterations
            if iterations >= 5000:
                running = False

            # Maximum number of iterations without significant change
            if unchanged_iterations >= 200:
                running = False

            # Error in optimiser
            error = optimiser.stop()
            if error:
                running = False

        # Store solution
        result['xbest'] = optimiser.xbest()
        result['fbest'] = fbest

        # Store solution, relative to likelihood at 'true' solution
        # This should be 1 or below 1 if the optimum was found
        result['fbest_relative'] = fbest / ftrue

        # Store convergence information
        result['evals'] = evals
        result['frels'] = frels

        # Store status
        result['status'] = 'done'

    def _analyse(self, results):
        # The test has passed if the obtained ``fbest_relative`` has stayed
        # near 3 sigma of the mean, with
        return pfunk.assert_not_deviated_from(
            1.0, self._pass_threshold, results, 'fbest_relative')

    def _plot(self, results):

        figs = []

        #
        # Plot 1: Relative score (fbest_relative) per commit.
        #
        figs.append(pfunk.plot.variable(
            results,
            'fbest_relative',
            self.name(),
            'Final f(best) / f(true)', 1 + 3 * self._pass_threshold)
        )

        #
        # Plot 2: Convergence
        #
        # Get good limits for plot
        evals, frels = results['evals', 'frels']
        frels = [f[-1] for f in frels]
        mid, rng = stats.scoreatpercentile(frels, 50), stats.iqr(frels)
        ymin = mid - 2 * rng
        ymax = mid + 2 * rng

        figs.append(pfunk.plot.convergence(
            results,
            'evals',
            'frels',
            self.name(),
            'Evaluations',
            'f(best) / f(true)',
            ymin, ymax)
        )

        # Return
        return figs


class OptimisationFN(Optimisation):
    """
    Optimisation on a fitzhugh-nagumo problem.
    """

    def _problem_name(self):
        return 'fn'

    def _problem(self):
        import numpy as np
        import pints
        import pints.toy

        # Create a model
        model = pints.toy.FitzhughNagumoModel()

        # Run a simulation
        xtrue = [0.1, 0.5, 3]
        times = np.linspace(0, 20, 200)
        values = model.simulate(xtrue, times)

        # Add some noise
        sigma = 0.5
        noisy = values + np.random.normal(0, sigma, values.shape)

        # Create problem
        problem = pints.MultiOutputProblem(model, times, noisy)
        score = pints.SumOfSquaresError(problem)

        # Select boundaries
        boundaries = pints.RectangularBoundaries([0, 0, 0], [10, 10, 10])

        # Select a random starting point
        x0 = boundaries.sample(1)[0]

        # Select an initial sigma
        sigma0 = (1 / 6) * boundaries.range()

        return score, xtrue, x0, sigma0, boundaries


class OptimisationLogistic(Optimisation):
    """
    Optimisation on a logistic model.
    """

    def _problem_name(self):
        return 'logistic'

    def _problem(self):
        import numpy as np
        import pints
        import pints.toy

        # Load a forward model
        model = pints.toy.LogisticModel()

        # Create some toy data
        xtrue = [0.015, 500]
        times = np.linspace(0, 1000, 1000)
        values = model.simulate(xtrue, times)

        # Add noise
        values += np.random.normal(0, 10, values.shape)

        # Create problem
        problem = pints.SingleOutputProblem(model, times, values)
        score = pints.SumOfSquaresError(problem)

        # Select some boundaries
        boundaries = pints.RectangularBoundaries([0, 400], [0.03, 600])

        # Select a random starting point
        x0 = boundaries.sample(1)[0]

        # Select an initial sigma
        sigma0 = (1 / 6) * boundaries.range()

        return score, xtrue, x0, sigma0, boundaries


class OptimisationBR(Optimisation):
    """
    Optimisation on a Beeler-Reuter model.
    """

    def _problem_name(self):
        return 'br'

    def _problem(self):
        import numpy as np
        import pints
        import pints.toy

        # Load a forward model
        model = pints.toy.ActionPotentialModel()

        # Create some toy data
        xtrue = model.suggested_parameters()
        times = model.suggested_times()
        values = model.simulate(xtrue, times)

        # Add noise
        values[:, 0] += np.random.normal(0, 1, values[:, 0].shape)
        values[:, 1] += np.random.normal(0, 5e-7, values[:, 1].shape)

        # Create problem and a weighted score function
        problem = pints.MultiOutputProblem(model, times, values)
        weights = [1 / 70, 1 / 0.000006]
        score = pints.SumOfSquaresError(problem, weights=weights)

        # Select some boundaries
        lower = xtrue - 2
        upper = xtrue + 2
        boundaries = pints.RectangularBoundaries(lower, upper)

        # Select a random starting point
        x0 = boundaries.sample(1)[0]

        # Select an initial sigma
        sigma0 = (1 / 6) * boundaries.range()

        return score, xtrue, x0, sigma0, boundaries
