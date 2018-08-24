#
# Simplest sampling test: Can we recover a unimodal normal distribution?
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


class MCMCNormal(pfunk.FunctionalTest):
    """
    Runs an MCMCSampling algorithm on a normal LogPDF. Stores the distance of
    the resulting mean to the true solution.

    Arguments:

    ``method``
        A *string* indicating the method to use, e.g. 'AdaptiveCovarianceMCMC'.
        (Must be a string, because we shouldn't import pints before we start
        testing.)

    """

    def __init__(self, method, nchains):

        # Can't check method here, don't want to import pints
        self._method = str(method)
        self._nchains = int(nchains)

        # Create name and initialise
        name = 'mcmc_normal_' + self._method + '_' + str(self._nchains)
        super(MCMCNormal, self).__init__(name)

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
        logpdf = pints.toy.MultimodalNormalLogPDF([xtrue])

        # Generate a random start point
        x0 = xtrue * np.random.normal(0, 1, size=(self._nchains, 2))

        # Create an optimisation problem
        mcmc = pints.MCMCSampling(logpdf, self._nchains, x0, method=method)
        mcmc.set_parallel(True)

        # Log to file
        if not DEBUG:
            mcmc.set_log_to_screen(False)
        mcmc.set_log_to_file(log_path)

        # Set max iterations
        mcmc.set_max_iterations(6000)
        if mcmc.method_needs_initial_phase():
            mcmc.set_initial_phase_iterations(2000)

        # Run
        chains = mcmc.run()

        if DEBUG:
            import matplotlib.pyplot as plt
            import pints.plot
            pints.plot.trace(chains)
            plt.show()

        # Use first chain only
        chain = chains[0]

        # Remove burn-in
        chain = chain[2000:, :]
        log.info('Chain shape (without burn-in): ' + str(chain.shape))
        log.info('Chain mean: ' + str(np.mean(chain, axis=0)))

        # Store true solution
        result['true'] = xtrue
        result['mean_p0'] = np.mean(chain[:, 0])
        result['mean_p1'] = np.mean(chain[:, 1])
        result['std_p0'] = np.std(chain[:, 0])
        result['std_p1'] = np.std(chain[:, 1])

        xmean = np.mean(chain, axis=0)
        result['distance'] = np.linalg.norm(xtrue - xmean)

        # Store effective sample size
        result['ess'] = pints.effective_sample_size(chain)

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

        # Figure: Effective sampling size
        fig = plt.figure()
        figs.append(fig)
        plt.suptitle(pfunk.date())
        plt.title('Normal LogPDF w. ' + self._method)
        plt.xlabel('Commit')
        plt.ylabel('Effective sampling size (mean & std)')
        commits, mean, std = pfunk.gather_statistics_per_commit(
            results, 'ess')
        plt.errorbar(commits, mean, yerr=std, ecolor='k', fmt='o-', capsize=3)
        fig.autofmt_xdate()

        return figs
