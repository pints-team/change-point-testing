#
# Sampling test: Can we recover a simple egg box distribution?
#
# This file is part of Pints Functional Testing.
#  Copyright (c) 2017-2019, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the Pints
#  functional testing software package.
#
import pfunk


class MCMCEggBox(pfunk.FunctionalTest):
    """
    Runs an MCMCSampling algorithm on a simple egg box LogPDF. Stores
    a Kullback-Leibler-based score for the difference between the result and
    the true solution.

    Arguments:

    ``writer_generator``
        A callable that will return a key-value store for test results.
    ``method``
        A *string* indicating the method to use, e.g. 'AdaptiveCovarianceMCMC'.
        (Must be a string, because we shouldn't import pints before we start
        testing.)

    """

    def __init__(self, writer_generator, method, nchains, pass_threshold):

        # Can't check method here, don't want to import pints
        self._method = str(method)
        self._nchains = int(nchains)
        self._pass_threshold = float(pass_threshold)

        # Create name and initialise
        name = 'mcmc_egg_box_' + self._method + '_' + str(self._nchains)
        super(MCMCEggBox, self).__init__(name, writer_generator)

    def _run(self, result):

        import pints
        import pints.toy
        import numpy as np

        import logging
        log = logging.getLogger(__name__)

        DEBUG = False

        # Show method name
        log.info('Using method: ' + self._method)

        # Get method class
        method = getattr(pints, self._method)

        # Check number of chains
        if isinstance(method, pints.SingleChainMCMC) and self._nchains > 1:
            log.warn('SingleChainMCMC run with more than 1 chain.')
        elif isinstance(method, pints.MultiChainMCMC) and self._nchains == 1:
            log.warn('MultiChainMCMC run with only 1 chain.')

        # Create a log pdf
        sigma = 2
        r = 4
        log_pdf = pints.toy.SimpleEggBoxLogPDF(sigma=sigma, r=r)

        # Generate random starting point(s)
        d = 2 * 6 * r * sigma
        log_prior = pints.MultivariateGaussianLogPrior(
            [0, 0], [[d, 0], [0, d]])
        x0 = log_prior.sample(self._nchains)

        # Set up a sampling routine
        mcmc = pints.MCMCController(log_pdf, self._nchains, x0, method=method)
        mcmc.set_parallel(False)  # allow external parallelisation instead

        # Log to file
        if not DEBUG:
            mcmc.set_log_to_screen(False)

        # Set max iterations
        n_iter = 50000
        n_burn = 10000
        n_init = 1000
        mcmc.set_max_iterations(n_iter)
        if mcmc.method_needs_initial_phase():
            mcmc.set_initial_phase_iterations(n_init)

        # Run
        chains = mcmc.run()

        if DEBUG:
            import matplotlib.pyplot as plt
            import pints.plot
            pints.plot.trace(chains)
            plt.show()

        # Combine chains (weaving, so we can see the combined progress per
        # iteration for multi-chain methods)
        chain = pfunk.weave(chains)

        # Remove burn-in
        # For multi-chain, multiply by n_chains because we wove the chains
        # together.
        chain = chain[n_burn * self._nchains:]
        log.info('Chain shape (without burn-in): ' + str(chain.shape))
        log.info('Chain mean: ' + str(np.mean(chain, axis=0)))

        # Store kullback-leibler-based score after burn-in
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
            'Egg box w. ' + self._method,
            'Kullback-Leibler-based score', 3 * self._pass_threshold)
        )

        # Figure: ESS per commit
        figs.append(pfunk.plot.variable(
            results,
            'ess',
            'Egg box w. ' + self._method,
            'Effective sample size')
        )
        figs.append(pfunk.ChangePints().data(results['kld']).figure())


        return figs
