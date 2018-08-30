#
# Simplest nested sampling test: Can we recover a unimodal normal distribution?
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


class NestedNormal(pfunk.FunctionalTest):
    """
    Runs a NestedSampling algorithm on a normal LogPDF. Stores the distance of
    the resulting mean to the true solution.

    Arguments:

    ``method``
        A *string* indicating the method to use, e.g. 'AdaptiveCovarianceMCMC'.
        (Must be a string, because we shouldn't import pints before we start
        testing.)

    """

    def __init__(self, method):

        # Can't check method here, don't want to import pints
        self._method = str(method)

        # Create name and initialise
        name = 'nested_normal_' + self._method
        super(NestedNormal, self).__init__(name)

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

        # Create a log pdf
        xtrue = np.array([2, 4])
        sigma = np.diag(np.array([1, 3]))
        log_pdf = pints.toy.NormalLogPDF(xtrue, sigma)

        # Create a log prior
        log_prior = pints.MultivariateNormalLogPrior(xtrue + 1, sigma * 2)

        # Create a nested sampler
        sampler = method(log_pdf, log_prior)

        # Log to file
        if not DEBUG:
            sampler.set_log_to_screen(False)
        sampler.set_log_to_file(log_path)

        # Set max iterations
        sampler.set_iterations(4000)
        sampler.set_posterior_samples(1000)

        # Run
        samples, logZ = sampler.run()

        # Calculate KLD after every n-th iteration
        n = 100
        iters = list(range(n, len(samples) + n, n))
        result['iters'] = iters
        result['klds'] = [log_pdf.kl_divergence(samples[:i]) for i in iters]

        # Store kullback-leibler divergence
        result['kld'] = log_pdf.kl_divergence(samples)

        # Store status
        result['status'] = 'done'

    def _analyse(self, results):
        return pfunk.assert_not_deviated_from(0, 0.15, results, 'kld')

    def _plot(self, results):

        figs = []

        # Figure: KL per commit
        figs.append(pfunk.plot.variable(
            results,
            'kld',
            'Normal w. ' + self._method,
            'Kullback-Leibler divergence')
        )

        # Figure: KL over time
        fig = plt.figure()
        figs.append(fig)
        plt.suptitle(pfunk.date())
        plt.title('Normal w. ' + self._method)
        plt.xlabel('Iteration')
        plt.ylabel('Kullback-Leibler divergence')
        iters, klds = results['iters', 'klds']
        for i, x in enumerate(iters):
            plt.plot(x, klds[i])

        return figs
