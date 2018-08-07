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


class SamplingNormal(pfunk.FunctionalTest):
    """
    Runs an MCMCSampling algorithm on a normal LogPDF. Stores the distance of
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
        name = 'sampling_normal_' + method
        super(SamplingNormal, self).__init__(name)

    def _run(self, result, log_path):

        import pints
        import pints.toy
        import numpy as np

        import logging
        log = logging.getLogger(__name__)

        # Store method name
        result['method'] = self._method
        log.info('Using method: ' + self._method)

        # Get method class
        method = getattr(pints, self._method)

        # Create a log pdf (use multi-modal, but with a single mode)
        x_true = np.array([2, 2])
        logpdf = pints.toy.MultimodalNormalLogPDF([x_true])

        # Generate a random start point
        x0 = [x_true * np.random.normal(0, 3, size=2)]

        # Create an optimisation problem
        mcmc = pints.MCMCSampling(logpdf, 1, x0, method=method)

        # Log to file
        mcmc.set_log_to_screen(False)
        mcmc.set_log_to_file(log_path)

        # Set max iterations
        mcmc.set_max_iterations(2000)
        if mcmc.method_needs_initial_phase():
            mcmc.set_initial_phase_iterations(1000)

        # Run
        chain = mcmc.run()[0]

        # Remove burn-in
        chain = chain[1000:, :]
        log.info('Chain shape (without burn-in): ' + str(chain.shape))
        log.info('Chain mean: ' + str(np.mean(chain, axis=0)))

        # Store true solution
        result['true'] = x_true
        result['mean_p0'] = np.mean(chain[:, 0])
        result['mean_p1'] = np.mean(chain[:, 1])
        result['std_p0'] = np.std(chain[:, 0])
        result['std_p1'] = np.std(chain[:, 1])

        x_mean = np.mean(chain, axis=0)
        result['distance'] = np.linalg.norm(x_true - x_mean)

        # Store status
        result['status'] = 'done'

    def _analyse(self, results):
        return pfunk.assert_not_deviated_from(
            1.0, 1.0, results, 'distance')

    def _plot(self, results):
        fig = plt.figure()
        plt.title('MCMCSampling on Normal LogPDF with ' + self._method)

        plt.xlabel('Commit')
        plt.ylabel('Distance from mean to true')

        commits, mean, std = pfunk.gather_statistics_per_commit(
            results, 'distance')

        plt.errorbar(commits, mean, yerr=std)

        fig.autofmt_xdate()

        return fig
