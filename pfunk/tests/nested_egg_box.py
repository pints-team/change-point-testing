#
# Nested sampling test: Can we recover a simple egg box distribution?
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


class NestedEggBox(pfunk.FunctionalTest):
    """
    Runs an NestedSampling algorithm on a simple egg box LogPDF. Stores
    a Kullback-Leibler-based score for the difference between the result and
    the true solution.

    Arguments:

    ``method``
        A *string* indicating the method to use, e.g. 'AdaptiveCovarianceMCMC'.
        (Must be a string, because we shouldn't import pints before we start
        testing.)

    """

    def __init__(self, method, pass_threshold):

        # Can't check method here, don't want to import pints
        self._method = str(method)
        self._pass_threshold = float(pass_threshold)

        # Create name and initialise
        name = 'nested_egg_box_' + self._method
        super(NestedEggBox, self).__init__(name)

    def _run(self, result, log_path):

        import pints
        import pints.toy
        import numpy as np

        import logging
        log = logging.getLogger(__name__)

        DEBUG = False

        # Store method name
        result['method'] = self._method
        log.info('Using method: ' + self._method)

        # Get method class
        method = getattr(pints, self._method)

        # Create a log pdf (use multi-modal, but with a single mode)
        sigma = 2
        r = 4
        log_pdf = pints.toy.SimpleEggBoxLogPDF(sigma=sigma, r=r)

        # Create a log prior
        d = 2 * 6 * r * sigma
        log_prior = pints.MultivariateNormalLogPrior(
            [0, 0], [[d, 0], [0, d]])

        # Create a nested sampler
        sampler = method(log_pdf, log_prior)

        # Log to file
        if not DEBUG:
            sampler.set_log_to_screen(False)
        sampler.set_log_to_file(log_path)

        # Set max iterations
        sampler.set_iterations(8000)
        sampler.set_posterior_samples(2000)

        # Run
        samples, logZ = sampler.run()

        # Calculate KL-based score after every n-th iteration
        n = 100
        iters = list(range(n, len(samples) + n, n))
        result['iters'] = iters
        result['klds'] = [log_pdf.kl_divergence(samples[:i]) for i in iters]

        # Store kullback-leibler-based score
        result['kld'] = log_pdf.kl_score(samples)

        # Store status
        result['status'] = 'done'

    def _analyse(self, results):
        return pfunk.assert_not_deviated_from(0, self._pass_threshold, results, 'kld')

    def _plot(self, results):

        figs = []

        # Figure: KL per commit
        figs.append(pfunk.plot.variable(
            results,
            'kld',
            'Egg box w. ' + self._method,
            'Kullback-Leibler-based score', 3*self._pass_threshold)
        )

        # Figure: KL over time
        figs.append(pfunk.plot.convergence(
            results,
            'iters',
            'klds',
            'Egg box w. ' + self._method,
            'Iteration',
            'Kullback-Leibler-based score',
            0, 1)
        )

        return figs
