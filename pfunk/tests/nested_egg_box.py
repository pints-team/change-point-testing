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

    def __init__(self, method):

        # Can't check method here, don't want to import pints
        self._method = str(method)

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
        sampler.set_max_iterations(8000)
        sampler.set_posterior_samples(2000)

        # Run
        samples, logZ = sampler.run()

        # Store kullback-leibler-based score
        result['kld'] = log_pdf.kl_score(samples)

        # Store status
        result['status'] = 'done'

    def _analyse(self, results):
        return pfunk.assert_not_deviated_from(0, 0.5, results, 'kld')

    def _plot(self, results):

        figs = []

        # Figure: KL per commit
        fig = plt.figure()
        figs.append(fig)
        plt.suptitle(pfunk.date())
        plt.title('Egg box w. ' + self._method)
        plt.xlabel('Commit')
        plt.ylabel('Kullback-Leibler-based score (mean & std)')
        commits, mean, std = pfunk.gather_statistics_per_commit(results, 'kld')
        plt.errorbar(commits, mean, yerr=std, ecolor='k', fmt='o-', capsize=3)
        fig.autofmt_xdate()

        return figs
