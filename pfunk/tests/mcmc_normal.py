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

    def __init__(self, method, nchains, pass_threshold, max_iter=10000):

        # Can't check method here, don't want to import pints
        self._method = str(method)
        self._nchains = int(nchains)
        self._pass_threshold = float(pass_threshold)
        self._max_iter = int(max_iter)

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

        # Check number of chains
        if isinstance(method, pints.SingleChainMCMC) and self._nchains > 1:
            log.warn('SingleChainMCMC run with more than 1 chain.')
        elif isinstance(method, pints.MultiChainMCMC) and self._nchains == 1:
            log.warn('MultiChainMCMC run with only 1 chain.')

        # Create a log pdf
        xtrue = np.array([2, 4])
        sigma = np.diag(np.array([1, 3]))
        log_pdf = pints.toy.GaussianLogPDF(xtrue, sigma)

        # Create a log prior
        log_prior = pints.MultivariateGaussianLogPrior(xtrue + 1, sigma * 2)

        # Generate random points
        x0 = log_prior.sample(self._nchains)

        # Create a realistic sigma - for some methods only!
        sigma = None
        if method == pints.HamiltonianMCMC:
            sigma = np.diag(np.array([1, 3]))

        # Create a sampling routine
        mcmc = pints.MCMCController(
            log_pdf, self._nchains, x0, sigma0=sigma, method=method)
        mcmc.set_parallel(True)

        # Log to file
        if not DEBUG:
            mcmc.set_log_to_screen(False)
        mcmc.set_log_to_file(log_path)

        # Set max iterations
        n_iter = self._max_iter
        n_burn = int(self._max_iter * 0.5)
        n_init = int(self._max_iter * 0.1)
        mcmc.set_max_iterations(n_iter)
        if mcmc.method_needs_initial_phase():
            mcmc.set_initial_phase_iterations(n_init)

        # Run
        chains = mcmc.run()

        if DEBUG:
            import pints.plot
            pints.plot.trace(chains)
            plt.show()

        # Combine chains (weaving, so we can see the combined progress per
        # iteration for multi-chain methods)
        chain = pfunk.weave(chains)

        # Calculate KLD for a sliding window
        n_samples = len(chain)              # Total samples
        n_window = 500 * self._nchains      # Window size
        n_jump = 20 * self._nchains         # Spacing between windows
        iters = list(range(0, n_samples - n_window + n_jump, n_jump))
        result['iters'] = iters
        result['klds'] = [
            log_pdf.kl_divergence(chain[i:i + n_window]) for i in iters]

        # Remove burn-in
        # For multi-chain, multiply by n_chains because we wove the chains
        # together.
        chain = chain[n_burn * self._nchains:]
        log.info('Chain shape (without burn-in): ' + str(chain.shape))
        log.info('Chain mean: ' + str(np.mean(chain, axis=0)))

        # Store kullback-leibler divergence after burn-in
        result['kld'] = log_pdf.kl_divergence(chain)

        # Store effective sample size
        result['ess'] = pints.effective_sample_size(chain)

        # Store status
        result['status'] = 'done'

    def _analyse(self, results):
        return pfunk.assert_not_deviated_from(
            0, self._pass_threshold, results, 'kld')

    def _plot(self, results):

        figs = []

        # Figure: KL per commit
        figs.append(pfunk.plot.variable(
            results,
            'kld',
            'Normal w. ' + self._method,
            'Kullback-Leibler divergence', 3 * self._pass_threshold)
        )

        # Figure: KL over time
        figs.append(pfunk.plot.convergence(
            results,
            'iters',
            'klds',
            'Normal w. ' + self._method,
            'Iteration (sliding window)',
            'Kullback-Leibler divergence',
            0, 10)
        )

        # Figure: ESS per commit
        figs.append(pfunk.plot.variable(
            results,
            'ess',
            'Normal w. ' + self._method,
            'Effective sample size')
        )

        return figs
