#
# Sampling test: Can we recover a simple egg box distribution?
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


class MCMCEggBox(pfunk.FunctionalTest):
    """
    Runs an MCMCSampling algorithm on a simple egg box LogPDF. Stores
    a Kullback-Leibler-based score for the difference between the result and
    the true solution.

    Arguments:

    ``method``
        A *string* indicating the method to use, e.g. 'AdaptiveCovarianceMCMC'.
        (Must be a string, because we shouldn't import pints before we start
        testing.)

    """

    def __init__(self, method, nchains, pass_threshold):

        # Can't check method here, don't want to import pints
        self._method = str(method)
        self._nchains = int(nchains)
        self._pass_threshold = float(pass_threshold)

        # Create name and initialise
        name = 'mcmc_egg_box_' + self._method + '_' + str(self._nchains)
        super(MCMCEggBox, self).__init__(name)

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
        log_pdf = pints.toy.SimpleEggBoxLogPDF(sigma=2, r=4)

        # Generate a random start point
        x0 = np.random.uniform(-20, 20, size=(self._nchains, 2))

        # Create an optimisation problem
        mcmc = pints.MCMCSampling(log_pdf, self._nchains, x0, method=method)
        mcmc.set_parallel(True)

        # Log to file
        if not DEBUG:
            mcmc.set_log_to_screen(False)
        mcmc.set_log_to_file(log_path)

        # Set max iterations
        mcmc.set_max_iterations(10000)
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

        # Calculate KL-based score after every n-th iteration
        n = 100
        iters = list(range(n, len(chain) + n, n))
        result['iters'] = iters
        result['klds'] = [log_pdf.kl_score(chain[:i]) for i in iters]

        # Remove burn-in
        chain = chain[5000:, :]
        log.info('Chain shape (without burn-in): ' + str(chain.shape))
        log.info('Chain mean: ' + str(np.mean(chain, axis=0)))

        # Store kullback-leibler divergence
        kld = log_pdf.kl_score(chain)
        result['kld'] = kld
        log.info('Final KLD: ' + str(kld))

        # Store effective sample size
        ess = pints.effective_sample_size(chain)
        result['ess'] = ess
        log.info('Final ESS: ' + str(ess))

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
            'Banana w. ' + self._method,
            'Iteration',
            'Kullback-Leibler-based score',
            0, 60000)
        )

        # Figure: ESS per commit
        figs.append(pfunk.plot.variable(
            results,
            'ess',
            'Egg box w. ' + self._method,
            'Effective sample size')
        )

        return figs
