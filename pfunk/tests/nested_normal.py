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

        # Create a log pdf (use multi-modal, but with a single mode)
        xtrue = np.array([2, 2])
        log_pdf = pints.toy.MultimodalNormalLogPDF([xtrue])

        # Create a log prior
        log_prior = pints.MultivariateNormalLogPrior(xtrue, np.eye(2) * 2)

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

        # Store true solution
        result['true'] = xtrue
        result['mean_p0'] = np.mean(samples[:, 0])
        result['mean_p1'] = np.mean(samples[:, 1])
        result['std_p0'] = np.std(samples[:, 0])
        result['std_p1'] = np.std(samples[:, 1])

        xmean = np.mean(samples, axis=0)
        result['distance'] = np.linalg.norm(xtrue - xmean)

        # Store status
        result['status'] = 'done'

    def _analyse(self, results):
        return pfunk.assert_not_deviated_from(
            1.0, 1.0, results, 'distance')

    def _plot(self, results):

        figs = []

        # Figure: Distance to true mean
        fig = plt.figure()
        figs.append(fig)
        plt.suptitle(pfunk.date())
        plt.title('Normal LogPDF w. ' + self._method)
        plt.xlabel('Commit')
        plt.ylabel('Distance from mean to true (mean & std)')
        commits, mean, std = pfunk.gather_statistics_per_commit(
            results, 'distance')
        plt.errorbar(commits, mean, yerr=std, ecolor='k', fmt='o-', capsize=3)
        fig.autofmt_xdate()

        return figs
