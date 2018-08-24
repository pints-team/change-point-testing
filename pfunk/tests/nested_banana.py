#
# Nested sampling test: Can we recover a twisted gaussian banana distribution?
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


class NestedBanana(pfunk.FunctionalTest):
    """
    Runs a NestedSampling algorithm on a twisted gaussian banana LogPDF. Stores
    the Kullback-Leibler divergence between the result and the true solution.

    Arguments:

    ``method``
        A *string* indicating the method to use, e.g. 'NestedEllipsoidSampler'.
        (Must be a string, because we shouldn't import pints before we start
        testing.)

    """

    def __init__(self, method):

        # Can't check method here, don't want to import pints
        self._method = str(method)

        # Create name and initialise
        name = 'nested_banana_' + self._method
        super(NestedBanana, self).__init__(name)

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
        log_pdf = pints.toy.TwistedGaussianLogPDF(dimension=2, b=0.1)

        # Create a log prior
        log_prior = pints.MultivariateNormalLogPrior(
            [0, 0], [[10, 0], [0, 10]])

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

        # Store kullback-leibler divergence
        result['kld'] = log_pdf.kl_divergence(samples)

        # Store status
        result['status'] = 'done'

    def _analyse(self, results):
        return pfunk.assert_not_deviated_from(0, 0.05, results, 'kld')

    def _plot(self, results):

        figs = []

        # Figure: KL per commit
        fig = plt.figure()
        figs.append(fig)
        plt.suptitle(pfunk.date())
        plt.title('Banana w. ' + self._method)
        plt.xlabel('Commit')
        plt.ylabel('Kullback-Leibler divergence (mean & std)')
        commits, mean, std = pfunk.gather_statistics_per_commit(results, 'kld')
        plt.errorbar(commits, mean, yerr=std, ecolor='k', fmt='o-', capsize=3)
        fig.autofmt_xdate()

        return figs
